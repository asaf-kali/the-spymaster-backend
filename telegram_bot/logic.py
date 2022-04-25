from typing import Dict, Optional, Type

from codenames.game import GameState, PlayerRole, TeamColor
from pydantic import BaseModel
from telegram import ForceReply, Update
from telegram import User as TelegramUser
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
from the_spymaster.utils import config, get_logger

log = get_logger(__name__)


class Session(BaseModel):
    game_id: int
    state: GameState


class EventHandler:
    def __init__(self, bot: "TheSpymasterBot", update: Update, context: CallbackContext):
        self.bot = bot
        self.update = update
        self.context = context

    @property
    def client(self) -> TheSpymasterClient:
        return self.bot.client

    @property
    def user(self) -> TelegramUser:
        return self.update.effective_user

    @property
    def session(self) -> Optional[Session]:
        return self.bot.sessions.get(self.user.id)

    @property
    def game_id(self) -> Optional[int]:
        if self.session is None:
            return None
        return self.session.game_id

    @classmethod
    def handler(cls, bot: "TheSpymasterBot"):
        def dispatch(update: Update, context: CallbackContext):
            instance = cls(bot, update, context)
            log.update_context(user_id=instance.user.id, game_id=instance.game_id)
            instance.handle()

        return dispatch

    def handle(self):
        raise NotImplementedError()


class TestEventHandler(EventHandler):
    def handle(self):
        log.info("It's working! 🎉")


class TheSpymasterBot:
    def __init__(self):
        self.sessions: Dict[int, Session] = {}
        self.client = TheSpymasterClient()

    def start(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        log.update_context(user_id=user_id)
        log.info("Got start event")
        response = self.client.start_game(StartGameRequest(language="english"))
        session = Session(game_id=response.game_id, state=response.game_state)
        self.sessions[user_id] = session
        update.message.reply_text(f"Game started with id {response.game_id}")
        self._fast_forward(user_id=user_id, update=update, context=context)
        log.info("Start done")

    def process_message(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        log.update_context(user_id=user_id)
        session = self.sessions.get(user_id)
        if not session:
            self.help(update, context)
            return
        text = update.message.text
        try:
            card_index = _get_card_index(session=session, text=text)
        except:  # noqa
            update.message.reply_text(
                f"Card '{text}' not found. Please reply with card index (0-24) or a word on the board."
            )
            return None
        request = GuessRequest(game_id=session.game_id, card_index=card_index)
        try:
            response = self.client.guess(request)
        except Exception as e:
            log.exception("Error while guessing")
            update.message.reply_text(f"Error: {e}")
            return
        session.state = response.game_state
        given_guess = response.given_guess
        if given_guess is None:
            pass  # This means we passed the turn
        else:
            card = given_guess.guessed_card
            update.message.reply_markdown_v2(rf"Card '*{card.word}*' is {card.color}, {given_guess.correct}\!")
        self._fast_forward(user_id=user_id, update=update, context=context)

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

    def _fast_forward(self, user_id: int, update: Update, context: CallbackContext):
        session = self.sessions[user_id]
        while not session.state.is_game_over and not _is_blue_guesser_turn(session):
            self._next_move(session=session, update=update)
        _send_board(session=session, update=update)
        if session.state.is_game_over:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"Game over! Winner: {session.state.winner}"
            )

    def _next_move(self, session: Session, update: Update):
        team_color = session.state.current_team_color.value.title()
        if session.state.current_player_role == PlayerRole.HINTER:
            update.message.reply_text(f"{team_color} hinter is thinking...")
        request = NextMoveRequest(game_id=session.game_id)
        response = self.client.next_move(request)
        session.state = response.game_state
        if response.given_hint:
            given_hint = response.given_hint
            update.message.reply_markdown_v2(
                rf"{team_color} hinter says '*{given_hint.word}*', *{given_hint.card_amount}* cards\."
            )
        if response.given_guess:
            given_guess = response.given_guess
            update.message.reply_markdown_v2(
                rf"{team_color} guesser says '*{given_guess.guessed_card.word}*', {given_guess.correct}\!"
            )

    def _get_game_state(self, game_id):
        return self.client.get_game_state(GetGameStateRequest(game_id=game_id)).game_state

    def generate_handler(self, handler_type: Type[EventHandler]):
        return handler_type.handler(self)

    def listen(self) -> None:
        log.info("Starting bot...")
        updater = Updater(config.telegram_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.process_message))
        dispatcher.add_handler(CommandHandler("test", self.generate_handler(TestEventHandler)))

        updater.start_polling()
        updater.idle()


def _is_blue_guesser_turn(session):
    return (
        session.state.current_team_color == TeamColor.BLUE and session.state.current_player_role == PlayerRole.GUESSER
    )


def _send_board(session: Session, update: Update):
    state = session.state
    board_to_send = state.board if state.is_game_over else state.board.censured
    update.message.reply_text(board_to_send.printable_string)


def _get_card_index(session: Session, text: str) -> int:
    try:
        return int(text)
    except ValueError:
        pass
    return session.state.board.find_card_index(text)
