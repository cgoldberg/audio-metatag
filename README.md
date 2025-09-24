# audio-tag

## Clean metadata and tag MP3 or FLAC audio files

---

- Copyright (c) 2015-2025 [Corey Goldberg][github-home]
- Development: [GitHub][github-repo]
- Download/Install: [PyPI][pypi-audio-tag]
- License: [MIT][mit-license]

----

## About:

`audio_tag` is a Python CLI program that cleans metadata and tags MP3 or FLAC
audio files. It can be used on individual files or a library of files.

- In order to process a file, it **must** be named in a specific format:
  - `Artist - Title.mp3` or `Artist - Title.flac`
  - File names must contain a delimiter (` - `) between `Artist` and `Title`,
    and end with a valid extension: `.mp3` or `.flac` (case-insensitive)
- It will skip any files that are not named according to the format specified above
- It will skip any files that are not valid MP3/Flac files
- If a filename is given as an option, it will only process that file
- If no filename is specified, it will process all files (recursively) in the current directory
- A different directory can be specified using the `--dir` option

**Warning**: Edits are done in-place. Backup your files first if you want a copy of the originals.

- Existing metadata (tags) and pictures are deleted
- Metadata tags for Artist and Title are added (id3v2 or flac tags)
- New tags are taken from the file name

## Requirements:

- Python 3.9+

## Installation:

Install from [PyPI][pypi-audio-tag]:

```
pip install audio-tag
```

## CLI Options:

```
coming soon
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
