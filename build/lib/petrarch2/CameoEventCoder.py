

import logging
import time
import utilities, PETRglobals, PETRreader, petrarch2


class CameoEventCoder:
    
    def __init__(self, config_folder='data/config/', config_file='PETR_config.ini'):
        #cli_args = petrarch2.parse_cli_args()
        utilities.init_logger('PETRARCH.log')
        logger = logging.getLogger('petr_log')
        PETRglobals.RunTimeString = time.asctime()
        logger.info('Using Config file: '+config_file)
        PETRreader.parse_Config(utilities._get_data(config_folder, config_file))
        petrarch2.read_dictionaries()
    
    
    def encode(self, article):
        return petrarch2.gen_cameo_event(article)
     