import logging
from Utils.Utils import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s\'%(msecs)03d %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='terminal'+today()+'_'+time()+'.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logging.info('Start logging...')
logger = logging.getLogger('info')


def print(_str):
    logger.debug(_str)