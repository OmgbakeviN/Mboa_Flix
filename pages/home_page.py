import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

from config import COLORS
from components.hero_section import HeroSection
from components.horizontal_movie_row import HorizontalMovieRow
from components.navbar import Navbar
from services.movie_service import (
    get_featured_movie,
    load_catalog,
    resolve_media_path,
    search_catalog
)


class HomePage(tk.Frame):
    def __init__(self, master, user=None, on_logout=None):
        super().__init__(master, bg=COLORS["background"])

        self.user = user or {}
        self.on_logout = on_logout

        self.catalog = load_catalog()
        self.selected_movie = get_featured_movie(self.catalog)

        self.hero_section = None
        self.content_widgets = []
        self.background_photo = None
        self.resize_after_id = None
        self.bg_item = None
        self.content_height = 700

        self.pack(fill="both", expand=True)

        self._build_shell()
        self.after(120, self._initialize_content)

    def _build_shell(self):
        self.content_canvas = tk.Canvas(
            self,
            bg=COLORS["background"],
            highlightthickness=0
        )
        self.content_canvas.place(
            x=0,
            y=82,
            relwidth=1,
            relheight=1,
            height=-82
        )

        self.bg_item = self.content_canvas.create_image(
            0,
            0,
            anchor="nw"
        )

        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.content_canvas.yview,
            bg=COLORS["surface"]
        )
        self.scrollbar.place(
            relx=1.0,
            x=-12,
            y=82,
            width=12,
            relheight=1.0,
            height=-82
        )

        self.content_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.navbar = Navbar(
            self,
            user=self.user,
            on_search=self._handle_search,
            on_logout=self.on_logout
        )
        self.navbar.place(x=0, y=0, relwidth=1, height=82)

        self.bind("<Configure>", self._handle_resize)

        self.content_canvas.bind("<MouseWheel>", self._on_vertical_scroll)
        self.content_canvas.bind("<Button-4>", self._on_vertical_scroll)
        self.content_canvas.bind("<Button-5>", self._on_vertical_scroll)

    def _initialize_content(self):
        self._build_content()
        self._render_background(self.selected_movie)

    def _build_content(self):
        for widget in self.content_widgets:
            widget.destroy()

        self.content_widgets.clear()
        self.content_canvas.delete("content")

        width = max(self.content_canvas.winfo_width(), 900)
        usable_width = max(width - 110, 760)

        x = 50
        y = 35

        if self.selected_movie:
            self.hero_section = HeroSection(
                self.content_canvas,
                movie=self.selected_movie,
                on_watch=self._handle_watch,
                on_details=self._handle_details
            )

            self.content_widgets.append(self.hero_section)

            self.content_canvas.create_window(
                x,
                y,
                window=self.hero_section,
                anchor="nw",
                width=590,
                height=250,
                tags="content"
            )

            y += 280

        top_row = HorizontalMovieRow(
            self.content_canvas,
            title="Top Movies",
            movies=self.catalog.get("top_movies", []),
            on_movie_hover=self._select_movie,
            on_movie_click=self._handle_details
        )

        self.content_widgets.append(top_row)

        self.content_canvas.create_window(
            x,
            y,
            window=top_row,
            anchor="nw",
            width=usable_width,
            height=245,
            tags="content"
        )

        y += 270

        for category in self.catalog.get("categories", []):
            row = HorizontalMovieRow(
                self.content_canvas,
                title=category.get("title", "Movies"),
                movies=category.get("movies", []),
                on_movie_hover=self._select_movie,
                on_movie_click=self._handle_details
            )

            self.content_widgets.append(row)

            self.content_canvas.create_window(
                x,
                y,
                window=row,
                anchor="nw",
                width=usable_width,
                height=245,
                tags="content"
            )

            y += 270

        if not self.catalog.get("top_movies") and not self.catalog.get("categories"):
            empty_label = tk.Label(
                self.content_canvas,
                text="No movies found.",
                bg="#050505",
                fg=COLORS["muted"],
                font=("Arial", 18, "bold")
            )

            self.content_widgets.append(empty_label)

            self.content_canvas.create_window(
                x,
                y,
                window=empty_label,
                anchor="nw",
                width=usable_width,
                height=120,
                tags="content"
            )

            y += 150

        self.content_height = y + 60

        self.content_canvas.configure(
            scrollregion=(0, 0, width, self.content_height)
        )

        self.content_canvas.tag_lower(self.bg_item)

    def _select_movie(self, movie):
        if not movie:
            return

        self.selected_movie = movie

        if self.hero_section:
            self.hero_section.set_movie(movie)

        self._render_background(movie)

    def _handle_search(self, query):
        self.catalog = search_catalog(query)
        self.selected_movie = get_featured_movie(self.catalog)

        self._build_content()
        self._render_background(self.selected_movie)

    def _handle_details(self, movie):
        self._select_movie(movie)
        # Next step: connect MovieDetailsPage here.

    def _handle_watch(self, movie):
        self._select_movie(movie)
        # Later: connect PlayerPage here.

    def _handle_resize(self, _event=None):
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)

        self.resize_after_id = self.after(
            140,
            self._refresh_layout
        )

    def _refresh_layout(self):
        self._build_content()
        self._render_background(self.selected_movie)

    def _on_vertical_scroll(self, event):
        if getattr(event, "num", None) == 4:
            self.content_canvas.yview_scroll(-3, "units")
        elif getattr(event, "num", None) == 5:
            self.content_canvas.yview_scroll(3, "units")
        else:
            self.content_canvas.yview_scroll(
                int(-1 * (event.delta / 120)) * 3,
                "units"
            )

        return "break"

    def _render_background(self, movie):
        width = max(self.content_canvas.winfo_width(), 900)
        height = max(
            self.content_canvas.winfo_height(),
            self.content_height,
            580
        )

        image = self._load_background_image(movie, width, height)
        accent = self._dominant_color(image)

        image = self._add_dark_overlay(image, accent)

        self.background_photo = ImageTk.PhotoImage(image)

        self.content_canvas.itemconfig(
            self.bg_item,
            image=self.background_photo
        )
        self.content_canvas.tag_lower(self.bg_item)

        if hasattr(self, "navbar") and self.navbar:
            self.navbar.set_accent_color(
                self._rgb_to_hex(accent)
            )

    def _load_background_image(self, movie, width, height):
        path = None

        if movie:
            path = (
                resolve_media_path(movie.get("backdrop"))
                or resolve_media_path(movie.get("banner"))
                or resolve_media_path(movie.get("poster"))
            )

        if path:
            image = Image.open(path).convert("RGB")
        else:
            image = self._placeholder_background(movie, width, height)

        return self._cover_image(image, width, height)

    def _placeholder_background(self, movie, width, height):
        title = movie.get("title", "Mboa Flix") if movie else "Mboa Flix"

        image = Image.new("RGB", (width, height), "#111111")
        draw = ImageDraw.Draw(image)

        for y in range(height):
            ratio = y / max(height - 1, 1)
            value = int(35 * (1 - ratio) + 5 * ratio)

            draw.line(
                (0, y, width, y),
                fill=(value, value, value)
            )

        draw.text(
            (width - 360, 120),
            title[:32],
            fill=(90, 90, 90)
        )

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

        resized = image.resize(
            (new_width, new_height),
            Image.LANCZOS
        )

        left = (new_width - width) // 2
        top = (new_height - height) // 2

        return resized.crop(
            (left, top, left + width, top + height)
        )

    def _dominant_color(self, image):
        small = image.resize((1, 1), Image.LANCZOS)
        return small.getpixel((0, 0))

    def _add_dark_overlay(self, image, accent):
        image = image.convert("RGBA")
        width, height = image.size

        black_overlay = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 135)
        )
        image = Image.alpha_composite(image, black_overlay)

        top_gradient = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )
        top_draw = ImageDraw.Draw(top_gradient)
        gradient_height = min(280, height)

        for y in range(gradient_height):
            alpha = int(170 * (1 - y / gradient_height))

            top_draw.line(
                (0, y, width, y),
                fill=(accent[0], accent[1], accent[2], alpha)
            )

        left_gradient = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )
        left_draw = ImageDraw.Draw(left_gradient)
        gradient_width = min(620, width)

        for x in range(gradient_width):
            alpha = int(220 * (1 - x / gradient_width))

            left_draw.line(
                (x, 0, x, height),
                fill=(0, 0, 0, alpha)
            )

        image = Image.alpha_composite(image, top_gradient)
        image = Image.alpha_composite(image, left_gradient)

        return image.convert("RGB")

    def _rgb_to_hex(self, color):
        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"