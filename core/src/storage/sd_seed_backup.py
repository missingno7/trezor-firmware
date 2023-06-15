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


class WrongSdCard(Exception):
    pass


def _get_device_dir() -> str:
    return f"/trezor/device_{storage.device.get_device_id().lower()}"


def _get_salt_path(new: bool = False) -> str:
    ext = ".new" if new else ""
    return f"{_get_device_dir()}/backup{ext}"


@with_filesystem
def _load_salt(path: str) -> bytearray | None:
    # Load the salt file if it exists.
    try:
        with fatfs.open(path, "r") as f:
            salt = bytearray(SD_SALT_LEN_BYTES)
            f.read(salt)

    except fatfs.FatFSError:
        return None


    return salt


@with_filesystem
def load_sd_seed_backup() -> bytearray | None:

    salt_path = _get_salt_path()
    new_salt_path = _get_salt_path(new=True)

    salt = _load_salt(salt_path)
    if salt is not None:
        return salt

    # Check if there is a new salt.
    salt = _load_salt(new_salt_path)
    if salt is None:
        # No valid salt file on this SD card.
        raise WrongSdCard

    # Normal salt file does not exist, but new salt file exists. That means that
    # SD salt regeneration was interrupted earlier. Bring into consistent state.
    # TODO Possibly overwrite salt file with random data.
    try:
        fatfs.unlink(salt_path)
    except fatfs.FatFSError:
        pass

    # fatfs.rename can fail with a write error, which falls through as an FatFSError.
    # This should be handled in calling code, by allowing the user to retry.
    fatfs.rename(new_salt_path, salt_path)
    return salt


@with_filesystem
def set_sd_seed_backup(salt: bytes, stage: bool = False) -> None:
    salt_path = _get_salt_path(stage)
    fatfs.mkdir("/trezor", True)
    fatfs.mkdir(_get_device_dir(), True)


    with fatfs.open(salt_path, "w") as f:
        f.write(salt)


@with_filesystem
def commit_sd_seed_backup() -> None:
    salt_path = _get_salt_path(new=False)
    new_salt_path = _get_salt_path(new=True)

    try:
        fatfs.unlink(salt_path)
    except fatfs.FatFSError:
        pass
    fatfs.rename(new_salt_path, salt_path)


@with_filesystem
def remove_sd_seed_backup() -> None:
    salt_path = _get_salt_path()
    # TODO Possibly overwrite salt file with random data.
    fatfs.unlink(salt_path)
