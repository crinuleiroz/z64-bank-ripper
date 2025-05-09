# Zelda64 Bank Ripper

## 🔧 How to Use
Drag and drop a decompressed Ocarina of Time or Majora's Mask ROM onto the script or use the following CLI command:
```
python <script name> <ROM file>
```
The script will check the size of the ROM to ensure it is decompressed, then it will read the ROM's header to detect the game and extract the audio binary files at the correct offsets.

> [!NOTE]
> The output folder will be in the same folder as the script — it will not be in the same folder as the input ROM file.

## 🖥️ ROM Decompression Utility
If you need to decompress a ROM, you can use [z64decompress](https://github.com/z64utils/z64decompress) by z64utils. Just drag and drop your ROM onto the executable (`.exe`) file.

## What is Extracted
The script only extracts banks whose length does not match the length of the origin game's bank at the given index. If you want to rip every single bank, make the following changes:

At line 148, change the code from this:
```py
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
```

To this (removing the conditional that checks the length):
```py
#if bank_lens[bank_index] != length:
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
```
