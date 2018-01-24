
from PyQt5.QtCore import QCoreApplication, Qt, QSize
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
            btn = Qw.QCheckBox(f'{n} - ' + match)
            cond = (df.loc[match, 'alias'] == df.loc[tok, 'alias']) \
                   and (df.loc[match, 'alias'] != '')
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
        self.setFocus()

    def print_table(self, df, vocab_limit=1000):
        temp_df = df.reset_index()
        nrows, ncols = temp_df.shape
        self.setColumnCount(ncols)
        self.setRowCount(min([nrows, vocab_limit]))

        for i in range(self.rowCount()):
            for j in range(ncols):
                self.setItem(i, j, Qw.QTableWidgetItem(str(temp_df.iat[i, j])))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setHorizontalHeaderLabels(temp_df.columns.tolist())
        self.setSelectionBehavior(Qw.QTableWidget.SelectRows)