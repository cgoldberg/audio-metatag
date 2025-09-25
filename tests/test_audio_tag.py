import os
import re
import shutil
from pathlib import Path

import mutagen
import pytest

import audio_tag

SAMPLES_DIR = Path("tests", "sample_files")


@pytest.fixture
def clean_files(tmp_path):
    for entry in SAMPLES_DIR.iterdir():
        if entry.is_file():
            shutil.copyfile(entry, tmp_path)
    return tmp_path


def get_sample_audio(filename):
    filepath = os.path.abspath(SAMPLES_DIR / filename)
    audio = mutagen.File(filepath, easy=True)
    return audio


def test_get_artist_and_title_from_filename_():
    filename = "Artist - Title.mp3"
    artist, title = audio_tag.get_artist_and_title_from_filename(filename)
    assert artist == "Artist"
    assert title == "Title"


def test_get_artist_and_title_from_filename_with_path():
    filepath = "/path/to/Artist - Title.flac"
    artist, title = audio_tag.get_artist_and_title_from_filename(filepath)
    assert artist == "Artist"
    assert title == "Title"


def test_get_artist_and_title_from_filename_with_invalid_filename():
    filename = "Invalid Filename.flac"
    with pytest.raises(Exception, match=re.escape("invalid filename (no delimiter found)")):
        audio_tag.get_artist_and_title_from_filename(filename)


#def test_clear_tags_mp3(clean_files):
#    sample_audio = get_sample_audio("Artist - Title.mp3")
#    audio = audio_tag.clear_tags(sample_audio)
#    audio_tag.clear(tags)
