from trezor.wire import ProcessError
from trezor import wire

def is_sdbackup_present():
    from trezor import sdcard
    return sdcard.is_present()


async def ensure_backup_sd_card(
    ctx: wire.GenericContext, ensure_filesystem: bool = True
) -> None:
    """Ensure a SD card is ready for use.

    This function runs the UI flow needed to ask the user to insert a SD card if there
    isn't one.

    If `ensure_filesystem` is True (the default), it also tries to mount the SD card
    filesystem, and allows the user to format the card if a filesystem cannot be
    mounted.
    """
    from trezor import sdcard, io

    while not sdcard.is_present():
        await _confirm_retry_insert_card(ctx)

    if not ensure_filesystem:
        return
    fatfs = io.fatfs  # local_cache_attribute
    while True:
        try:
            try:
                with sdcard.filesystem(mounted=False):
                    fatfs.mount()
            except fatfs.NoFilesystem:
                # card not formatted. proceed out of the except clause
                pass
            else:
                # no error when mounting
                return

            # Proceed to formatting. Failure is caught by the outside OSError handler
            with sdcard.filesystem(mounted=False):
                fatfs.mkfs()
                fatfs.mount()
                fatfs.setlabel("TREZOR")

            # format and mount succeeded
            return

        except OSError:
            # formatting failed, or generic I/O error (SD card power-on failed)
            await confirm_retry_sd(ctx)



async def sd_card_backup_seed(
    ctx: Context, mnemonic_secret: bytes
) -> None:
    from storage.sd_seed_backup import set_sd_seed_backup

    # Ensure sd card
    await ensure_backup_sd_card(ctx)

    # Write seed backup
    set_sd_seed_backup(mnemonic_secret)


def verify_sd_backup_seed(mnemonic_secret: bytes) -> None:
    from storage.sd_seed_backup import load_sd_seed_backup

    # Ensure correct mnemonic can be loaded
    restored_secret = load_sd_seed_backup()
    if mnemonic_secret != restored_secret:
        raise ProcessError("SD retrieved seed differs from stored seed")

