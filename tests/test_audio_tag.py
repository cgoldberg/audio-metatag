import re
import shutil
from pathlib import Path

import mutagen
import pytest

import audio_tag

SAMPLES_DIR = Path("tests", "sample_files").absolute()


def copy_files(filenames, path):
    for f in filenames:
        samples_path = SAMPLES_DIR / f
        if samples_path.is_file():
            shutil.copyfile(samples_path, path / samples_path.name)


def get_audio(filename, path):
    filepath = path / filename
    audio = mutagen.File(filepath, easy=True)
    return audio


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
    assert "foo" in audio["artist"]
    assert "bar" in audio["title"]
    return True


def test_get_artist_and_title_from_filename():
    filepath = Path("Artist - Title.mp3")
    artist, title = audio_tag.get_artist_and_title(filepath)
    assert artist == "Artist"
    assert title == "Title"


def test_get_artist_and_title_from_filename_with_path():
    filepath = Path("/path/to/Artist - Title.flac")
    artist, title = audio_tag.get_artist_and_title(filepath)
    assert artist == "Artist"
    assert title == "Title"


def test_get_artist_and_title_from_filename_with_invalid_name():
    filepath = Path("Invalid Filename.flac")
    with pytest.raises(Exception, match=re.escape("invalid filename (no delimiter found)")):
        audio_tag.get_artist_and_title(filepath)


def test_clear_tags_mp3(tmp_path):
    filename = "Artist - Title.mp3"
    copy_files([filename], tmp_path)
    tmp_audio = get_audio(filename, tmp_path)
    audio = audio_tag.clear_tags(tmp_audio)
    assert verify_tags_cleared(audio)


def test_clear_tags_flac(tmp_path):
    filename = "Artist - Title.flac"
    copy_files([filename], tmp_path)
    tmp_audio = get_audio(filename, tmp_path)
    audio = audio_tag.clear_tags(tmp_audio)
    assert verify_tags_cleared(audio)


def test_clear_tags_ogg(tmp_path):
    filename = "Artist - Title.ogg"
    copy_files([filename], tmp_path)
    tmp_audio = get_audio(filename, tmp_path)
    audio = audio_tag.clear_tags(tmp_audio)
    assert verify_tags_cleared(audio)


def test_set_tags_mp3(tmp_path):
    filename = "Artist - Title.mp3"
    copy_files([filename], tmp_path)
    tmp_audio = get_audio(filename, tmp_path)
    cleared_audio = audio_tag.clear_tags(tmp_audio)
    audio = audio_tag.set_tags(cleared_audio, "foo", "bar")
    assert verify_tags_set(audio, "foo", "bar")


def test_set_tags_flac(tmp_path):
    filename = "Artist - Title.flac"
    copy_files([filename], tmp_path)
    tmp_audio = get_audio(filename, tmp_path)
    cleared_audio = audio_tag.clear_tags(tmp_audio)
    audio = audio_tag.set_tags(cleared_audio, "foo", "bar")
    assert verify_tags_set(audio, "foo", "bar")


def test_set_tags_ogg(tmp_path):
    filename = "Artist - Title.ogg"
    copy_files([filename], tmp_path)
    tmp_audio = get_audio(filename, tmp_path)
    cleared_audio = audio_tag.clear_tags(tmp_audio)
    audio = audio_tag.set_tags(cleared_audio, "foo", "bar")
    assert verify_tags_set(audio, "foo", "bar")
