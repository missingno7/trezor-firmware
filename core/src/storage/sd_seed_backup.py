from micropython import const
from typing import TYPE_CHECKING

import storage.device
from trezor import io, utils
from trezor.sdcard import with_filesystem

if TYPE_CHECKING:
    from typing import TypeVar, Callable

    T = TypeVar("T", bound=Callable)

if utils.USE_SD_CARD:
    fatfs = io.fatfs  # global_import_cache

SD_CARD_HOT_SWAPPABLE = False
SD_SALT_LEN_BYTES = const(512)
SD_BACKUP_PATH = "/trezor/backup"

class WrongSdCard(Exception):
    pass


@with_filesystem
def _load_backup(path: str) -> bytes | None:
    # Load the mnemonic secret backup file if it exists.
    try:
        with fatfs.open(path, "r") as f:
            mnemonic_secret_backup = bytearray(SD_SALT_LEN_BYTES)
            f.read(mnemonic_secret_backup)

    except fatfs.FatFSError:
        return None


    return mnemonic_secret_backup.decode('utf-8').rstrip('\x00').encode()


@with_filesystem
def load_sd_seed_backup() -> bytes | None:
    mnemonic_secret_backup = _load_backup(SD_BACKUP_PATH)
    if mnemonic_secret_backup is not None:
        return mnemonic_secret_backup



@with_filesystem
def set_sd_seed_backup(mnemonic_secret: bytes) -> None:
    fatfs.mkdir("/trezor", True)

    with fatfs.open(SD_BACKUP_PATH, "w") as f:
        f.write(mnemonic_secret)


@with_filesystem
def remove_sd_seed_backup() -> None:
    # TODO Possibly overwrite mnemonic file with random data.
    fatfs.unlink(SD_BACKUP_PATH)
