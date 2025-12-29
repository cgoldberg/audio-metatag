# Copyright (c) 2015-2025 Corey Goldberg
# MIT License

import argparse
import logging
import sys
from pathlib import Path

import mutagen
import mutagen.apev2
import mutagen.easyid3

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
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
    if "audio/x-mp3" in audio.mime:
        # some MP3's have APEv2 tags also
        audio.tags = mutagen.apev2.APEv2()
        audio.delete()
        audio.tags = mutagen.easyid3.EasyID3()
    elif "audio/x-flac" in audio.mime:
        audio.clear_pictures()
    audio.delete()
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


def get_tags(filepath):
    file_label = f"{light_blue_arrowhead()}  File: {filepath}"
    tags = {}
    try:
        audio = mutagen.File(filepath, easy=True)
        if audio is None:
            logger.error(f"{file_label}\n   {red_x()} Error:\n     unknown error\n")
            return None
        else:
            if isinstance(audio.tags, mutagen.easyid3.EasyID3):
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
                if audio.tags is not None:
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
        audio = mutagen.File(filepath, easy=True)
        if audio is None:
            logger.error(f"{file_label}\n   {red_x()} Error:\n     unknown error\n")
            return None, None
        cleaned_audio = clear_tags(audio)
        if clean_only:
            save(cleaned_audio)
        else:
            tagged_audio = set_tags(cleaned_audio, artist, title)
            save(tagged_audio)
    except Exception as e:
        logger.error(f"{file_label}\n   {red_x()} Error:\n     {e}\n")
        return None, None
    return artist, title


def process_file(filepath, clean_only=False, show_only=False):
    file_label = f"{light_blue_arrowhead()}  File: {filepath}"
    if not filepath.exists():
        logger.error(f"{file_label}\n   {red_x()} Error:\n     can't find file\n")
        return False
    if filepath.name.lower().endswith(FILE_EXTENSIONS):
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
