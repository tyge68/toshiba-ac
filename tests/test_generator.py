from toshiba_ac.generator import IRCodeGenerator, UnitType, ModeType, SpecialModeType, FanType

__author__ = "Thierry Ygé"
__credits__ = "K3A.me"
__copyright__ = "Thierry Ygé"
__license__ = "MIT"


def test_make_bit():
    assert IRCodeGenerator.make_bit(True) == "+591 -1643 "
    assert IRCodeGenerator.make_bit(False) == "+591 -591 "


def test_make_cmd_raw():
    parts, pulses, err = IRCodeGenerator.make_cmd_raw(0, 0, 0)
    assert parts == "0xF20D00FF 0x00000000 0x00"
    assert pulses.startswith("+4496 -4414 ")
    assert pulses.endswith("+600 ")
    assert err is None


def test_to_data_fmt():
    data_formatted = IRCodeGenerator.to_data_format("0xF20D00FF 0x00000000 0x00")
    assert data_formatted == "F20D00FF0000000000"


def test_make_mode_fan_temp_set21():
    parts, pulses, err = IRCodeGenerator.make_mode_fan_temp(
        UnitType.UnitA,
        ModeType.HeatingMode,
        SpecialModeType.NoSpecialMode,
        FanType.Fan1,
        21
    )
    assert parts == "0xF20D03FC 0x01404300 0x02"
    assert pulses is not None
    assert err is None

def test_make_mode_fan_temp_poweroff():
    parts, pulses, err = IRCodeGenerator.make_mode_fan_temp(
        UnitType.UnitA,
        ModeType.PwrOffMode,
        SpecialModeType.NoSpecialMode,
        FanType.Fan1,
        21
    )
    assert parts == "0xF20D03FC 0x01404700 0x06"
    assert pulses is not None
    assert err is None

