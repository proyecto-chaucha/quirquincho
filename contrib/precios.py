import requests
import logging
from contrib.setexredis import *

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


API_BTC = 'https://apiv2.bitcoinaverage.com/indices/global/ticker/short?crypto=%s&fiat=USD,CLP'
API_ORIONX = 'https://stats.orionx.com/ticker'
CURRENCIES = {
    'CLP': '🇨🇱',
    'EUR': '🇪🇺',
    'JPY': '🇯🇵',
    'MXN': '🇲🇽',
    'GBP': '🇬🇧',
    'ARS': '🇦🇷',
}


def precio(bot, update, args):
    try:
        if args:
            crypto = str(args[0]).upper()
        else:
            crypto = 'BTC'

        if crypto in ('CHA', 'TRX', 'XLM', 'DASH', 'DAI', 'LUK', 'BNB'):
            msg = _orionx('%sCLP' % crypto, update)
        elif crypto in CURRENCIES:
            msg = _clp(crypto)
        else:
            msg = _precio(crypto)
    except Exception as e:
        logger.error(str(e))
        msg = "Error >:(\n\n"
        msg += "Modo de uso: /precio [CHA|BTC|LTC|XMR|ETH|BCH|XRP|XLM|DASH|DAI|LUK|CLP]"

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


def _precio(crypto):
    response = requests.get(API_BTC % crypto)
    if response.status_code != 200:
        return "Moneda no soportada"

    data = response.json()
    clp_price = data["%sCLP" % crypto]["last"]
    usd_price = data["%sUSD" % crypto]["last"]
    return "1 {} ({:3,.2f} 🇺🇸) = {:3,.0f} 🇨🇱".format(crypto, usd_price, clp_price)


def _clp(target_currency):
    response = requests.get("https://www.valor-dolar.cl/currencies_rates.json")
    if response.status_code == 200:
        data = response.json()
        clp_price, currency_price = False, False

        for currency in data["currencies"]:
            if clp_price and currency_price:
                break
            if currency["code"] == "CLP":
                clp_price = float(currency["rate"])
                if target_currency == "CLP":
                    return "1 USD 🇺🇸 = %.2f 🇨🇱" % clp_price
            elif currency["code"] == target_currency:
                currency_price = float(currency["rate"])

        usd_target_price = 1 / currency_price
        clp_target_price = clp_price * usd_target_price
        return "1 %s %s = %.2f CLP 🇨🇱" % (target_currency, CURRENCIES.get(target_currency), clp_target_price)

    return "Error obteniendo precio del CLP"
