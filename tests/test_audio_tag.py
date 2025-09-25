import os
import re

import mutagen
import pytest

import audio_tag


SAMPLES_DIR = os.path.join("tests", "sample_files")


#@pytest.fixture
#def clean_metadata():
#    for entry in os.scandir(SAMPLES_DIR):
#        if entry.is_file():
#            cleared_audio = audio_tag.clear_tags()
#            tagged
#            print()
#            print(entry.name)


def get_sample_audio(filename):
    filepath = os.path.abspath(os.path.join(SAMPLES_DIR, filename))
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


#def test_clear_tags_mp3(clean_metadata):
#    audio = audio_tag.clear_tags(audio_tag.get_sample_audio("Artist - Title.mp3"))


