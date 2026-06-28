import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

from config import COLORS
from components.auth_modal import AuthModal
from components.movie_card import MovieCard
from components.navbar import Navbar
from services.movie_service import (
    get_featured_movie,
    load_catalog,
    resolve_media_path,
    search_catalog
)


class HomePage(tk.Frame):
    def __init__(
        self,
        master,
        user=None,
        selected_movie=None,
        on_logout=None,
        on_auth_success=None,
        on_open_details=None,
        on_watch=None
    ):
        super().__init__(master, bg=COLORS["background"])

        self.user = user
        self.on_logout = on_logout
        self.on_auth_success = on_auth_success
        self.on_open_details = on_open_details
        self.on_watch = on_watch

        self.catalog = load_catalog()
        self.selected_movie = selected_movie or get_featured_movie(self.catalog)

        self.hero_section = None
        self.content_widgets = []
        self.background_photo = None
        self.resize_after_id = None
        self.bg_item = None
        self.content_height = 700

        self.auth_modal = None
        self.pending_movie = None
        self.pending_action = None

        self.rows = []

        self.card_width = 218
        self.card_height = 142
        self.card_total_height = 194
        self.card_gap = 16

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
            on_logout=self.on_logout,
            on_home=getattr(self.master, "show_home_page", None),
            on_food=getattr(self.master, "show_food_page", None),
            on_about=getattr(self.master, "show_about_page", None),
            active_page="home"
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
        self.rows.clear()

        self.content_canvas.delete("content")

        width = max(self.content_canvas.winfo_width(), 900)
        usable_width = max(width - 110, 760)

        x = 50

        # We keep an empty visual space at the top so the movie background image can breathe.
        # No black hero text box anymore.
        y = 330

        y = self._create_movie_row(
            title="Top Movies",
            movies=self.catalog.get("top_movies", []),
            x=x,
            y=y,
            usable_width=usable_width
        )

        for category in self.catalog.get("categories", []):
            y = self._create_movie_row(
                title=category.get("title", "Movies"),
                movies=category.get("movies", []),
                x=x,
                y=y,
                usable_width=usable_width
            )

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

        self.content_height = y + 80

        self.content_canvas.configure(
            scrollregion=(0, 0, width, self.content_height)
        )

        self.content_canvas.tag_lower(self.bg_item)
        self.content_canvas.tag_raise("content")

    def _create_movie_row(self, title, movies, x, y, usable_width):
        self.content_canvas.create_text(
            x,
            y,
            text=title,
            fill=COLORS["text"],
            font=("Arial", 16, "bold"),
            anchor="nw",
            tags="content"
        )

        card_y = y + 42

        row = {
            "x": x,
            "y": card_y,
            "offset": 0,
            "items": [],
            "usable_width": usable_width,
            "total_width": 0
        }

        if not movies:
            empty_label = tk.Label(
                self.content_canvas,
                text="No movies found.",
                bg="#050505",
                fg=COLORS["muted"],
                font=("Arial", 11)
            )

            self.content_widgets.append(empty_label)

            item_id = self.content_canvas.create_window(
                x,
                card_y,
                window=empty_label,
                anchor="nw",
                width=300,
                height=70,
                tags="content"
            )

            row["items"].append(item_id)
            self.rows.append(row)

            return y + 150

        for index, movie in enumerate(movies):
            card = MovieCard(
                self.content_canvas,
                movie=movie,
                on_hover=self._select_movie,
                on_click=self._handle_details,
                width=self.card_width,
                height=self.card_height
            )

            self.content_widgets.append(card)

            card_x = x + index * (self.card_width + self.card_gap)

            item_id = self.content_canvas.create_window(
                card_x,
                card_y,
                window=card,
                anchor="nw",
                width=self.card_width,
                height=self.card_total_height,
                tags="content"
            )

            row["items"].append(item_id)

            self._bind_card_horizontal_scroll(card, row)

        total_width = len(movies) * (self.card_width + self.card_gap)
        row["total_width"] = total_width
        row["max_offset"] = max(0, total_width - usable_width)

        self.rows.append(row)

        return y + 255

    def _bind_card_horizontal_scroll(self, widget, row):
        widget.bind(
            "<MouseWheel>",
            lambda event, selected_row=row: self._on_row_mousewheel(event, selected_row)
        )
        widget.bind(
            "<Button-4>",
            lambda event, selected_row=row: self._on_row_mousewheel(event, selected_row)
        )
        widget.bind(
            "<Button-5>",
            lambda event, selected_row=row: self._on_row_mousewheel(event, selected_row)
        )

        for child in widget.winfo_children():
            self._bind_card_horizontal_scroll(child, row)

    def _on_row_mousewheel(self, event, row):
        if row.get("max_offset", 0) <= 0:
            return "break"

        if getattr(event, "num", None) == 4:
            delta = -90
        elif getattr(event, "num", None) == 5:
            delta = 90
        else:
            delta = int(-1 * (event.delta / 120)) * 90

        row["offset"] = max(
            0,
            min(row["offset"] + delta, row["max_offset"])
        )

        self._update_row_positions(row)

        return "break"

    def _update_row_positions(self, row):
        for index, item_id in enumerate(row["items"]):
            card_x = (
                row["x"]
                + index * (self.card_width + self.card_gap)
                - row["offset"]
            )

            self.content_canvas.coords(
                item_id,
                card_x,
                row["y"]
            )

    def _select_movie(self, movie):
        if not movie:
            return

        self.selected_movie = movie
        self._render_background(movie)

    def _handle_search(self, query):
        self.catalog = search_catalog(query)
        self.selected_movie = get_featured_movie(self.catalog)

        self._build_content()
        self._render_background(self.selected_movie)

    def _handle_details(self, movie):
        self._select_movie(movie)

        if not self._is_authenticated():
            self._open_auth_modal(movie, action="details")
            return

        if callable(self.on_open_details):
            self.on_open_details(movie)

    def _handle_watch(self, movie):
        self._select_movie(movie)

        if not self._is_authenticated():
            self._open_auth_modal(movie, action="watch")
            return

        if callable(self.on_watch):
            self.on_watch(movie)

    def _is_authenticated(self):
        return bool(self.user and self.user.get("email"))

    def _open_auth_modal(self, movie, action="details"):
        self.pending_movie = movie
        self.pending_action = action

        if self.auth_modal:
            self.auth_modal.destroy()

        self.auth_modal = AuthModal(
            self,
            movie=movie,
            initial_mode="sign_in",
            on_success=self._handle_auth_success,
            on_close=self._close_auth_modal
        )

    def _handle_auth_success(self, user):
        if self.auth_modal:
            self.auth_modal.destroy()
            self.auth_modal = None

        if callable(self.on_auth_success):
            self.on_auth_success(
                user,
                self.pending_movie,
                self.pending_action
            )

    def _close_auth_modal(self):
        self.auth_modal = None
        self.pending_movie = None
        self.pending_action = None

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

        self._keep_background_fixed()

        return "break"

    def _keep_background_fixed(self):
        top_y = self.content_canvas.canvasy(0)

        self.content_canvas.coords(
            self.bg_item,
            0,
            top_y
        )

        self.content_canvas.tag_lower(self.bg_item)
        self.content_canvas.tag_raise("content")

    def _render_background(self, movie):
        width = max(self.content_canvas.winfo_width(), 900)
        height = max(self.content_canvas.winfo_height(), 580)

        image = self._load_background_image(movie, width, height)
        accent = self._dominant_color(image)

        image = self._add_dark_overlay(image, accent)

        self.background_photo = ImageTk.PhotoImage(image)

        self.content_canvas.itemconfig(
            self.bg_item,
            image=self.background_photo
        )

        self._keep_background_fixed()

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
            (0, 0, 0, 125)
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
            alpha = int(175 * (1 - y / gradient_height))

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
        gradient_width = min(680, width)

        for x in range(gradient_width):
            alpha = int(230 * (1 - x / gradient_width))

            left_draw.line(
                (x, 0, x, height),
                fill=(0, 0, 0, alpha)
            )

        bottom_gradient = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )
        bottom_draw = ImageDraw.Draw(bottom_gradient)
        gradient_height = min(260, height)

        for y in range(height - gradient_height, height):
            ratio = (y - (height - gradient_height)) / gradient_height
            alpha = int(185 * ratio)

            bottom_draw.line(
                (0, y, width, y),
                fill=(0, 0, 0, alpha)
            )

        image = Image.alpha_composite(image, top_gradient)
        image = Image.alpha_composite(image, left_gradient)
        image = Image.alpha_composite(image, bottom_gradient)

        return image.convert("RGB")

    def _rgb_to_hex(self, color):
        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"