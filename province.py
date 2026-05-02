from PySide6.QtGui import QPixmap, QImage, QBitmap, QTransform, QColor, QPainter, QRegion
from PySide6.QtCore import Qt
from utilities import getFile
from functools import cache
import numpy as np
import re
import os

def blendColors(base: QColor, overlay: QColor) -> QColor:
    a = overlay.alphaF()
    
    r = overlay.redF() * a + base.redF() * (1 - a)
    g = overlay.greenF() * a + base.greenF() * (1 - a)
    b = overlay.blueF() * a + base.blueF() * (1 - a)
    
    return QColor.fromRgbF(r, g, b)

class ProvinceBuilder:
    WIDTH  = 5616
    HEIGHT = 2160
    WHITE_COLOR = QColor(255, 255, 255)
    SELECTION_COLOR = QColor(255, 255, 0, 100)
    def __init__(self, path):
        self.path = path
        self.provinceImage = QImage(getFile(path, "map/provinces.bmp"))
        self.terrainImage = QImage(getFile(self.path, "map/terrain.bmp"))
        self.history_path = getFile(self.path, "history/pops/1836.1.1")
        self.csv = getFile(self.path, "map/definition.csv")
        self.pixmap = QPixmap(self.provinceImage)
        self.reloadPixmap()
        self.provincesPops = self.getPopulation()
        self.provincesColors = self.getProvincesColors()
        self.colorsProvinces = {v: k for k, v in self.provincesColors.items()}
        self.addedProvinces = []
        self.selectedMask = None
    def savePop(self):
        idprovinces = re.compile(r'^(\d+) = {', re.MULTILINE)
        sizeprovinces  = re.compile(r'size = (\d+)', re.MULTILINE)
        def changetext(txt: str) -> str:
            newtext = ""
            id = 0
            offset = 0
            for line in txt.splitlines():
                gotid = idprovinces.search(line)
                gotsize = sizeprovinces.search(line)
                if gotid:
                    id = int(gotid.group(1))
                    offset = 0
                elif gotsize:
                    line = sizeprovinces.sub(f"size = {int(self.provincesPops[id][offset])}", line)
                    offset += 1
                newtext += line + "\n"
            last_size = 0
            return newtext
        for _, _, files in os.walk(self.history_path):
            for txt in files:
                txt_path = getFile(self.history_path, txt)
                with open(txt_path, "r+") as file:
                    newtext = changetext(file.read())
                    file.seek(0)
                    file.write(newtext)
                    file.truncate()
    def selectedProvinces(self) -> list:
        return [str(v) for v in self.addedProvinces]
    def changePopTo(self, val: int):
        population = self.population()
        for k, v in self.provincesPops.items():
            if not k in self.addedProvinces:
                continue
            for i, pop in enumerate(v):
                percentage = pop/population
                newpop = percentage*val
                self.provincesPops[k][i] = newpop
    def population(self) -> int:
        selectedPop = [sum(v) if k in self.addedProvinces else 0 for k, v in self.provincesPops.items()]
        return sum(selectedPop)
    def reloadPixmap(self):
        self.visualpixmap = self.pixmap.copy()
    def getProvincesColors(self) -> map[int, int]:
        rgx = re.compile(r'(\d+)\.?;(\d+)\.?;(\d+)\.?;(\d+)\.?;', re.MULTILINE)
        output = {}
        with open(self.csv, "r", errors="ignore") as file:
            for match in rgx.finditer(file.read()):
                id = int(match.group(1))
                r = int(match.group(2))
                g = int(match.group(3))
                b = int(match.group(4))
                output[id] = QColor(r, g, b).rgb()
        return output
    def getPopulation(self) -> map[int, list[int]]:
        output = {}
        def parseContents(text: str) -> map[int, int]:
            ouptut = {}
            idprovinces = re.compile(r'^(\d+) = {', re.MULTILINE).finditer(text)
            sizeprovinces  = re.compile(r'size = (\d+)', re.MULTILINE).finditer(text)
            lasts  = re.compile(r'^}', re.MULTILINE).finditer(text)

            last_size = None
            for idprovince in idprovinces:
                id = int(idprovince.group(1))
                pos = int(idprovince.span()[1])
                pos_last = next(lasts).span()[1]
                sizes = []
                if not last_size is None:
                    sizes.append(last_size)
                for size in sizeprovinces:
                    pos_size = size.span()[1]
                    if pos_size >= pos_last:
                        last_size = int(size.group(1))
                        break
                    sizes.append(int(size.group(1)))
                output[id] = sizes
            return {}
        for _, _, files in os.walk(self.history_path):
            for txt in files:
                txt_path = getFile(self.history_path, txt)
                with open(txt_path, errors="ignore") as file:
                    contents = parseContents(file.read())
                    output = output | contents
        return output
    def removeSea(self) -> ProvinceBuilder:
        mask = QPixmap(self.terrainImage).createMaskFromColor(self.WHITE_COLOR)
        self.pixmap.setMask(mask)
        self.reloadPixmap()
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
        self.reloadPixmap()
        return self
    def getProvincePixel(self, x: int, y: int) -> QColor:
        return self.provinceImage.pixelColor(x, self.HEIGHT-y)
    def provinceIsSea(self, x: int, y: int) -> bool:
        color = self.terrainImage.pixelColor(x, self.HEIGHT-y)
        if color == self.WHITE_COLOR:
            return True
        return False
    def provinceIsSelected(self, x: int, y: int) -> bool:
        color = self.getProvincePixel(x, y)
        id = self.colorsProvinces[color.rgb()]
        if id in self.addedProvinces:
            return True
        return False
    def updatePixmap(self):
        self.reloadPixmap()
        if self.selectedMask is None:
            return
        painter = QPainter(self.visualpixmap)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.SELECTION_COLOR)
        painter.setClipRegion(self.selectedMask)
        painter.drawRect(self.pixmap.rect())
        painter.end()
    def deselectProvince(self, color: QColor) -> int:
        mask = QRegion(QBitmap.fromImage(self.provinceImage.createMaskFromColor(color.rgb(), Qt.MaskOutColor)))
        id = self.colorsProvinces[color.rgb()]
        self.addedProvinces.remove(id)
        self.selectedMask = self.selectedMask.xored(mask)
        self.updatePixmap()
        return id
    def selectProvince(self, color: QColor) -> int:
        mask = QRegion(QBitmap.fromImage(self.provinceImage.createMaskFromColor(color.rgb(), Qt.MaskOutColor)))
        id = self.colorsProvinces[color.rgb()]
        self.addedProvinces.append(id)
        if self.selectedMask is None:
            self.selectedMask = mask
        else:
            self.selectedMask = self.selectedMask.united(mask)
        self.updatePixmap()
        return id
    def getPixmap(self) -> QPixmap:
        return self.visualpixmap.transformed(QTransform().scale(1, -1))
