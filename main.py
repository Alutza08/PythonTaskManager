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
            
