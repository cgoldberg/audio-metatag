import re
import shutil
from pathlib import Path

import mutagen
import pytest

import audio_tag

FILE_EXTENSIONS = ["mp3", "flac", "ogg"]
VALID_FILE_STEM = "Artist - Title"
ORIGINAL_ARTIST_TAG = "Test Artist"
ORIGINAL_TITLE_TAG = "Test Title"


def copy_files(filename, path):
    samples_filepath = Path("tests", "sample_files", filename).absolute()
    shutil.copyfile(samples_filepath, path / samples_filepath.name)
    audio = mutagen.File(samples_filepath, easy=True)
    assert ORIGINAL_ARTIST_TAG in audio["artist"]
    assert ORIGINAL_TITLE_TAG in audio["title"]


def get_audio(filename, path):
    filepath = path / filename
    audio = mutagen.File(filepath, easy=True)
    return audio


def clear_tags(file_extension, path):
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_files(filename, path)
    tmp_audio = get_audio(filename, path)
    audio = audio_tag.clear_tags(tmp_audio)
    return audio


def set_tags(file_extension, path, artist, title):
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_files(filename, path)
    tmp_audio = get_audio(filename, path)
    cleared_audio = audio_tag.clear_tags(tmp_audio)
    audio = audio_tag.set_tags(cleared_audio, artist, title)
    return audio


def retag(file_extension, path, clean_only=False):
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_files(filename, path)
    filepath = path / filename
    artist, title = audio_tag.retag(filepath, clean_only=clean_only)
    audio = mutagen.File(filepath, easy=True)
    return audio, artist, title


def verify_tags_cleared(audio):
    assert len(audio.tags) == 0
    with pytest.raises(KeyError):
        audio["artist"]
    with pytest.raises(KeyError):
        audio["title"]
    return True


def verify_tags_set(audio, artist, title):
    assert len(audio.tags) == 2
    assert len(audio["artist"]) == 1
    assert len(audio["title"]) == 1
    assert artist in audio["artist"]
    assert title in audio["title"]
    return True


def test_get_artist_and_title_from_filename_with_invalid_name():
    filepath = Path("Invalid Filename.mp3")
    with pytest.raises(Exception, match=re.escape("invalid filename (no delimiter found)")):
        audio_tag.get_artist_and_title(filepath)


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_get_artist_and_title_from_filename(file_extension):
    filepath = Path(f"{VALID_FILE_STEM}.{file_extension}")
    artist, title = audio_tag.get_artist_and_title(filepath)
    assert artist == "Artist"
    assert title == "Title"


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_get_artist_and_title_from_filename_with_path(file_extension):
    filepath = Path(f"/path/to/{VALID_FILE_STEM}.{file_extension}")
    artist, title = audio_tag.get_artist_and_title(filepath)
    assert artist == "Artist"
    assert title == "Title"


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_clear_tags_ogg(file_extension, tmp_path):
    audio = clear_tags(file_extension, tmp_path)
    assert verify_tags_cleared(audio)


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_set_tags(file_extension, tmp_path):
    artist = "Artist"
    title = "Title"
    audio = set_tags(file_extension, tmp_path, artist, title)
    assert verify_tags_set(audio, artist, title)


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_retag_clean(file_extension, tmp_path):
    audio, artist, title = retag(file_extension, tmp_path, clean_only=True)
    assert not artist
    assert not title
    assert verify_tags_cleared(audio)


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_retag(file_extension, tmp_path):
    expected_artist = "Artist"
    expected_title = "Title"
    audio, artist, title = retag(file_extension, tmp_path)
    assert artist == expected_artist
    assert title == expected_title
    assert verify_tags_set(audio, expected_artist, expected_title)
