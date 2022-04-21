from telegram import ForceReply, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from utils import config, configure_logging, get_logger

log = get_logger(__name__)
configure_logging(level="DEBUG", formatter="json")


# Define a few command handlers. These usually take the two arguments update and context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    log.update_context(user_id=update.effective_user.id)
    log.info("Got start event")
    user = update.effective_user
    message = rf"Hi {user.mention_markdown_v2()}\!"
    log.debug(f"Replying {message}")
    update.message.reply_markdown_v2(message, reply_markup=ForceReply(selective=True))
    log.info("Start done")


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    log.update_context(user_id=update.effective_user.id)
    log.info("Got help event")
    update.message.reply_text("Help!")


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    log.update_context(user_id=update.effective_user.id)
    log.info("Got message")
    update.message.reply_text(update.message.text)


def listen() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.telegram_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    listen()
