import tkinter as tk
from PIL import Image, ImageTk
from config import COLORS, ASSETS_DIR, APP_NAME
from services.sound_service import play_intro_sound


class LoadingPage(tk.Frame):
    def __init__(self, master, on_finish=None):
        super().__init__(master, bg=COLORS["background"])
        self.on_finish = on_finish
        self.running = True
        self.angle = 0

        self.logo_base = self._load_logo()
        self.logo_photo = None

        self.pack(fill="both", expand=True)
        self._build_ui()

        play_intro_sound()
        self._animate_logo()

        self.after(2600, self._finish_loading)

    def _load_logo(self):
        logo_path = ASSETS_DIR / "logo.png"

        if not logo_path.exists():
            return None

        image = Image.open(logo_path).convert("RGBA")
        image.thumbnail((170, 170), Image.LANCZOS)
        return image

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["background"])
        container.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_label = tk.Label(
            container,
            bg=COLORS["background"]
        )
        self.logo_label.pack(pady=(0, 25))

        self.text_label = tk.Label(
            container,
            text="Loading...",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Arial", 16, "bold")
        )
        self.text_label.pack()

        if self.logo_base is None:
            self.logo_label.config(
                text=APP_NAME,
                fg=COLORS["primary"],
                font=("Arial", 32, "bold")
            )

    def _animate_logo(self):
        if not self.running or self.logo_base is None:
            return

        self.angle = (self.angle + 8) % 360

        rotated = self.logo_base.rotate(
            self.angle,
            resample=Image.BICUBIC,
            expand=True
        )

        canvas = Image.new("RGBA", (230, 230), (0, 0, 0, 0))
        rotated.thumbnail((210, 210), Image.LANCZOS)

        x = (230 - rotated.width) // 2
        y = (230 - rotated.height) // 2
        canvas.paste(rotated, (x, y), rotated)

        self.logo_photo = ImageTk.PhotoImage(canvas)
        self.logo_label.config(image=self.logo_photo)

        self.after(50, self._animate_logo)

    def _finish_loading(self):
        self.running = False

        if self.on_finish:
            self.on_finish()

    def destroy(self):
        self.running = False
        super().destroy()