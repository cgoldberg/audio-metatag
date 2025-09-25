#!/usr/bin/env python
#
# Copyright (c) 2015-2025 Corey Goldberg
# MIT License


import argparse
import logging
import os
import pathlib
import sys

import mutagen

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


SUPPORTED_FORMATS = ("FLAC", "MP3", "OGG")
# SUPPORTED_FORMATS = ("FLAC", "MP3")
FILE_EXTENSIONS = tuple(f".{x.lower()}" for x in SUPPORTED_FORMATS)


def get_artist_and_title_from_filename(filepath):
    root_filename = pathlib.Path(filepath).stem
    if " - " not in root_filename:
        raise Exception("invalid filename (no delimiter found)")
    artist, title = root_filename.split(" - ", 1)
    return artist, title


def clear_and_set_tags(audio, artist, title):
    audio.delete()
    audio["artist"] = artist
    audio["title"] = title
    if "audio/x-mp3" in audio.mime:
        audio.save(v1=0, v2_version=3)
    elif "audio/x-flac" in audio.mime:
        audio.clear_pictures()
        audio.save(deleteid3=True)
    elif "application/x-ogg" in audio.mime:
        audio.save()
    else:
        raise Exception("unrecognized media type")


def retag(filepath):
    try:
        artist, title = get_artist_and_title_from_filename(filepath)
        audio = mutagen.File(filepath, easy=True)
        if audio is None:
            logger.error(f"File:\n  {filepath}\nError:\n  unknown error\n")
            return None, None
        clear_and_set_tags(audio, artist, title)
    except Exception as e:
        logger.error(f"File:\n  {filepath}\nError:\n  {e}\n")
        return None, None
    return artist, title


def process_file(filepath):
    processed = False
    if filepath.lower().endswith(FILE_EXTENSIONS):
        artist, title = retag(filepath)
        if None not in (artist, title):
            logger.info(
                f"File:\n  {filepath}\nTags:\n  artist: {artist}\n  title: {title}\n"
            )
            processed = True
    return processed


def run(path, filenames):
    print()
    processed_count = total_count = 0
    if filenames:
        for fn in filenames:
            total_count += 1
            filepath = os.path.abspath(os.path.join(path, fn))
            if process_file(filepath):
                processed_count += 1
    else:
        for root, dirs, files in os.walk(path):
            for fn in files:
                total_count += 1
                filepath = os.path.abspath(os.path.join(root, fn))
                if process_file(filepath):
                    processed_count += 1
    f = "files"
    if processed_count == 1:
        f = "file"
    logger.info(f"{'-' * 80}\nProcessed {processed_count} audio {f}")
    return processed_count, total_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename", nargs="*", help="file to process (multiple allowed)"
    )
    parser.add_argument("--dir", default=os.getcwd(), help="start directory")
    args = parser.parse_args()
    filenames = args.filename
    try:
        run(args.dir, filenames)
    except KeyboardInterrupt:
        sys.exit("\nexiting program ...")
