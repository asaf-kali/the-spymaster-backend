from typing import Optional

from django.conf import settings
from solvers.models import (
    DEFAULT_MODEL_ADAPTER,
    HEBREW_SUFFIX_ADAPTER,
    ModelFormatAdapter,
    ModelIdentifier,
    load_model_async,
    set_language_data_folder,
)

from the_spymaster.utils import get_logger

log = get_logger(__name__)
DEFAULT_MODELS = {
    "hebrew": ModelIdentifier(language="hebrew", model_name="skv-ft-150", is_stemmed=True),
    "english": ModelIdentifier(language="english", model_name="wiki-50", is_stemmed=False),
}
DEFAULT_LANGUAGES = [language for language in DEFAULT_MODELS.keys()]


def load_default_models_async(language_data_folder: Optional[str] = None):
    if language_data_folder is None:
        language_data_folder = settings.LANGUAGE_DATA_FOLDER
    log.info(f"Loading default models from {language_data_folder}")
    set_language_data_folder(language_data_folder)
    for model_id in DEFAULT_MODELS.values():
        load_model_async(model_identifier=model_id)


def get_adapter_for_model(model_id: ModelIdentifier) -> ModelFormatAdapter:
    return HEBREW_SUFFIX_ADAPTER if model_id.language == "hebrew" and model_id.is_stemmed else DEFAULT_MODEL_ADAPTER
