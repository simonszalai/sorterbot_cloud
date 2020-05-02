import logging
import logging.handlers

logger = logging.getLogger('SORTERBOT_CLOUD')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# http_handler = logging.handlers.HTTPHandler('localhost:8000', '/log/', method='POST')
http_handler = logging.handlers.HTTPHandler('docker.for.mac.host.internal:8000', '/log/', method='POST')
handler.setFormatter(formatter)
logger.addHandler(http_handler)

logger.setLevel(logging.DEBUG)
logger.setLevel(level=logging.DEBUG)
