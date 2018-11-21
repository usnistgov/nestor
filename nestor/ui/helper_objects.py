import PyQt5.QtGui as Qg
import PyQt5.QtWidgets as Qw
from PyQt5.QtCore import Qt


class QTableWidget_token(Qw.QTableWidget):

    def __init__(self):
        Qw.QTableWidget.__init__(self)
        #TODO set the resiz of the collumn and line to false
        #TODO set the original collunm size based on the header size

    def set_vocabLimit(self,vocab_limite):
        self.vocab_limite = vocab_limite

    def set_dataframe(self, dataframe):
        """set the dataframe

        Parameters
        ----------
        dataframe :
            return:

        Returns
        -------

        """
        #TODO THURSTON why test_app->mywindow->setDataframe Do we need all the mask and stuff ?
        self.dataframe=dataframe

    def printDataframe_tableView(self):
        """print the dataframe into the table view
        :return:

        Parameters
        ----------

        Returns
        -------

        """




        if self.dataframe is not None:

            temp_df = self.dataframe.reset_index()
            nrows, ncols = temp_df.shape
            self.setColumnCount(ncols - 1)  # ignore score column
            self.setRowCount(min([nrows, self.vocab_limite]))
            for i in range(self.rowCount()):
                for j in range(ncols - 1):  # ignore score column
                    self.setItem(i, j, Qw.QTableWidgetItem(str(temp_df.iat[i, j])))

            i
            try:
                for index in self.userUpdate:
                    if index <1000:
                        self.item(index, 0).setBackground(Qg.QColor(77, 255, 184))

            except AttributeError:
                pass

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

    def set_checkBoxes_initial(self, token_list, autoMatch_score, dataframe, alias):
        """create and print the checkboxes
        check it on condition

        Parameters
        ----------
        token_list :
            param autoMatch_score:
        autoMatch_score :
            
        dataframe :
            
        alias :
            

        Returns
        -------

        """
        self.clean_checkboxes()
        for token, score in token_list:
            btn = Qw.QCheckBox(token)
            self.addButton(btn)
            self.layout.addWidget(btn)

            #auto_checked
            if alias is '':
                if score >= autoMatch_score:
                    btn.setChecked(True)
            else:
                if dataframe.loc[btn.text(), 'alias'] == alias:
                    btn.setChecked(True)

        self.spacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.spacer)

    def set_checkBoxes_rechecked(self, token_list, btn_checked):
        """check the button that was send in the btn_checked

        Parameters
        ----------
        token_list :
            param btn_checked:
        btn_checked :
            

        Returns
        -------

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
        """remove all from the layout
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        for btn in self.buttons():
            self.removeButton(btn)
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.layout.removeItem(self.spacer)

    def checkedButtons(self):
        """

        Parameters
        ----------

        Returns
        -------
        type
            :return:

        """
        checkedbtns = []
        for btn in self.buttons():
            if btn.isChecked():
                checkedbtns.append(btn)
        return checkedbtns


class CompositionNGramItem:

    def __init__(self, layout):
        self.layout = layout
        self.nb_onegrame = 0


    def printTokenView(self, layout, token, classification, notes, synonyms):
        """print the view of a given token
        :return:

        Parameters
        ----------
        layout :
            
        token :
            
        classification :
            
        notes :
            
        synonyms :
            

        Returns
        -------

        """
        #Alias
        text_alias = Qw.QLabel()
        text_alias.setText("alias: ")
        text_alias.setObjectName("label_Ngram_conpositionAliasText_" + token )
        layout.addWidget(text_alias, self.nb_onegrame,0, 1,1, Qt.AlignTop)

        label_alias = Qw.QLabel()
        label_alias.setText(token)
        label_alias.setObjectName("label_Ngram_conpositionAliasValue_" + token )
        layout.addWidget(label_alias, self.nb_onegrame,1, 1,1)

        #Classification
        text_classification = Qw.QLabel()
        text_classification.setText("type: ")
        text_classification.setObjectName("label_Ngram_conpositionClassificationText_" + token)
        layout.addWidget(text_classification, self.nb_onegrame+1,0, 1,1,Qt.AlignTop)

        label_ne = Qw.QLabel()
        label_ne.setText(classification)
        label_ne.setObjectName("label_Ngram_conpositionClassificationValue_" + token)
        layout.addWidget(label_ne, self.nb_onegrame + 1, 1, 1,1)

        #Notes
        final_note = []
        char10 = []
        lenght = 0
        if len(notes) > 1:
            for note in notes.split(" "):
                lenght += len(note)
                char10.append(note)
                if lenght > 10:
                    final_note.append(" ".join(char10))
                    char10 = []
                    lenght = 0
            final_note.append(" ".join(char10))
            notes  = "\n".join(final_note)

            text_note = Qw.QLabel()
            text_note.setText("notes: ")
            text_note.setObjectName("label_Ngram_conpositionNotesText_" + token)
            layout.addWidget(text_note, self.nb_onegrame + 2, 0, 1, 1, Qt.AlignTop)

            label_note = Qw.QLabel()
            label_note.setText(str(notes))
            label_note.setObjectName("label_Ngram_conpositionNotesValue_" + token)
            layout.addWidget(label_note, self.nb_onegrame + 2, 1, 1,1)

        #Synonyms
        text_synonyms = Qw.QLabel()
        text_synonyms.setText("synonyms: ")
        text_synonyms.setObjectName("label_Ngram_conpositionASynonymsText_" + token )
        layout.addWidget(text_synonyms, self.nb_onegrame+3,0, 1,1, Qt.AlignTop)

        label_synonyms = Qw.QLabel()
        label_synonyms.setText('\n'.join(synonyms))
        label_synonyms.setObjectName("label_Ngram_conpositionSynonymsValue_" + token)
        layout.addWidget(label_synonyms, self.nb_onegrame + 3, 1, 1,1)

        separator = Qw.QFrame()
        separator.setFrameShape(Qw.QFrame.HLine)
        separator.setFrameShadow(Qw.QFrame.Sunken)
        separator.setObjectName("separator" + token)
        layout.addWidget(separator, self.nb_onegrame+4,0,1,1)
        separator2 = Qw.QFrame()
        separator2.setFrameShape(Qw.QFrame.HLine)
        separator2.setFrameShadow(Qw.QFrame.Sunken)
        separator2.setObjectName("separator" + token)
        layout.addWidget(separator2, self.nb_onegrame+4,1,1,1)

        return layout

    def printView(self, dataframe, token_Ngram):
        """print the information of the

        Parameters
        ----------
        dataframe :
            param token:
        token_Ngram :
            

        Returns
        -------

        """
        self.clearLayout(self.layout)

        for token_1gram in token_Ngram.split(" "):
            match = dataframe[(dataframe['alias'] == token_1gram)|(dataframe.index == token_1gram)]
            item = match.iloc[0]
            synonyms = match.index.tolist()

            gridLayout = Qw.QGridLayout()
            gridLayout.setObjectName("gridLayout_Ngram_Composition" + token_1gram)
            gridLayout = self.printTokenView(gridLayout, token_1gram, item["NE"], item["notes"], synonyms)
            self.layout.addLayout(gridLayout)
            self.nb_onegrame += 5

        verticalSpacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.layout.addItem(verticalSpacer)

    def clearLayout(self,layout):
        """recursive function that clear the widget and the layout inside a given layout

        Parameters
        ----------
        layout :
            return:

        Returns
        -------

        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        self.nb_onegrame = 0



        # except (KeyError, TypeError):
        #     Qw.QMessageBox.about(self, 'cannot plot', "One of the axes you have selected is not in your database")



    #
    #     self.dataframe_Original= dataframe_Original
    # if dataframe_1Gram is not None:
    #     self.dataframe_vocab1Gram=dataframe_1Gram
    #     self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_vocab1Gram)
    #     self.tableWidget_1gram_TagContainer.printDataframe_tableView()
    #     self.update_progress_bar(self.progressBar_1gram_TagComplete, self.dataframe_vocab1Gram)
    #
    # if dataframe_NGram is not None:
    #     self.dataframe_vocabNGram=dataframe_NGram
    #     self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_vocabNGram)
    #     self.tableWidget_Ngram_TagContainer.printDataframe_tableView()
    #     self.update_progress_bar(self.progressBar_Ngram_TagComplete, self.dataframe_vocabNGram)