from config import salt, satoshi, fee, magic
from requests import get, post
from bitcoin import *

def OP_RETURN_bin_to_hex(string):
	return binascii.b2a_hex(string).decode('utf-8')

def OP_RETURN_payload(string):
	metadata = bytes(string, 'utf-8')
	metadata_len= len(metadata)
	
	if metadata_len<=75:
		payload=bytearray((metadata_len,))+metadata # length byte + data (https://en.bitcoin.it/wiki/Script)
	elif metadata_len<=256:
		payload=b"\x4c"+bytearray((metadata_len,))+metadata # OP_PUSHDATA1 format
	else:
		payload=b"\x4d"+bytearray((metadata_len%256,))+bytearray((int(metadata_len/256),))+metadata # OP_PUSHDATA2 format

	return payload

def sendTx(info, amount, receptor, op_return):
		addr = info[0]
		privkey = info[1]
		
		info = getbalance(addr)
		confirmed_balance = info[0]
		inputs = info[1]

		if not len(receptor) == 34 and receptor[0] == 'c':
			msg = "Dirección inválida"

		elif not confirmed_balance >= amount:
			msg = "Balance insuficiente"

		elif not amount > 0:
			msg = "Monto inválido"

		else:
			# Transformar valores a Chatoshis
			used_amount = int(amount*satoshi)
			used_fee = int(fee*satoshi)

			# Utilizar solo las unspent que se necesiten
			used_balance = 0
			used_inputs = []

			for i in inputs:
				used_balance += i['value']
				used_inputs.append(i)
				if used_balance > used_amount:
					break

			# OP_RETURN
			payload = OP_RETURN_payload(op_return)
			script = '6a'+OP_RETURN_bin_to_hex(payload)

			# Creación de salida
			if used_amount == used_balance:
				outputs = [{'address' : receptor, 'value' : (used_amount - used_fee)}, {'value' : 0, 'script' : script}]
			else:
				outputs = [{'address' : receptor, 'value' : used_amount}, {'address' : addr, 'value' : int(used_balance - used_amount - used_fee)}, {'value' : 0, 'script' : script}]

			# Transacción
			tx = mktx(used_inputs, outputs)

			# Firma
			for i in range(len(used_inputs)):
				tx = sign(tx, i, privkey)

			broadcasting = post('https://explorer.cha.terahash.cl/api/tx/send', data={'rawtx' : tx})

			try:
				msg = "insight.chaucha.cl/tx/%s" % broadcasting.json()['txid']
			except:
				msg = broadcasting.text()
			
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
