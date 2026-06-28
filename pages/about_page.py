import tkinter as tk
from PIL import Image, ImageTk, ImageFilter

from config import COLORS, ASSETS_DIR, APP_NAME
from components.navbar import Navbar


class AboutPage(tk.Frame):
    def __init__(
        self,
        master,
        user=None,
        on_home=None,
        on_food=None,
        on_about=None,
        on_logout=None
    ):
        super().__init__(master, bg=COLORS["background"])

        self.user = user or {}
        self.on_home = on_home
        self.on_food = on_food
        self.on_about = on_about
        self.on_logout = on_logout

        self.background_photo = None
        self.background_original = self._load_background()

        self.pack(fill="both", expand=True)

        self._build_ui()
        self.bind("<Configure>", self._on_resize)
        self.after(100, self._render_background)

    def _build_ui(self):
        self.background_label = tk.Label(self, bd=0)
        self.background_label.place(x=0, y=82, relwidth=1, relheight=1, height=-82)

        self.navbar = Navbar(
            self,
            user=self.user,
            on_search=None,
            on_logout=self.on_logout,
            on_home=self.on_home,
            on_food=self.on_food,
            on_about=self.on_about,
            active_page="about"
        )
        self.navbar.place(x=0, y=0, relwidth=1, height=82)

        self.content = tk.Frame(
            self,
            bg="#050505",
            highlightbackground="#282828",
            highlightthickness=1
        )
        self.content.place(
            relx=0.5,
            rely=0.54,
            anchor="center",
            width=760,
            height=420
        )

        title = tk.Label(
            self.content,
            text=f"About {APP_NAME}",
            bg="#050505",
            fg=COLORS["text"],
            font=("Arial", 34, "bold")
        )
        title.pack(pady=(45, 20), padx=45, anchor="w")

        paragraph_1 = (
            "Mboa Flix is a desktop streaming experience created to celebrate "
            "Cameroonian culture through stories, movies, series, food and music. "
            "The goal is not only to watch content, but also to discover the beauty, "
            "energy and identity of Cameroon through a modern and interactive interface."
        )

        paragraph_2 = (
            "Through Mboa Flix, users can explore local entertainment, learn about "
            "traditional dishes, discover musical influences and connect with the "
            "creative spirit of our country. It is a cultural application designed "
            "to make Cameroon feel present, visible and proudly represented on screen."
        )

        p1 = tk.Label(
            self.content,
            text=paragraph_1,
            bg="#050505",
            fg=COLORS["text"],
            font=("Arial", 13),
            wraplength=660,
            justify="left"
        )
        p1.pack(padx=45, pady=(0, 22), anchor="w")

        p2 = tk.Label(
            self.content,
            text=paragraph_2,
            bg="#050505",
            fg=COLORS["muted"],
            font=("Arial", 13),
            wraplength=660,
            justify="left"
        )
        p2.pack(padx=45, anchor="w")

    def _load_background(self):
        path = ASSETS_DIR / "background.png"

        if path.exists():
            return Image.open(path).convert("RGB")

        return Image.new("RGB", (1100, 680), "#050505")

    def _render_background(self):
        width = max(self.winfo_width(), 900)
        height = max(self.winfo_height() - 82, 500)

        image = self._cover_image(self.background_original, width, height)
        image = image.filter(ImageFilter.GaussianBlur(radius=4))

        dark = Image.new("RGB", image.size, "#000000")
        image = Image.blend(image, dark, 0.62)

        self.background_photo = ImageTk.PhotoImage(image)
        self.background_label.config(image=self.background_photo)
        self.background_label.lower()

    def _cover_image(self, image, width, height):
        image_ratio = image.width / image.height
        target_ratio = width / height

        if target_ratio > image_ratio:
            new_width = width
            new_height = int(width / image_ratio)
        else:
            new_height = height
            new_width = int(height * image_ratio)

        resized = image.resize((new_width, new_height), Image.LANCZOS)

        left = (new_width - width) // 2
        top = (new_height - height) // 2

        return resized.crop((left, top, left + width, top + height))

    def _on_resize(self, _event=None):
        self.after(120, self._render_background)