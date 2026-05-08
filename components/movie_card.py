import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

from config import COLORS
from services.movie_service import resolve_media_path


class MovieCard(tk.Frame):
    def __init__(
        self,
        master,
        movie,
        on_hover=None,
        on_click=None,
        width=218,
        height=142
    ):
        super().__init__(
            master,
            width=width,
            height=height + 52,
            bg="#101010",
            highlightbackground="#252525",
            highlightthickness=1,
            cursor="hand2"
        )

        self.movie = movie
        self.on_hover = on_hover
        self.on_click = on_click

        self.card_width = width
        self.image_height = height

        self.photo = None

        self.pack_propagate(False)

        self._build_ui()
        self._bind_events_recursive(self)

    def _build_ui(self):
        image = self._load_movie_image()
        self.photo = ImageTk.PhotoImage(image)

        self.image_label = tk.Label(
            self,
            image=self.photo,
            bd=0,
            bg="#101010",
            cursor="hand2"
        )
        self.image_label.pack(fill="x")

        info = tk.Frame(self, bg="#101010", cursor="hand2")
        info.pack(fill="x", padx=10, pady=(7, 0))

        title = self.movie.get("title", "Untitled")

        self.title_label = tk.Label(
            info,
            text=title,
            bg="#101010",
            fg=COLORS["text"],
            font=("Arial", 10, "bold"),
            anchor="w",
            cursor="hand2"
        )
        self.title_label.pack(fill="x")

        rating = self.movie.get("rating", "N/A")
        year = self.movie.get("year", "")
        meta = f"★ {rating}   {year}"

        self.meta_label = tk.Label(
            info,
            text=meta,
            bg="#101010",
            fg=COLORS["muted"],
            font=("Arial", 9),
            anchor="w",
            cursor="hand2"
        )
        self.meta_label.pack(fill="x", pady=(2, 0))

    def _load_movie_image(self):
        path = (
            resolve_media_path(self.movie.get("poster"))
            or resolve_media_path(self.movie.get("backdrop"))
        )

        if path:
            image = Image.open(path).convert("RGB")
        else:
            image = self._placeholder_image()

        return self._cover_image(
            image,
            self.card_width,
            self.image_height
        )

    def _placeholder_image(self):
        image = Image.new(
            "RGB",
            (self.card_width, self.image_height),
            "#202020"
        )

        draw = ImageDraw.Draw(image)
        title = self.movie.get("title", "Mboa Flix")

        draw.rectangle(
            (0, 0, self.card_width, self.image_height),
            fill="#202020"
        )
        draw.rectangle(
            (0, self.image_height - 45, self.card_width, self.image_height),
            fill="#0a0a0a"
        )
        draw.text((12, 12), "MBOA FLIX", fill="#E50914")
        draw.text((12, self.image_height - 32), title[:24], fill="white")

        return image

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

    def _bind_events_recursive(self, widget):
        widget.bind("<Enter>", self._handle_enter)
        widget.bind("<Leave>", self._handle_leave)
        widget.bind("<Button-1>", self._handle_click)

        for child in widget.winfo_children():
            self._bind_events_recursive(child)

    def _handle_enter(self, _event=None):
        self.configure(
            highlightbackground=COLORS["primary"],
            highlightthickness=2
        )

        if callable(self.on_hover):
            self.on_hover(self.movie)

    def _handle_leave(self, _event=None):
        self.configure(
            highlightbackground="#252525",
            highlightthickness=1
        )

    def _handle_click(self, _event=None):
        if callable(self.on_click):
            self.on_click(self.movie)