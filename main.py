import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QPushButton, QVBoxLayout, QWidget, QDockWidget
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor


class Board(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

        # Drawing variables
        self.is_drawing = False
        self.last_point = None
        self.pen = QPen(Qt.black, 2)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.last_point = self.mapToScene(event.pos())
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
            self.last_point = current_point
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_drawing = False
            self.last_point = None
        super().mouseReleaseEvent(event)

    def add_note(self):
        rect = QRectF(50, 50, 100, 100)
        note = QGraphicsRectItem(rect)
        note.setBrush(QBrush(QColor("yellow")))
        note.setFlags(
            QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable
        )
        text = QGraphicsTextItem("New Note", note)
        text.setTextInteractionFlags(Qt.TextEditorInteraction)
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

