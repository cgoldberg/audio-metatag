# audio-tag

## Clean metadata and tag audio files (MP3, FLAC, Ogg Vorbis)

---

- Copyright (c) 2015-2025 [Corey Goldberg][github-home]
- Development: [GitHub][github-repo]
- Download/Install: [PyPI][pypi-audio-tag]
- License: [MIT][mit-license]

----

## About:

`audio_tag` is a Python CLI program that cleans metadata and adds artist/title
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

Install from [PyPI][pypi-audio-tag]:

```
pip install audio-tag
```

## CLI Options:

```
usage: audio_tag [-h] [-d DIR] [-c] [filename ...]

positional arguments:
  filename       file to process (multiple allowed)

options:
  -h, --help     show this help message and exit
  -d, --dir DIR  start directory
  -c, --clean    only clean metadata (don't write tags)
```

## Usage Examples:

#### Install from PyPI with pipx, Run:

```
pipx install audio-tag
audio_tag
```

#### Clone Repo, Create/Activate Virtual Environment, Install from Source, Run:

```
git clone git@github.com:cgoldberg/audio-tag.git
cd ./audio-tag
python3 -m venv venv
source venv/bin/activate
pip install .
audio_tag
```

[github-home]: https://github.com/cgoldberg
[github-repo]: https://github.com/cgoldberg/audio-tag
[pypi-audio-tag]: https://pypi.org/project/audio-tag
[mit-license]: https://raw.githubusercontent.com/cgoldberg/audio-tag/refs/heads/main/LICENSE
