#!/usr/bin/env python

import argparse
import os
import warnings
from typing import List, Optional, Tuple

import keyboardlayout as kl
import keyboardlayout.pygame as klp
import pygame

try:
    from .player import Player
    from .startup_helpers import (
        get_audio_data,
        get_keyboard_info,
        get_or_create_key_sounds,
        get_parser,
        SOUND_FADE_MILLISECONDS,
        AUDIO_ASSET_PREFIX,
        CURRENT_WORKING_DIR,
        KEYBOARD_ASSET_PREFIX,
        configure_pygame_audio_and_set_ui,
    )
except:
    from player import Player
    from startup_helpers import (
        get_audio_data,
        get_keyboard_info,
        get_or_create_key_sounds,
        get_parser,
        SOUND_FADE_MILLISECONDS,
        AUDIO_ASSET_PREFIX,
        CURRENT_WORKING_DIR,
        KEYBOARD_ASSET_PREFIX,
        configure_pygame_audio_and_set_ui,
    )
# from multiprocessing import Process, Pipe
from threading import Thread
from queue import Queue


def play_until_user_exits(
    framerate_hz,
    channels,
    keys: List[kl.Key],
    key_sounds: List[pygame.mixer.Sound],
    keyboard: klp.KeyboardLayout,
    debug=False,
):
    """Start the player event loops."""
    sound_by_key = dict(zip())
    playing = True
    queue = Queue()

    player_process = Thread(
        target=Player().start,
        args=(
            keys,
            key_sounds,
            framerate_hz,
            channels,
            queue,
            sound_by_key,
            SOUND_FADE_MILLISECONDS,
            debug,
        ),
    )
    player_process.start()
    while playing:
        for event in pygame.event.get():
            # pylint: disable=no-member
            if event.type == pygame.QUIT:
                playing = False
                break
            if hasattr(event, "key") and event.key == pygame.K_ESCAPE:
                playing = False
                break

            key = keyboard.get_key(event)
            if key is None:
                continue
            key = keyboard.get_key(event)
            if key is None:
                continue
            queue.put({"key": key, "down": event.type == pygame.KEYDOWN})

    player_process.join()
    print("Goodbye")


def process_args(parser: argparse.ArgumentParser, args: Optional[List]) -> Tuple:
    """Process the command line arguments."""
    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    # Enable warnings from scipy if requested
    if not args.verbose:
        warnings.simplefilter("ignore")

    wav_path = args.wav
    if wav_path.startswith(AUDIO_ASSET_PREFIX):
        wav_path = os.path.join(CURRENT_WORKING_DIR, wav_path)

    keyboard_path = args.keyboard
    if keyboard_path.startswith(KEYBOARD_ASSET_PREFIX):
        keyboard_path = os.path.join(CURRENT_WORKING_DIR, keyboard_path)
    return wav_path, keyboard_path, args.clear_cache, args.verbose


def play_pianoputer(  # pylint:disable=too-many-locals
    args: Optional[List[str]] = None,
):
    """Initialize the keyboard, sounds, and event loops."""
    parser = get_parser()
    wav_path, keyboard_path, clear_cache, debug = process_args(parser, args)
    _, framerate_hz, channels = get_audio_data(wav_path)
    results = get_keyboard_info(keyboard_path)
    keys, tones, color_to_key, key_color, key_txt_color = results
    key_sounds = get_or_create_key_sounds(
        wav_path, framerate_hz, channels, tones, clear_cache, keys
    )

    _, keyboard = configure_pygame_audio_and_set_ui(
        keyboard_path, color_to_key, key_color, key_txt_color
    )
    print(
        "Ready for you to play!\n"
        "Press the keys on your keyboard. "
        "To exit presss ESC or close the pygame window"
    )
    play_until_user_exits(framerate_hz, channels, keys, key_sounds, keyboard, debug)


if __name__ == "__main__":
    play_pianoputer()
