import json
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QPushButton,
    QVBoxLayout, QWidget, QDockWidget, QSlider, QLabel, QLineEdit, QMenu, QAction, QComboBox, QFileDialog, QColorDialog
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QCursor, QTransform, QFont


class Board(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

        self.setSceneRect(0, 0, 800, 600)
        self.is_drawing = False
        self.is_eraser = False
        self.currently_erasing = False
        self.last_point = None
        self.pen = QPen(Qt.black, 5)
        self.drawing_enabled = False
        self.lines = []

        self.eraser_size = 20
        self.zoom_factor = 1.0
        self.is_dragging = False
        self.drag_start_pos = QPointF(0, 0)
        self.selected_note = None  # Keep track of the selected note

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())

        if isinstance(item, QGraphicsRectItem):  # If the clicked item is a note
            self.selected_note = item  # Track the selected note

            # Create a context menu
            context_menu = QMenu(self)

            # Add Delete action
            delete_action = QAction("Delete Note", self)
            delete_action.triggered.connect(self.delete_selected_note)
            context_menu.addAction(delete_action)

            context_menu.exec_(self.mapToGlobal(event.pos()))

    def delete_selected_note(self):
        if self.selected_note:
            self.scene.removeItem(self.selected_note)  # Remove the selected note from the scene
            self.selected_note = None  # Clear the selected note tracker

    def wheelEvent(self, event):
        # Zoom in when scrolling up, zoom out when scrolling down
        zoom_in = event.angleDelta().y() > 0
        factor = 1.1  # Define zoom factor for zooming in or out

        if zoom_in:
            self.zoom_factor *= factor
        else:
            self.zoom_factor /= factor

        # Set the zoom scale
        self.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))

        # Ensure the zoom factor stays within reasonable limits (prevent over-zooming)
        self.zoom_factor = max(0.1, min(self.zoom_factor, 3.0))  # Set max zoom level to 3x and min to 0.1x

        super().wheelEvent(event)

    def toggle_drawing(self):
        self.drawing_enabled = not self.drawing_enabled
        self.is_eraser = False

    def toggle_eraser(self):
        self.is_eraser = not self.is_eraser
        self.drawing_enabled = False
        if self.is_eraser:
            self.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())

        if isinstance(item, QGraphicsRectItem):  # Check if the clicked item is a note
            super().mousePressEvent(event)
            return  # Prevent board dragging when clicking a note

        if self.drawing_enabled and event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.last_point = self.mapToScene(event.pos())
        elif self.is_eraser and event.button() == Qt.LeftButton:
            self.currently_erasing = True
            if self.currently_erasing:
                self.erase_lines(event)
        elif event.button() == Qt.LeftButton:
            # Start dragging the board
            self.is_dragging = True
            self.drag_start_pos = event.pos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_drawing and self.last_point:
            current_point = self.mapToScene(event.pos())
            line = self.scene.addLine(
                self.last_point.x(),
                self.last_point.y(),
                current_point.x(),
                current_point.y(),
                self.pen,
            )
            self.lines.append(line)
            self.last_point = current_point
        elif self.is_eraser and self.currently_erasing:
            self.erase_lines(event)
        elif self.is_dragging:
            # Reverse the scene movement: subtract delta to move the scene in the opposite direction
            delta = event.pos() - self.drag_start_pos
            self.setSceneRect(self.sceneRect().translated(-delta.x(), -delta.y()))  # Reverse the translation
            self.drag_start_pos = event.pos()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_drawing = False
            self.is_dragging = False
            self.last_point = None
            self.currently_erasing = False
        super().mouseReleaseEvent(event)

    def erase_lines(self, event):
        eraser_rect = QRectF(self.mapToScene(event.pos()) - QPointF(self.eraser_size / 2, self.eraser_size / 2),
                             QSizeF(self.eraser_size, self.eraser_size))

        for line in self.lines[:]:
            if eraser_rect.intersects(line.boundingRect()):
                self.scene.removeItem(line)
                self.lines.remove(line)

    def change_pen_color(self, callback=None):
        color = QColorDialog.getColor(initial=QColor(self.pen.color()), parent=self)
        if color.isValid():
            self.pen.setColor(color)
            if callback:
                callback(color.name())

    def add_note(self, note_text, size="normal"):
        # Define the note sizes
        if size == "small":
            rect = QRectF(50, 50, 150, 150)  # Smaller note size
            font = QFont("Arial", 12)
        elif size == "normal":
            rect = QRectF(50, 50, 200, 200)  # Default note size
            font = QFont("Arial", 16)
        elif size == "large":
            rect = QRectF(50, 50, 250, 250)  # Larger note size
            font = QFont("Arial", 21)

        note = QGraphicsRectItem(rect)
        note.setBrush(QBrush(QColor("yellow")))
        note.setFlags(
            QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable
        )

        text = QGraphicsTextItem(note_text, note)

        # Set a larger font
        text.setFont(font)

        # Enable text wrapping within the note's rectangle
        text.setTextWidth(rect.width() - 10)  # 10px margin
        text.setTextInteractionFlags(Qt.TextEditorInteraction)

        text_rect = text.boundingRect()
        # Position the text at the top-left corner of the note, with a margin
        text.setPos(
            rect.left() + 5,  # 5px margin from the left
            rect.top() + 5    # 5px margin from the top
        )

        self.scene.addItem(note)

    def update_pen_size(self, value):
        self.pen.setWidth(value)

    def update_eraser_size(self, value):
        self.eraser_size = value

    def save_board(self):
        board_data = {
            "notes": [],
            "lines": [],
        }

        for item in self.scene.items():
            if isinstance(item, QGraphicsRectItem) and item.childItems():
                text_item = item.childItems()[0]
                note_data = {
                    "text": text_item.toPlainText(),
                    "pos": [item.scenePos().x(), item.scenePos().y()],
                    "size": [item.rect().width(), item.rect().height()],
                }
                board_data["notes"].append(note_data)

        for line in self.lines:
            line_data = {
                "start": (line.line().x1(), line.line().y1()),
                "end": (line.line().x2(), line.line().y2()),
            }
            board_data["lines"].append(line_data)

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Board", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'w') as file:
                json.dump(board_data, file, indent=4)

    def load_board(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Board", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r') as file:
                board_data = json.load(file)

            self.scene.clear()
            self.lines.clear()

            for note_data in board_data.get("notes", []):
                note_text = note_data["text"]
                width, height = note_data["size"]
                x, y = note_data["pos"]

                rect = QRectF(0, 0, width, height)
                note = QGraphicsRectItem(rect)
                note.setBrush(QBrush(QColor("yellow")))
                note.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)

                text = QGraphicsTextItem(note_text, note)
                text.setFont(QFont("Arial", 16))
                text.setTextWidth(rect.width() - 10)
                text.setPos(5, 5)

                note.setPos(x, y)
                self.scene.addItem(note)

            for line_data in board_data.get("lines", []):
                start = QPointF(*line_data["start"])
                end = QPointF(*line_data["end"])
                line = self.scene.addLine(start.x(), start.y(), end.x(), end.y(), self.pen)
                self.lines.append(line)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager Board")

        self.board = Board()
        self.setCentralWidget(self.board)

        # Add buttons for functionality
        dock = QDockWidget("Tools", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        button_layout = QVBoxLayout()

        # Button to toggle drawing mode
        toggle_drawing_button = QPushButton("Toggle Drawing Mode")
        toggle_drawing_button.clicked.connect(self.board.toggle_drawing)
        button_layout.addWidget(toggle_drawing_button)

        # Button to change pen color
        color_button = QPushButton("Choose Pen Color")
        color_button.clicked.connect(lambda: self.board.change_pen_color(self.update_color_preview))
        button_layout.addWidget(color_button)

        # Label to preview selected pen color
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(40, 20)
        self.color_preview.setStyleSheet(f"background-color: {self.board.pen.color().name()}; border: 2px solid #4B2E2B; border-radius: 3px;")
        button_layout.addWidget(self.color_preview)


        # Button to toggle eraser mode
        toggle_eraser_button = QPushButton("Toggle Eraser Mode")
        toggle_eraser_button.clicked.connect(self.board.toggle_eraser)
        button_layout.addWidget(toggle_eraser_button)

        # Input for note text
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Enter note text here")
        button_layout.addWidget(self.note_input)

        # ComboBox for selecting note size
        self.size_combo_box = QComboBox()
        self.size_combo_box.addItem("Small")
        self.size_combo_box.addItem("Normal")
        self.size_combo_box.addItem("Large")
        button_layout.addWidget(QLabel("Select Note Size:"))
        button_layout.addWidget(self.size_combo_box)

        # Button to add a note
        add_note_button = QPushButton("Add Note")
        add_note_button.clicked.connect(self.add_note)
        button_layout.addWidget(add_note_button)

        # Slider for drawing pen size
        self.pen_size_slider = QSlider(Qt.Horizontal)
        self.pen_size_slider.setRange(1, 20)
        self.pen_size_slider.setValue(5)
        self.pen_size_slider.valueChanged.connect(self.update_pen_size)
        pen_size_label = QLabel(f"Pen Size: {self.pen_size_slider.value()}")
        self.pen_size_slider.valueChanged.connect(lambda: pen_size_label.setText(f"Pen Size: {self.pen_size_slider.value()}"))
        button_layout.addWidget(pen_size_label)
        button_layout.addWidget(self.pen_size_slider)

        # Slider for eraser size
        self.eraser_size_slider = QSlider(Qt.Horizontal)
        self.eraser_size_slider.setRange(1, 50)
        self.eraser_size_slider.setValue(20)
        self.eraser_size_slider.valueChanged.connect(self.update_eraser_size)
        eraser_size_label = QLabel(f"Eraser Size: {self.eraser_size_slider.value()}")
        self.eraser_size_slider.valueChanged.connect(lambda: eraser_size_label.setText(f"Eraser Size: {self.eraser_size_slider.value()}"))
        button_layout.addWidget(eraser_size_label)
        button_layout.addWidget(self.eraser_size_slider)

        # Button to save the board
        save_button = QPushButton("Save Board")
        save_button.clicked.connect(self.board.save_board)
        button_layout.addWidget(save_button)

        # Button to load the board
        load_button = QPushButton("Load Board")
        load_button.clicked.connect(self.board.load_board)
        button_layout.addWidget(load_button)

        # Create a container for the buttons
        button_container = QWidget()
        button_container.setLayout(button_layout)
        dock.setWidget(button_container)

        wood_style = """
        QWidget {
            background-color: #DEB887;  /* BurlyWood */
            color: #4B2E2B;             /* Dark brown text */
            font-family: Arial;
            font-size: 14px;
        }

        QPushButton {
            background-color: #A0522D;
            color: white;
            border: 1px solid #8B4513;
            border-radius: 5px;
            padding: 5px;
        }

        QPushButton:hover {
            background-color: #8B4513;
        }

        QLineEdit, QComboBox {
            background-color: #F5DEB3;  /* Wheat */
            border: 1px solid #A0522D;
            border-radius: 4px;
            padding: 3px;
        }

        QLabel {
            font-weight: bold;
        }

        QSlider::groove:horizontal {
            height: 6px;
            background: #A0522D;
        }

        QSlider::handle:horizontal {
            background: #4B2E2B;
            border: 1px solid #8B4513;
            width: 12px;
            margin: -5px 0;
            border-radius: 6px;
        }

        QDockWidget {
            titlebar-close-icon: none;
            titlebar-normal-icon: none;
            font-weight: bold;
            background-color: #DEB887;
        }
        """
        button_container.setStyleSheet(wood_style)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def add_note(self):
        note_text = self.note_input.text()
        note_size = self.size_combo_box.currentText()

        if note_text:  # Only add the note if text is provided
            if note_size == "Small":
                self.board.add_note(note_text, size="small")
            elif note_size == "Normal":
                self.board.add_note(note_text, size="normal")
            elif note_size == "Large":
                self.board.add_note(note_text, size="large")

            self.note_input.clear()  # Clear input after adding

    def update_pen_size(self, value):
        self.board.update_pen_size(value)

    def update_eraser_size(self, value):
        self.board.update_eraser_size(value)

    def update_color_preview(self, color_name):
        self.color_preview.setStyleSheet(f"background-color: {color_name}; border: 1px solid black;")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
