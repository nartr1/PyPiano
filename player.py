"""The event loop that listens for events and plays the corresponding sounds."""
import pygame
from startup_helpers import AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED, BITS_32BIT


class Player:  # pylint:disable=too-few-public-methods
    """Helper class for playing events."""

    def __init__(
        self,
    ):
        """Initialize the playing dict."""
        self.playing = {}

    def start(
        self,
        keys,
        key_sounds,
        framerate_hz,
        channels,
        queue,
        sound_by_key,
        SOUND_FADE_MILLISECONDS,
    ):
        """Start the event loop and play all events."""
        pedal_down = False
        # audio
        pygame.mixer.init(
            framerate_hz,
            BITS_32BIT,
            channels,
            buffer=4096,
            allowedchanges=AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED,
        )

        sound_by_key = dict(zip(keys, key_sounds))
        while True:
            key = queue.get()
            if key is not None:
                # pylint: disable=no-member
                if key["down"] and key["key"].value == "space":
                    pedal_down = not pedal_down
                    print("Pedal :", pedal_down)
                    continue
                try:
                    sound = sound_by_key[key["key"]]
                except KeyError:
                    continue
                if key["down"] and pedal_down:
                    channel = pygame.mixer.find_channel(force=True)
                    channel.play(sound, fade_ms=SOUND_FADE_MILLISECONDS)
                    self.playing[key["key"].value] = channel
                    continue
                if key["down"]:
                    try:
                        channel = self.playing[key["key"].value]
                        channel.stop()
                    except KeyError:
                        channel = pygame.mixer.find_channel(force=True)
                    channel.play(sound, fade_ms=SOUND_FADE_MILLISECONDS)
                    self.playing[key["key"].value] = channel

                elif not key["down"] and not pedal_down:
                    try:
                        channel = self.playing[key["key"].value]
                        channel.fadeout(SOUND_FADE_MILLISECONDS)
                    except KeyError:
                        pass
