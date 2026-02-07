# audio-metatag

### Clean metadata and tag audio files (MP3, FLAC, Ogg Vorbis)

---

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/audio-metatag)](https://pypi.org/project/audio-metatag)

- Copyright (c) 2015-2026 [Corey Goldberg][github-home]
- Development: [GitHub][github-repo]
- Download/Install: [PyPI][pypi-audio-metatag]
- License: [MIT][mit-license]

----

## About:

`audio_metatag` is a Python CLI program for cleaning metadata and adding
ARTIST/TITLE tags to MP3, FLAC, and Ogg Vorbis audio files. It can be used on
individual files or a library of files.

- In order to tag a file, it **must** be named in a specific format:
  - `Artist - Title.mp3`, `Artist - Title.flac`, `Artist - Title.ogg`
  - File names must contain a delimiter (` - `) between `Artist` and `Title`,
    and end with a valid extension: `.mp3`, `.flac`, `.ogg` (case-insensitive)
- It will skip any files that are not named according to the format specified above

**Warning**: Edits are done in-place. Backup your files first if you want a
copy of the originals.

- Existing metadata is deleted
- ARTIST and TITLE tag data is taken from the filename
- New metadata is saved to the file

## Requirements:

- Python 3.12+

## Installation:

Install from [PyPI][pypi-audio-metatag]:

```
pip install audio-metatag
```

## CLI Options:

- If filenames are given as command-line options, it will only process those files
- If no filename is specified, it will process all files (recursively) in the current directory
- A different directory can be specified using the `--dir` option

```
usage: audio_metatag [-h] [-d DIR] [-c] [-s] [filename ...]

positional arguments:
  filename       [optional] file to process (multiple allowed)

options:
  -h, --help     show this help message and exit
  -d, --dir DIR  start directory
  -c, --clean    only clean metadata (don't write new tags)
  -s, --show     only show metadata (don't remove or write tags)
```

## Usage Examples:

#### Install from PyPI with pipx:

```
pipx install audio-metatag
```

#### Clean metadata and tag a single file:

```
audio_metatag "Some Artist - Some Title.mp3"
```

#### Clean metadata and tag all files in current directory (recurse subdirectories):

```
audio_metatag
```

#### Clean metadata from all files in a directory (recurse subdirectories):

```
audio_metatag --clean --dir=/path/to/files
```

----

## Metadata Details:

### Metadata that is clean/removed:

- FLAC
  - VORBIS_COMMENT
  - PICTURE
  - SEEKTABLE
  - CUESHEET
  - APPLICATION
  - PADDING
  - ID3 (extraneous)

- MP3
  - ID3v1
  - ID3v2
  - APEv2

- Ogg Vorbis
  - Vorbis Comments

### Metadata where new tags are written:

- FLAC
  - VORBIS_COMMENT

- MP3
  - ID3v2.4

- Ogg Vorbis
  - Vorbis Comments

----

[github-home]: https://github.com/cgoldberg
[github-repo]: https://github.com/cgoldberg/audio-metatag
[pypi-audio-metatag]: https://pypi.org/project/audio-metatag
[mit-license]: https://raw.githubusercontent.com/cgoldberg/audio-metatag/refs/heads/main/LICENSE
