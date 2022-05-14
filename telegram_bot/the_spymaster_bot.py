from typing import Dict, Optional, Type

from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from telegram_bot.handlers import (
    ConfigDifficultyHandler,
    ConfigLanguageHandler,
    ConfigModelHandler,
    ConfigSolverHandler,
    ContinueGetIdHandler,
    ContinueHandler,
    CustomHandler,
    EventHandler,
    FallbackHandler,
    GetSessionsHandler,
    HelpMessageHandler,
    LoadModelsHandler,
    ProcessMessageHandler,
    StartEventHandler,
)
from telegram_bot.models import BotState, Session, SessionId
from telegram_bot.spymaster_client import TheSpymasterClient
from the_spymaster.utils import get_config, get_logger

log = get_logger(__name__)


class TheSpymasterBot:
    def __init__(self, base_backend: str = None):
        self.sessions: Dict[SessionId, Session] = {}
        self.client = TheSpymasterClient(base_backend=base_backend)

    def set_session(self, session_id: SessionId, session: Optional[Session]):
        if not session:
            self.sessions.pop(session_id, None)
        self.sessions[session_id] = session  # type: ignore

    def get_session(self, session_id: SessionId) -> Optional[Session]:
        return self.sessions.get(session_id)

    def generate_handler(self, handler_type: Type[EventHandler]):
        return handler_type.handler(self)

    def listen(self) -> None:
        log.info("Starting bot...")
        config = get_config()
        updater = Updater(config.telegram_token)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler("start", self.generate_handler(StartEventHandler))
        custom_handler = CommandHandler("custom", self.generate_handler(CustomHandler))
        config_language_handler = MessageHandler(Filters.text, self.generate_handler(ConfigLanguageHandler))
        config_difficulty_handler = MessageHandler(Filters.text, self.generate_handler(ConfigDifficultyHandler))
        config_model_handler = MessageHandler(Filters.text, self.generate_handler(ConfigModelHandler))
        config_solver_handler = MessageHandler(Filters.text, self.generate_handler(ConfigSolverHandler))
        continue_game_handler = CommandHandler("continue", self.generate_handler(ContinueHandler))
        continue_get_id_handler = MessageHandler(Filters.text, self.generate_handler(ContinueGetIdHandler))
        fallback_handler = CommandHandler("quit", self.generate_handler(FallbackHandler))
        help_message_handler = CommandHandler("help", self.generate_handler(HelpMessageHandler))
        get_sessions_handler = CommandHandler("sessions", self.generate_handler(GetSessionsHandler))
        load_models_handler = CommandHandler("load_models", self.generate_handler(LoadModelsHandler))
        process_message_handler = MessageHandler(
            Filters.text & ~Filters.command, self.generate_handler(ProcessMessageHandler)
        )

        conv_handler = ConversationHandler(
            entry_points=[
                start_handler,
                custom_handler,
                continue_game_handler,
                help_message_handler,
                get_sessions_handler,
                load_models_handler,
            ],
            states={
                BotState.ConfigLanguage: [config_language_handler],
                BotState.ConfigDifficulty: [config_difficulty_handler, fallback_handler],
                BotState.ConfigModel: [config_model_handler, fallback_handler],
                BotState.ConfigSolver: [config_solver_handler, fallback_handler],
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
