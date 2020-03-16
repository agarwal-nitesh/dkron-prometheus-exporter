import logging
import sys

# Setup logging
log_file_name = './prom_exporter.log'
print('Logging to File : ' + log_file_name)
logger = logging.getLogger('prom_logs')
handler = logging.FileHandler(log_file_name)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s')
logging.getLogger('prom_logs').addHandler(logging.StreamHandler(sys.stdout))
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
