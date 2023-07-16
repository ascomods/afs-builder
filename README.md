# AFS Builder

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

*Copyright © 2023 Ascomods*

## Description

AFS Builder is an open-source tool that can extract and rebuild / create AFS archives.
It's mostly designed for games from the Dragon Ball Raging Blast series (RB/RB2, UT),
but it may work with other games using the AFS file format (e.g: Budokai / Budokai Tenkaichi games...).

AFS files built with this tool are compatible with AFSExplorer.

Credits to revel8n and to the rest of the RB modding community for their contributions.

## Building

Python version: `3.7.9`

Dependencies:
```
natsort: 7.1.1
colorama: 0.4.6
Wine for linux support (tested with 8.1, might work with earlier versions)
```
Install libraries using pip:
```
pip install -r requirements.txt
```
Build using PyInstaller:
```
pyinstaller app.spec
```

## Usage

List all available commands:
```
AFS_Builder.exe -h
```

### Extraction

Extract an AFS archive (-f to overwrite):
```
AFS_Builder.exe -x my_file.afs -o output_folder -f
```
If no output folder was provided, a folder with the name of the archive will be created in the current folder.

Extract an AFS archive with decompression (slow, only for RB/RB2 & UT games):
```
AFS_Builder.exe -x my_file.afs -o output_folder -f -d True
```

### Creation

Build an AFS archive from a folder (-f to overwrite):
```
AFS_Builder.exe -b input_folder -o my_file.afs -f
```

Build an AFS archive from a folder with compression (very slow depending of archive file size, only for RB/RB2 & UT games).
By default, the compression method used is for RB:
```
AFS_Builder.exe -b input_folder -o my_file.afs -f -c True
```

Build an AFS archive from a folder with compression for UT:
```
AFS_Builder.exe -b input_folder -o my_file.afs -f -c True -g dbut
```

### Update

Update an AFS archive with an AFL file:
```
AFS_Builder.exe -u my_file.afs -afl my_name_list.afl
```

### Entry listing

List files from an AFS archive:
```
AFS_Builder.exe -l my_file.afs
```

List files from an AFS archive and export the name list into an AFL file:
```
AFS_Builder.exe -l my_file.afs -afl my_name_list.afl
```