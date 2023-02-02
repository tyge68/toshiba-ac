from typing import Tuple
from enum import Enum

UINT8_MASK = int("0xFF", 0)
NoChecksum = int("0x60", 0)


class UnitType(Enum):
    UnitA = 0
    UnitB = 1


class ModeType(Enum):
    AutoMode = 0
    CoolingMode = 1
    DryingMode = 2
    HeatingMode = 3
    PwrOffMode = 7


class FanType(Enum):
    FanAuto = 0
    Fan1 = 2
    Fan2 = 3
    Fan3 = 4
    Fan4 = 5
    Fan5 = 6


class CmdType(Enum):
    CheckFixSwingCommand = 1
    ModeFanTempCommand = 3
    HiPowerEcoCommand = 4


class SpecialModeType(Enum):
    NoSpecialMode = 0
    HiPowerSpecialMode = 1
    EcoSpecialMode = 3


class IRCodeGenerator:

    @staticmethod
    def make_bit(val: bool) -> str:
        if val:
            return "+591 -1643 "  # one
        else:
            return "+591 -591 "  # zero

    @staticmethod
    def make_cmd_raw(
            cmd: int,
            state: int,
            end_byte: int
    ) -> Tuple[str, str, TypeError]:
        prefix = int("0xF20D0000", 0)
        if cmd > UINT8_MASK:
            return "", TypeError("sendCmd: cmd must be in range [0, 0xFF]")
        # command
        prefix |= ((cmd & UINT8_MASK) << 8)
        # checksum
        prefix |= ((prefix >> 24) & UINT8_MASK) ^ ((prefix >> 16) & UINT8_MASK) ^ ((prefix >> 8) & UINT8_MASK)
        # print command parts
        parts = "0x{0:08X} 0x{1:08X} 0x{2:02X}".format(prefix, state & int("0xFFFFFFFF", 0), end_byte & UINT8_MASK)
        # construct pulse output
        pulses = "+4496 -4414 "  # header
        for i in range(31, 0, -1):
            pulses += IRCodeGenerator.make_bit(prefix & (1 << i) != 0)
        for i in range(31, 0, -1):
            pulses += IRCodeGenerator.make_bit(state & (1 << i) != 0)
        for i in range(7, 0, -1):
            pulses += IRCodeGenerator.make_bit(end_byte & (1 << i) != 0)
        pulses += "+600 "  # tail
        return parts, pulses, None

    @staticmethod
    def make_mode_fan_temp(
            unit: UnitType,
            mode: ModeType,
            special_mode: SpecialModeType,
            fan: FanType,
            temp_celsius: int
    ) -> Tuple[str, str, TypeError]:
        #          abcd efgh ijkl mnop qrst uvwx yz23 4567     checksum - dec
        # 23 deg    0000 0001 0110 0000 0000 0001 0000 0000     0110 0000 - 96
        #                    ijkl - temp above 17 (so 0000 is 17)
        #                                    vwx – 000:auto, 001:cooling, 010:drying, 011:heating, 111:pwroff
        #               efgh - special mode bits (1 - normal mode, 9 - hipower or eco depending on endByte)
        special_mode_bits = 1
        if special_mode is not SpecialModeType.NoSpecialMode:
            special_mode_bits = 9
        state = special_mode_bits << 24  # to set "h" bit to 1 or efgh to 9 (special mode)
        if temp_celsius < 17 or temp_celsius > 30:
            return "", "", TypeError("sendCmd: temperature must be in the range [17, 30]")
        state |= ((temp_celsius - 17) & int("0x0F", 0)) << 20  # 4 bits of temp over 17
        state |= (fan.value & int("0x1F", 0)) << 13  # 3 bits of fan type
        state |= (mode.value & int("0x1F", 0)) << 8  # 3 bits of mode type
        if special_mode is not SpecialModeType.NoSpecialMode:
            end_byte = special_mode
        else:
            # common state checksum
            end_byte = ((state >> 24) & UINT8_MASK) \
                       ^ ((state >> 16) & UINT8_MASK) \
                       ^ ((state >> 8) & UINT8_MASK) \
                       ^ (state & UINT8_MASK)
        # first 4bits of command are unit index
        return IRCodeGenerator.make_cmd_raw((unit.value << 4) | CmdType.ModeFanTempCommand.value, state, end_byte)

    @staticmethod
    def to_data_format(parts: str):
        return parts.replace("0x", "").replace(" ", "")