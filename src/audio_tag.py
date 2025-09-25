#!/usr/bin/env python
#
# Copyright (c) 2015-2025 Corey Goldberg
# MIT License


import argparse
import logging
import os
import sys
from pathlib import Path

import mutagen

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


SUPPORTED_FORMATS = ("FLAC", "MP3", "OGG")
FILE_EXTENSIONS = tuple(f".{x.lower()}" for x in SUPPORTED_FORMATS)


def get_artist_and_title_from_filename(filepath):
    root_filename = Path(filepath).stem
    if " - " not in root_filename:
        raise Exception("invalid filename (no delimiter found)")
    artist, title = root_filename.split(" - ", 1)
    return artist, title


def clear_tags(audio):
    audio.delete()
    if "audio/x-flac" in audio.mime:
        audio.clear_pictures()
    return audio


def set_tags(audio, artist, title):
    audio["artist"] = artist
    audio["title"] = title
    return audio


def save(audio):
    if "audio/x-mp3" in audio.mime:
        audio.save(v1=0, v2_version=3)
    elif "audio/x-flac" in audio.mime:
        audio.save(deleteid3=True)
    elif "application/x-ogg" in audio.mime:
        audio.save()
    else:
        raise Exception("unrecognized media type")
    return audio


def retag(filepath, clean_only=False):
    try:
        if clean_only:
            artist, title = False, False
        else:
            artist, title = get_artist_and_title_from_filename(filepath)
        audio = mutagen.File(filepath, easy=True)
        if audio is None:
            logger.error(f"File:\n  {filepath}\nError:\n  unknown error\n")
            return None, None
        cleaned_audio = clear_tags(audio)
        if clean_only:
            save(cleaned_audio)
        else:
            tagged_audio = set_tags(cleaned_audio, artist, title)
            save(tagged_audio)
    except Exception as e:
        logger.error(f"File:\n  {filepath}\nError:\n  {e}\n")
        return None, None
    return artist, title


def process_file(filepath, clean_only=False):
    processed = False
    if not Path(filepath).exists():
        logger.error(f"File:\n  {filepath}\nError:\n  can't find file\n")
    if filepath.lower().endswith(FILE_EXTENSIONS):
        artist, title = retag(filepath, clean_only)
        if clean_only:
            if artist is not None:
                if not artist:
                    logger.info(f"File:\n  {filepath}\nTags:\n  no tags saved\n")
                    processed = True
        else:
            if artist is not None:
                logger.info(f"File:\n  {filepath}\nTags:\n  artist: {artist}\n  title: {title}\n")
                processed = True
    return processed


def run(path, filenames, clean_only=False):
    print()
    cleaned_count = total_count = 0
    if filenames:
        for fn in filenames:
            total_count += 1
            filepath = os.path.abspath(Path(path, fn))
            if process_file(filepath, clean_only):
                cleaned_count += 1
    else:
        for root, dirs, files in os.walk(path):
            for fn in files:
                total_count += 1
                filepath = os.path.abspath(Path(root, fn))
                if process_file(filepath, clean_only):
                    cleaned_count += 1
    f = "files"
    if cleaned_count == 1:
        f = "file"
    logger.info(f"{'-' * 40}\nCleaned {cleaned_count} audio {f}")
    return cleaned_count, total_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="*", help="file to process (multiple allowed)")
    parser.add_argument("-d", "--dir", default=Path.cwd(), help="start directory")
    parser.add_argument("-c", "--clean", action="store_true", help="only clean metadata (don't write tags)")
    args = parser.parse_args()
    filenames = args.filename
    path = args.dir
    clean_only = args.clean
    if not Path(path).exists():
        sys.exit(f"Error: can't find '{path}'")
    try:
        run(path, filenames, clean_only)
    except KeyboardInterrupt:
        sys.exit("\nExiting program ...")
