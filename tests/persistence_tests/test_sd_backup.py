# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

from trezorlib import device

from .. import buttons
from ..device_handler import BackgroundDeviceHandler
from ..emulators import Emulator
from ..upgrade_tests import core_only

@core_only
def test_sd_card_backup_and_recovery(core_emulator: Emulator):
    device_handler = BackgroundDeviceHandler(core_emulator.client)
    debug = device_handler.debuglink()

    # Confirm device state
    features = device_handler.features()
    assert features.initialized is False

    # Create wallet and do the SD card backup
    device_handler.run(device.reset, pin_protection=False)
    assert debug.wait_layout().title() == "WALLET CREATION"

    layout = debug.click(buttons.OK, wait=True)
    assert "wallet created successfully" in layout.text_content()

    layout = debug.click(buttons.OK, wait=True)
    assert "perform the SD card backup?" in layout.text_content()

    layout = debug.click(buttons.OK, wait=True)
    assert "Your backup is done." in layout.text_content()

    layout = debug.click(buttons.OK, wait=True)
    assert layout.main_component() == "Homescreen"

    # Confirm device state
    assert device_handler.result() == "Initialized"
    features = device_handler.features()
    assert features.initialized is True

    # Wipe the device
    device_handler.run(device.wipe)

    debug = device_handler.debuglink()
    assert debug.wait_layout().title() == "WIPE DEVICE"

    layout = debug.click_hold(buttons.OK, hold_ms=1500)
    assert layout.main_component() == "Homescreen"

    # Confirm device state
    assert device_handler.result() == "Device wiped"
    features = device_handler.features()
    assert features.initialized is False

    # Recover from SD card backup
    device_handler.run(device.recover, pin_protection=False)

    debug = device_handler.debuglink()
    assert debug.wait_layout().title() == "SD CARD RECOVERY"

    layout = debug.click(buttons.OK, wait=True)
    assert layout.text_content() == "You have finished recovering your wallet."

    layout = debug.click(buttons.OK, wait=True)
    assert layout.main_component() == "Homescreen"

