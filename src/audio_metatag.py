# Copyright (c) 2015-2026 Corey Goldberg
# MIT License

import argparse
import logging
import os
import sys
from pathlib import Path

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC, StreamInfo
from mutagen.mp3 import MP3, EasyMP3
from mutagen.oggvorbis import OggVorbis

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
logger = logging.getLogger(__name__)


FILE_EXTENSIONS = ("mp3", "flac", "ogg")


def is_supported_format(audio):
    if audio is not None and isinstance(audio, (EasyID3, FLAC, MP3, OggVorbis)):
        return True
    return False


def get_artist_and_title(filepath):
    root_filename = filepath.stem
    if " - " not in root_filename:
        raise Exception("invalid filename (no delimiter found)")
    artist, title = root_filename.split(" - ", 1)
    return artist, title


def remove_metadata(audio):
    match audio:
        case FLAC():
            audio.clear()
            # keep only STREAMINFO, remove all other metadata blocks
            audio.metadata_blocks = [block for block in audio.metadata_blocks if isinstance(block, StreamInfo)]
            # some FLACs have invalid ID3 tags included
            audio.save(deleteid3=True)
        case OggVorbis():
            audio.clear()
            audio.save()
        case MP3():
            # remove ID3v2
            audio.clear()
            audio.delete()
            audio.tags = None
            audio.save()
            # remove ID3v1 and APEv2 by truncating the file
            with open(audio.filename, "rb+") as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                # remove ID3v1
                if size >= 128:
                    f.seek(size - 128)
                    if f.read(3) == b"TAG":
                        f.truncate(size - 128)
                        size -= 128
                # remove APEv2
                if size >= 32:
                    f.seek(size - 32)
                    if f.read(8) == b"APETAGEX":
                        # APEv2 header stores tag size at offset 12 (4 bytes little-endian)
                        # (tag header is at end of file)
                        f.seek(size - 32 + 12)
                        tag_size = int.from_bytes(f.read(4), "little")
                        f.truncate(size - tag_size)
    return mutagen.File(audio.filename)


def set_tags(audio, artist, title):
    if isinstance(audio, MP3):
        easy = EasyID3()
        easy.filename = audio.filename
        easy["artist"] = artist
        easy["title"] = title
        easy.save()
    else:
        audio["artist"] = artist
        audio["title"] = title
        audio.save()
    return mutagen.File(audio.filename)


def get_tags(filepath):
    file_label = f"{light_blue_arrowhead()}  File: {filepath}"
    tags = {}
    try:
        audio = mutagen.File(filepath, easy=True)
        if not is_supported_format(audio):
            logger.error(f"{file_label}\n   {red_x()} Error:\n     unsupported media format\n")
            return None
        else:
            if isinstance(audio, EasyMP3):
                id3_tags = {tag: value[0] for tag, value in audio.tags.items()} if audio.tags is not None else {}
                # some MP3's have APEv2 tags also
                ape = mutagen.apev2.APEv2File(filepath)
                ape_tags = {}
                if ape.tags is not None:
                    for tag, value in ape.tags.items():
                        ape_tags[f"ape_{tag.lower()}"] = (
                            "<BINARY>" if isinstance(value, mutagen.apev2.APEBinaryValue) else value
                        )
                tags = id3_tags | ape_tags
            else:
                if audio.tags is None:
                    tags = {}
                else:
                    tags = {tag: value for tag, value in audio.tags}
    except Exception as e:
        logger.error(f"{file_label}\n   {red_x()} Error:\n     {e}\n")
        return None
    return tags


def retag(filepath, clean_only=False):
    file_label = f"{light_blue_arrowhead()}  File: {filepath}"
    try:
        if clean_only:
            artist, title = False, False
        else:
            artist, title = get_artist_and_title(filepath)
        audio = mutagen.File(filepath)
        if not is_supported_format(audio):
            logger.error(f"{file_label}\n   {red_x()} Error:\n     unsupported media format\n")
            return None, None
        cleaned_audio = remove_metadata(audio)
        if not clean_only:
            set_tags(cleaned_audio, artist, title)
    except Exception as e:
        logger.error(f"{file_label}\n   {red_x()} Error:\n     {e}\n")
        return None, None
    return artist, title


def process_file(filepath, clean_only=False, show_only=False):
    file_label = f"{light_blue_arrowhead()}  File: {filepath}"
    if not filepath.exists():
        logger.error(f"{file_label}\n   {red_x()} Error:\n     can't find file\n")
        return False
    if filepath.suffix.lower().lstrip(".") in FILE_EXTENSIONS:
        if show_only:
            tags = get_tags(filepath)
            if tags is None:
                return False
            else:
                logger.info(f"{file_label}\n   {light_blue_arrow()} Tags:")
                for tag, value in tags.items():
                    logger.info(f"     {tag}: {value}")
                logger.info("")
                return True
        else:
            artist, title = retag(filepath, clean_only)
            if clean_only:
                if artist is not None:
                    if not artist:
                        logger.info(f"{file_label}\n   {light_blue_arrow()} Tags:\n     all tags cleaned\n")
                        return True
            else:
                if artist is not None:
                    logger.info(
                        f"{file_label}\n   {light_blue_arrow()} Tags:\n     artist: {artist}\n     title: {title}\n"
                    )
                    return True
    return False


def run(path, filenames, clean_only=False, show_only=False):
    processed_count = total_count = 0
    if filenames:
        for f in filenames:
            total_count += 1
            filepath = Path(path / f).resolve()
            if process_file(filepath, clean_only, show_only):
                processed_count += 1
    else:
        for root, dirs, files in path.walk():
            for f in sorted(files):
                total_count += 1
                filepath = Path(root / f).resolve()
                if process_file(filepath, clean_only, show_only):
                    processed_count += 1
    if show_only:
        action_msg = "Showed tags from"
    elif clean_only:
        action_msg = "Cleaned"
    else:
        action_msg = "Cleaned and tagged"
    label_msg = "file" if processed_count == 1 else "files"
    status_msg = f"{action_msg} {processed_count} audio {label_msg}"
    return status_msg


def colored_symbol(unicode_char, rgb):
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m{unicode_char}\033[0m"


def red_x():
    return colored_symbol("\u2717", (255, 0, 0))


def green_checkmark():
    return colored_symbol("\u2714", (0, 255, 0))


def light_blue_arrow():
    return colored_symbol("\u2794", (144, 213, 255))


def light_blue_arrowhead():
    return colored_symbol("\u27a4", (144, 213, 255))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="*", help="[optional] file to process (multiple allowed)")
    parser.add_argument("-d", "--dir", default=Path.cwd().resolve(), help="start directory")
    parser.add_argument("-c", "--clean", action="store_true", help="only clean metadata (don't write new tags)")
    parser.add_argument("-s", "--show", action="store_true", help="only show metadata (don't remove or write tags)")
    args = parser.parse_args()
    clean_only = args.clean
    show_only = args.show
    if clean_only and show_only:
        sys.exit(f"{red_x()} Error: can't use both --clean and --show")
    path = Path(args.dir)
    filenames = sorted(Path(f) for f in args.filename)
    if not path.exists():
        sys.exit(f"{red_x()} Error: can't find '{path}'")
    try:
        status_msg = run(path, filenames, clean_only, show_only)
        logger.info(f"{green_checkmark()}  {status_msg}")
    except KeyboardInterrupt:
        sys.exit()
