import pyaml, yaml
import pandas as pd
import chardet
from pathlib import Path
import PyQt5.QtWidgets as Qw


import nestor.keyword as kex
from .openFilesUI_app import MyOpenFilesWindow
from .selectCSVHeadersUI_app import MySelectCsvHeadersWindow
from .taggingUI_app import MyTaggingToolWindow, TermsOfServiceDialog


class MainWindow:
    def __init__(self):
        self.icnoPtah=None
        self.projectPath = Path(__file__).parent.parent.parent
        self.yamlPath = Path.home()/'.nestor-tmp'
        self.yamlPath.mkdir(parents=True, exist_ok=True)
        self.yamlPath_config = self.yamlPath/"ui-config.yaml"
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
            },
            'csvheader_mapping': None
        }
        self.config_default = self.openYAMLConfig_File(self.yamlPath_config, self.config_new)
        self.config_new.update(self.config_default)


        self.csvHeaderMapping_path = self.projectPath/ 'nestor' / 'store_data'/ 'csvHeader.yaml'
        self.csvHeaderOriginal = self.openYAMLConfig_File(self.csvHeaderMapping_path)

        self.tokenExtractor_1Gram = None
        self.tokenExtractor_nGram = None

        # instanciate the dataframe
        self.clean_rawText = None
        self.dataframe_Original = None
        self.dataframe_1Gram = None
        self.dataframe_NGram = None


        #instanciate windows
        self.window_OpenFiles = MyOpenFilesWindow(self.icnoPtah, self.close_otherWindow, self.openWindow_to_selectWindow)
        self.window_selectCSVHeader = MySelectCsvHeadersWindow(self.icnoPtah, self.close_otherWindow, self.selectWindow_to_taggingWindow)
        self.window_taggingTool = MyTaggingToolWindow(self.icnoPtah, self.close_taggingUIWindow)

        self.window_taggingTool.actionFrom_AutoPopulate_From1gramVocab.triggered.connect(self.onClick_windowTaggingTool_selectTab)


        #send the old config value to initialize the view
        self.window_OpenFiles.set_config(self.config_default)
        self.window_OpenFiles.show()

    def onClick_windowTaggingTool_selectTab(self, index):
        """when changing the tab in the taggingUI window (from the 1gram to the Ngram)
        Update the Ngram Dataframe and print it back
        :return:

        Parameters
        ----------
        index :


        Returns
        -------

        """
        self.update_ngram_from_1gram(init=self.dataframe_NGram)
        self.window_taggingTool._set_dataframes(dataframe_NGram=self.dataframe_NGram)

    def openWindow_to_selectWindow(self):
        """When click on the save button in the OpenFiles Window
           Open the selectCSVHeader Window
           :return:

        Parameters
        ----------

        Returns
        -------

        """

        # done is True when self.window_OpenFiles.get_AllFilesPath() was executed with success
        done, self.config_new = self.window_OpenFiles.get_config(self.config_new)

        if done:
            self.window_OpenFiles.close()

            # add values to the original dataframe
            try:
                self.dataframe_Original = pd.read_csv(self.config_new['file']['filePath_OriginalCSV']['path'])
                self.window_taggingTool._set_dataframes(dataframe_Original=self.dataframe_Original)
            except UnicodeDecodeError:
                print("WAIT --> your file are not an UTF8 file, we are searching the good encoding")
                print("(you might want to open it and save it as UTF8 for the next time, it is way faster))")
                encoding = chardet.detect(open(self.config_new['file']['filePath_OriginalCSV']['path'], 'rb').read())['encoding']
                self.dataframe_Original = pd.read_csv(self.config_new['file']['filePath_OriginalCSV']['path'], encoding=encoding)


            #if the csv file of the old and the new config are equals the header will be equals
            if self.config_default['file']['filePath_OriginalCSV']['path'] == self.config_new['file']['filePath_OriginalCSV']['path'] \
                    and self.config_default['file']['filePath_OriginalCSV']['path'] is not None:
                self.config_new['file']['filePath_OriginalCSV']['headers'] = self.config_default['file']['filePath_OriginalCSV']['headers']


            # set the checkBox and the dropdown in the window
            self.window_selectCSVHeader.csvHeaderMapping = self.config_new.get('csvheader_mapping')
            self.window_selectCSVHeader.set_checkBoxesValues(self.dataframe_Original.columns.values.tolist())

            self.window_selectCSVHeader.set_config(self.config_new, self.csvHeaderOriginal)


            self.window_selectCSVHeader.show()

    def selectWindow_to_taggingWindow(self):
        """When click on the save button in the selectCSVHeader Window
        Open the taggingTool Window
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        done, self.config_new = self.window_selectCSVHeader.get_config(self.config_new)

        if done:

            # [print(l) for l in self.config_new['file']['filePath_OriginalCSV']['headers']]

            # Clean the natural lang text...merge columns.
            columns = self.config_new['file']['filePath_OriginalCSV']['headers']
            special_replace = self.config_new.get('special_replace', None)
            nlp_selector = kex.NLPSelect(columns=columns, special_replace=special_replace)  # sklearn-style
            self.clean_rawText = nlp_selector.transform(self.dataframe_Original)  # a series object

            # init the token extractor and clean the raw text
            self.tokenExtractor_1Gram = kex.TokenExtractor()  # sklearn-style TF-IDF calc
            list_tokenExtracted = self.tokenExtractor_1Gram.fit_transform(self.clean_rawText)  # helper list of tokens if wanted

            # create the 1Gram dataframe
            filename1 = Path(self.config_new['file']['filePath_1GrammCSV']['path'])
            self.dataframe_1Gram = kex.generate_vocabulary_df(self.tokenExtractor_1Gram, filename=filename1)

            filename2 = Path(self.config_new['file']['filePath_nGrammCSV']['path'])
            self.update_ngram_from_1gram(filename=filename2)

            self.window_selectCSVHeader.close()

            # send the dataframes to the tagging window
            self.window_taggingTool._set_config(self.config_new, self.csvHeaderOriginal)
            self.window_taggingTool._set_dataframes(self.dataframe_1Gram, self.dataframe_NGram)
            self.window_taggingTool._set_tokenExtractor(tokenExtractor_1Gram= self.tokenExtractor_1Gram)
            self.window_taggingTool._set_cleanRawText(clean_rawText=self.clean_rawText)

            self.window_taggingTool.show()

    def update_ngram_from_1gram(self, filename=None, init=None):
        """update the Bgram dataframe from the new 1gram input

        Parameters
        ----------
        filename :
            param init: (Default value = None)
        init :
             (Default value = None)

        Returns
        -------

        """

        self.clean_rawText_1Gram = kex.token_to_alias(self.clean_rawText, self.dataframe_1Gram)
        self.tokenExtractor_nGram = kex.TokenExtractor(ngram_range=(2, 2))
        list_tokenExtracted = self.tokenExtractor_nGram.fit_transform(self.clean_rawText_1Gram)

        # create the n gram dataframe

        self.dataframe_NGram = kex.generate_vocabulary_df(self.tokenExtractor_nGram, filename=filename, init=init)

        NE_types = self.config_default['NE_info']['NE_types']
        NE_map_rules = self.config_default['NE_info']['NE_map']
        self.dataframe_NGram = kex.ngram_automatch(self.dataframe_1Gram, self.dataframe_NGram, NE_types, NE_map_rules)

        self.window_taggingTool._set_tokenExtractor(tokenExtractor_nGram=self.tokenExtractor_nGram)
        self.window_taggingTool._set_cleanRawText(clean_rawText_1Gram=self.clean_rawText_1Gram)

        #print('Done --> Updated Ngram classification from 1-gram vocabulary!')


    def openYAMLConfig_File(self, yaml_path, dict=None):
        """open a Yaml file based on the given path
        :return: a dictionary

        Parameters
        ----------
        yaml_path :
            
        dict :
             (Default value = None)

        Returns
        -------

        """
        if yaml_path.is_file():
            with open(yaml_path, 'r') as yamlfile:
                config = yaml.load(yamlfile)
                print("OPEN --> YAML file at: ", yaml_path)
        else:
            config = dict
            with open(yaml_path, 'w') as yamlfile:
                pyaml.dump(config, yamlfile)
                print("CREATE --> YAML file at: ", yaml_path)
        return config


    def saveYAMLConfig_File(self, yaml_path, dict):
        """save a Yaml file based on the given path
        :return: a dictionary

        Parameters
        ----------
        yaml_path :
            
        dict :
            

        Returns
        -------

        """
        with open(yaml_path, 'w') as yamlfile:
            pyaml.dump(dict, yamlfile)
            print("SAVE --> YAML file at: ", yaml_path)


    def close_taggingUIWindow(self, event):
        """Trigger when closing the window tagginUI
        :return:

        Parameters
        ----------
        event :
            

        Returns
        -------

        """
        choice = Qw.QMessageBox.question(self.window_taggingTool, 'Shut it Down',
                                  'Do you want to save your changes before closing?',
                                     Qw.QMessageBox.Save | Qw.QMessageBox.Close | Qw.QMessageBox.Cancel)

        self.saveYAMLConfig_File(self.yamlPath_config, self.config_new)
        if choice == Qw.QMessageBox.Save:
            print("SAVE AND CLOSE --> vocab 1gram and Ngram, as well as the config file")
            self.window_taggingTool.onClick_saveButton(self.window_taggingTool.dataframe_1Gram, self.config_new['file']['filePath_1GrammCSV']['path'])
            self.window_taggingTool.onClick_saveButton(self.window_taggingTool.dataframe_NGram, self.config_new['file']['filePath_nGrammCSV']['path'])

        elif choice == Qw.QMessageBox.Cancel:
            print("NOTHING --> config file saved (in case)")
            event.ignore()
        else:
            print("CLOSE NESTOR --> we save your config file so it is easier to open it next time")
            pass


    def close_otherWindow(self, window):
        """trigger when closing the other window
        :return:

        Parameters
        ----------
        window :
            

        Returns
        -------

        """
        self.config_new = window._get_config(self.config_new)
        self.saveYAMLConfig_File(self.yamlPath_config, self.config_new)
        choice = Qw.QMessageBox.question(self.window_taggingTool, 'Shut it Down',
                                         'Do you want to save the new configuration file?',
                                         Qw.QMessageBox.Yes | Qw.QMessageBox.No)

        if choice == Qw.QMessageBox.Yes:
            print('exiting program...')
            app.exec_()


