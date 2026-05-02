def popSelector(window, builder: ProvinceBuilder):
    window.popSelectorImg.setPixmap(builder.getPixmap())

    def updateValues():
        window.popChanged.setText(str(builder.population()))
        window.currentPop.setText(str(builder.population()))
        window.removedPop.setText("0")
        window.selectedProvinces.setText(", ".join(builder.selectedProvinces()))
    def clickedSelector(x, y):
        if builder.provinceIsSea(x, y):
            return
        color = builder.getProvincePixel(x, y)
        if builder.provinceIsSelected(x, y):
            builder.deselectProvince(color)
        else:
            builder.selectProvince(color)

        window.popSelectorImg.setPixmap(builder.getPixmap())
        updateValues()
    def changePop():
        try:
            txt = str(eval(window.popChanged.text()))
        except:
            txt = window.currentPop.text()
        window.popChanged.setText(txt)
        window.removedPop.setText(str(int(float(window.currentPop.text())-float(txt))))
    def confirmChanges():
        builder.changePopTo(int(float(window.popChanged.text())))
        updateValues()
    def saveChanges():
        builder.savePop()
    def changeDate(index):
        try:
            builder.changeDate(index)
            updateValues()
        except FileNotFoundError as e:
            errorOut(window, str(e))
            window.dateDropdown.setCurrentIndex(builder.indexDate())
    def clearSelection():
        builder.clearSelection()
        window.popSelectorImg.setPixmap(builder.getPixmap())
        updateValues()

    window.dateDropdown.addItems(builder.allDates())

    window.popSelectorImg.installEventFilter(window)
    window.popSelectorImg.clicked.connect(clickedSelector)
    window.popChanged.returnPressed.connect(changePop)
    window.confirmPopChange.clicked.connect(confirmChanges)
    window.savePopChange.clicked.connect(saveChanges)
    window.dateDropdown.activated.connect(changeDate)
    window.clearPopMap.clicked.connect(clearSelection)
