import sys
import yaml
import pandas as pd
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
        self.config_default = self.openYAMLConfig_File(self.yamlPath_config)
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
                                'numberToken_show': None,
                                'similarityMatrix_threshold': None
                                }
                            }
        # instanciate the dataframe
        self.df_Original = None
        self.df_1Gram = None
        self.df_nGram = None


        #instanciate windows
        self.window_OpenFiles = MyOpenFilesWindow(self.icnoPtah)
        self.window_selectCSVHeader = MySelectCsvHeadersWindow(self.icnoPtah)
        self.window_taggingTool = MyTaggingToolWindow(self.icnoPtah)

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
            self.df_Original = pd.read_csv(self.config_new['file']['filePath_OriginalCSV']['path'])

            # set the checkBox in the window
            self.window_selectCSVHeader.set_checkBoxesValues(self.df_Original.columns.values.tolist())

            #if the csv file of the old and the new config are equals the header will be equals
            if self.config_default['file']['filePath_OriginalCSV']['path'] == self.config_new['file']['filePath_OriginalCSV']['path']:
                self.config_new['file']['filePath_OriginalCSV']['headers'] = self.config_default['file']['filePath_OriginalCSV']['headers']

            self.window_selectCSVHeader.set_config(self.config_new)
            self.window_selectCSVHeader.show()

    def selectWindow_to_taggingWindow(self):
        """
        When click on the save button in the selectCSVHeader Window
        Open the taggingTool Window
        :return:
        """
        # TODO GET CONFIG OF PREVIOUS
        done, self.config_new = self.window_selectCSVHeader.get_config(self.config_new)

        #print(self.config_new )

        if done:

            [print(l) for l in self.config_new['file']['filePath_OriginalCSV']['headers']]

            # Clean the natural lang text...merge columns.
            nlp_selector = kex.NLPSelect(columns=self.config_new['file']['filePath_OriginalCSV']['headers'])  # sklearn-style
            clean_rawText = nlp_selector.transform(self.df_Original)  # a series object

            #init the token extractor and clean the raw text
            tokenExtractor = kex.TokenExtractor()  # sklearn-style TF-IDF calc
            list_tokenExtracted = tokenExtractor.fit_transform(clean_rawText)  # helper list of tokens if wanted

            #create the .Gram dataframe
            if self.config_new['file']['filePath_1GrammCSV']['path'] is None:
                filename = self.config_new['file']['filePath_1GrammCSV']['path']
                init = None
            else:
                filename = None
                init = self.config_new['file']['filePath_1GrammCSV']['path']
            self.df_1Gram = tokenExtractor.annotation_assistant(filename=filename, init = init)

            # if self.config_new['file']['filePath_nGrammCSV']['path'] is None:
            #     filename = self.config_new['file']['filePath_nGrammCSV']['path']
            #     init = None
            # else:
            #     filename = None
            #     init = self.config_new['file']['filePath_nGrammCSV']['path']

            #self.df_nGram =tokenExtractor.annotation_assistant(filename=filename, init=init)
            self.df_nGram =None
            #TODO self.df_nGrammCSV = tokenExtractor.annotation_assistant(init=self.config_new['file']['filePath_nGrammCSV']['path'])

            #print(self.df_1GrammCSV)

            #print(self.config_new)
            self.window_selectCSVHeader.close()

            #send the dataframes to the tagging window
            self.window_taggingTool.set_config(self.config_new)

            self.window_taggingTool.set_dataframes(self.df_1Gram, self.df_nGram)
            self.window_taggingTool.show()


    def openYAMLConfig_File(self, yaml_path):
        """
        open a Yaml file based on the given path
        :return: a dictionary
        """
        with open(yaml_path, 'r') as yamlfile:
            config =   yaml.load(yamlfile)
            print("yaml file open")
        return config

    def saveYAMLConfig_File(self, yaml_path, dict):
        """
        save a Yaml file based on the given path
        :return: a dictionary
        """
        with open(yaml_path, 'w') as yamlfile:
            yaml.dump(dict, yamlfile)
            print("yaml file save")


if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())