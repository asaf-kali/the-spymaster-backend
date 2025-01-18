from codenames.utils.vocabulary.languages import SupportedLanguage
from the_spymaster_api.structs import BaseRequest


class MiniStartGameRequest(BaseRequest):
    language: SupportedLanguage = SupportedLanguage.ENGLISH
    total_points: int = 8
    timer_tokens: int = 5
    allowed_mistakes: int = 4
