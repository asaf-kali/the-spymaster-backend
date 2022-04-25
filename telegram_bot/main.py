import django

django.setup()
from telegram_bot.logic import TheSpymasterBot
from the_spymaster.utils import get_logger

log = get_logger(__name__)

if __name__ == "__main__":
    bot = TheSpymasterBot()
    bot.listen()
