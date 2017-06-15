# import logging
# import os
# from logging.handlers import RotatingFileHandler

# FORMART = '%(asctime)s [yunpan] [  %(funcName)s ] %(levelname)s [%(pathname)s--line:%(lineno)d] %(message)s'

# logger = logging.getLogger('yunpan')
# logger.setLevel(logging.WARNING)
# formatter = logging.Formatter(FORMART)

# info = RotatingFileHandler(
#     "info.log", maxBytes=10 * 1024 * 1024, backupCount=5)
# info.setLevel(logging.INFO)
# info.setFormatter(formatter)
# logger.addHandler(info)
