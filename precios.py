import requests
import logging

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

        if crypto in ('CHA', 'LUK'):
            msg = _orionx('%sCLP' % crypto)
        else:
            msg = _precio(crypto)
    except Exception as e:
        logger.error(str(e))
        msg = "Error >:(\n\n"
        msg += "Modo de uso: /precio [BTC|LTC|XMR|ETH|BCH|XRP|XLM]"

    logger.info("price(%i) => %s" % (update.message.from_user.id, msg))
    update.message.reply_text("%s" % msg)


def btc(bot, update, args):
    precio(bot, update, ('BTC',))


def eth(bot, update, args):
    precio(bot, update, ('ETH',))


def bch(bot, update, args):
    precio(bot, update, ('BCH',))


def cha(bot, update):
    try:
        msg = _orionx("CHACLP")
    except Exception as e:
        logger.error(str(e))
        msg = "Error >:("

    logger.info("cha(%i) => %s" % (update.message.from_user.id, msg))
    update.message.reply_text("%s" % msg)


def luk(bot, update):
    try:
        msg = _orionx("LUKCLP")
    except Exception as e:
        logger.error(str(e))
        msg = "Error >:("

    logger.info("luk(%i) => %s" % (update.message.from_user.id, msg))
    update.message.reply_text("%s" % msg)


def _orionx(crypto):
    response = requests.get(API_ORIONX)
    if response.status_code != 200:
        return 'Error al obtener el precio desde Orionx'

    price = int(response.json().get(crypto).get('lastPrice'))
    return "1 %s = %d 🇨🇱" % (crypto.replace('CLP', ''), price)


def _precio(crypto):
    response = requests.get(API_BTC % crypto)
    if response.status_code != 200:
        return "Moneda no soportada"

    data = response.json()
    clp_price = data["%sCLP" % crypto]["last"]
    usd_price = data["%sUSD" % crypto]["last"]
    return "1 {} ({:3,.2f} 🇺🇸) = {:3,.0f} 🇨🇱".format(crypto, usd_price, clp_price)
