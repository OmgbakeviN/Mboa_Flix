import platform
import subprocess
from config import ASSETS_DIR


def play_intro_sound():
    sound_file = ASSETS_DIR / "intro.wav"

    if not sound_file.exists():
        return

    try:
        system = platform.system()

        if system == "Windows":
            import winsound
            winsound.PlaySound(
                str(sound_file),
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )

        elif system == "Darwin":
            subprocess.Popen(
                ["afplay", str(sound_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        else:
            subprocess.Popen(
                ["aplay", str(sound_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

    except Exception:
        pass