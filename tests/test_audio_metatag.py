import logging
import re
import shutil
from pathlib import Path

import mutagen
import pytest

import audio_metatag
from audio_metatag import FILE_EXTENSIONS

SAMPLES_PATH = Path("tests", "sample_files").resolve()
VALID_FILE_STEM = "Artist - Title"
LOG_LEVEL = logging.INFO


def copy_file(filename, path):
    Path(path / Path(filename).parent).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SAMPLES_PATH / filename, path / filename)


def verify_tags_set(audio, artist, title):
    assert len(audio.tags) == 2
    assert len(audio["artist"]) == 1
    assert len(audio["title"]) == 1
    assert artist in audio["artist"]
    assert title in audio["title"]
    return True


def test_get_artist_and_title_from_filename_with_invalid_filename():
    filepath = Path("Invalid Filename.mp3")
    with pytest.raises(Exception, match=re.escape("invalid filename (no delimiter found)")):
        audio_metatag.get_artist_and_title(filepath)


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_get_artist_and_title_from_filename(file_extension):
    filepath = Path(f"{VALID_FILE_STEM}.{file_extension}")
    artist, title = audio_metatag.get_artist_and_title(filepath)
    assert artist == "Artist"
    assert title == "Title"


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_get_artist_and_title_from_filename_with_path(file_extension):
    filepath = Path(f"/path/to/{VALID_FILE_STEM}.{file_extension}")
    artist, title = audio_metatag.get_artist_and_title(filepath)
    assert artist == "Artist"
    assert title == "Title"


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_remove_metadata(file_extension, tmp_path):
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    audio = mutagen.File(filepath)
    clean_audio = audio_metatag.remove_metadata(audio)
    assert clean_audio.tags is None or not clean_audio.tags


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_set_tags(file_extension, tmp_path):
    artist = "Artist"
    title = "Title"
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    audio = mutagen.File(filepath)
    audio_metatag.set_tags(audio, artist, title)
    tagged_audio = mutagen.File(filepath, easy=True)
    assert verify_tags_set(tagged_audio, artist, title)


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_get_tags(file_extension, tmp_path):
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    tags = audio_metatag.get_tags(filepath)
    assert len(tags) == 2
    assert tags["artist"] == "Test Artist"
    assert tags["title"] == "Test Title"


def test_get_tags_invalid_file(tmp_path, caplog):
    filename = "Invalid - File.mp3"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    tags = audio_metatag.get_tags(filepath)
    assert tags is None
    assert f"\u27a4  File: {filepath}\n   \u2717 Error:" in caplog.text


def test_get_tags_unsupported_format(tmp_path, caplog):
    filename = "Unsupported - Format.mp3"  # this actually a WAV file
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    tags = audio_metatag.get_tags(filepath)
    assert tags is None
    assert f"\u27a4  File: {filepath}\n   \u2717 Error:\n     unsupported media format\n" in caplog.text


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_retag(file_extension, tmp_path):
    artist = "Artist"
    title = "Title"
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    tagged_artist, tagged_title = audio_metatag.retag(filepath)
    assert tagged_artist == artist
    assert tagged_title == title
    audio = mutagen.File(filepath, easy=True)
    assert verify_tags_set(audio, artist, title)


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_retag_clean(file_extension, tmp_path):
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    artist, title = audio_metatag.retag(filepath, clean_only=True)
    assert not artist
    assert not title
    audio = mutagen.File(filepath, easy=True)
    assert audio.tags is None or not audio.tags


def test_retag_invalid_filename(tmp_path):
    filename = "Invalid Filename.mp3"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    artist, title = audio_metatag.retag(filepath)
    assert artist is None
    assert title is None


def test_retag_invalid_file(tmp_path, caplog):
    filename = "Invalid - File.mp3"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    artist, title = audio_metatag.retag(filepath)
    assert artist is None
    assert title is None
    assert f"\u27a4  File: {filepath}\n   \u2717 Error:" in caplog.text


def test_retag_unsupported_format(tmp_path, caplog):
    filename = "Unsupported - Format.mp3"  # this actually a WAV file
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    artist, title = audio_metatag.retag(filepath)
    assert artist is None
    assert title is None
    assert f"\u27a4  File: {filepath}\n   \u2717 Error:\n     unsupported media format\n" in caplog.text


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_process(file_extension, tmp_path, caplog):
    artist = "Artist"
    title = "Title"
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    caplog.set_level(LOG_LEVEL)
    processed = audio_metatag.process_file(filepath)
    assert processed is True
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert f"\u27a4  File: {filepath}\n   \u2794 Tags:\n     artist: {artist}\n     title: {title}\n" in caplog.text
    audio = mutagen.File(filepath, easy=True)
    assert verify_tags_set(audio, artist, title)


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_process_clean(file_extension, tmp_path, caplog):
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    caplog.set_level(LOG_LEVEL)
    processed = audio_metatag.process_file(filepath, clean_only=True)
    assert processed is True
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert f"\u27a4  File: {filepath}\n   \u2794 Tags:\n     all tags cleaned\n" in caplog.text
    audio = mutagen.File(filepath, easy=True)
    assert audio.tags is None or not audio.tags


@pytest.mark.parametrize("file_extension", FILE_EXTENSIONS)
def test_process_show(file_extension, tmp_path, caplog):
    artist = "Test Artist"
    title = "Test Title"
    filename = f"{VALID_FILE_STEM}.{file_extension}"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    caplog.set_level(LOG_LEVEL)
    processed = audio_metatag.process_file(filepath, show_only=True)
    assert processed is True
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert f"\u27a4  File: {filepath}\n   \u2794 Tags:\n" in caplog.text
    assert f"     artist: {artist}\n" in caplog.text
    assert f"     title: {title}\n" in caplog.text


def test_process_invalid_filename(tmp_path, caplog):
    filename = "Invalid Filename.mp3"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    caplog.set_level(LOG_LEVEL)
    processed = audio_metatag.process_file(filepath)
    assert processed is False
    for record in caplog.records:
        assert record.levelname == "ERROR"
    assert f"\u27a4  File: {filepath}\n   \u2717 Error:\n     invalid filename (no delimiter found)\n" in caplog.text


def test_process_unknown_file(caplog):
    filename = Path("Unknown - File.mp3")
    processed = audio_metatag.process_file(filename)
    assert processed is False
    for record in caplog.records:
        assert record.levelname == "ERROR"
    assert f"\u27a4  File: {filename}\n   \u2717 Error:\n     can't find file\n" in caplog.text


def test_run_filenames(tmp_path, caplog):
    artist = "Artist"
    title = "Title"
    filenames = [f"{VALID_FILE_STEM}.{file_extension}" for file_extension in FILE_EXTENSIONS]
    for filename in filenames:
        copy_file(filename, tmp_path)
    caplog.set_level(LOG_LEVEL)
    status_msg = audio_metatag.run(tmp_path, filenames)
    assert "Cleaned and tagged 3 audio files" in status_msg
    for record in caplog.records:
        assert record.levelname == "INFO"
    for filepath in (tmp_path / filename for filename in filenames):
        assert f"\u27a4  File: {filepath}\n   \u2794 Tags:\n     artist: {artist}\n     title: {title}\n" in caplog.text
        audio = mutagen.File(filepath, easy=True)
        assert verify_tags_set(audio, artist, title)


def test_run_filenames_clean(tmp_path, caplog):
    filenames = [f"{VALID_FILE_STEM}.{file_extension}" for file_extension in FILE_EXTENSIONS]
    for filename in filenames:
        copy_file(filename, tmp_path)
    caplog.set_level(LOG_LEVEL)
    status_msg = audio_metatag.run(tmp_path, filenames, clean_only=True)
    assert "Cleaned 3 audio files" in status_msg
    for record in caplog.records:
        assert record.levelname == "INFO"
    for filepath in (tmp_path / filename for filename in filenames):
        assert f"\u27a4  File: {filepath}\n   \u2794 Tags:\n     all tags cleaned\n" in caplog.text
        audio = mutagen.File(filepath, easy=True)
        assert audio.tags is None or not audio.tags


def test_run_dir(tmp_path, caplog):
    artist = "Artist"
    title = "Title"
    filenames = [path.relative_to(SAMPLES_PATH) for path in SAMPLES_PATH.rglob("*") if path.is_file()]
    num_files = len(filenames)
    for filename in filenames:
        copy_file(filename, tmp_path)
    caplog.set_level(LOG_LEVEL)
    status_msg = audio_metatag.run(tmp_path, [])
    assert "Cleaned and tagged 4 audio files" in status_msg
    for record in caplog.records:
        assert record.levelname in ("ERROR", "INFO")
    temp_files = [tmp_path / filename for filename in filenames]
    assert num_files == len(temp_files)
    for filepath in temp_files:
        matches = (
            f"\u27a4  File: {filepath}\n   \u2794 Tags:\n     artist: {artist}\n     title: {title}\n",
            f"\u27a4  File: {filepath}\n   \u2717 Error:\n",
        )
        assert any([match in caplog.text for match in matches])


def test_run_dir_clean(tmp_path, caplog):
    filenames = [path.relative_to(SAMPLES_PATH) for path in SAMPLES_PATH.rglob("*") if path.is_file()]
    num_files = len(filenames)
    for filename in filenames:
        copy_file(filename, tmp_path)
    caplog.set_level(LOG_LEVEL)
    status_msg = audio_metatag.run(tmp_path, [], clean_only=True)
    assert "Cleaned 5 audio files" in status_msg
    for record in caplog.records:
        assert record.levelname in ("ERROR", "INFO")
    temp_files = [tmp_path / filename for filename in filenames]
    assert num_files == len(temp_files)
    for filepath in temp_files:
        matches = (
            f"\u27a4  File: {filepath}\n   \u2794 Tags:\n     all tags cleaned\n",
            f"\u27a4  File: {filepath}\n   \u2717 Error:\n",
        )
        assert any([match in caplog.text for match in matches])
