import django
from codenames.game import GameState, PlayerRole, TeamColor

django.setup()
from telegram import ForceReply, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from api.client import TheSpymasterClient
from api.models.request import (
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
    StartGameRequest,
)
from the_spymaster.utils import config, configure_logging, get_logger

configure_logging()
log = get_logger(__name__)


class TheSpymasterBot:
    def __init__(self):
        self.sessions = {}
        self.client = TheSpymasterClient()

    def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        log.update_context(user_id=user.id)
        log.info("Got start event")
        update.message.reply_markdown_v2(rf"Hi {user.mention_markdown_v2()}\!", reply_markup=ForceReply(selective=True))
        response = self.client.start_game(StartGameRequest())
        self.sessions[user.id] = response.game_id
        update.message.reply_text(f"Game started with id {response.game_id}")
        # update.message.reply_text(response.game_state.board.censured.printable_string)
        self._fast_forward(user_id=user.id, update=update, game_state=response.game_state)
        log.info("Start done")

    def _fast_forward(self, user_id: int, update: Update, game_state: GameState = None):
        game_id = self.sessions[user_id]
        if not game_state:
            game_state = self._get_game_state(game_id)
        while game_state.current_team_color != TeamColor.BLUE or game_state.current_player_role != PlayerRole.GUESSER:
            update.message.reply_text("Thinking...")
            request = NextMoveRequest(game_id=game_id)
            response = self.client.next_move(request)
            game_state = response.game_state
            if response.given_hint:
                update.message.reply_text(response.given_hint.json())
            if response.given_guess:
                update.message.reply_text(response.given_guess.json())
        update.message.reply_text(game_state.board.censured.printable_string)

    def process(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        game_id = self.sessions[user_id]
        request = GuessRequest(game_id=game_id, card_index=update.message.text)
        response = self.client.guess(request)
        update.message.reply_text(f"{response.given_guess.correct}!")
        self._fast_forward(user_id=user_id, update=update, game_state=response.game_state)

    def _get_game_state(self, game_id):
        return self.client.get_game_state(GetGameStateRequest(game_id=game_id)).game_state

    def listen(self) -> None:
        updater = Updater(config.telegram_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.start))
        # dispatcher.add_handler(CommandHandler("help", self.help_command))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.process))

        updater.start_polling()
        updater.idle()


if __name__ == "__main__":
    bot = TheSpymasterBot()
    bot.listen()
