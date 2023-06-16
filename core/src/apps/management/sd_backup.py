from trezor.wire import ProcessError
from trezor import wire

def is_sdbackup_present():
    from trezor import sdcard
    return sdcard.is_present()



async def sd_card_backup_seed(
    ctx: wire.Context, mnemonic_secret: bytes
) -> None:
    from storage.sd_seed_backup import set_sd_seed_backup
    from apps.common.sdcard import ensure_backup_sd_card

    # Ensure sd card for backup
    await ensure_backup_sd_card(ctx)

    # Write seed backup
    set_sd_seed_backup(mnemonic_secret)


def verify_sd_backup_seed(mnemonic_secret: bytes) -> bool:
    from storage.sd_seed_backup import load_sd_seed_backup

    # Ensure correct mnemonic can be loaded
    restored_secret = load_sd_seed_backup()
    return mnemonic_secret == restored_secret

