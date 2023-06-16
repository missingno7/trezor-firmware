from trezor import wire



async def sd_card_backup_seed(
    ctx: wire.Context, mnemonic_secret: bytes
) -> None:
    from storage.sd_seed_backup import set_sd_seed_backup
    from apps.common.sdcard import ensure_sd_backup

    # Ensure sd card for backup
    await ensure_sd_backup(ctx)

    # Write seed backup
    set_sd_seed_backup(mnemonic_secret)


def verify_sd_backup_seed(mnemonic_secret: bytes) -> bool:
    from storage.sd_seed_backup import load_sd_seed_backup

    # Ensure correct mnemonic can be loaded
    restored_secret = load_sd_seed_backup()
    return mnemonic_secret == restored_secret

