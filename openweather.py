import requests
import logging

from config import WEATHER_API_KEY

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'


def clima(bot, update, args):
    try:
        if args:
            city = ' '.join(args)
        else:
            city = 'Santiago'

        msg = _clima(city)
    except Exception as e:
        logger.error(str(e))
        msg = "Error >:(\n\n"
        msg += "Modo de uso: /clima [ciudad]"

    logger.info("clima(%s) => %s" % (update.message.from_user.id, msg))
    update.message.reply_text("%s" % msg)


def _clima(city):
    response = requests.get(WEATHER_URL.format(city=city, api_key=WEATHER_API_KEY))
    if response.status_code == 200:
        data = response.json()
        return "%s: %d°C %s (%d%% Humedad) / Min: %d°C Max: %d°C" % (
            data["name"],
            data["main"]["temp"],
            _icono(data["weather"][0]["id"]),
            data["main"]["humidity"],
            data["main"]["temp_min"],
            data["main"]["temp_max"],
        )
    return "Clima no encontrado :("


def _icono(condicion):
    if condicion < 300:
        return '🌩'
    elif condicion < 400:
        return '🌧'
    elif condicion < 600:
        return '☔️'
    elif condicion < 700:
        return '☃️'
    elif condicion < 800:
        return '🌫'
    elif condicion == 800:
        return '☀️'
    elif condicion <= 804:
        return '☁️'
    else:
        return '🤷‍'
