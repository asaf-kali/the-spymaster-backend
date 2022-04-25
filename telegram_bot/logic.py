from typing import Dict, Optional, Type

from codenames.game import CardColor, GameState, PlayerRole, TeamColor
from pydantic import BaseModel
from requests import HTTPError
from telegram import ReplyKeyboardMarkup, Update
from telegram import User as TelegramUser
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from api.client import TheSpymasterClient
from api.models.request import GuessRequest, NextMoveRequest, StartGameRequest
from api.models.response import ErrorResponse
from the_spymaster.utils import config, get_logger

log = get_logger(__name__)
BLUE_EMOJI = CardColor.BLUE.emoji
RED_EMOJI = CardColor.RED.emoji


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
    def chat_id(self) -> int:
        return self.update.effective_chat.id

    @property
    def session(self) -> Optional[Session]:
        return self.bot.sessions.get(self.user.id)

    @property
    def state(self) -> Optional[GameState]:
        if self.session is None:
            return None
        return self.session.state

    @property
    def game_id(self) -> Optional[int]:
        if self.session is None:
            return None
        return self.session.game_id

    @classmethod
    def handler(cls, bot: "TheSpymasterBot"):
        def dispatch(update: Update, context: CallbackContext):
            instance = cls(bot, update, context)
            try:
                log.update_context(user_id=instance.user.id, game_id=instance.game_id)
            except Exception as e:
                log.warning(f"Failed to update context: {e}")
            instance.handle()

        return dispatch

    def handle(self):
        raise NotImplementedError()

    def trigger(self, other: Type["EventHandler"]):
        other(bot=self.bot, update=self.update, context=self.context).handle()

    def send_message(self, text: str, **kwargs):
        self.context.bot.send_message(chat_id=self.chat_id, text=text, **kwargs)

    def send_markdown(self, text: str, **kwargs):
        self.send_message(text=text, parse_mode="Markdown", **kwargs)

    def fast_forward(self):
        session = self.session
        if session is None:
            return
        while not session.state.is_game_over and not _is_blue_guesser_turn(session):
            self._next_move()
        self.send_board()
        if session.state.is_game_over:
            self.send_message(f"Game over! Winner: {session.state.winner}")

    def _next_move(self):
        session = self.session
        team_color = session.state.current_team_color.value.title()
        if session.state.current_player_role == PlayerRole.HINTER:
            self.send_score()
            self.send_message(f"{team_color} hinter is thinking...")
        request = NextMoveRequest(game_id=session.game_id)
        response = self.client.next_move(request)
        session.state = response.game_state
        if response.given_hint:
            given_hint = response.given_hint
            self.send_markdown(rf"{team_color} hinter says '*{given_hint.word}*', *{given_hint.card_amount}* cards.")
        if response.given_guess:
            given_guess = response.given_guess
            self.send_markdown(
                rf"{team_color} guesser says '*{given_guess.guessed_card.word}*', {given_guess.correct}!"
            )

    def send_score(self):
        score = self.session.state.remaining_score
        message = f"Score: {score[TeamColor.BLUE]}{BLUE_EMOJI} - {score[TeamColor.RED]}{RED_EMOJI}"
        self.send_message(message)

    def send_board(self):
        state = self.session.state
        board_to_send = state.board if state.is_game_over else state.board.censured
        table = board_to_send.table_view(raw_cards=True)
        keyboard = build_keyboard(table)
        message = "Game over!" if state.is_game_over else "It's your turn!"
        self.send_message(message, reply_markup=keyboard)


def build_keyboard(table) -> ReplyKeyboardMarkup:
    reply_keyboard = []
    for row in table.rows:
        row_keyboard = []
        for word in row:
            row_keyboard.append(word)
        reply_keyboard.append(row_keyboard)
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


class StartEventHandler(EventHandler):
    def handle(self):
        log.info("Got start event")
        request = StartGameRequest(language="english")
        response = self.client.start_game(request)
        session = Session(game_id=response.game_id, state=response.game_state)
        self.bot.set_session(self.user.id, session=session)
        self.send_message(f"Game started with id {response.game_id}")
        self.fast_forward()


class ProcessMessageHandler(EventHandler):
    def handle(self):
        session = self.session
        if not session:
            self.trigger(HelpMessageHandler)
            return
        text = self.update.message.text
        try:
            card_index = _get_card_index(session=session, text=text)
        except:  # noqa
            self.send_message(f"Card '{text}' not found. Please reply with card index (0-24) or a word on the board.")
            return None
        request = GuessRequest(game_id=session.game_id, card_index=card_index)
        response = self.client.guess(request)
        session.state = response.game_state
        given_guess = response.given_guess
        if given_guess is None:
            pass  # This means we passed the turn
        else:
            card = given_guess.guessed_card
            self.send_markdown(rf"Card '*{card.word}*' is {card.color}, {given_guess.correct}!")
        self.fast_forward()


class HelpMessageHandler(EventHandler):
    def handle(self):
        log.info("Got help message")
        message = f"""Hi {self.user.name}!
/start - start a new game.
/help - show this help.

How to play:
You are the blue guesser. The bot will play all other players.
When the blue hinter sends a hint, you can reply with a card index (0-24) or just type the word on the board.
To pass the turn write '-1', to quit write '-2'.
"""
        self.send_markdown(message)


class ErrorHandler(EventHandler):
    def handle(self):
        e = self.context.error
        log.info(f"Handling error {e}")
        try:
            if isinstance(e, HTTPError):
                self._handle_http_error(e)
                return
        except:  # noqa
            log.exception("Failed to handle error")
        log.exception(e)
        self.send_message(f"Something went wrong: {e}")

    def _handle_http_error(self, e: HTTPError):
        data = e.response.json()
        response = ErrorResponse(**data)
        self.send_message(f"{response.message}: {response.details}")


class TheSpymasterBot:
    def __init__(self):
        self.sessions: Dict[int, Session] = {}
        self.client = TheSpymasterClient()

    def set_session(self, user_id: int, session: Session):
        self.sessions[user_id] = session

    def generate_handler(self, handler_type: Type[EventHandler]):
        return handler_type.handler(self)

    def listen(self) -> None:
        log.info("Starting bot...")
        updater = Updater(config.telegram_token)
        dispatcher = updater.dispatcher

        dispatcher.add_error_handler(self.generate_handler(ErrorHandler))
        dispatcher.add_handler(CommandHandler("start", self.generate_handler(StartEventHandler)))
        dispatcher.add_handler(CommandHandler("help", self.generate_handler(HelpMessageHandler)))
        dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self.generate_handler(ProcessMessageHandler))
        )

        updater.start_polling()
        updater.idle()


def _is_blue_guesser_turn(session):
    return (
        session.state.current_team_color == TeamColor.BLUE and session.state.current_player_role == PlayerRole.GUESSER
    )


def _get_card_index(session: Session, text: str) -> int:
    try:
        return int(text)
    except ValueError:
        pass
    return session.state.board.find_card_index(text)
