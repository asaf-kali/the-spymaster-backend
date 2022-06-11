import os
import shutil
from typing import Iterable

import boto3
from django.conf import settings
from gensim.models import KeyedVectors
from solvers.models import (
    DEFAULT_MODEL_ADAPTER,
    HEBREW_SUFFIX_ADAPTER,
    ModelFormatAdapter,
    ModelIdentifier,
)
from solvers.models import load_model as _load_model
from solvers.models import set_language_data_folder
from the_spymaster_util import AsyncTaskManager, get_logger

log = get_logger(__name__)
DEFAULT_MODELS = {
    "hebrew": ModelIdentifier(language="hebrew", model_name="skv-ft-150", is_stemmed=True),
    "english": ModelIdentifier(language="english", model_name="wiki-50", is_stemmed=False),
}
DEFAULT_LANGUAGES = [language for language in DEFAULT_MODELS.keys()]


def load_models(model_ids: Iterable[ModelIdentifier]) -> int:
    log.info(f"Loading default models from {settings.LANGUAGE_DATA_FOLDER}")
    set_language_data_folder(settings.LANGUAGE_DATA_FOLDER)
    task_manager = AsyncTaskManager(collect_results=False)
    for model_id in DEFAULT_MODELS.values():
        task_manager.add_task(load_model, (model_id,))
    for model_id in model_ids:
        task_manager.add_task(load_model, (model_id,))
    task_manager.join()
    log.info(f"Loaded {task_manager.total_task_count} models.")
    return task_manager.total_task_count


def load_model(model_id: ModelIdentifier) -> KeyedVectors:
    if settings.SHOULD_LOAD_MODELS_FROM_S3:
        fetcher = _get_s3_fetcher(language_data_folder=settings.LANGUAGE_DATA_FOLDER)
        fetcher.download_model(model_id=model_id)
    return _load_model(model_identifier=model_id)


def get_adapter_for_model(model_id: ModelIdentifier) -> ModelFormatAdapter:
    return HEBREW_SUFFIX_ADAPTER if model_id.language == "hebrew" and model_id.is_stemmed else DEFAULT_MODEL_ADAPTER


class S3ModelFetcher:
    def __init__(self, bucket_name: str, local_language_data_dir: str):
        self.bucket_name = bucket_name
        self.local_language_data_dir = local_language_data_dir
        if not os.path.exists(self.local_language_data_dir):
            os.makedirs(self.local_language_data_dir, exist_ok=True)
        self.boto_client = boto3.client("s3")

    def download_model(self, model_id: ModelIdentifier):
        model_local_path = os.path.join(self.local_language_data_dir, model_id.language, model_id.model_name)
        if os.path.exists(model_local_path):
            log.info(f"Model already exists at {model_local_path}")
            return model_local_path
        zip_path = self._download_zip(model_id=model_id)
        self._extract_zip(zip_path=zip_path, model_id=model_id)
        return model_local_path

    def _download_zip(self, model_id: ModelIdentifier) -> str:
        zip_path = os.path.join(self.local_language_data_dir, f"{model_id.language}-{model_id.model_name}.zip")
        if os.path.exists(zip_path):
            log.info(f"Model already exists at {zip_path}")
            return zip_path
        s3_key = f"language_data/{model_id.language}/{model_id.model_name}.zip"
        download_extra = {
            "model_id": model_id.dict(),
            "bucket_name": self.bucket_name,
            "s3_key": s3_key,
            "zip_path": zip_path,
        }
        log.info("Downloading model from S3", extra=download_extra)
        self.boto_client.download_file(
            Bucket=self.bucket_name,
            Key=s3_key,
            Filename=zip_path,
        )
        log.info("Download model completed", extra=download_extra)
        return zip_path

    def _extract_zip(self, zip_path: str, model_id: ModelIdentifier):
        language_dir = os.path.join(self.local_language_data_dir, model_id.language)
        os.makedirs(language_dir, exist_ok=True)
        log.info(f"Extracting model {model_id} from {zip_path} to {language_dir}")
        shutil.unpack_archive(zip_path, language_dir)
        os.remove(zip_path)


def _get_s3_fetcher(language_data_folder: str):
    return S3ModelFetcher(bucket_name=settings.S3_BUCKET_NAME, local_language_data_dir=language_data_folder)
