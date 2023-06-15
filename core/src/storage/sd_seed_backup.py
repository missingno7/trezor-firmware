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


def _get_backup_path(new: bool = False) -> str:
    ext = ".new" if new else ""
    return f"/trezor/backup{ext}"


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
    backup_path = _get_backup_path()

    mnemonic_secret_backup = _load_backup(backup_path)
    if mnemonic_secret_backup is not None:
        return mnemonic_secret_backup

    new_backup_path = _get_backup_path(new=True)

    # Check if there is a new mnemonic.
    mnemonic_secret_backup = _load_backup(new_backup_path)
    if mnemonic_secret_backup is None:
        # No valid mnemonic file on this SD card.
        raise WrongSdCard

    # Normal mnemonic file does not exist, but new mnemonic file exists. That means that
    # SD mnemonic regeneration was interrupted earlier. Bring into consistent state.
    # TODO Possibly overwrite mnemonic file with random data.
    try:
        fatfs.unlink(backup_path)
    except fatfs.FatFSError:
        pass

    # fatfs.rename can fail with a write error, which falls through as an FatFSError.
    # This should be handled in calling code, by allowing the user to retry.
    fatfs.rename(new_backup_path, backup_path)
    return mnemonic_secret_backup


@with_filesystem
def set_sd_seed_backup(mnemonic_secret: bytes, stage: bool = False) -> None:
    backup_path = _get_backup_path(stage)
    fatfs.mkdir("/trezor", True)

    with fatfs.open(backup_path, "w") as f:
        f.write(mnemonic_secret)

@with_filesystem
def commit_sd_seed_backup() -> None:
    backup_path = _get_backup_path(new=False)
    new_backup_path = _get_backup_path(new=True)

    try:
        fatfs.unlink(backup_path)
    except fatfs.FatFSError:
        pass
    fatfs.rename(new_backup_path, backup_path)


@with_filesystem
def remove_sd_seed_backup() -> None:
    backup_path = _get_backup_path()
    # TODO Possibly overwrite mnemonic file with random data.
    fatfs.unlink(backup_path)
