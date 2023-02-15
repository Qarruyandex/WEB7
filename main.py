import geocoder


def main():
    KEY = ""
    import sys
    from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtCore import Qt
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    class AppWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.initUI()
            self.setFocusPolicy(Qt.StrongFocus)
            self.map = QLabel(self)
            self.text = QLineEdit(self)
            self.index = False
            self.address = QLabel(self)
            self.address.move(5, 470)
            self.address.resize(500, 30)
            self.btn = QPushButton('Сбросить результат', self)
            self.btn.resize(120, 25)
            self.btn.move(100, 0)
            self.btn.clicked.connect(self.clean)
            self.map.resize(500, 500)
            self.map_ll = [36, 56]
            self.point = ()
            self.map_l = 0
            self.map_ls = ['map', 'sat', 'sat,skl']
            self.zoom = 6
            self.refresh_map()

        def initUI(self):
            self.setGeometry(500, 300, 500, 600)

        def clean(self):
            self.point = ()
            self.refresh_map()
            self.address.setText('')

        def keyPressEvent(self, event):
            d = 0.1  # TODO: make a zoom-based delta
            if event.key() == Qt.Key_Return:
                self.map_ll = geocoder.get_coords(self.text.text())
                self.point = self.map_ll.copy()
                self.address.setText(geocoder.geocode(self.text.text())['metaDataProperty']['GeocoderMetaData']['text'])
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
            if event.key() == Qt.Key_F12:
                if self.index:
                    self.address.setText(geocoder.geocode(self.text.text())['metaDataProperty']['GeocoderMetaData']['text'])
                    self.index = False
                else:
                    if geocoder.geocode(self.text.text())["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']:
                        self.address.setText(f"{self.address.text()} индекс: {geocoder.geocode(self.text.text())['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']}")
                        self.index = True
                    else:
                        print('К сожалению, у выбраной точки нет почтового индекса')
            self.refresh_map()

        def refresh_map(self):
            try:
                if self.point:
                    map_params = {
                        "ll": ','.join(map(str, self.map_ll)),
                        "l": self.map_ls[self.map_l],
                        "z": self.zoom,
                        'pt': f"{self.point[0]},{self.point[1]},pm2dgl"
                    }
                else:
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
            except Exception as e:
                print(type(e).__name__)

    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
