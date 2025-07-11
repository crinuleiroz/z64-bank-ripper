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
The script only extracts banks whose length does not match the length of the origin game's bank at the given index. If you want to rip vanilla banks, change `EXTRACT_VANILLA` at the top of the file from `False` to `True`
