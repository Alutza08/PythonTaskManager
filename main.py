import sys
from multiprocessing.dummy import current_process

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QPushButton, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

class Board(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

        #Drawing variables
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
        super().mouseReleaseEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_drawing = False
            self.last_point = None
        super().mouseReleaseEvent(event)

    def add_note(self):
        rect = QRectF(50,50,100,100)
        note = QGraphicsRectItem(rect)
        note.setBrush(QBrush(QColor("yellow")))
        note.setFlags(
            QGraphicsTextItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable
        )
        text = QGraphicsTextItem("New Note", note)
        text.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.scene.addItem(note)
