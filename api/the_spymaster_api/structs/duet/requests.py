from codenames.utils.vocabulary.languages import SupportedLanguage
from the_spymaster_api.structs import BaseRequest


class StartGameRequest(BaseRequest):
    language: SupportedLanguage = SupportedLanguage.ENGLISH
    timer_tokens: int = 9
    allowed_mistakes: int = 9
