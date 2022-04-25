import django
from codenames.game import GameState, PlayerRole, TeamColor
from pydantic import BaseModel

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


class Session(BaseModel):
    game_id: int
    state: GameState


class TheSpymasterBot:
    def __init__(self):
        self.sessions = {}
        self.client = TheSpymasterClient()

    def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        log.update_context(user_id=user.id)
        log.info("Got start event")
        response = self.client.start_game(StartGameRequest(language="english"))
        session = Session(game_id=response.game_id, state=response.game_state)
        self.sessions[user.id] = session
        update.message.reply_text(f"Game started with id {response.game_id}")
        # update.message.reply_text(response.game_state.board.censured.printable_string)
        self._fast_forward(user_id=user.id, update=update)
        log.info("Start done")

    def _fast_forward(self, user_id: int, update: Update):
        session = self.sessions[user_id]
        while not session.state.is_game_over and (
            session.state.current_team_color != TeamColor.BLUE
            or session.state.current_player_role != PlayerRole.GUESSER
        ):
            if session.state.current_player_role == PlayerRole.HINTER:
                update.message.reply_text("Thinking...")
            request = NextMoveRequest(game_id=session.game_id)
            response = self.client.next_move(request)
            session.state = response.game_state
            if response.given_hint:
                update.message.reply_text(f"Hinter says: {response.given_hint.json(ensure_ascii=False)}")
            if response.given_guess:
                update.message.reply_text(f"Guesser says: {response.given_guess.guessed_card.json(ensure_ascii=False)}")
        update.message.reply_text(session.state.board.censured.printable_string)
        if session.state.is_game_over:
            update.message.reply_text(f"Game over! Winner: {session.state.winner}")

    def process(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        session = self.sessions.get(user_id)
        if not session:
            self.help(update, context)
            return
        text = update.message.text
        try:
            card_index = int(text)
        except ValueError:
            try:
                card_index = session.state.board.find_card_index(text)
            except Exception:  # noqa
                update.message.reply_text(
                    f"Card '{text}' not found. Please reply with card index (0-24) or a word on the board."
                )
                return
        request = GuessRequest(game_id=session.game_id, card_index=card_index)
        try:
            response = self.client.guess(request)
        except Exception as e:
            update.message.reply_text(f"Error: {e}")
            return
        session.state = response.game_state
        if response.given_guess is None:
            pass
            # update.message.reply_text(f"Pass")
        else:
            update.message.reply_text(f"{response.given_guess.guessed_card.color}, {response.given_guess.correct}!")
        self._fast_forward(user_id=user_id, update=update)

    def _get_game_state(self, game_id):
        return self.client.get_game_state(GetGameStateRequest(game_id=game_id)).game_state

    def help(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        message = rf"""Hi {user.name}\!
/start \- start a new game\.
/help \- show this help\.

How to play:
You are the blue guesser\. The bot will play all other players\.
When the blue hinter sends a hint, you can reply with a card index \(0\-24\) or just type the word on the board\.
To pass the turn write '\-1'\, to quit write '\-2'\.
"""
        update.message.reply_markdown_v2(message, reply_markup=ForceReply(selective=True))

    def listen(self) -> None:
        updater = Updater(config.telegram_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.process))

        updater.start_polling()
        updater.idle()


if __name__ == "__main__":
    bot = TheSpymasterBot()
    bot.listen()
