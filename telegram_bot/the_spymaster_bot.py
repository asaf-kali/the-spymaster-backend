from enum import IntEnum, auto
from random import random
from time import sleep
from typing import Any, Dict, List, Optional, Type

from codenames.game import (
    PASS_GUESS,
    QUIT_GAME,
    Board,
    Card,
    CardColor,
    GameState,
    PlayerRole,
    TeamColor,
    WinningReason,
)
from pydantic import BaseModel
from requests import HTTPError
from telegram import Message, ReplyKeyboardMarkup, Update
from telegram import User as TelegramUser
from telegram.error import BadRequest as TelegramBadRequest
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from api.logic.language import DEFAULT_LANGUAGES
from api.models.game import Difficulty, GameConfig
from api.models.request import (
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
    StartGameRequest,
)
from api.models.response import ErrorResponse
from telegram_bot.client import TheSpymasterClient
from the_spymaster.utils import config, get_logger

log = get_logger(__name__)
BLUE_EMOJI = CardColor.BLUE.emoji
RED_EMOJI = CardColor.RED.emoji
WIN_REASON_TO_EMOJI = {
    WinningReason.TARGET_SCORE_REACHED: "🤓",
    WinningReason.OPPONENT_HIT_BLACK: "😵",
    WinningReason.OPPONENT_QUIT: "🥴",
}
COMMAND_TO_INDEX = {"-pass": PASS_GUESS, "-quit": QUIT_GAME}


class BotState(IntEnum):
    Entry = auto()
    ConfigLanguage = auto()
    ConfigDifficulty = auto()
    ConfigSolver = auto()
    ContinueGetId = auto()
    Playing = auto()


class Session(BaseModel):
    game_id: Optional[int]
    state: Optional[GameState]
    last_keyboard_message: Optional[int]
    config: Optional[GameConfig]


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
    def username(self) -> Optional[str]:
        if not self.user:
            return None
        return self.user.username

    @property
    def user_full_name(self) -> Optional[str]:
        if not self.user:
            return None
        return self.user.full_name

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
        def dispatch(update: Update, context: CallbackContext) -> Any:
            instance = cls(bot, update, context)
            try:
                log.update_context(user_id=instance.user.id, game_id=instance.game_id)
            except Exception as e:
                log.warning(f"Failed to update context: {e}")
            try:
                log.debug(f"Dispatching to event handler: {cls.__name__}")
                return instance.handle()
            except Exception as e:
                instance._handle_error(e)
            finally:
                log.reset_context()

        return dispatch

    def handle(self):
        raise NotImplementedError()

    def trigger(self, other: Type["EventHandler"]) -> Any:
        return other(bot=self.bot, update=self.update, context=self.context).handle()

    def send_text(self, text: str, put_log: bool = False, **kwargs) -> Message:
        if put_log:
            log.info(text)
        return self.context.bot.send_message(chat_id=self.chat_id, text=text, **kwargs)

    def send_markdown(self, text: str, **kwargs) -> Message:
        return self.send_text(text=text, parse_mode="Markdown", **kwargs)

    def fast_forward(self):
        session = self.session
        if session is None:
            return None
        while not session.state.is_game_over and not _is_blue_guesser_turn(session):
            self._next_move()
        self.send_board()
        if session.state.is_game_over:
            self.send_game_summary()
            self.bot.set_session(self.user.id, None)
            self.trigger(HelpMessageHandler)
            return None
        return BotState.Playing

    def remove_keyboard(self):
        if not self.session or not self.session.last_keyboard_message:
            return
        log.debug("Removing keyboard")
        try:
            self.context.bot.edit_message_reply_markup(
                chat_id=self.chat_id, message_id=self.session.last_keyboard_message
            )
        except TelegramBadRequest:
            pass
        self.session.last_keyboard_message = None

    def send_game_summary(self):
        self._send_hinters_intents()
        self._send_winner_text()

    def _send_winner_text(self):
        winner = self.state.winner
        player_won = winner.team_color == TeamColor.BLUE
        winning_emoji = "🎉" if player_won else "😭"
        reason_emoji = WIN_REASON_TO_EMOJI[winner.reason]
        status = "won" if player_won else "lose"
        text = f"You {status}! {winning_emoji}\n{winner.team_color} team won: {winner.reason.value} {reason_emoji}"
        self.send_text(text, put_log=True)

    def _send_hinters_intents(self):
        relevant_hints = [hint for hint in self.state.raw_hints if hint.for_words]
        if not relevant_hints:
            return
        intent_strings = [f"'*{hint.word}*' for {hint.for_words}" for hint in relevant_hints]
        intent_string = "\n".join(intent_strings)
        text = f"Hinters intents were:\n{intent_string}\n"
        self.send_markdown(text)

    def _next_move(self):
        team_color = self.state.current_team_color.value.title()
        if self.state.current_player_role == PlayerRole.HINTER:
            self.send_score()
            self.send_text(f"{team_color} hinter is thinking... 🤔")
        if self._should_skip_turn():
            self.send_text(f"{team_color} guesser has skipped the turn.")
            request = GuessRequest(game_id=self.game_id, card_index=PASS_GUESS)
            response = self.client.guess(request=request)
        else:
            request = NextMoveRequest(game_id=self.game_id, solver=self.session.config.solver)
            response = self.client.next_move(request=request)
            if response.given_hint:
                given_hint = response.given_hint
                text = f"{team_color} hinter says '*{given_hint.word}*' with *{given_hint.card_amount}* card(s)."
                self.send_markdown(text, put_log=True)
            if response.given_guess:
                given_guess = response.given_guess
                text = f"{team_color} guesser says '*{given_guess.guessed_card.word}*', {given_guess.correct}!"
                self.send_markdown(text)
        self.session.state = response.game_state
        sleep(0.2 + random() / 2)

    def send_score(self):
        score = self.state.remaining_score
        text = f"{BLUE_EMOJI}  *{score[TeamColor.BLUE]}*  remaining card(s)  *{score[TeamColor.RED]}*  {RED_EMOJI}"
        self.send_markdown(text)

    def send_board(self, message: str = None):
        state = self.state
        board_to_send = state.board if state.is_game_over else state.board.censured
        table = board_to_send.as_table
        keyboard = build_board_keyboard(table, is_game_over=state.is_game_over)
        if message is None:
            message = "Game over!" if state.is_game_over else "Pick your guess!"
            if state.bonus_given:
                message += " (bonus round)"
        text = self.send_markdown(message, reply_markup=keyboard)
        self.session.last_keyboard_message = text.message_id

    def _refresh_game_state(self):
        request = GetGameStateRequest(game_id=self.game_id)
        response = self.client.get_game_state(request=request)
        self.session.state = response.game_state

    def _handle_error(self, e: Exception):
        log.debug(f"Handling error: {e}")
        try:
            if isinstance(e, HTTPError):
                self._handle_http_error(e)
                return
        except:  # noqa
            log.exception("Failed to handle error")
        log.exception(e)
        try:
            self.send_text(f"💔 Something went wrong: {e}")
        except:  # noqa
            pass
        # Try refreshing the state
        try:
            self._refresh_game_state()
        except:  # noqa
            log.exception("Failed to refresh game state")

    def _handle_http_error(self, e: HTTPError):
        data = e.response.json()
        response = ErrorResponse(**data)
        self.send_text(f"{response.message}: {response.details}", put_log=True)

    def _should_skip_turn(self) -> bool:
        dice = random()
        return (
            self.state.current_player_role == PlayerRole.GUESSER
            and dice < self.session.config.difficulty.pass_probability
        )


class StartEventHandler(EventHandler):
    def handle(self):
        log.update_context(username=self.username, full_name=self.user_full_name)
        log.info(f"Got start event from {self.user_full_name}")
        existing_config = self.session.config if self.session else None
        session_config = existing_config or GameConfig()
        log.debug("Session config", extra={"session_config": session_config.dict()})
        request = StartGameRequest(language=session_config.language)
        response = self.client.start_game(request)
        session = Session(game_id=response.game_id, state=response.game_state, config=session_config)
        self.bot.set_session(self.user.id, session=session)
        self.remove_keyboard()
        self.send_markdown(f"Game *#{response.game_id}* is starting! 🥳")
        return self.fast_forward()


class ProcessMessageHandler(EventHandler):
    def handle(self):
        text = self.update.message.text.lower()
        log.info(f"Processing message: '{text}'")
        self.remove_keyboard()
        session = self.session
        if not session or not session.state:
            self.trigger(HelpMessageHandler)
            return
        try:
            command = COMMAND_TO_INDEX.get(text, text)
            card_index = _get_card_index(board=session.state.board, text=command)
        except:  # noqa
            self.send_board(f"Card '*{text}*' not found. Please reply with card index (1-25) or a word on the board.")
            return None
        request = GuessRequest(game_id=self.game_id, card_index=card_index)
        response = self.client.guess(request)
        session.state = response.game_state
        given_guess = response.given_guess
        if given_guess is None:
            pass  # This means we passed the turn
        else:
            card = given_guess.guessed_card
            result = "Correct! ✅" if given_guess.correct else "Wrong! ❌"
            self.send_markdown(f"Card '*{card.word}*' is {card.color.emoji}, {result}")
        return self.fast_forward()


class CustomHandler(EventHandler):
    def handle(self):
        game_config = GameConfig()
        session = Session(config=game_config)
        self.bot.set_session(self.user.id, session=session)
        keyboard = build_language_keyboard()
        self.send_text("🌍 Pick language:", reply_markup=keyboard)
        return BotState.ConfigLanguage


class ConfigLanguageHandler(EventHandler):
    def handle(self):
        text = self.update.message.text.lower()
        log.info(f"Setting language: '{text}'")
        self.session.config.language = text
        keyboard = build_difficulty_keyboard()
        self.send_text("🥵 Pick difficulty:", reply_markup=keyboard)
        return BotState.ConfigDifficulty


class ConfigDifficultyHandler(EventHandler):
    def handle(self):
        text = self.update.message.text.lower()
        log.info(f"Setting difficulty: '{text}'")
        self.session.config.difficulty = Difficulty(text)
        return self.trigger(StartEventHandler)


class ConfigSolverHandler(EventHandler):
    def handle(self):
        pass


class ContinueHandler(EventHandler):
    def handle(self):
        self.send_text("This is not implemented yet 😢")


class ContinueGetIdHandler(EventHandler):
    def handle(self):
        pass


class FallbackHandler(EventHandler):
    def handle(self):
        pass


class HelpMessageHandler(EventHandler):
    def handle(self):
        log.info("Got help message")
        text = f"""Hi {self.user.name}!
/start - start a new game.
/custom - start a new game with custom configurations.
/continue - continue an old game.
/help - show this message.

How to play:
You are the blue guesser. The bot will play all other roles. \
When the blue hinter sends a hint, you can reply with a card index (1-25), \
or just click the word on the keyboard. \
Use '-pass' and '-quit' to pass the turn and quit the game.
"""
        self.send_markdown(text)


class TheSpymasterBot:
    def __init__(self, base_backend: str = None):
        self.sessions: Dict[int, Session] = {}
        self.client = TheSpymasterClient(base_backend=base_backend)

    def set_session(self, user_id: int, session: Optional[Session]):
        if not session:
            self.sessions.pop(user_id, None)
        self.sessions[user_id] = session

    def generate_handler(self, handler_type: Type[EventHandler]):
        return handler_type.handler(self)

    def listen(self) -> None:
        log.info("Starting bot...")
        updater = Updater(config.telegram_token)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler("start", self.generate_handler(StartEventHandler))
        custom_handler = CommandHandler("custom", self.generate_handler(CustomHandler))
        config_language_handler = MessageHandler(Filters.text, self.generate_handler(ConfigLanguageHandler))
        config_difficulty_handler = MessageHandler(Filters.text, self.generate_handler(ConfigDifficultyHandler))
        config_solver_handler = MessageHandler(Filters.text, self.generate_handler(ConfigSolverHandler))
        continue_game_handler = CommandHandler("continue", self.generate_handler(ContinueHandler))
        continue_get_id_handler = MessageHandler(Filters.text, self.generate_handler(ContinueGetIdHandler))
        fallback_handler = CommandHandler("quit", self.generate_handler(FallbackHandler))
        help_message_handler = CommandHandler("help", self.generate_handler(HelpMessageHandler))
        process_message_handler = MessageHandler(
            Filters.text & ~Filters.command, self.generate_handler(ProcessMessageHandler)
        )

        conv_handler = ConversationHandler(
            entry_points=[start_handler, custom_handler, continue_game_handler, help_message_handler],
            states={
                BotState.ConfigLanguage: [config_language_handler],
                BotState.ConfigDifficulty: [config_difficulty_handler],
                BotState.ConfigSolver: [config_solver_handler],
                BotState.ContinueGetId: [continue_get_id_handler],
                BotState.Playing: [process_message_handler],
            },
            fallbacks=[fallback_handler],
            allow_reentry=True,
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_handler(process_message_handler)

        updater.start_polling()
        updater.idle()


def build_board_keyboard(table, is_game_over: bool) -> ReplyKeyboardMarkup:
    reply_keyboard = []
    for row in table.rows:
        row_keyboard = []
        for card in row:
            card: Card
            if is_game_over:
                content = f"{card.color.emoji} {card.word}"
            else:
                content = card.color.emoji if card.revealed else card.word
            row_keyboard.append(content)
        reply_keyboard.append(row_keyboard)
    reply_keyboard.append(list(COMMAND_TO_INDEX.keys()))
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def build_language_keyboard():
    languages = _title_list(DEFAULT_LANGUAGES)
    return ReplyKeyboardMarkup([languages], one_time_keyboard=True)


def build_difficulty_keyboard():
    difficulties = _title_list([Difficulty.EASY.value, Difficulty.MEDIUM.value, Difficulty.HARD.value])
    keyboard = ReplyKeyboardMarkup([difficulties], one_time_keyboard=True)
    return keyboard


def _title_list(strings: List[str]) -> List[str]:
    return [s.title() for s in strings]


def _is_blue_guesser_turn(session):
    return (
        session.state.current_team_color == TeamColor.BLUE and session.state.current_player_role == PlayerRole.GUESSER
    )


def _get_card_index(board: Board, text: str) -> int:
    try:
        index = int(text)
        if index > 0:
            index -= 1
        return index
    except ValueError:
        pass
    return board.find_card_index(text)
