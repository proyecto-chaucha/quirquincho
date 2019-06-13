from config import RANDOM_SALT, COIN, ADDRESS_PREFIX, INSIGHT
from requests import get, post
from bitcoin import *
from binascii import a2b_hex, b2a_hex
import time


def getTx(addr, max_read):
    info = get(INSIGHT + '/api/txs/?address=' + addr).json()
    msg = ''
    counter = 0

    for x in range(int(info['pagesTotal'])):
        info = get(INSIGHT + '/api/txs/?address=' + addr + '&pageNum=' + str(x)).json()
        for i in info['txs']:
            for j in i['vout']:
                hex_script = j['scriptPubKey']['hex']
                if hex_script.startswith('6a'):
                    if len(hex_script) <= 77*2:
                        sub_script = hex_script[4:]
                    else:
                        sub_script = hex_script[6:]

                    msg_str = a2b_hex(sub_script).decode(
                        'utf-8', errors='ignore')
                    fecha = time.strftime(
                        '%d.%m.%Y %H:%M:%S', time.localtime(int(i['time'])))

                    if msg_str.find('Quirquincho') < 0 and msg_str.find('/dice') < 0:
                        if counter < max_read:
                            msg += '[' + fecha + '](http://insight.chaucha.cl/tx/' + \
                                i['txid'] + '): `' + msg_str + '`\n'
                            counter += 1

    return msg


def OP_RETURN_payload(string):
    metadata = bytes(string, 'utf-8')
    metadata_len = len(metadata)

    if metadata_len <= 75:
        payload = bytearray((metadata_len,)) + metadata
    elif metadata_len <= 256:
        payload = b"\x4c" + bytearray((metadata_len,)) + metadata
    else:
        payload = b"\x4d" + \
            bytearray((metadata_len % 256,)) + \
            bytearray((int(metadata_len/256),)) + metadata

    return payload


def sendTx(info, amount, receptor, op_return=''):
    addr, privkey = info
    confirmed_balance, inputs, unconfirmed = getbalance(addr)

    if not len(receptor) == 34 and receptor[0] == 'c':
        return "Dirección inválida"

    elif amount > confirmed_balance:
        return "Balance insuficiente"

    elif amount <= 0:
        return "Monto inválido"

    # Transformar valores a Chatoshis
    used_amount = int(amount*COIN)

    # Utilizar solo las unspent que se necesiten
    used_balance = 0
    used_inputs = []

    for i in inputs:
        used_balance += i['value']
        used_inputs.append(i)
        if used_balance > used_amount:
            break

    # Output
    outputs = [{'address': receptor, 'value': used_amount}]

    # OP_RETURN
    if len(op_return) > 0 and len(op_return) <= 255:
        payload = OP_RETURN_payload(op_return)
        script = '6a' + \
            b2a_hex(payload).decode('utf-8', errors='ignore')

        outputs.append({'value': 0, 'script': script})

    # Transacción
    template_tx = mktx(used_inputs, outputs)
    size = len(a2b_hex(template_tx))

    # FEE = 0.01 CHA/kb
    # MAX FEE = 0.1 CHA

    fee = int((size/1024)*0.01*COIN) 
    fee = 1e7 if fee > 1e7 else fee

    if used_balance == amount:
        outputs[0] = {'address': receptor, 'value': used_amount - fee}
        tx = mktx(used_inputs, outputs)
    else:
        tx = mksend(used_inputs, outputs, addr, fee)

    for i in range(len(used_inputs)):
        tx = sign(tx, i, privkey)
    
    broadcasting = post(INSIGHT + '/api/tx/send', data={'rawtx': tx})

    try:
        msg = INSIGHT + "/tx/%s" % broadcasting.json()['txid']
    except:
        msg = broadcasting.text

    return msg


def getaddress(user_id):
    privkey = sha256(str(user_id) + str(RANDOM_SALT))
    addr = privtoaddr(privkey, ADDRESS_PREFIX)
    return [addr, privkey]


def getbalance(addr):
    unspent = get(INSIGHT + '/api/addr/' + addr + '/utxo').json()

    confirmed = unconfirmed = 0

    inputs = []
    for i in unspent:
        if i['confirmations'] >= 1 and i['amount'] >= 0.001:
            confirmed += i['amount']
            inputs_tx = {
                'output': i['txid'] + ':' + str(i['vout']),
                'value': i['satoshis'],
                'address': i['address']}

            inputs.append(inputs_tx)
        else:
            unconfirmed += i['amount']

    return [confirmed, inputs, unconfirmed]
