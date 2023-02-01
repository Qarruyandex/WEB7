def main():
    KEY = ""
    import sys
    from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtCore import Qt
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    class AppWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.initUI()
            self.map = QLabel(self)
            self.map.resize(500, 500)
            self.map_ll = [36, 56]
            self.map_l = 0
            self.map_ls = ['map', 'sat', 'sat,skl']
            self.zoom = 6
            self.refresh_map()

        def initUI(self):
            self.setGeometry(500, 500, 500, 500)

        def keyPressEvent(self, event):
            d = 0.1  # TODO: make a zoom-based delta
            if event.key() == Qt.Key_PageUp and self.zoom < 17:
                self.zoom += 1
            if event.key() == Qt.Key_PageDown and self.zoom > 0:
                self.zoom -= 1
            if event.key() == Qt.Key_Left and self.map_ll[0] > 0:
                self.map_ll[0] -= d
            if event.key() == Qt.Key_Right and self.map_ll[0] < 179:
                self.map_ll[0] += d
            if event.key() == Qt.Key_Down and self.map_ll[1] > 0:
                self.map_ll[1] -= d
            if event.key() == Qt.Key_Up and self.map_ll[1] < 179:
                self.map_ll[1] += d
            if event.key() == Qt.Key_Space:
                self.map_l = (self.map_l + 1) % 3
            self.refresh_map()

        def refresh_map(self):
            map_params = {
                "ll": ','.join(map(str, self.map_ll)),
                "l": self.map_ls[self.map_l],
                "z": self.zoom
            }
            session = requests.Session()
            retry = Retry(total=10, connect=5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('https://', adapter)
            resp = session.get("https://static-maps.yandex.ru/1.x/", params=map_params)
            with open("tmp.png", "wb") as tmp:
                tmp.write(resp.content)
            pixmap = QPixmap()
            pixmap.load("tmp.png")
            self.map.setPixmap(pixmap)

    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
