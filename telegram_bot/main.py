from telegram_bot.the_spymaster_bot import TheSpymasterBot
from the_spymaster.utils import configure_logging, get_config, get_logger

log = get_logger(__name__)

if __name__ == "__main__":
    configure_logging()
    config = get_config()
    bot = TheSpymasterBot(base_backend=config.base_backend_url)
    bot.listen()
