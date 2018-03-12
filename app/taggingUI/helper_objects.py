import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw
from sympy.core.tests.test_arit import same_and_same_prec


class QTableWidget_token(Qw.QTableWidget):

    def __init__(self):
        Qw.QTableWidget.__init__(self)
        #TODO set the resiz of the collumn and line to false
        #TODO set the original collunm size based on the header size

    def set_vocabLimit(self,vocab_limite):
        self.vocab_limite = vocab_limite

    def set_dataframe(self, dataframe):
        """
        set the dataframe
        :param dataframe:
        :return:
        """
        #TODO THURSTON why test_app->mywindow->setDataframe Do we need all the mask and stuff ?
        self.dataframe=dataframe

    def printDataframe_tableView(self):
        """
        print the dataframe into the table view
        :return:
        """

        if self.dataframe is not None:
            temp_df = self.dataframe.reset_index()
            nrows, ncols = temp_df.shape
            self.setColumnCount(ncols - 1)  # ignore score column
            self.setRowCount(min([nrows, self.vocab_limite]))
            for i in range(self.rowCount()):
                for j in range(ncols - 1):  # ignore score column
                    self.setItem(i, j, Qw.QTableWidgetItem(str(temp_df.iat[i, j])))

            self.resizeColumnsToContents()
            self.resizeRowsToContents()
            self.setHorizontalHeaderLabels(temp_df.columns.tolist()[:-1])  # ignore score column
            self.setSelectionBehavior(Qw.QTableWidget.SelectRows)

class QButtonGroup_similarityPattern(Qw.QButtonGroup):

    def __init__(self, layout):
        Qw.QButtonGroup.__init__(self)
        self.setExclusive(False)
        self.layout = layout
        self.spacer=None

    def set_checkBoxes_initial(self, token_list, autoMatch_score):
        """
        create and print the checkboxes
        :param token_list:
        :param autoMatch_score:
        :return:
        """
        self.clean_checkboxes()
        for token, score in token_list:
            btn = Qw.QCheckBox(token)
            if score >= autoMatch_score:
                btn.toggle()
            self.addButton(btn)
            self.layout.addWidget(btn)

        self.spacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.spacer)

    def set_checkedBoxes(self, dataframe, alias):
        """
        lookup in the dataframe if a token has the same alias and toggle it if it is not
        :return:
        """
        same_tok = None

        for btn in self.buttons():
            if dataframe.loc[btn.text(), 'alias'] == alias and btn.isChecked() == False:
                btn.toggle()


    def set_checkBoxes_rechecked(self, token_list, btn_checked):
        """
        check the button that was send in the btn_checked
        :param token_list:
        :param btn_checked:
        :return:
        """
        self.clean_checkboxes()
        for token, score in token_list:
            btn = Qw.QCheckBox(token)
            if token in btn_checked:
                btn.toggle()
            self.addButton(btn)
            self.layout.addWidget(btn)

        self.spacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.spacer)

    def clean_checkboxes(self):
        """
        remove all from the layout
        :return:
        """
        for widg in self.buttons():
            self.removeButton(widg)
            self.layout.removeWidget(widg)
            widg.deleteLater()
        self.layout.removeItem(self.spacer)

    def checkedButtons(self):
        """
        return the list of all checked buttons
        :return:
        """
        checkedbtns = []
        for btn in self.buttons():
            if btn.isChecked():
                checkedbtns.append(btn)
        return checkedbtns




# class My1gTokenLayout:
#
#     def __init__(self, layout, df):
#         self.layout = layout
#         self.df_onegrame = df[df['NE'].notnull() & df['alias'].notnull()].groupby("alias")
#         self.nb_onegrame = 0
#
#     def print_lookup_token(self, alias):
#         tokens = alias.split(" ")
#         self.clearLayout()
#         for token in tokens:
#             ne, note, synonym = self.token_info(token)
#             self.print_token_info(token, ne, note, synonym)
#             self.nb_onegrame += 1
#
#         verticalSpacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
#         self.layout.addItem(verticalSpacer)
#
#     def clearLayout(self):
#         for i in reversed(range(self.layout.count())):
#             if self.layout.itemAt(i).widget() is not None:
#                 self.layout.itemAt(i).widget().deleteLater()
#         self.nb_onegrame = 0
#
#     def token_info(self, token):
#         try :
#             ne = self.df_onegrame.get_group(token).NE[0]
#             note = self.df_onegrame.get_group(token).notes[0]
#             synonym = "\n".join(self.df_onegrame.get_group(token).index.tolist())
#         except KeyError:
#             print(token, " not in the dataframe")
#             ne = ""
#             note = ""
#             synonym = ""
#
#         return ne, note, synonym
#
#     def print_token_info(self, token, ne, note, synonyms):
#         localization = self.nb_onegrame * 5
#
#         text_alias = Qw.QLabel()
#         text_alias.setText("ALIAS: ")
#         text_alias.setObjectName("text_alias")
#         self.layout.addWidget(text_alias, localization,0)
#
#         text_classification = Qw.QLabel()
#         text_classification.setText("CLASSIFICATION: ")
#         text_classification.setObjectName("text_classification")
#         self.layout.addWidget(text_classification, localization+1,0)
#
#         text_note = Qw.QLabel()
#         text_note.setText("NOTES: ")
#         text_note.setObjectName("text_note")
#         self.layout.addWidget(text_note, localization+2,0)
#
#         text_synonyms = Qw.QLabel()
#         text_synonyms.setText("SYNONYMS: ")
#         text_synonyms.setObjectName("text_synonyms")
#         self.layout.addWidget(text_synonyms, localization+3,0)
#
#         label_alias = Qw.QLabel()
#         label_alias.setText(token)
#         label_alias.setObjectName("label_alias")
#         self.layout.addWidget(label_alias, localization+0,1)
#
#         label_ne = Qw.QLabel()
#         label_ne.setText(ne)
#         label_ne.setObjectName("label_classification")
#         self.layout.addWidget(label_ne, localization + 1,1)
#
#         label_note = Qw.QLabel()
#         label_note.setText(str(note))
#         label_note.setObjectName("label_note")
#         self.layout.addWidget(label_note,localization+2,1)
#
#         label_synonyms = Qw.QLabel()
#         label_synonyms.setText(synonyms)
#         label_synonyms.setObjectName("label_synonyms")
#         self.layout.addWidget(label_synonyms,localization + 3,1)
#
#         self.separator = Qw.QFrame()
#         self.separator.setFrameShape(Qw.QFrame.HLine)
#         self.separator.setFrameShadow(Qw.QFrame.Sunken)
#         self.separator.setObjectName("separator")
#         self.layout.addWidget(self.separator, localization+4,0)
#         self.separator2 = Qw.QFrame()
#         self.separator2.setFrameShape(Qw.QFrame.HLine)
#         self.separator2.setFrameShadow(Qw.QFrame.Sunken)
#         self.separator2.setObjectName("separator")
#         self.layout.addWidget(self.separator2, localization+4,1)
#
