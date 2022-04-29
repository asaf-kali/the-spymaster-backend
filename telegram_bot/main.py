import django

django.setup()
from telegram_bot.the_spymaster_bot import TheSpymasterBot
from the_spymaster.utils import config, get_logger

log = get_logger(__name__)

if __name__ == "__main__":
    bot = TheSpymasterBot(base_backend=config.base_backend_url)
    bot.listen()
