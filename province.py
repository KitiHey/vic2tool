from PySide6.QtGui import QPixmap, QImage, QBitmap, QTransform, QColor
from utilities import getFile
import numpy as np

class ProvinceBuilder:
    WIDTH  = 5616
    HEIGHT = 2160
    def __init__(self, path):
        self.path = path
        self.provinceImage = QImage(getFile(path, "map/provinces.bmp"))
        self.pixmap = QPixmap(self.provinceImage)
    def removeSea(self) -> ProvinceBuilder:
        mask = QPixmap(getFile(self.path, "map/rivers.bmp")).createMaskFromColor(QColor(255, 0, 128))
        self.pixmap.setMask(mask)
        return self
    def qimgToArray(self, inputImg: QImage) -> np.ndarray:
        img = inputImg.convertToFormat(QImage.Format.Format_RGBA8888)
        ptr = img.bits()    
        arr = np.frombuffer(ptr, np.uint8).reshape((self.HEIGHT, img.bytesPerLine() // 4, 4))
        return arr[:, :self.WIDTH, :].copy()
    def arrayToQimg(self, arr: np.ndarray) -> QImage:
        img = QImage(self.WIDTH, self.HEIGHT, QImage.Format.Format_RGBA8888)
        ptr = img.bits()
        ptr_view = np.frombuffer(ptr, np.uint8).reshape((self.HEIGHT, img.bytesPerLine() // 4, 4))
        ptr_view[:, :self.WIDTH, :] = arr
        return img.copy()
    def removeProvinceColors(self) -> ProvinceBuilder:        
        newimage = self.pixmap.toImage()
        #for i in range(self.WIDTH):
        #    for j in range(self.HEIGHT):
        #        pixelColor = QColor(self.provinceImage.pixel(i, j))
        #        boundary = False
        #        for x, y in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        #            if i+x >= 0 and j+y > 0 and i+x < self.WIDTH and j+y < self.HEIGHT and QColor(self.provinceImage.pixel(i+x, j+y)) != pixelColor:
        #                boundary = True
        #        if boundary:
        #            newimage.setPixel(i, j, 0x000000)
        #        else:
        #            newimage.setPixel(i, j, 0xFFFFFF)
        arr = self.qimgToArray(self.provinceImage)
        rgb = arr[:, :, :3]
        
        left  = np.roll(rgb,  1, axis=1)
        right = np.roll(rgb, -1, axis=1)
        up    = np.roll(rgb,  1, axis=0)
        down  = np.roll(rgb, -1, axis=0)
        
        boundary = (
            (rgb != left).any(axis=2) |
            (rgb != right).any(axis=2) |
            (rgb != up).any(axis=2) |
            (rgb != down).any(axis=2)
        )
        
        out = np.ones_like(rgb) * 255
        out[boundary] = 0
        
        out_rgba = np.dstack([out, out, out, np.full(out.shape[:2], 255, dtype=np.uint8)])
        out_rgba = out_rgba[:, :, :4]
        self.pixmap = QPixmap(self.arrayToQimg(out_rgba))
        return self
    def getPixmap(self) -> QPixmap:
        return self.pixmap.transformed(QTransform().scale(1, -1))
