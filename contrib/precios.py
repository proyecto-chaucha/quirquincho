import requests
import logging
from contrib.setexredis import *

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


API_ORIONX = 'https://stats.orionx.com/ticker'
COINS = ['CHA', 'TRX', 'XLM', 'DASH', 'DAI', 'LUK', 'BNB', 'BTC', 'ETH', 'BCH', 'XRP']


def precio(bot, update, args):
    try:
        if args:
            crypto = str(args[0]).upper()
        else:
            crypto = 'BTC'

        if crypto not in COINS:
            raise Exception("Moneda no soportada")

        msg = _orionx('%sCLP' % crypto, update)
    except Exception as e:
        logger.error(str(e))
        msg = "Error >:(\n\n"
        msg += "Modo de uso: /precio [CHA|BTC|LTC|ETH|BCH|XRP|XLM|DASH|DAI|LUK|CLP]"

    logger.info("price(%i) => %s" % (update.message.from_user.id, msg))
    update.message.reply_text("%s" % msg)


def _orionx(crypto, update):
    user = update.message.from_user
    priceMem = getRedisPriceCoin(crypto, user)
    if priceMem != "":
        return "1 {} = {:3,.0f} 🇨🇱".format(crypto.replace('CLP', ''), int(priceMem))
    else:
        response = requests.get(API_ORIONX)
        if response.status_code != 200:
            return 'Error al obtener el precio desde Orionx'

        price = int(response.json().get(crypto).get('lastPrice'))
        setRedisPriceCoin(crypto, user, price)
        return "1 {} = {:3,.0f} 🇨🇱".format(crypto.replace('CLP', ''), price)
