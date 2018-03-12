import pandas as pd
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw


class MyQButtonGroup(Qw.QButtonGroup):

    def __init__(self, layout):
        super(MyQButtonGroup, self).__init__()
        self.setExclusive(False)
        self.layout = layout

    def update_checkboxes(self, tok, matches, df):
        self.clean_checkboxes()
        self.create_checkboxes(tok, matches, df)
        self.set_shortcut()

    def clean_checkboxes(self):
        for widg in self.buttons():
            self.removeButton(widg)
            self.layout.removeWidget(widg)
            widg.deleteLater()

    def create_checkboxes(self, tok, matches, df):

        nbr_widget = self.layout.count()
        for n, (match, score) in enumerate(matches):
            # btn = Qw.QCheckBox(f'{n} - ' + match)
            btn = Qw.QCheckBox(match)
            # print(type(match), type(tok))
            print("------------------")
            print(match)
            print(tok)
            same_tok = df.loc[match, 'alias'] == df.loc[tok, 'alias']
            no_alias = df.loc[match, 'alias'] != ''
            # print(df.loc[match, 'alias'], df.loc[tok, 'alias'])
            # print(same_tok, no_alias)
            cond = same_tok and no_alias
            if (match == tok) or cond:
                btn.toggle()
            self.addButton(btn)
            self.layout.insertWidget(self.layout.count() - nbr_widget, btn)

    def set_shortcut(self):
        """
        Create the shorcut for all the checkbox
        """

        for n, btn in enumerate(self.buttons()):
            btn.setShortcut(f'Alt+{n}')


class MyQTableWidget(Qw.QTableWidget):

    def __init__(self, Qwidget, window):
        super(MyQTableWidget, self).__init__(Qwidget)

        sizePolicy = Qw.QSizePolicy(Qw.QSizePolicy.Expanding, Qw.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(16777215, 16777215))
        self.setEditTriggers(Qw.QAbstractItemView.EditKeyPressed)
        self.setTabKeyNavigation(False)
        self.setDragDropOverwriteMode(False)
        self.setSelectionMode(Qw.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(Qw.QAbstractItemView.SelectRows)
        self.setObjectName("vocabTableWidget")
        self.setColumnCount(0)
        self.setRowCount(0)


    def print_table(self, df, vocab_limit=1000):
        temp_df = df.reset_index()
        nrows, ncols = temp_df.shape
        self.setColumnCount(ncols - 1)  # ignore score column
        self.setRowCount(min([nrows, vocab_limit]))

        for i in range(self.rowCount()):
            for j in range(ncols - 1):  # ignore score column
                self.setItem(i, j, Qw.QTableWidgetItem(str(temp_df.iat[i, j])))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setHorizontalHeaderLabels(temp_df.columns.tolist()[:-1])  # ignore score column
        self.setSelectionBehavior(Qw.QTableWidget.SelectRows)


class My1gTokenLayout:

    def __init__(self, layout, df):
        self.layout = layout
        self.df_onegrame = df[df['NE'].notnull() & df['alias'].notnull()].groupby("alias")
        self.nb_onegrame = 0

    def print_lookup_token(self, alias):
        tokens = alias.split(" ")
        self.clearLayout()
        for token in tokens:
            ne, note, synonym = self.token_info(token)
            self.print_token_info(token, ne, note, synonym)
            self.nb_onegrame += 1

        verticalSpacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.layout.addItem(verticalSpacer)

    def clearLayout(self):
        for i in reversed(range(self.layout.count())):
            if self.layout.itemAt(i).widget() is not None:
                self.layout.itemAt(i).widget().deleteLater()
        self.nb_onegrame = 0

    def token_info(self, token):
        try :
            ne = self.df_onegrame.get_group(token).NE[0]
            note = self.df_onegrame.get_group(token).notes[0]
            synonym = "\n".join(self.df_onegrame.get_group(token).index.tolist())
        except KeyError:
            print(token, " not in the dataframe")
            ne = ""
            note = ""
            synonym = ""

        return ne, note, synonym

    def print_token_info(self, token, ne, note, synonyms):
        localization = self.nb_onegrame * 5

        text_alias = Qw.QLabel()
        text_alias.setText("ALIAS: ")
        text_alias.setObjectName("text_alias")
        self.layout.addWidget(text_alias, localization,0)

        text_classification = Qw.QLabel()
        text_classification.setText("CLASSIFICATION: ")
        text_classification.setObjectName("text_classification")
        self.layout.addWidget(text_classification, localization+1,0)

        text_note = Qw.QLabel()
        text_note.setText("NOTES: ")
        text_note.setObjectName("text_note")
        self.layout.addWidget(text_note, localization+2,0)

        text_synonyms = Qw.QLabel()
        text_synonyms.setText("SYNONYMS: ")
        text_synonyms.setObjectName("text_synonyms")
        self.layout.addWidget(text_synonyms, localization+3,0)

        label_alias = Qw.QLabel()
        label_alias.setText(token)
        label_alias.setObjectName("label_alias")
        self.layout.addWidget(label_alias, localization+0,1)

        label_ne = Qw.QLabel()
        label_ne.setText(ne)
        label_ne.setObjectName("label_classification")
        self.layout.addWidget(label_ne, localization + 1,1)

        label_note = Qw.QLabel()
        label_note.setText(str(note))
        label_note.setObjectName("label_note")
        self.layout.addWidget(label_note,localization+2,1)

        label_synonyms = Qw.QLabel()
        label_synonyms.setText(synonyms)
        label_synonyms.setObjectName("label_synonyms")
        self.layout.addWidget(label_synonyms,localization + 3,1)

        self.separator = Qw.QFrame()
        self.separator.setFrameShape(Qw.QFrame.HLine)
        self.separator.setFrameShadow(Qw.QFrame.Sunken)
        self.separator.setObjectName("separator")
        self.layout.addWidget(self.separator, localization+4,0)
        self.separator2 = Qw.QFrame()
        self.separator2.setFrameShape(Qw.QFrame.HLine)
        self.separator2.setFrameShadow(Qw.QFrame.Sunken)
        self.separator2.setObjectName("separator")
        self.layout.addWidget(self.separator2, localization+4,1)



# print()
# print()