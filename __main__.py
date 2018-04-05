from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from requests import get, post
from bitcoin import *
from config import *
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def getaddress(user_id):
	privkey = sha256(str(user_id) + str(salt))
	addr = privtoaddr(privkey, magic)
	return [addr, privkey]

def getbalance(addr):
	# Captura de balance por tx sin gastar
	unspent = get('https://explorer.cha.terahash.cl/api/addr/' + addr + '/utxo').json()
		
	confirmed = unconfirmed = 0

	inputs = []
	for i in unspent:
		if i['confirmations'] >= 6:
			confirmed += i['amount']
			inputs_tx = {'output' : i['txid'] + ':' + str(i['vout']), 'value' : i['satoshis'], 'address' : i['address']}
			inputs.append(inputs_tx)
		else:
			unconfirmed += i['amount']

	return [confirmed, inputs, unconfirmed]


def send(bot, update, args):
	try:
		user = update.message.from_user

		amount = float(args[0])
		receptor = args[1]

		info = getaddress(user.id)
		addr = info[0]
		privkey = info[1]
		
		info = getbalance(addr)
		confirmed_balance = info[0]
		inputs = info[1]

		if not len(receptor) == 34 and receptor[0] == 'c':
			msg = "Dirección inválida"

		elif not confirmed_balance - fee >= amount:
			msg = "Balance insuficiente"

		elif not amount > 0:
			msg	= "Monto inválido"

		else:
			# Transformar valores a Chatoshis
			amount = int(amount*satoshi)
			used_fee = int(fee*satoshi)

			# Utilizar solo las unspent que se necesiten
			used_balance = 0
			used_inputs = []

			for i in inputs:
				used_balance += i['value']
				used_inputs.append(i)
				if used_balance >= amount:
					break 

			# Creación de salida
			outputs = [{'address' : receptor, 'value' : amount}]

			# Agregar transacción de vuelto si es necesario
			if not int(used_balance - amount) == 0:
				outputs.append({'address' : addr, 'value' : int(used_balance - (amount + used_fee))}) 

			# Transacción
			tx = mktx(used_inputs, outputs)

			# Firma
			for i in range(len(used_inputs)):
				tx = sign(tx, i, privkey)

			broadcasting = post('https://explorer.cha.terahash.cl/api/tx/send', data={'rawtx' : tx})

			try:
				msg = "insight.chaucha.cl/tx/%s" % broadcasting.json()['txid']
			except:
				msg = "ERROR: %s" % broadcasting.text()
	except:
		msg = "Error de formato >:C"

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

	logger.info("balance(%i) => %s" % (user.id, msg))
	update.message.reply_text("%s" % msg)

def error(bot, update, error):
	logger.warning('Update: "%s" - Error: "%s"' % (update, error))

# Main loop
def main():
	# Configuración
	updater = Updater(token)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Listado de comandos
	dp.add_handler(CommandHandler("balance", balance))
	dp.add_handler(CommandHandler("send", send, pass_args=True))

	# log all errors
	dp.add_error_handler(error)

	# Inicio de bot
	logger.info("Quirquincho V 2.0")
	updater.start_polling()

	updater.idle()


if __name__ == '__main__':
	main()