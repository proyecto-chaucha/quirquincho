import requests
import logging
from setexredis import *

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


API_BTC = 'https://apiv2.bitcoinaverage.com/indices/global/ticker/short?crypto=%s&fiat=USD,CLP'
API_ORIONX = 'https://stats.orionx.com/ticker'


def precio(bot, update, args):
    try:
        if args:
            crypto = str(args[0]).upper()
        else:
            crypto = 'BTC'

        if crypto in ('CHA', 'TRX', 'XLM', 'DASH', 'DAI', 'LUK', 'BNB'):
            msg = _orionx('%sCLP' % crypto,update)
        else:
            msg = _precio(crypto)
    except Exception as e:
        logger.error(str(e))
        msg = "Error >:(\n\n"
        msg += "Modo de uso: /precio [CHA|BTC|LTC|XMR|ETH|BCH|XRP|XLM|DASH|DAI|LUK]"

    logger.info("price(%i) => %s" % (update.message.from_user.id, msg))
    update.message.reply_text("%s" % msg)


def _orionx(crypto,update):
    user = update.message.from_user
    priceMem = getRedisPriceCoin(crypto,user)
    if priceMem != "":
        return "1 {} = {:3,.0f} 🇨🇱".format(crypto.replace('CLP', ''), int(priceMem))
    else:
        response = requests.get(API_ORIONX)
        if response.status_code != 200:
            return 'Error al obtener el precio desde Orionx'

        price = int(response.json().get(crypto).get('lastPrice'))
        setRedisPriceCoin(crypto,user,price)
        return "1 {} = {:3,.0f} 🇨🇱".format(crypto.replace('CLP', ''), price)


def _precio(crypto):
    response = requests.get(API_BTC % crypto)
    if response.status_code != 200:
        return "Moneda no soportada"

    data = response.json()
    clp_price = data["%sCLP" % crypto]["last"]
    usd_price = data["%sUSD" % crypto]["last"]
    print(type(usd_price))
    return "1 {} ({:3,.2f} 🇺🇸) = {:3,.0f} 🇨🇱".format(crypto, usd_price, clp_price)
