# Based on https://gist.github.com/ian-whitestone/a3452fe38fda9025631045381a18a6df

import os
import re
import shutil
from re import Pattern
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
    exclude_expressions = unified_settings.get("exclude_expressions", [])
    clean_archive(archive_path=zappa.zip_path, exclude_expressions=exclude_expressions)


class ArchiveCleaner:
    def __init__(self, archive_path: str):
        if archive_path.endswith(".tar.gz"):
            self.archive_format, extension = "tarball", ".tar.gz"
        elif archive_path.endswith(".zip"):
            self.archive_format, extension = "zip", ".zip"
        else:
            raise Exception(f"Unknown archive format: {archive_path}")
        self.archive_file_path = absolute_path(archive_path)
        self.temp_unarchive_dir = absolute_path(archive_path.replace(extension, ""))
        self.new_archive_path = self.archive_file_path + ".new"
        self.manager = _manager_factory(self.new_archive_path, self.archive_format)
        self.prefix_length = len(self.temp_unarchive_dir)

    def clean(self, exclude_patterns: List[Pattern]):
        self._unpack_archive()
        self._remake_archive(exclude_patterns=exclude_patterns)
        self._remove_unarchive_dir()
        self._swap_archives()

    def _unpack_archive(self):
        print(f"Unpacking {self.archive_file_path} to {self.temp_unarchive_dir}")
        shutil.unpack_archive(self.archive_file_path, self.temp_unarchive_dir)

    def _remake_archive(self, exclude_patterns: List[Pattern]):
        walk_list = list(os.walk(self.temp_unarchive_dir))
        for root, _, files in tqdm(walk_list):
            zip_relative_root = root[self.prefix_length :].lstrip(os.sep)
            should_ignore_directory = any(pattern.match(zip_relative_root) for pattern in exclude_patterns)
            if should_ignore_directory:
                continue
            for file_name in files:
                full_path = os.path.join(root, file_name)
                zip_relative_path = os.path.join(zip_relative_root, file_name)
                self._add_file(full_path=full_path, zip_relative_path=zip_relative_path)
        self.manager.close()

    def _add_file(self, full_path: str, zip_relative_path: str):
        # Make sure that the files are all correctly chmodded
        # Related: https://github.com/Miserlou/Zappa/issues/484
        # Related: https://github.com/Miserlou/Zappa/issues/682
        os.chmod(full_path, READ_EXECUTE_WRITE_MODE)
        self.manager.add(full_path=full_path, zip_relative_path=zip_relative_path)

    def _swap_archives(self):
        print(f"Renaming {self.new_archive_path} to {self.archive_file_path}")
        os.remove(self.archive_file_path)
        os.rename(self.new_archive_path, self.archive_file_path)

    def _remove_unarchive_dir(self):
        print(f"Removing {self.temp_unarchive_dir}")
        shutil.rmtree(self.temp_unarchive_dir)


def clean_archive(archive_path: str, exclude_expressions: List[str]):
    if not exclude_expressions:
        print("No exclude_expressions provided for stage.")
        return
    print(f"Cleaning {archive_path} from excluded files: {exclude_expressions}")
    exclude_patterns = [re.compile(exclude) for exclude in exclude_expressions]
    cleaner = ArchiveCleaner(archive_path=archive_path)
    cleaner.clean(exclude_patterns=exclude_patterns)


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
    archive_path = "the-spymaster-dev-1655152205.zip"
    exclude_patterns = [
        re.compile("boto3"),
        re.compile("botocore"),
        re.compile("scipy"),
        re.compile("pydantic"),
        re.compile("gensim"),
        re.compile("pandas"),
        re.compile("numpy"),
        re.compile("scipy"),
        re.compile("networkx"),
    ]
    cleaner = ArchiveCleaner(archive_path=archive_path)
    cleaner.clean(exclude_patterns=exclude_patterns)


if __name__ == "__main__":
    example()
