from config import salt, satoshi, fee, magic
from requests import get, post
from bitcoin import *

def sendTx(info, amount, receptor):
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
			msg = "Monto inválido"

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

			return msg


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
