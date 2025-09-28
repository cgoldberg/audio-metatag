#!/usr/bin/env python
#
# Copyright (c) 2015-2025 Corey Goldberg
# MIT License

import argparse
import logging
import sys
from pathlib import Path

import mutagen

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


SUPPORTED_FORMATS = ("FLAC", "MP3", "OGG")
FILE_EXTENSIONS = tuple(f".{x.lower()}" for x in SUPPORTED_FORMATS)


def get_artist_and_title(filepath):
    root_filename = filepath.stem
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
            artist, title = get_artist_and_title(filepath)
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
    if not filepath.exists():
        logger.error(f"File:\n  {filepath}\nError:\n  can't find file\n")
    if filepath.name.lower().endswith(FILE_EXTENSIONS):
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
    processed_count = total_count = 0
    if filenames:
        for f in filenames:
            total_count += 1
            filepath = Path(path / f).resolve()
            if process_file(filepath, clean_only):
                processed_count += 1
    else:
        for root, dirs, files in path.walk():
            for f in sorted(files):
                total_count += 1
                filepath = Path(root / f).resolve()
                if process_file(filepath, clean_only):
                    processed_count += 1
    action_msg = "Cleaned" if clean_only else "Cleaned and tagged"
    label_msg = "file" if processed_count == 1 else "files"
    status_msg = f"{action_msg} {processed_count} audio {label_msg}"
    return status_msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="*", help="file to process (multiple allowed)")
    parser.add_argument("-d", "--dir", default=Path.cwd().resolve(), help="start directory")
    parser.add_argument("-c", "--clean", action="store_true", help="only clean metadata (don't write tags)")
    args = parser.parse_args()
    path = Path(args.dir)
    filenames = sorted(Path(f) for f in args.filename)
    clean_only = args.clean
    if not path.exists():
        sys.exit(f"Error: can't find '{path}'")
    try:
        logger.info("")
        status_msg = run(path, filenames, clean_only)
        logger.info("-" * 40)
        logger.info(status_msg)
    except KeyboardInterrupt:
        sys.exit("\nExiting program ...")
