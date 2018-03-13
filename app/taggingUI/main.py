import sys
import yaml
import pandas as pd
from PyQt5.QtCore import Qt

from mlp import kex
from app.taggingUI.openFilesUI_app import MyOpenFilesWindow
from app.taggingUI.selectCSVHeadersUI_app import MySelectCsvHeadersWindow
from app.taggingUI.taggingUI_app import MyTaggingToolWindow

import PyQt5.QtWidgets as Qw


class Main:
    def __init__(self):
        #TODO create the YAML file if not exists
        self.icnoPtah="NIST_logo.png"
        self.yamlPath_config = "config.yaml"
        self.config_new = {
            'file':
                {
                    'filePath_OriginalCSV':
                        {
                            'path': None,
                            'headers': None,
                        },
                    'filePath_1GrammCSV':
                        {
                            'path': None
                        },
                    'filePath_nGrammCSV':
                        {
                            'path': None
                        }
                },
            'value':
                {
                    'numberToken_show': 1000,
                    'similarityMatrix_threshold': 50,
                    'similarityMatrix_alreadyChecked': 99
                },
            'NE_info': {
                'NE_map': {'I I': 'I',
                           'S I': 'S I',
                           'P I': 'P I',
                           'I S': 'S I',
                           'I P': 'P I',
                           'S S': 'X',
                           'P P': 'X',
                           'S P': 'X',
                           'P S': 'X'},
                'NE_types': 'IPSUX'
            }
        }
        self.config_default = self.openYAMLConfig_File(self.yamlPath_config, self.config_new)

        # instanciate the dataframe
        self.dataframe_Original = None
        self.dataframe_1Gram = None
        self.dataframe_nGram = None


        #instanciate windows
        self.window_OpenFiles = MyOpenFilesWindow(self.icnoPtah, self.close_otherWindow)
        self.window_selectCSVHeader = MySelectCsvHeadersWindow(self.icnoPtah, self.close_otherWindow)
        self.window_taggingTool = MyTaggingToolWindow(self.icnoPtah, self.close_taggingUIWindow)

        # add connect to windows
        self.window_OpenFiles.pushButton_openFiles_Save.clicked.connect(self.openWindow_to_selectWindow)
        self.window_selectCSVHeader.pushButton_selectCSVHeaders_save.clicked.connect(self.selectWindow_to_taggingWindow)

        #send the old config value to initialize the view
        self.window_OpenFiles.set_config(self.config_default)
        self.window_OpenFiles.show()

    def openWindow_to_selectWindow(self):
        """
           When click on the save button in the OpenFiles Window
           Open the selectCSVHeader Window
           :return:
        """

        # done is True when self.window_OpenFiles.get_AllFilesPath() was executed with success
        done, self.config_new = self.window_OpenFiles.get_config(self.config_new)

        if done:
            print(self.config_new['file']['filePath_OriginalCSV']['path'])
            print(self.config_new['file']['filePath_1GrammCSV']['path'])
            print(self.config_new['file']['filePath_nGrammCSV']['path'] )
            print(self.config_new['value']['numberToken_show'])
            print(self.config_new['value']['similarityMatrix_threshold'])

            self.window_OpenFiles.close()

            # add values to the original dataframe
            self.dataframe_Original = pd.read_csv(self.config_new['file']['filePath_OriginalCSV']['path'])

            # set the checkBox in the window
            self.window_selectCSVHeader.set_checkBoxesValues(self.dataframe_Original.columns.values.tolist())

            #if the csv file of the old and the new config are equals the header will be equals
            if self.config_default['file']['filePath_OriginalCSV']['path'] == self.config_new['file']['filePath_OriginalCSV']['path'] \
                    and self.config_default['file']['filePath_OriginalCSV']['path'] is not None:
                self.config_new['file']['filePath_OriginalCSV']['headers'] = self.config_default['file']['filePath_OriginalCSV']['headers']

            self.window_selectCSVHeader.set_config(self.config_new)
            self.window_selectCSVHeader.show()

    def selectWindow_to_taggingWindow(self):
        """
        When click on the save button in the selectCSVHeader Window
        Open the taggingTool Window
        :return:
        """
        done, self.config_new = self.window_selectCSVHeader.get_config(self.config_new)

        if done:

            [print(l) for l in self.config_new['file']['filePath_OriginalCSV']['headers']]

            # Clean the natural lang text...merge columns.
            nlp_selector = kex.NLPSelect(columns=self.config_new['file']['filePath_OriginalCSV']['headers'])  # sklearn-style
            clean_rawText = nlp_selector.transform(self.dataframe_Original)  # a series object

            #init the token extractor and clean the raw text
            tokenExtractor_1Gram = kex.TokenExtractor()  # sklearn-style TF-IDF calc
            list_tokenExtracted = tokenExtractor_1Gram.fit_transform(clean_rawText)  # helper list of tokens if wanted

            #create the 1Gram dataframe
            filename1 = self.config_new['file']['filePath_1GrammCSV']['path']
            self.dataframe_1Gram = tokenExtractor_1Gram.annotation_assistant(filename=filename1)
            clean_rawText_1Gram = kex.token_to_alias(clean_rawText, self.dataframe_1Gram)
            tokenExtractor_nGram = kex.TokenExtractor(ngram_range=(2, 2))
            list_tokenExtracted = tokenExtractor_nGram.fit_transform(clean_rawText_1Gram)

            #create the n gram dataframe
            filename2 = self.config_new['file']['filePath_nGrammCSV']['path']
            self.dataframe_nGram = tokenExtractor_nGram.annotation_assistant(filename=filename2)

            NE_types = self.config_default['NE_info']['NE_types']
            NE_map_rules = self.config_default['NE_info']['NE_map']
            self.dataframe_nGram = kex.ngram_automatch(self.dataframe_1Gram, self.dataframe_nGram, NE_types, NE_map_rules)

            self.window_selectCSVHeader.close()

            #send the dataframes to the tagging window
            self.window_taggingTool.set_config(self.config_new)
            self.window_taggingTool.set_dataframes(self.dataframe_1Gram, self.dataframe_nGram)

            self.window_taggingTool.show()


    def openYAMLConfig_File(self, yaml_path, dict=None):
        """
        open a Yaml file based on the given path
        :return: a dictionary
        """
        try:
            with open(yaml_path, 'r') as yamlfile:
                config = yaml.load(yamlfile)
                print("yaml file open")
            return config
        except FileNotFoundError:
            with open(yaml_path, 'w') as yamlfile:
                yaml.dump(dict, yamlfile)
                print("yaml file created")
            return dict


    def saveYAMLConfig_File(self, yaml_path, dict):
        """
        save a Yaml file based on the given path
        :return: a dictionary
        """
        with open(yaml_path, 'w') as yamlfile:
            yaml.dump(dict, yamlfile)
            print("yaml file save")


    def close_taggingUIWindow(self):
        """
        Trigger when closing the window tagginUI
        :return:
        """
        choice = Qw.QMessageBox.question(self.window_taggingTool, 'Shut it Down',
                                  'Do you want to save your changes before closing?',
                                     Qw.QMessageBox.Yes | Qw.QMessageBox.No)

        self.saveYAMLConfig_File(self.yamlPath_config, self.config_new)
        if choice == Qw.QMessageBox.Yes:
            self.window_taggingTool.onClick_saveButton(self.window_taggingTool.dataframe_1Gram, self.config_new['file']['filePath_1GrammCSV']['path'])
            self.window_taggingTool.onClick_saveButton(self.window_taggingTool.dataframe_NGram, self.config_new['file']['filePath_nGrammCSV']['path'])
            print('exiting program...')
            app.exec_()


    def close_otherWindow(self, window):
        """
        trigger when closing the other window
        :return:
        """
        self.config_new = window.get_config(self.config_new)
        choice = Qw.QMessageBox.question(self.window_taggingTool, 'Shut it Down',
                                         'Do you want to save the new configuration file?',
                                         Qw.QMessageBox.Yes | Qw.QMessageBox.No)

        if choice == Qw.QMessageBox.Yes:
            self.saveYAMLConfig_File(self.yamlPath_config, self.config_new)
            print('exiting program...')
            app.exec_()


if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())

