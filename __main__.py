from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import token
from redchaucha import *
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def op_return(bot, update):
	try:
		user = update.message.from_user
		info = getaddress(user.id)
		
		op_return = update.message.text.replace('/op_return ', '')

		msg = sendTx(info, 0.001, info[0], op_return)
		
	except:
		msg = "Error de formato >:C\n\n"
		msg += "Modo de uso: /op_return mensaje"

	logger.info("op_return(%i) => %s" % (user.id, msg))
	update.message.reply_text("%s" % msg)			


def sendall(bot, update, args):
	try:
		user = update.message.from_user
		info = getaddress(user.id)
		
		receptor = args[0]

		max_amount = getbalance(info[0])[0]
		msg = sendTx(info, max_amount, receptor, 'Quirquincho')
		
	except:
		msg = "Error de formato >:C\n\n"
		msg += "Modo de uso: /sendall address"

	logger.info("sendall(%i) => %s" % (user.id, msg))
	update.message.reply_text("%s" % msg)			

def send(bot, update, args):
	try:
		user = update.message.from_user
		info = getaddress(user.id)
		
		amount = float(args[0])
		receptor = args[1]

		msg = sendTx(info, amount, receptor, 'Quirquincho')

	except:
		msg = "Error de formato >:C\n\n"
		msg += "Modo de uso: /send monto address"

	logger.info("send(%i) => %s" % (user.id, msg))
	update.message.reply_text("%s" % msg)	


def balance(bot, update):
	try:
		# Descubrimiento de address
		user = update.message.from_user

		addr = getaddress(user.id)[0]
		balance = getbalance(addr)

		total = balance[0] + balance[2]

		# MSG
		msg = "Tienes %f CHA en tu dirección\n"
		msg += "%f CHA para utilizar y %f CHA sin confirmar.\n\n"
		msg += "Tu address es %s"

		msg = msg % (total, balance[0], balance[2], addr)
	except:
		msg = "No se pudo ejecutar la lectura de balance :C"

	logger.info("balance(%i) => %s" % (user.id, msg.replace('\n', '')))
	update.message.reply_text("%s" % msg)

def error(bot, update, error):
	logger.warning('Update: "%s" - Error: "%s"' % (update, error))

# Main loop
def main():
	global quirquincho

	# Configuración
	updater = Updater(token)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Listado de comandos
	dp.add_handler(CommandHandler("balance", balance))
	dp.add_handler(CommandHandler("op_return", op_return))
	dp.add_handler(CommandHandler("send", send, pass_args=True))
	dp.add_handler(CommandHandler("sendall", sendall, pass_args=True))

	# log all errors
	dp.add_error_handler(error)

	quirquincho = getaddress('Quirquincho')
	# Inicio de bot
	logger.info("Quirquincho V 2.0 - %s" % quirquincho[0])
	updater.start_polling()

	updater.idle()


if __name__ == '__main__':
	main()