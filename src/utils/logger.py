"""
A Python logger to format the logs and send them to the Control Panel using an HTTPHandler.

"""


import os
import logging
import logging.handlers


logger = logging.getLogger('SORTERBOT_CLOUD')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

if os.getenv("CONTROL_PANEL_HOST"):
    http_handler = logging.handlers.HTTPHandler(os.getenv("CONTROL_PANEL_HOST"), '/log/', method='POST')
    handler.setFormatter(formatter)
    logger.addHandler(http_handler)

logger.setLevel(logging.DEBUG)
logger.setLevel(level=logging.DEBUG)
