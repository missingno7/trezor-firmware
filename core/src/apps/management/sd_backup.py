from trezor.wire import ProcessError

def is_sdbackup_present():
    from trezor import sdcard
    return sdcard.is_present()



async def sd_card_backup_seed(
    ctx: Context, mnemonic_secret: bytes
) -> None:
    from storage.sd_seed_backup import set_sd_seed_backup
    from apps.common.sdcard import ensure_sdcard

    # Ensure sd card
    await ensure_sdcard(ctx)

    # Write seed backup
    set_sd_seed_backup(mnemonic_secret)



def ensure_sd_card_backup_seed(mnemonic_secret: bytes) -> None:
    from storage.sd_seed_backup import set_sd_seed_backup
    from trezor import sdcard, io

    # Force format sd card
    fatfs = io.fatfs  # local_cache_attribute
    with sdcard.filesystem(mounted=False):
        fatfs.mkfs()
        fatfs.mount()
        fatfs.setlabel("TREZOR")

    # Write seed backup
    set_sd_seed_backup(mnemonic_secret)


def verify_sd_backup_seed(mnemonic_secret: bytes) -> None:
    from storage.sd_seed_backup import load_sd_seed_backup

    # Ensure correct mnemonic can be loaded
    restored_secret = load_sd_seed_backup()
    if mnemonic_secret != restored_secret:
        raise ProcessError("SD retrieved seed differs from stored seed")
