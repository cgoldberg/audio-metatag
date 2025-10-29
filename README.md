# audio-metatag

### Clean metadata and tag audio files (MP3, FLAC, Ogg Vorbis)

---

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/audio-metatag)](https://pypi.org/project/audio-metatag)

- Copyright (c) 2015-2025 [Corey Goldberg][github-home]
- Development: [GitHub][github-repo]
- Download/Install: [PyPI][pypi-audio-tag]
- License: [MIT][mit-license]

----

## About:

`audio_metatag` is a Python CLI program that cleans metadata and adds artist/title
tags to MP3, FLAC, or Ogg vorbis audio files. It can be used on individual
files or a library of files.

- In order to process a file, it **must** be named in a specific format:
  - `Artist - Title.mp3`, `Artist - Title.flac`, `Artist - Title.ogg`
  - File names must contain a delimiter (` - `) between `Artist` and `Title`,
    and end with a valid extension: `.mp3`, `.flac`, `.ogg` (case-insensitive)
- It will skip any files that are not named according to the format specified above
- If filenames are given as command-line options, it will only process those files
- If no filename is specified, it will process all files (recursively) in the current directory
- A different directory can be specified using the `--dir` option

**Warning**: Edits are done in-place. Backup your files first if you want a copy of the originals.

- Existing metadata (tags) and pictures are deleted
- Artist and Title tag data is taken from the filename
- Metadata tags are saved to the file (id3v2, flac, ogg)

## Requirements:

- Python 3.12+

## Installation:

Install from [PyPI][pypi-audio-metatag]:

```
pip install audio-metatag
```

## CLI Options:

```
usage: audio_metatag [-h] [-d DIR] [-c] [filename ...]

positional arguments:
  filename       file to process (multiple allowed)

options:
  -h, --help     show this help message and exit
  -d, --dir DIR  start directory
  -c, --clean    only clean metadata (don't write tags)
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

[github-home]: https://github.com/cgoldberg
[github-repo]: https://github.com/cgoldberg/audio-metatag
[pypi-audio-tag]: https://pypi.org/project/audio-metatag
[mit-license]: https://raw.githubusercontent.com/cgoldberg/audio-metatag/refs/heads/main/LICENSE
