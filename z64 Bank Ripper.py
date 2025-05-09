import os
import sys
import binascii
from typing import BinaryIO
from time import strftime

# Last updated
LAST_UPDATED = '2025.05.08'

# Create ANSI formatting for terminal messages
# ANSI COLORS: https://talyian.github.io/ansicolors/
RESET  = "\x1b[0m"
BLUE   = "\x1b[38;5;14m"
PINK   = "\x1b[38;5;218m"
GREEN  = "\x1b[38;5;115m"
GREY   = "\x1b[38;5;8m"
YELLOW = "\x1b[33m"

OOT_BLUE = "\x1b[38;5;39m"
MM_PURPLE = "\x1b[38;5;141m"

ROM_FILE = sys.argv[1]
ROM_LENGTH = 67108864

AUDIOBIN_OFFSETS: dict[str, dict[str, tuple[int, int]]] = {
  "oot": {
    #"Audiobank":        (0x0000D390, 0x0001CA50),
    "Audiobank_index":  (0x00B896A0, 0x00000270),
  },
  "mm": {
    #"Audiobank":        (0x00020700, 0x000263F0),
    "Audiobank_index":  (0x00C776C0, 0x000002A0),
  }
}

OOT_BANK_SIZES = [
  0x3AA0, 0x17B0, 0x0CE0, 0x15D0, 0x0100,
  0x0B60, 0x0520, 0x0840, 0x0B20, 0x0FC0,
  0x09D0, 0x0390, 0x0320, 0x06F0, 0x0390,
  0x0B40, 0x09E0, 0x0560, 0x0CC0, 0x03A0,
  0x0AA0, 0x0A60, 0x0BF0, 0x01F0, 0x0860,
  0x05B0, 0x0250, 0x04E0, 0x04C0, 0x0C00,
  0x0270, 0x0640, 0x1300, 0x11A0, 0x1720,
  0x0DE0, 0x0660, 0x3940
]

MM_BANK_SIZES = [
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
  def detected_game(game : str, color : str):
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
{GREY}[{PINK}>{GREY}]:{RESET} {YELLOW}Warning:{RESET} The number of banks is {YELLOW}0x{number}{RESET} instead of {"0x26" if game == "oot" else "0x29"}.
''')

def extract_and_write_files(rom: BinaryIO, offset: int, size: int, game: str, output_dir, bank_lens):
  rom.seek(offset)
  audiobank_table = rom.read(size)

  hexified_table_data = binascii.hexlify(audiobank_table)
  if game == "oot" and hexified_table_data[0:4] != b'0026':
      SysMsg.bank_number_error(game, int(hexified_table_data[0:4]))
  elif game == "mm" and hexified_table_data[0:4] != b'0029':
      SysMsg.bank_number_error(game, int(hexified_table_data[0:4]))

  bank_index = 0
  audiobank_table_dmaspaced = [audiobank_table[i:i+0x10] for i in range(0x10, len(audiobank_table), 0x10)]
  for dma in audiobank_table_dmaspaced:
    address = int.from_bytes(dma[0:4], "big")
    length = int.from_bytes(dma[4:8], "big")

    if bank_lens[bank_index] != length:
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      output_dir += "/"

      metadata = dma[8:16]
      bank_index_hex = hex(bank_index).lstrip("0x").zfill(2)
      filename = output_dir + bank_index_hex

      with open(f"{filename}.zbank", 'wb') as zbank:
        rom.seek(offset + address)
        zbank.write(rom.read(length))

      with open(f"{filename}.bankmeta", 'wb') as bankmeta:
        bankmeta.write(metadata)

    bank_index += 1

def main(game) -> None:
  output_dir = f"{game}_" + strftime("%Y-%m-%d_%H%M")

  if game == "oot":
    with open(ROM_FILE, 'rb') as rom:
      offset = AUDIOBIN_OFFSETS["oot"]["Audiobank_index"][0]
      size = AUDIOBIN_OFFSETS["oot"]["Audiobank_index"][1]
      SysMsg.extracting_data()
      extract_and_write_files(rom, offset, size, game, output_dir, OOT_BANK_SIZES)

  if game == "mm":
    with open(ROM_FILE, 'rb') as rom:
      offset = AUDIOBIN_OFFSETS["mm"]["Audiobank_index"][0]
      size = AUDIOBIN_OFFSETS["mm"]["Audiobank_index"][1]
      SysMsg.extracting_data()
      extract_and_write_files(rom, offset, size, game, output_dir, MM_BANK_SIZES)

if __name__ == "__main__":
  SysMsg.header()

  if os.path.getsize(ROM_FILE) != ROM_LENGTH:
    SysMsg.compressed_rom()

  SysMsg.read_rom_header()
  with open(ROM_FILE, 'rb') as rom:
    rom_header = rom.read(64)

    # OCARINA OF TIME BIG ENDIAN
    if b"THE LEGEND OF ZELDA \x00\x00\x00\x00\x00\x00\x00CZLE\x00" in rom_header:
      SysMsg.detected_game("Ocarina of Time", OOT_BLUE)
      game = "oot"

    # MAJORA'S MASK BIG ENDIAN
    elif b"ZELDA MAJORA'S MASK \x00\x00\x00\x00\x00\x00\x00NZSE\x00" in rom_header:
      SysMsg.detected_game("Majora's Mask", MM_PURPLE)
      game = "mm"

    # OCARINA OF TIME BYTESWAPPED
    elif b"HT EELEGDNO  FEZDL A\x00\x00\x00\x00\x00\x00C\x00L\x00E" in rom_header:
      SysMsg.detected_game("Ocarina of Time", OOT_BLUE)
      SysMsg.byteswapped_rom()

    # MAJORA'S MASK BYTESWAPPED
    elif b"EZDL AAMOJARS'M SA K\x00\x00\x00\x00\x00\x00N\x00SZ\x00E" in rom_header:
      SysMsg.detected_game("Majora's Mask", MM_PURPLE)
      SysMsg.byteswapped_rom()

    # OCARINA OF TIME LITTLE ENDIAN
    elif b"EHTEGELO DNEZ F ADL\x00\x00\x00\x00C\x00\x00\x00\x00ELZ" in rom_header:
      SysMsg.detected_game("Ocarina of Time", OOT_BLUE)
      SysMsg.little_endian_rom()

    # MAJORA'S MASK LITTLE ENDIAN
    elif b"DLEZAM AAROJM S' KSA\x00\x00\x00\x00N\x00\x00\x00\x00ESZ" in rom_header:
      SysMsg.detected_game("Majora's Mask", MM_PURPLE)
      SysMsg.little_endian_rom()

    # UNKNOWN GAME
    else:
      SysMsg.unknown_game()

  main(game)
  SysMsg.complete()
