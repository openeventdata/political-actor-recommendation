

import logging
import time
import utilities, PETRglobals, PETRreader, petrarch2


class EventCoder:
    
    def __init__(self, petrGlobal={}, config_folder='data/config/', config_file='PETR_config.ini'):
        #cli_args = petrarch2.parse_cli_args()
        if not petrGlobal:
            utilities.init_logger('PETRARCH.log')
            logger = logging.getLogger('petr_log')
            PETRglobals.RunTimeString = time.asctime()
            logger.info('Using Config file: '+config_file)
            PETRreader.parse_Config(utilities._get_data(config_folder, config_file))
            petrarch2.read_dictionaries()
            print("SUCCESSFULL ON LOADING DICTIONARIES")
        else:
            print ("LOADING FROM MAP")
            self.load(petrGlobal)
        
    
    def encode(self, article):
        return petrarch2.gen_cameo_event(article)
    
    def load(self, petrGlobals):
        PETRglobals.VerbDict = petrGlobals['VerbDict']
        PETRglobals.ActorDict = petrGlobals['ActorDict']
        PETRglobals.ActorCodes = petrGlobals['ActorCodes']
        PETRglobals.AgentDict = petrGlobals['AgentDict']
        PETRglobals.DiscardList = petrGlobals['DiscardList']
        PETRglobals.IssueList = petrGlobals['IssueList']
        PETRglobals.IssueCodes = petrGlobals['IssueCodes']
        PETRglobals.ConfigFileName = petrGlobals['ConfigFileName']
        PETRglobals.VerbFileName = petrGlobals['VerbFileName']
        PETRglobals.ActorFileList = petrGlobals['ActorFileList']
        PETRglobals.AgentFileName = petrGlobals['AgentFileName']
        PETRglobals.DiscardFileName = petrGlobals['DiscardFileName']
        PETRglobals.TextFileList = petrGlobals['TextFileList']
        PETRglobals.EventFileName = petrGlobals['EventFileName']
        PETRglobals.IssueFileName = petrGlobals['IssueFileName']
        PETRglobals.AttributeList = petrGlobals['AttributeList']
        PETRglobals.NewActorLength = petrGlobals['NewActorLength']
        PETRglobals.RequireDyad = petrGlobals['RequireDyad']
        PETRglobals.StoponError = petrGlobals['StoponError']
        PETRglobals.WriteActorRoot = petrGlobals['WriteActorRoot']
        PETRglobals.WriteActorText = petrGlobals['WriteActorText']
        PETRglobals.WriteEventText = petrGlobals['WriteEventText']
        PETRglobals.RunTimeString = petrGlobals['RunTimeString']
        PETRglobals.CodeBySentence = petrGlobals['CodeBySentence']
        PETRglobals.PauseBySentence = petrGlobals['PauseBySentence']
        PETRglobals.PauseByStory = petrGlobals['PauseByStory']
        PETRglobals.CodeBySentence = petrGlobals['CodeBySentence']
        PETRglobals.PauseBySentence = petrGlobals['PauseBySentence']
        PETRglobals.PauseByStory = petrGlobals['PauseByStory']
        PETRglobals.CommaMin = petrGlobals['CommaMin']
        PETRglobals.CommaMax = petrGlobals['CommaMax']
        PETRglobals.CommaBMin = petrGlobals['CommaBMin']
        PETRglobals.CommaBMax = petrGlobals['CommaBMax']
        PETRglobals.CommaEMin = petrGlobals['CommaEMin']
        PETRglobals.CommaEMax = petrGlobals['CommaEMax']
        PETRglobals.stanfordnlp = petrGlobals['stanfordnlp']
        PETRglobals.CodePrimer = petrGlobals['CodePrimer']
        PETRglobals.RootPrimer = petrGlobals['RootPrimer']
        PETRglobals.TextPrimer = petrGlobals['TextPrimer']
    
    
    def get_PETRGlobals(self):
        petrGlobals = {}
        
        petrGlobals['VerbDict'] = PETRglobals.VerbDict
        petrGlobals['ActorDict'] = PETRglobals.ActorDict
        petrGlobals['ActorCodes'] = PETRglobals.ActorCodes
        petrGlobals['AgentDict'] = PETRglobals.AgentDict 
        petrGlobals['DiscardList'] = PETRglobals.DiscardList
        petrGlobals['IssueList'] = PETRglobals.IssueList
        petrGlobals['IssueCodes'] = PETRglobals.IssueCodes

        petrGlobals['ConfigFileName'] = PETRglobals.ConfigFileName
        petrGlobals['VerbFileName'] = PETRglobals.VerbFileName
        petrGlobals['ActorFileList'] = PETRglobals.ActorFileList
        petrGlobals['AgentFileName'] = PETRglobals.AgentFileName
        petrGlobals['DiscardFileName'] = PETRglobals.DiscardFileName
        petrGlobals['TextFileList'] = PETRglobals.TextFileList
        petrGlobals['EventFileName'] = PETRglobals.EventFileName
        petrGlobals['IssueFileName'] = PETRglobals.IssueFileName 
        
        petrGlobals['AttributeList'] = PETRglobals.AttributeList
        
        petrGlobals['NewActorLength'] = PETRglobals.NewActorLength
        petrGlobals['RequireDyad'] = PETRglobals.RequireDyad
        petrGlobals['StoponError'] = PETRglobals.StoponError
        
        petrGlobals['WriteActorRoot'] = PETRglobals.WriteActorRoot
        petrGlobals['WriteActorText'] = PETRglobals.WriteActorText
        petrGlobals['WriteEventText'] = PETRglobals.WriteEventText
        
        petrGlobals['RunTimeString'] = PETRglobals.RunTimeString

        petrGlobals['CodeBySentence'] = PETRglobals.CodeBySentence
        petrGlobals['PauseBySentence'] = PETRglobals.PauseBySentence
        petrGlobals['PauseByStory'] = PETRglobals.PauseByStory
        
        petrGlobals['CodeBySentence'] = PETRglobals.CodeBySentence
        petrGlobals['PauseBySentence'] = PETRglobals.PauseBySentence
        petrGlobals['PauseByStory'] = PETRglobals.PauseByStory
        
 
        petrGlobals['CommaMin'] = PETRglobals.CommaMin
        petrGlobals['CommaMax'] = PETRglobals.CommaMax
        petrGlobals['CommaBMin'] = PETRglobals.CommaBMin
        
        petrGlobals['CommaBMax'] = PETRglobals.CommaBMax
        petrGlobals['CommaEMin'] = PETRglobals.CommaEMin
        petrGlobals['CommaEMax'] = PETRglobals.CommaEMax

        petrGlobals['stanfordnlp'] = PETRglobals.stanfordnlp

       
        petrGlobals['CodePrimer'] = PETRglobals.CodePrimer   
        petrGlobals['RootPrimer'] = PETRglobals.RootPrimer  
        petrGlobals['TextPrimer'] = PETRglobals.TextPrimer
        
        return petrGlobals