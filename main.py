import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QPushButton,
    QVBoxLayout, QWidget, QDockWidget
)

from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QCursor, QTransform, QFont
from PyQt5.QtGui import QPixmap


class Board(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

        # Set fixed size for the board
        self.setSceneRect(0, 0, 800, 600)  # Fixed size for the scene (adjust as necessary)

        # Drawing variables
        self.is_drawing = False
        self.is_eraser = False
        self.last_point = None
        self.pen = QPen(Qt.black, 5)
        self.drawing_enabled = False
        self.lines = []

        # Eraser behavior
        self.eraser_size = 20
        self.zoom_factor = 1.0  # Default zoom level

        # For dragging the board
        self.is_dragging = False
        self.drag_start_pos = QPointF(0, 0)

        self.note_sprite = QPixmap("paper_note.jpg")

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
        elif self.is_eraser:
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
        super().mouseReleaseEvent(event)

    def erase_lines(self, event):
        eraser_rect = QRectF(self.mapToScene(event.pos()) - QPointF(self.eraser_size / 2, self.eraser_size / 2),
                             QSizeF(self.eraser_size, self.eraser_size))

        for line in self.lines[:]:
            if eraser_rect.intersects(line.boundingRect()):
                self.scene.removeItem(line)
                self.lines.remove(line)

    def add_note(self):
        rect = QRectF(50, 50, 200, 200)
        note = QGraphicsRectItem(rect)
        note.setBrush(QBrush(QColor("yellow")))
        note.setFlags(
            QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable
        )

        text = QGraphicsTextItem("New Note", note)

        # Set a larger font
        font = QFont("Arial", 12)  # Adjust size as needed
        text.setFont(font)

        text.setTextInteractionFlags(Qt.TextEditorInteraction)

        text_rect = text.boundingRect()
        text.setPos(
            rect.center().x() - text_rect.width() / 2,
            rect.center().y() - text_rect.height() / 2
        )

        self.scene.addItem(note)

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

        # Button to toggle eraser mode
        toggle_eraser_button = QPushButton("Toggle Eraser Mode")
        toggle_eraser_button.clicked.connect(self.board.toggle_eraser)
        button_layout.addWidget(toggle_eraser_button)

        # Button to add a note
        add_note_button = QPushButton("Add Note")
        add_note_button.clicked.connect(self.board.add_note)
        button_layout.addWidget(add_note_button)

        # Create a container for the buttons
        button_container = QWidget()
        button_container.setLayout(button_layout)
        dock.setWidget(button_container)

        self.addDockWidget(Qt.LeftDockWidgetArea, dock)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
