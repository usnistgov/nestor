import sys
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import *
import PyQt5.QtWidgets as qw
# from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
# from PyQt5.QtWidgets import QAction, QMessageBox, QCheckBox, QProgressBar
# from PyQt5.QtWidgets import QComboBox, QLabel, QStyleFactory, QFontDialog
# from PyQt5.QtWidgets import QCalendarWidget, QColorDialog, QTextEdit, QFileDialog

class Window(qw.QMainWindow):

    def __init__(self):
        """
        core app stuff goes here, like main menu, etc.
        """
        super(Window, self).__init__()
        self.setGeometry(100,100,500,300)
        self.setWindowTitle("PyQT Tuts!")
        self.setWindowIcon(QIcon('yarhar150.png'))

        ### Main Menu
        extractAction = qw.QAction('Get To the Choppah. B|', self)
        extractAction.setShortcut('Ctrl+Q')
        extractAction.setStatusTip('Leave The App')
        # use connect when you do stuff to trigger things
        extractAction.triggered.connect(self.close_application)

        openEditor = qw.QAction('&Editor', self)
        openEditor.setShortcut("Ctrl+E")
        openEditor.setStatusTip('Open Editor')
        openEditor.triggered.connect(self.editor)

        openFile = qw.QAction('&Open File', self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.file_open)

        saveFile = qw.QAction('&Save File', self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.file_save)

        self.statusBar()  # makes it exists, didn't need var

        mainMenu = self.menuBar()  # var; needs to be modified later
        # repeat for other things
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

        editorMenu = mainMenu.addMenu('&Editor')
        editorMenu.addAction(openEditor)

        ### exec home stuff
        self.home()

    def home(self):
        """
        stuff specific to this page
        """
        btn = qw.QPushButton('quit', self)
        # use connect when you do stuff to trigger things
        btn.clicked.connect(self.close_application)  # from QtCore

        # adjust placement of btn
        btn.resize(btn.sizeHint())  # auto sizing based on context
        # btn.resize(btn.minimumSizeHint())  # auto small based on context
        btn.move(0, 100)

        ### add a toolbar
        extractAction = qw.QAction(QIcon('yarhar150.png'), 'Flee the Scene', self)
        extractAction.triggered.connect(self.close_application)
        self.toolBar = self.addToolBar('Extraction')
        self.toolBar.addAction(extractAction)

        fontChoice = qw.QAction('Font', self)
        fontChoice.triggered.connect(self.font_choice)
        self.toolBar = self.addToolBar('Font')
        self.toolBar.addAction(fontChoice)

        color = QColor(0,0,0)
        fontColor = qw.QAction('Font bg Color', self)
        fontColor.triggered.connect(self.color_picker)
        self.toolBar.addAction(fontColor)

        ### Add a checkbox
        checkBox = qw.QCheckBox('Enlarge Window', self)
        checkBox.move(300, 25)
        checkBox.toggle()
        checkBox.stateChanged.connect(self.enlarge_window)

        self.progress = qw.QProgressBar(self)
        self.progress.setGeometry(200, 80, 250, 20)

        self.btn = qw.QPushButton('Download?', self)
        self.btn.move(200, 120)
        self.btn.clicked.connect(self.download)

        ### Style changer gui
        print(self.style().objectName())
        self.styleChoice = qw.QLabel('gtk+', self)

        comboBox = qw.QComboBox(self)
        comboBox.addItem('gtk+')
        comboBox.addItem('motif')
        comboBox.addItem('Windows')
        comboBox.addItem('cde')
        comboBox.addItem('Plastique')
        comboBox.addItem('Cleanlooks')
        comboBox.addItem('windowsvista')
        comboBox.move(25, 250)
        self.styleChoice.move(25, 150)
        comboBox.activated[str].connect(self.style_choice)

        cal = qw.QCalendarWidget(self)
        cal.move(500,200)
        cal.resize(200,200)



        self.show()

    def color_picker(self):
        color = qw.QColorDialog.getColor()
        self.styleChoice.setStyleSheet('QWidget { background-color: %s}' % color.name())

    def editor(self):
        self.textEdit = qw.QTextEdit()
        self.setCentralWidget(self.textEdit)

    def file_open(self):
        name, _ = qw.QFileDialog.getOpenFileName(self, 'Open File')
        file = open(name, 'rt')

        self.editor()
        with file:
            text = file.read()
            self.textEdit.setText(text)

    def file_save(self):
        name,_ = qw.QFileDialog.getSaveFileName(self, 'Save File')
        file = open(name, 'wt')
        text = self.textEdit.toPlainText()
        file.write(text)
        file.close()

    def font_choice(self):
        font, valid = qw.QFontDialog.getFont()
        if valid:
            self.styleChoice.setFont(font)

    def style_choice(self, text):
        self.styleChoice.setText(text)
        qw.QApplication.setStyle(qw.QStyleFactory.create(text))

    def close_application(self):
        # this running means somewhere, an option to leave has been clicked
        choice = qw.QMessageBox.question(self, 'Extract!',
                                      'Get into the Choppa?',
                                      qw.QMessageBox.Yes | qw.QMessageBox.No)
        if choice == qw.QMessageBox.Yes:
            print('Extracting NAAOOWWW!! B|')
            sys.exit()
        else:
            pass

    def enlarge_window(self, state):
        if state == Qt.Checked:
            self.setGeometry(100, 100, 1000, 600)
        else:
            self.setGeometry(100, 100, 500, 300)

    def download(self):
        self.completed = 0
        while self.completed <100:
            self.completed +=0.0001
            self.progress.setValue(self.completed)

if __name__ == "__main__":  # had to add this otherwise app crashed
    def run():
        app = qw.QApplication(sys.argv)
        GUI = Window()
        sys.exit(app.exec_())

    run()