# Set to "True" to extract only vanilla banks, "False" to only extract changed banks
EXTRACT_VANILLA = False


from time import strftime
from typing import BinaryIO
import binascii
import sys
import os


LAST_UPDATED = '2025.05.20'

# Create ANSI formatting for terminal messages
# ANSI COLORS: https://talyian.github.io/ansicolors/
RESET  = '\x1b[0m'
BLUE   = '\x1b[38;5;14m'
PINK   = '\x1b[38;5;218m'
GREEN  = '\x1b[38;5;115m'
GREY   = '\x1b[38;5;8m'
YELLOW = '\x1b[33m'

OOT_BLUE  = '\x1b[38;5;39m'
MM_PURPLE = '\x1b[38;5;141m'

ROM_FILE = sys.argv[1]
ROM_SIZE = 67108864

GAME_SIGNATURES: dict[str, dict[str, str]] = {
    'big_endian': {
        'oot': {
            'signature': b"THE LEGEND OF ZELDA \x00\x00\x00\x00\x00\x00\x00CZLE\x00",
            'name': "Ocarina of Time",
            'color': OOT_BLUE
        },
        'mm': {
            'signature': b"ZELDA MAJORA'S MASK \x00\x00\x00\x00\x00\x00\x00NZSE\x00",
            'name': "Majora's Mask",
            'color': MM_PURPLE
        }
    },
    'little_endian': {
        'oot': {
            'signature': b"EHTEGELO DNEZ F ADL\x00\x00\x00\x00C\x00\x00\x00\x00ELZ",
            'name': "Ocarina of Time",
            'color': OOT_BLUE
        },
        'mm': {
            'signature': b"DLEZAM AAROJM S' KSA\x00\x00\x00\x00N\x00\x00\x00\x00ESZ",
            'name': "Majora's Mask",
            'color': MM_PURPLE
        }
    },
    'byteswapped': {
        'oot': {
            'signature': b"HT EELEGDNO  FEZDL A\x00\x00\x00\x00\x00\x00C\x00L\x00E",
            'name': "Ocarina of Time",
            'color': OOT_BLUE
        },
        'mm': {
            'signature': b"EZDL AAMOJARS'M SA K\x00\x00\x00\x00\x00\x00N\x00SZ\x00E",
            'name': "Majora's Mask",
            'color': MM_PURPLE
        }
    }
}

AUDIOBIN_OFFSETS: dict[str, dict[str, tuple[int, int]]] = {
    'oot': {
        'Audiobank':        (0x0000D390, 0x0001CA50),
        'Audiobank_index':  (0x00B896A0, 0x00000270),
    },
    'mm': {
        'Audiobank':        (0x00020700, 0x000263F0),
        'Audiobank_index':  (0x00C776C0, 0x000002A0),
    }
}

NUM_BANKS: dict[str, str] = {
    'oot': b'0026',
    'mm': b'0029'
}

OOT_BANK_SIZES: list[int] = [
    0x3AA0, 0x17B0, 0x0CE0, 0x15D0, 0x0100,
    0x0B60, 0x0520, 0x0840, 0x0B20, 0x0FC0,
    0x09D0, 0x0390, 0x0320, 0x06F0, 0x0390,
    0x0B40, 0x09E0, 0x0560, 0x0CC0, 0x03A0,
    0x0AA0, 0x0A60, 0x0BF0, 0x01F0, 0x0860,
    0x05B0, 0x0250, 0x04E0, 0x04C0, 0x0C00,
    0x0270, 0x0640, 0x1300, 0x11A0, 0x1720,
    0x0DE0, 0x0660, 0x3940
]

MM_BANK_SIZES: list[int] = [
    0x81C0, 0x36D0, 0x0CE0, 0x15D0, 0x0B60,
    0x0BE0, 0x0FC0, 0x06F0, 0x0560, 0x0CC0,
    0x0AA0, 0x0A60, 0x0BF0, 0x04C0, 0x0C00,
    0x0DE0, 0x0660, 0x14D0, 0x0C50, 0x1150,
    0x0520, 0x0770, 0x0500, 0x0940, 0x0840,
    0x1440, 0x0300, 0x0AE0, 0x06F0, 0x05B0,
    0x0810, 0x0520, 0x0FF0, 0x15E0, 0x00D0,
    0x14B0, 0x1410, 0x1540, 0x0390, 0x0520,
    0x03F0
]


class SysMsg:
    @staticmethod
    def header():
        print(f'''\
{GREY}[▪]----------------------------------[▪]
 |    {RESET}{PINK}AUDIOBANK RIPPER {GREY}v{LAST_UPDATED}    |
[▪]----------------------------------[▪]{RESET}
''')

    @staticmethod
    def complete():
        print(f'''\
{GREY}[▪]----------------------------------[▪]
 |     {RESET}{GREEN}Process is now completed      {GREY}|
[▪]----------------------------------[▪]{RESET}
''')
        os.system('pause')

    @staticmethod
    def compressed_rom():
        print(f'''\
{GREY}[{PINK}>{GREY}]:{RESET} Error: ROM file is not decompressed!
''')
        os.system('pause')
        sys.exit(1)

    @staticmethod
    def read_rom_header():
        print(f'''\
{GREY}[{PINK}>{GREY}]:{RESET} Reading ROM header:     {BLUE}"{ROM_FILE}"{RESET}''')

    @staticmethod
    def detected_game(game: str, color: str):
        print(f'''\
{GREY}[{PINK}>{GREY}]:{RESET} Detected game:          {color}"{game}"{RESET}
''')

    @staticmethod
    def byteswapped_rom():
        print(f'''\
{GREY}[{PINK}>{GREY}]:{RESET} Error: ROM file byte order is "Byteswapped", use {PINK}tool64{RESET} to change the byte order to "Big Endian"!
''')
        os.system('pause')
        sys.exit(1)

    @staticmethod
    def little_endian_rom():
        print(f'''\
{GREY}[{PINK}>{GREY}]:{RESET} Error: ROM file byte order is "Little Endian", use {PINK}tool64{RESET} to change the byte order to "Big Endian"!
''')
        os.system('pause')
        sys.exit(1)

    @staticmethod
    def unknown_game():
        print(f'''\
{GREY}[{PINK}>{GREY}]:{RESET} Error: Decompressed ROM has an unexpected ROM header!
''')
        os.system('pause')
        sys.exit(1)

    @staticmethod
    def extracting_data():
        print(f'''\
{GREY}[{PINK}>{GREY}]:{RESET} Extracting and writing banks and bankmeta...{RESET}
''')

    @staticmethod
    def bank_number_error(game, number):
        print(f'''\
{GREY}[{PINK}>{GREY}]:{RESET} {YELLOW}Warning:{RESET} The number of banks is {YELLOW}0x{number}{RESET} instead of {'0x26' if game == 'oot' else '0x29'}.
''')


def extract_banks(rom: BinaryIO, audiobank_loc: int, address: int, size: int, output_dir: str, bank_index: int, entry):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir += '/'

    metadata = entry[8:16]
    bank_index_hex = hex(bank_index).lstrip('0x').zfill(2)
    filename = output_dir + bank_index_hex

    with open(f'{filename}.zbank', 'wb') as zbank:
        rom.seek(audiobank_loc + address)
        zbank.write(rom.read(size))

    with open(f'{filename}.bankmeta', 'wb') as bankmeta:
        bankmeta.write(metadata)


def extract_and_write_files(rom: BinaryIO, audiobank_loc: int, offset: int, size: int, game: str, output_dir, bank_sizes):
    rom.seek(offset)
    audiobank_table = rom.read(size)
    hexified_table_data = binascii.hexlify(audiobank_table)

    num_banks = NUM_BANKS.get(game)
    if num_banks and hexified_table_data[:4] != num_banks:
        SysMsg.bank_number_error(game, int(hexified_table_data[0:4]))

    # Parse DMA audiobank table entries while skipping the first 0x10 bytes (header)
    table_entries = [audiobank_table[i:i+0x10] for i in range(0x10, len(audiobank_table), 0x10)]

    for index, entry in enumerate(table_entries):
        address = int.from_bytes(entry[0:4], 'big')
        size = int.from_bytes(entry[4:8], 'big')

        is_vanilla_size: bool = bank_sizes[index] == size

        if (EXTRACT_VANILLA and is_vanilla_size) or (not EXTRACT_VANILLA and not is_vanilla_size):
            extract_banks(rom, audiobank_loc, address, size, output_dir, index, entry)


def main(game) -> None:
    output_dir = f'{game}_' + strftime('%Y-%m-%d_%H%M')

    match game:
        case 'oot':
            bank_sizes = OOT_BANK_SIZES
        case 'mm':
            bank_sizes = MM_BANK_SIZES

    with open(ROM_FILE, 'rb') as rom:
        offset = AUDIOBIN_OFFSETS[game]['Audiobank_index'][0]
        size = AUDIOBIN_OFFSETS[game]['Audiobank_index'][1]
        audiobank_loc = AUDIOBIN_OFFSETS[game]['Audiobank'][0]
        SysMsg.extracting_data()
        extract_and_write_files(rom, audiobank_loc, offset, size, game, output_dir, bank_sizes)


if __name__ == '__main__':
    SysMsg.header()

    if os.path.getsize(ROM_FILE) != ROM_SIZE:
        SysMsg.compressed_rom()

    SysMsg.read_rom_header()
    with open(ROM_FILE, 'rb') as rom:
        rom_header: bytes = rom.read(64)

        game: str = None
        match_data: tuple[str, ...] = None

        for endianness, games in GAME_SIGNATURES.items():
            for game_key, info in games.items():
                if info['signature'] in rom_header:
                    match_data = (endianness, game_key, info)
                    break
            if match_data:
                break

        if match_data:
            endianness, game, info = match_data
            SysMsg.detected_game(info['name'], info['color'])

            match endianness:
                case 'little_endian':
                    SysMsg.little_endian_rom()
                case 'byteswapped':
                    SysMsg.byteswapped_rom()
                case 'big_endian':
                    pass
        else:
            SysMsg.unknown_game()

    main(game)
    SysMsg.complete()
