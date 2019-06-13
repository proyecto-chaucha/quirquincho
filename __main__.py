from random import randint
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

from config import TELEGRAM_TOKEN, RANDOM_SALT, DEFINE
from redchaucha import *

from contrib.setexredis import *
from contrib.precios import precio

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def mensajes(bot, update, args):
    try:
        user = update.message.from_user
        addr = getaddress(user.id)[0]

        max_read = int(args[0])

        if max_read > 0:
            msg = getTx(addr, max_read)

        if len(msg) == 0:
            msg = 'No tienes mensajes en el blockchain'
    except:
        msg = "Error >:C\nIntenta más tarde...\n\n"
        msg += "Modo de uso: /mensajes cantidad"

    logger.info("mensajes(%i) => %s" % (user.id, msg))
    update.message.reply_text("%s" % msg, parse_mode=ParseMode.MARKDOWN)


def op_return(bot, update, args):
    try:
        user = update.message.from_user
        info = getaddress(user.id)
        op_return = ' '.join(args)

        if len(op_return) > 0:
            msg = sendTx(info, 0.001, info[0], op_return)
        else:
            msg = "No hay mensaje, no puedo hacer nada :C"
    except:
        msg = "Error >:C\nIntenta más tarde..."

    logger.info("op_return(%i) => %s" % (user.id, msg))
    update.message.reply_text("%s" % msg)


def start(bot, update):
    msg = "*Holi !*"
    logger.info("start() => %s" % (msg))
    update.message.reply_text("%s" % msg, parse_mode=ParseMode.MARKDOWN)


def qr(bot, update):
    user = update.message.from_user
    info = getaddress(user.id)

    logger.info("qr(%i) => %s" % (user.id, info[0]))
    update.message.reply_photo(
        photo='https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=2&data=' + info[0])


def send(bot, update, args):
    try:
        user = update.message.from_user
        info = getaddress(user.id)

        amount = float(args[0])
        receptor = args[1]

        msg = sendTx(info, amount, receptor, 'Quirquincho')

    except:
        msg = "Error >:C\nIntenta más tarde...\n\n"
        msg += "Modo de uso: /send monto address"

    logger.info("send(%i) => %s" % (user.id, msg))
    update.message.reply_text("%s" % msg)


def balance(bot, update):
    try:
        # Descubrimiento de address
        user = update.message.from_user

        addr = getaddress(user.id)[0]
        confirmed, inputs, unconfirmed = getbalance(addr)

        total = confirmed + unconfirmed

        # MSG
        msg = "Tienes %.8f CHA en tu dirección\n"
        msg += "%.8f CHA para utilizar y %.8f CHA sin confirmar.\n\n"
        msg += "Tu address es %s"

        msg = msg % (total, confirmed, unconfirmed, addr)
    except:
        msg = "No se pudo ejecutar la lectura de balance :C"

    logger.info("balance(%i) => %s" % (user.id, msg.replace('\n', ' - ')))
    update.message.reply_text("%s" % msg)


def dice(bot, update, args):
    try:

        user = update.message.from_user
        usrInfo = getaddress(user.id)
        botBalance = getbalance(quirquincho[0])[0]
        usrBalance = getbalance(usrInfo[0])[0]

        if args[0] == 'house':
            msg = 'Aún puedes ganar %.8f chauchas!' % float(botBalance)
        else:
            bet = float(args[0])
            betFee = round(bet*0.025, 8)  # Fee del 2.5%
            if usrBalance >= bet and botBalance > 0 and bet > 0.001:
                num = randint(0, 50)
                msg = '%.8f CHA (fee: %.8f)\n' % (bet, betFee)
                if num >= 25:
                    msg = 'Perdiste ' + msg
                    msg += sendTx(usrInfo, bet, quirquincho[0], '/dice')
                else:
                    msg = 'Ganaste ' + msg
                    msg += sendTx(quirquincho, bet, usrInfo[0], '/dice')
                sendTx(usrInfo, betFee, quirquincho[0], 'dice tax')

            else:
                msg = 'No tienes chauchas suficientes'

    except:
        msg = "Error >:C\nIntenta más tarde...\n\n"
        msg += 'Modo de uso: \n - /dice cantidad\n - /dice house'

    logger.info("dice(%i) => %s" % (user.id, msg.replace('\n', ' - ')))
    update.message.reply_text("%s" % msg)


def define(bot, update, args):
    try:

        word = args[0]  # Si no viene el argumento se cae
        originalword = args[0]
        if len(args) > 1:
            word = " ".join(args)
        word = word.lower()

        if args[0] == 'url':
            msg = DEFINE

        user = update.message.from_user
        usrInfo = getaddress(user.id)
        botBalance = getbalance(quirquincho[0])[0]
        botBalanceDefine = getbalance(quirquinchoDefine[0])[0]

        # print(botBalanceDefine)
        usrBalance = getbalance(usrInfo[0])[0]

        info = get(DEFINE)
        # Se setea el encoding a ISO-8859-1
        info.encoding = info.apparent_encoding
        info = info.json()

        val = 0
        for definitions in info:
            if definitions['title'].lower() == word:
                retorno = redisWeekValidation(word, user)
                msg = retorno + \
                    "*%s*: %s" % (originalword.capitalize(),
                                  definitions['definition'])

                if retorno == "" and user.id not in set(getWinners()) and redisDayValidation(word, user):
                    textoTransaccion = sendTx(
                        quirquinchoDefine, 1, usrInfo[0], '/define')
                    if not textoTransaccion.startswith("explorer"):
                        logger.info("/define sendTx (%i) => %s" %
                                    (user.id, textoTransaccion))
                    else:
                        texto = "!!*Has ganado una chaucha*!!\n\nQuirquincho te la enviará a tu direccion: %s\n\n" % getaddress(user.id)[
                            0]
                        msg = texto+msg+"\n\n"
                        msg += textoTransaccion
                        # Se incluye en lista de ganadores. Son 14. Al 15avo se comienza a quitar de la lista
                        arrayWinners(user)
                elif retorno == "":
                    msg = "!!*Busca una nueva definición y obtén tu chaucha diaria*!!.\n\n" + \
                        msg  # Este tiene un pto para identificar donde cae

                val = 1
                break
        if val == 0:
            msg = "No  existe la definicion  :'( \n\n"
            msg += "Revisar el link %s para más definiciones" % DEFINE
            #msg += "Si quieres proponer esta definicion utiliza el comando adddefinition"
    except Exception as e:
        print(e)
        msg = "Error >:C\nIntenta más tarde...\n\n"
        msg += 'Modo de uso: \n - /define concepto'

    #logger.info("define(%s) => %s" % (user.username, msg.replace('\n', ' - ')))
    update.message.reply_text("%s" % msg, parse_mode=ParseMode.MARKDOWN)


def azar(bot, update, args):
    try:
        max_number = int(args[0])
        rand_number = randint(0, max_number)

        msg = "Número al azar (0, %s): %s\n" % (max_number, rand_number)
    except:
        msg = "Error >:C\n\n"
        msg += "Modo de uso: /azar [N]"

    logger.info("random(%i) => %s" % (update.message.from_user.id, msg))
    update.message.reply_text("%s" % msg)


def error(bot, update, error):
    logger.warning('Update: "%s" - Error: "%s"' % (update, error))

# Main loop


def main():
    global quirquincho
    global quirquinchoDefine

    # Configuración
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Listado de comandos
    dp.add_handler(CommandHandler("qr", qr))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("dice", dice, pass_args=True))
    dp.add_handler(CommandHandler("define", define, pass_args=True))
    dp.add_handler(CommandHandler("mensajes", mensajes, pass_args=True))
    dp.add_handler(CommandHandler("op_return", op_return, pass_args=True))
    dp.add_handler(CommandHandler("send", send, pass_args=True))
    dp.add_handler(CommandHandler("azar", azar, pass_args=True))
    dp.add_handler(CommandHandler("precio", precio, pass_args=True))

    # log all errors
    dp.add_error_handler(error)

    quirquincho = getaddress('Quirquincho' + str(RANDOM_SALT))
    # Se hace una wallet nueva para el traspaso de coins
    quirquinchoDefine = getaddress(str(RANDOM_SALT))
    # Inicio de bot
    logger.info("Quirquincho V 2.0 - %s" % quirquincho[0])
    logger.info("QuirquinchoDefine V 2.0 - %s" % quirquinchoDefine[0])

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
