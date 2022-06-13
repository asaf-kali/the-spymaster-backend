# Based on https://gist.github.com/ian-whitestone/a3452fe38fda9025631045381a18a6df

import os
import re
import shutil
from tarfile import TarInfo
from tarfile import open as open_tar
from typing import List
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

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


class ArchiveCleaner:
    def __init__(self, archive_path: str, layer_packages: List[str]):
        if archive_path.endswith(".tar.gz"):
            self.archive_format, extension = "tarball", ".tar.gz"
        elif archive_path.endswith(".zip"):
            self.archive_format, extension = "zip", ".zip"
        else:
            raise Exception(f"Unknown archive format: {archive_path}")
        self.zip_name = os.path.basename(archive_path)
        self.archive_file_path = absolute_path(archive_path)
        self.wip_dir = absolute_path(archive_path.replace(extension, ""))
        self.temp_unarchive_dir = os.path.join(self.wip_dir, "content")
        self.lambda_dir = os.path.join(self.wip_dir, "lambda")
        self.layer_dir = os.path.join(self.wip_dir, "layer")
        self.new_archive_path = self.wip_dir + "-new.zip"
        self.layer_archive_path = self.wip_dir + "-layer.zip"
        # self.lambda_manager = _manager_factory(self.new_archive_path, self.archive_format)
        # self.layer_manager = _manager_factory(self.layer_archive_path, self.archive_format)
        self.prefix_length = len(self.temp_unarchive_dir)
        self.layer_patterns = [re.compile(rf"^{exclude}.*") for exclude in layer_packages]

    def clean(self):
        self._unpack_archive()
        self._remake_archive()
        self._remove_wip_dir()
        # self._swap_archives()

    def _unpack_archive(self):
        print(f"Unpacking {self.archive_file_path} to {self.temp_unarchive_dir}")
        shutil.unpack_archive(self.archive_file_path, self.temp_unarchive_dir)

    def _remake_archive(self):
        walk_list = list(os.walk(self.temp_unarchive_dir))
        os.makedirs(self.lambda_dir, exist_ok=True)
        os.makedirs(self.layer_dir, exist_ok=True)
        for root, _, files in tqdm(walk_list):
            zip_relative_root = root[self.prefix_length:].lstrip(os.sep)
            should_move_to_layer = any(pattern.match(zip_relative_root) for pattern in self.layer_patterns)
            # manager = self.layer_manager if should_move_to_layer else self.lambda_manager
            component_dir = self.layer_dir if should_move_to_layer else self.lambda_dir
            for file_name in files:
                zip_relative_path = os.path.join(zip_relative_root, file_name)
                src_path = os.path.join(root, file_name)
                dst_path = os.path.join(component_dir, zip_relative_path)
                dst_dir = os.path.dirname(dst_path)
                os.makedirs(dst_dir, exist_ok=True)
                # Make sure that the files are all correctly chmodded
                # Related: https://github.com/Miserlou/Zappa/issues/484
                # Related: https://github.com/Miserlou/Zappa/issues/682
                # os.chmod(full_path, READ_EXECUTE_WRITE_MODE)
                # TODO: instead of add the file, move it to the correct location
                os.rename(src=src_path, dst=dst_path)
                # manager.add(full_path=dst_path, zip_relative_path=zip_relative_path)
        print(f"Creating {self.new_archive_path}")
        # self.lambda_manager.close()
        # self.layer_manager.close()

    def _swap_archives(self):
        print(f"Renaming {self.new_archive_path} to {self.archive_file_path}")
        os.remove(self.archive_file_path)
        os.rename(self.new_archive_path, self.archive_file_path)

    def _remove_wip_dir(self):
        print(f"Removing {self.wip_dir}")
        shutil.rmtree(self.wip_dir)


def clean_archive(archive_path: str, layer_packages: List[str]):
    print(f"Cleaning {archive_path} from excluded files: {layer_packages}")
    cleaner = ArchiveCleaner(archive_path=archive_path, layer_packages=layer_packages)
    cleaner.clean()


class ArchiveManager:
    def add(self, full_path: str, zip_relative_path: str):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class ZipArchiveManager(ArchiveManager):
    def __init__(self, archive_path: str, compression_method: int):
        self.archive = ZipFile(archive_path, "w", compression_method)
        self.compression_method = compression_method

    def add(self, full_path: str, zip_relative_path: str):
        # Actually put the file into the proper place in the zip
        # Related: https://github.com/Miserlou/Zappa/pull/716
        zip_info = ZipInfo(zip_relative_path)
        zip_info.create_system = 3
        zip_info.external_attr = READ_EXECUTE_WRITE_MODE << int(16)  # Is this P2/P3 functional?
        with open(full_path, "rb") as f:
            self.archive.writestr(zip_info, f.read(), self.compression_method)

    def close(self):
        self.archive.close()


class TarballArchiveManager(ArchiveManager):
    def __init__(self, archive_path: str):
        self.archive = open_tar(archive_path, "w|gz")

    def add(self, full_path: str, zip_relative_path: str):
        tarinfo = TarInfo(zip_relative_path)
        tarinfo.mode = READ_EXECUTE_WRITE_MODE

        stat = os.stat(full_path)
        tarinfo.mtime = int(stat.st_mtime)
        tarinfo.size = stat.st_size
        with open(full_path, "rb") as f:
            self.archive.addfile(tarinfo, f)

    def close(self):
        self.archive.close()


def _manager_factory(archive_file_path: str, archive_format: str):
    if archive_format == "zip":
        print("Re-packaging project as zip.")
        manager = _get_zip_manager(archive_file_path)
    elif archive_format == "tarball":
        print("Re-packaging project as gzipped tarball.")
        manager = TarballArchiveManager(archive_path=archive_file_path)
    else:
        raise Exception(f"Unknown archive format: {archive_format}")
    return manager


def _get_zip_manager(archive_path: str):
    try:
        compression_method = ZIP_DEFLATED
    except ImportError:  # pragma: no cover
        compression_method = ZIP_STORED
    return ZipArchiveManager(archive_path=archive_path, compression_method=compression_method)


def absolute_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def example():
    archive_path = "the-spymaster-dev-1655156817.zip"
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
