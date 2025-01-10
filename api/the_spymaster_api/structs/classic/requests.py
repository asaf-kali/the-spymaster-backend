from codenames.classic.team import ClassicTeam
from codenames.utils.vocabulary.languages import SupportedLanguage
from the_spymaster_api.structs import BaseRequest


class StartGameRequest(BaseRequest):
    language: SupportedLanguage = SupportedLanguage.ENGLISH
    first_team: ClassicTeam | None = None
