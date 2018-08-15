import yaml
import pandas as pd
import chardet
from pathlib import Path
import PyQt5.QtWidgets as Qw

import nestor.keyword as kex
from collections import OrderedDict

# from .. import keyword as kex

# from .helper_objects import *
from .openFilesUI_app import MyOpenFilesWindow
from .selectCSVHeadersUI_app import MySelectCsvHeadersWindow
from .taggingUI_app import MyTaggingToolWindow, TermsOfServiceDialog


class MainWindow:
    def __init__(self):
        self.icnoPtah=None
        self.yamlPath = Path.home()/'.nestor-tmp'
        print(self.yamlPath)
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

        self.csvHeaderMapping_path = self.yamlPath / "csvHeaderMapping.yaml"
        self.csvHeaderOriginal = {
            'issue':
                {
                    'description_problem': 'issue-description_problem',
                    'description_solution': 'issue-description_solution',
                    'description_cause': 'issue-description_cause',
                    'description_effect': 'issue-description_effect',
                    'machine_down': 'issue-machine_down',
                    'necessary_part': 'issue-necessary_part',
                    'part_in_process': 'issue-part_in_process',
                    'cost': 'issue-cost',
                    'id': 'issue-id',

                    'date_machine_down': 'issue-date_machine_down',
                    'date_workorder_start' : 'issue-date_workorder_start',
                    'date_maintenance_technician_arrive': 'issue-date_maintenance_technician_arrive',
                    'date_solution_found': 'issue-date_solution_found',
                    'date_part_ordered': 'issue-date_part_ordered',
                    'date_part_received': 'issue-date_part_received',
                    'date_solution_solve': 'issue-date_solution_solve',
                    'date_machine_up': 'issue-date_machine_up',
                    'date_workorder_completion' : 'issue-date_workorder_completion',
                },
            'technician':
                {
                    'name': 'technician-name',
                    'skills': 'technician-skills',
                    'crafts': 'technician-crafts',
                },
            'operator':
                {
                    'name': 'operator-name'
                },

            'machine':
                {
                    'name': 'machine-name',
                    'manufacturer': 'machine-manufacturer',
                    'locasion': 'machine-locasion',
                    'type': 'machine-type'
                }
            }
        self.csvHeaderOriginal = self.openYAMLConfig_File(self.csvHeaderMapping_path, self.csvHeaderOriginal)

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
        self.window_taggingTool = MyTaggingToolWindow(self.icnoPtah, self.close_taggingUIWindow, self.onClick_windowTaggingTool_selectTab)


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

        # if Ngramm
        if index == 1:
            # self.dataframe_nGram = self.tokenExtractor_nGram.generate_vocabulary_df(init = NEED THIS)
            self.update_ngram_from_1gram(init=self.dataframe_NGram)
            self.window_taggingTool._set_dataframes(dataframe_NGram=self.dataframe_NGram)
        # elif index == 2:
        #     df = self.window_taggingTool.dataframe_completeness
        #     self.window_taggingTool.completenessPlot._set_dataframe(df)
        #     self.window_taggingTool.completenessPlot.plot_it()


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
                print("Searching the good encoding")
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

        print('Updated Ngram definitions from latest 1-gram vocabulary!')


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
                print("yaml file open")
        else:
            config = dict
            with open(yaml_path, 'w') as yamlfile:
                yaml.dump(config, yamlfile)
                print("yaml file created")
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
            yaml.dump(dict, yamlfile)
            print("yaml file save")


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
            print("save and close")
            self.window_taggingTool.onClick_saveButton(self.window_taggingTool.dataframe_1Gram, self.config_new['file']['filePath_1GrammCSV']['path'])
            self.window_taggingTool.onClick_saveButton(self.window_taggingTool.dataframe_NGram, self.config_new['file']['filePath_nGrammCSV']['path'])

        elif choice == Qw.QMessageBox.Cancel:
            print("It's ok if you miss clicked we got your back!!!")
            event.ignore()
        else:
            print("close without saving")
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


