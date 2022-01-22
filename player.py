"""The event loop that listens for events and plays the corresponding sounds."""
import pygame

try:
    from .startup_helpers import (
        AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED,
        BITS_32BIT,
        DAMPER_PEDAL,
    )
except:
    from startup_helpers import (
        AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED,
        BITS_32BIT,
        DAMPER_PEDAL,
    )


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
        debug,
    ):
        """Start the event loop and play all events."""
        s_pedal_down = False
        d_pedal_down = False
        # audio
        # pygame.mixer.init(
        #     framerate_hz,
        #     BITS_32BIT,
        #     channels,
        #     buffer=8192,
        #     allowedchanges=AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED,
        # )
        # pygame.mixer.set_num_channels(32)
        sound_by_key = dict(zip(keys, key_sounds))
        while True:
            key = queue.get()
            if key is not None:
                # if debug:
                #     print(f"Key: {key['key'].value} {'Down' if key['down'] else 'Up'}")
                # pylint: disable=no-member
                if key["down"] and key["key"].value == "space":
                    s_pedal_down = not s_pedal_down
                    print("Sostenuto Pedal :", s_pedal_down)
                    if not s_pedal_down:
                        for channel in self.playing.values():
                            channel.stop()
                            # channel.wait_done()
                    continue
                if key["down"] and key["key"].value == "right alt":
                    d_pedal_down = not d_pedal_down
                    print("Damper Pedal :", d_pedal_down)
                    continue
                try:
                    sound = sound_by_key[key["key"]]
                except KeyError:
                    continue

                if key["down"]:
                    try:
                        channel = self.playing[key["key"].value]
                        channel.stop()
                        # channel.wait_done()
                    except KeyError:
                        self.playing[key["key"].value] = sound.play()
                        continue
                    except AttributeError:
                        pass
                    self.playing[key["key"].value] = sound.play()

                elif not key["down"] and not s_pedal_down:
                    try:
                        channel = self.playing[key["key"].value]
                        channel.stop()
                        # channel.wait_done()
                        del self.playing[key["key"].value]
                    except KeyError:
                        pass
            # elif len(self.playing) > 0:
            #     if not self.playing.values()[0].is_playing():
            #         self.playing.values()[0].wait_done()
            #         del self.playing.values()[0]
