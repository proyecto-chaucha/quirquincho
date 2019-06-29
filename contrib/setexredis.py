import redis
import json
import datetime
import time
from random import randint
import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def redisWeekValidation(concept, user):
    msg = ""
    r = redis.StrictRedis()  # obtengo instancia de Redis
    logger.info("redisWeekValidation(%i) => %s" % (user.id, concept))
    if r.exists(concept) != 0:  # Si el concepto consultado ya existe (1 week), entonces no paga
        if r.exists("valordiario") == 0:
            prevuser = r.get(concept).decode("utf-8")
            msg = "El usuario @%s ya ha consultado por la definicion semanal '%s'\n\n" % (
                prevuser, concept.capitalize())
            msg += "!!*Aún puedes ganar la chaucha diaria*!!\n"
        msg += "!!*Busca una nueva definición y obtén tu chaucha diaria*!!\n\n"

    return msg


def redisDayValidation(concept, user):

    r = redis.StrictRedis()  # obtengo instancia de Redis
    if r.exists("valordiario") == 0:  # Si el concepto diario no existe, se crea y paga
        now = datetime.datetime.now()  # Ahora
        tomorrow = now + datetime.timedelta(days=1)  # Mañana
        # 2 Semanas. Implica más conceptos
        week = now + datetime.timedelta(days=14)
        # Segundos hasta el día siguiente en la mañana, entre 9 y 13, entre 0 y 59 min
        # Con esto evito el posible bot que a las 00 consulta al privado
        myhour = randint(9, 13)
        mymin = randint(0, 59)
        seconds_until_midnight = (tomorrow.replace(
            hour=myhour, minute=mymin, second=0, microsecond=0) - now).total_seconds()
        # Segundos hasta proxima semana
        seconds_until_oneweek_midnight = (week.replace(
            hour=0, minute=0, second=0, microsecond=0) - now).total_seconds()

        # Se obtienen valores enteros para pasarlos a Redis
        seconds_until_oneweek_midnight_int = int(
            round(seconds_until_oneweek_midnight))
        seconds_until_midnight_int = int(round(seconds_until_midnight))

        # Se guarda en la variable valordiario el username premiado del día
        logger.info("redisDayValidation(%i) => valor seconds diario [%i]" % (
            user.id, seconds_until_midnight_int))
        r.setex("valordiario", seconds_until_midnight_int, user.username)
        # Se guarda en la variable concept el username premiado del día y se guarda 1 semana
        # Con esto evitamos que se consulte a diario por el concepto 'blockchain', forzando
        # la rotación de los diferentes conceptos
        logger.info("redisDayValidation(%i) => valor seconds week [%i]" % (
            user.id, seconds_until_oneweek_midnight_int))
        r.setex(concept, seconds_until_oneweek_midnight_int, user.username)
        return True

    return False


def arrayWinners(user):
    r = redis.StrictRedis()  # obtengo instancia de Redis
    array = []
    if r.exists("winners") != 0:  # si el valor existe
        # Si ya existe, obtengo el array de redis
        array = json.loads(r.get('winners').decode('utf-8'))
    array.append(user.id)
    if len(array) > 13:
        # Quito el primer elemento. El array se va moviendo tipo shift
        del array[0]
    json_winners = json.dumps(array)
    r.set('winners', json_winners)


def getWinners():
    r = redis.StrictRedis()  # obtengo instancia de Redis
    array = []
    if r.exists("winners") != 0:  # si el valor existe
        return json.loads(r.get('winners').decode('utf-8'))
    return array


def getRedisPriceCoin(crypto, user):
    r = redis.StrictRedis()  # obtengo instancia de Redis
    logger.info("getRedisPriceCoin(%i) => %s" % (user.id, crypto))
    if r.exists(crypto) != 0:
        return r.get(crypto)
    return ""


def setRedisPriceCoin(crypto, user, valor):
    r = redis.StrictRedis()  # obtengo instancia de Redis
    logger.info("setRedisPriceCoin(%i) => %s" % (user.id, crypto))
    r.setex(crypto, 60*2, valor)
    return ""
