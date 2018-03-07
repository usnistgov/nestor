import sys
from app.taggingUI.openFilesUI_app import MyOpenFilesWindow
from app.taggingUI.selectCSVHeadersUI_app import MySelectCsvHeadersWindow
from app.taggingUI.taggingUI_app import MyTaggingToolWindow

import PyQt5.QtWidgets as Qw

class Main:
    def __init__(self):
        self.window_OpenFiles = MyOpenFilesWindow()
        self.window_selectCSVHeader = MySelectCsvHeadersWindow()
        self.window_taggingTool = MyTaggingToolWindow()

        self.window_OpenFiles.pushButton_openFiles_Save.clicked.connect(self.openWindow_to_selectWindow)
        self.window_selectCSVHeader.pushButton_selectCSVHeaders_save.clicked.connect(self.selectWindow_to_taggingWindow)

        self.window_OpenFiles.show()

    def openWindow_to_selectWindow(self):
        """
           When click on the save button in the OpenFiles Window
           Open the selectCSVHeader Window
           :return:
        """

        # done is True when self.window_OpenFiles.get_AllFilesPath() was executed with success
        done, self.filePath_OriginalCSV, self.filePath_1GrammCSV, self.filePath_nGrammCSV = self.window_OpenFiles.get_AllFilesPath()

        if done:
            print(self.filePath_OriginalCSV)
            print(self.filePath_1GrammCSV)
            print(self.filePath_nGrammCSV)

            self.window_OpenFiles.close()

            self.window_selectCSVHeader.set_CSVHeader(self.filePath_OriginalCSV)
            self.window_selectCSVHeader.init_selectHeaderView()
            self.window_selectCSVHeader.show()

    def selectWindow_to_taggingWindow(self):
        """
        When click on the save button in the selectCSVHeader Window
        Open the taggingTool Window
        :return:
        """
        done, self.list_header_rawText = self.window_selectCSVHeader.get_buttonChecked()

        if done:

            [print(l) for l in self.list_header_rawText]

            # The TFIDF stuff go there

            self.window_selectCSVHeader.close()
            self.window_taggingTool.show()

if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())