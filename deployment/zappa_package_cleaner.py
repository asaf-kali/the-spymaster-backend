# Based on https://gist.github.com/ian-whitestone/a3452fe38fda9025631045381a18a6df
# Blog post: https://ianwhitestone.work/zappa-zip-callbacks/

import os
import re
import shutil
from typing import List

from tqdm import tqdm
from zappa.cli import ZappaCLI

READ_EXECUTE_WRITE_MODE = 0o755


def main(zappa: ZappaCLI):
    """Clean up zappa package before deploying to AWS

    Args:
        zappa (ZappaCLI): ZappaCLI object from zappa/cli.py. Automatically
            gets passed in by callback initiation:
            https://github.com/Miserlou/Zappa/blob/746385d9483a536b6c363bab0a15fec1d27818e7/zappa/cli.py#L1939-L1980
    """
    print("Running zappa package cleaner")
    common_settings = zappa.zappa_settings.get("common", {})
    stage_settings = zappa.zappa_settings.get(zappa.api_stage, {})
    unified_settings = {**common_settings, **stage_settings}
    layer_packages = unified_settings.get("layer_packages", [])
    if not layer_packages:
        print("No layer_packages provided for stage.")
        return
    clean_archive(archive_path=zappa.zip_path, layer_packages=layer_packages)


def clean_archive(archive_path: str, layer_packages: List[str]):
    print(f"Cleaning {archive_path} from excluded files: {layer_packages}")
    cleaner = ArchiveCleaner(archive_path=archive_path, layer_packages=layer_packages)
    cleaner.clean()


class ArchiveCleaner:
    def __init__(self, archive_path: str, layer_packages: List[str]):
        if archive_path.endswith(".tar.gz"):
            self.archive_format, extension = "tarball", ".tar.gz"
        elif archive_path.endswith(".zip"):
            self.archive_format, extension = "zip", ".zip"
        else:
            raise Exception(f"Unknown archive format: {archive_path}")
        self.original_archive_path = absolute_path(archive_path)
        self.archive_name = archive_path.replace(extension, "")
        self.wip_dir = absolute_path(self.archive_name)
        self.content_dir = os.path.join(self.wip_dir, "content")
        self.lambda_dir = os.path.join(self.wip_dir, "lambda")
        self.layer_dir = os.path.join(self.wip_dir, "layer")
        self.lambda_archive_name = self.archive_name + "-new"
        self.layer_archive_name = self.archive_name + "-layer"
        self.prefix_length = len(self.content_dir)
        self.layer_patterns = [re.compile(rf"^{exclude}.*") for exclude in layer_packages]

    def clean(self):
        self._unpack_archive()
        self._reorder_files()
        self._create_layer_docker_image()
        # self._zip_lambda_archive()
        # self._remove_wip_dir()
        # self._replace_old_archive()

    def _unpack_archive(self):
        print(f"Unpacking archive to {self.content_dir}...")
        shutil.unpack_archive(self.original_archive_path, self.content_dir)

    def _reorder_files(self):
        print("Reordering files...")
        walk_list = list(os.walk(self.content_dir))
        os.makedirs(self.lambda_dir, exist_ok=True)
        os.makedirs(self.layer_dir, exist_ok=True)
        for root, _, files in tqdm(walk_list):
            zip_relative_root = root[self.prefix_length :].lstrip(os.sep)
            should_move_to_layer = any(pattern.match(zip_relative_root) for pattern in self.layer_patterns)
            component_dir = self.layer_dir if should_move_to_layer else self.lambda_dir
            for file_name in files:
                zip_relative_path = os.path.join(zip_relative_root, file_name)
                src_path = os.path.join(root, file_name)
                dst_path = os.path.join(component_dir, zip_relative_path)
                dst_dir = os.path.dirname(dst_path)
                os.makedirs(dst_dir, exist_ok=True)
                os.rename(src=src_path, dst=dst_path)

    def _zip_lambda_archive(self):
        print(f"Zipping lambda to {self.lambda_archive_name}...")
        shutil.make_archive(self.lambda_archive_name, "zip", self.lambda_dir)

    def _create_layer_docker_image(self):
        print(f"Creating layer docker image {self.layer_archive_name}...")
        pass

    def _replace_old_archive(self):
        print(f"Replacing original archive with {self.lambda_archive_name}")
        lambda_archive_path = absolute_path(self.lambda_archive_name + ".zip")
        os.remove(self.original_archive_path)
        os.rename(lambda_archive_path, self.original_archive_path)

    def _remove_wip_dir(self):
        print(f"Removing {self.wip_dir}")
        shutil.rmtree(self.wip_dir)


def absolute_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def example():
    archive_path = "the-spymaster-dev-1655223648.zip"
    layer_packages = [
        "boto3",
        "botocore",
        "scipy",
        "pydantic",
        "gensim",
        "pandas",
        "numpy",
        "scipy",
        "networkx",
        "cryptography",
        "mypy",
        "virtualenv",
        "selenium",
    ]
    clean_archive(archive_path=archive_path, layer_packages=layer_packages)


if __name__ == "__main__":
    example()
