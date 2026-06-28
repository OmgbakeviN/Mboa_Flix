import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFilter

from config import COLORS
from components.navbar import Navbar
from components.primary_button import PrimaryButton
from services.movie_service import resolve_media_path


class MovieDetailsPage(tk.Frame):
    def __init__(
        self,
        master,
        movie,
        user=None,
        on_back=None,
        on_logout=None,
        on_watch=None
    ):
        super().__init__(master, bg=COLORS["background"])

        self.movie = movie or {}
        self.user = user or {}
        self.on_back = on_back
        self.on_logout = on_logout
        self.on_watch = on_watch

        self.page_bg_photo = None
        self.panel_bg_photo = None
        self.poster_photo = None

        self.resize_after_id = None

        self.panel_x = 58
        self.panel_y = 40
        self.panel_width = 1180
        self.panel_height = 520

        self.pack(fill="both", expand=True)

        self._build_shell()
        self.after(120, self._render_all)

    def _build_shell(self):
        self.page_canvas = tk.Canvas(
            self,
            bg=COLORS["background"],
            highlightthickness=0,
            bd=0
        )
        self.page_canvas.place(
            x=0,
            y=82,
            relwidth=1,
            relheight=1,
            height=-82
        )

        self.page_bg_item = self.page_canvas.create_image(
            0,
            0,
            anchor="nw"
        )

        self.navbar = Navbar(
            self,
            user=self.user,
            on_search=None,
            on_logout=self.on_logout,
            on_home=getattr(self.master, "show_home_page", None),
            on_food=getattr(self.master, "show_food_page", None),
            on_about=getattr(self.master, "show_about_page", None),
            active_page="movies"
        )
        self.navbar.place(x=0, y=0, relwidth=1, height=82)

        self.panel_frame = tk.Frame(
            self.page_canvas,
            bg="#000000",
            highlightbackground="#2f2f2f",
            highlightthickness=1,
            bd=0
        )

        self.panel_canvas = tk.Canvas(
            self.panel_frame,
            bg="#000000",
            highlightthickness=0,
            bd=0
        )
        self.panel_canvas.pack(fill="both", expand=True)

        self.panel_window = self.page_canvas.create_window(
            self.panel_x,
            self.panel_y,
            window=self.panel_frame,
            anchor="nw",
            width=self.panel_width,
            height=self.panel_height
        )

        self.panel_frame.config(
            width=self.panel_width,
            height=self.panel_height
        )

        self.panel_canvas.config(
            width=self.panel_width,
            height=self.panel_height
        )

        self.bind("<Configure>", self._on_resize)

    def _render_all(self):
        self.update_idletasks()
        self._update_panel_size()
        self._render_page_background()
        self._render_panel()

    def _update_panel_size(self):
        page_width = max(self.page_canvas.winfo_width(), 900)
        page_height = max(self.page_canvas.winfo_height(), 580)

        self.panel_width = max(page_width - 120, 760)
        self.panel_height = min(max(page_height - 80, 520), 620)

        self.page_canvas.itemconfig(
            self.panel_window,
            width=self.panel_width,
            height=self.panel_height
        )

        self.panel_frame.config(
            width=self.panel_width,
            height=self.panel_height
        )

        self.panel_canvas.config(
            width=self.panel_width,
            height=self.panel_height
        )

    def _render_page_background(self):
        width = max(self.page_canvas.winfo_width(), 900)
        height = max(self.page_canvas.winfo_height(), 580)

        image = self._load_page_background_image(width, height)
        accent = self._dominant_color(image)

        image = self._add_page_overlay(image, accent)

        self.page_bg_photo = ImageTk.PhotoImage(image)

        self.page_canvas.itemconfig(
            self.page_bg_item,
            image=self.page_bg_photo
        )
        self.page_canvas.tag_lower(self.page_bg_item)

        self.navbar.set_accent_color(self._rgb_to_hex(accent))

    def _render_panel(self):
        panel_width = self.panel_width
        panel_height = self.panel_height

        bg_image = self._load_panel_background_image(
            panel_width,
            panel_height
        )
        bg_image = self._add_panel_overlay(bg_image)

        self.panel_bg_photo = ImageTk.PhotoImage(bg_image)

        self.panel_canvas.delete("all")

        for child in self.panel_canvas.winfo_children():
            child.destroy()

        self.panel_canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.panel_bg_photo
        )

        self._draw_panel_content(panel_width, panel_height)

    def _draw_panel_content(self, panel_width, panel_height):
        back_button = tk.Button(
            self.panel_canvas,
            text="← Back",
            command=self._back,
            bg="#151515",
            fg=COLORS["text"],
            activebackground="#232323",
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 11, "bold"),
            padx=18,
            pady=8
        )

        self.panel_canvas.create_window(
            24,
            22,
            window=back_button,
            anchor="nw"
        )

        poster_image = self._load_poster()
        self.poster_photo = ImageTk.PhotoImage(poster_image)

        poster_label = tk.Label(
            self.panel_canvas,
            image=self.poster_photo,
            bd=0,
            bg="#111111"
        )

        self.panel_canvas.create_window(
            28,
            76,
            window=poster_label,
            anchor="nw",
            width=300,
            height=430
        )

        info_x = 370
        info_y = 92
        content_width = max(panel_width - info_x - 48, 320)

        category_text = self.movie.get("category", "Mboa Flix").upper()

        self.panel_canvas.create_text(
            info_x,
            info_y,
            text=category_text,
            fill=COLORS["primary"],
            font=("Arial", 11, "bold"),
            anchor="nw"
        )

        title_item = self.panel_canvas.create_text(
            info_x,
            info_y + 34,
            text=self.movie.get("title", "Untitled"),
            fill=COLORS["text"],
            font=("Arial", 36, "bold"),
            anchor="nw",
            width=content_width
        )

        title_bbox = self.panel_canvas.bbox(title_item)
        title_bottom = title_bbox[3] if title_bbox else info_y + 92

        rating = self.movie.get("rating", "N/A")
        match = self.movie.get("match", "")
        year = self.movie.get("year", "")
        duration = self.movie.get("duration", "")
        movie_type = self.movie.get("type", "")

        meta_text = f"★ {rating}    {match} Match    {year}    {duration}    {movie_type}"

        meta_item = self.panel_canvas.create_text(
            info_x,
            title_bottom + 18,
            text=meta_text,
            fill=COLORS["muted"],
            font=("Arial", 12, "bold"),
            anchor="nw",
            width=content_width
        )

        meta_bbox = self.panel_canvas.bbox(meta_item)
        meta_bottom = meta_bbox[3] if meta_bbox else title_bottom + 42

        description_item = self.panel_canvas.create_text(
            info_x,
            meta_bottom + 26,
            text=self.movie.get("description", ""),
            fill=COLORS["text"],
            font=("Arial", 12),
            anchor="nw",
            width=content_width
        )

        description_bbox = self.panel_canvas.bbox(description_item)
        description_bottom = description_bbox[3] if description_bbox else meta_bottom + 82

        tags_frame = self._build_tags_frame()

        if self.movie.get("tags", []):
            self.panel_canvas.create_window(
                info_x,
                description_bottom + 24,
                window=tags_frame,
                anchor="nw"
            )
            next_y = description_bottom + 84
        else:
            next_y = description_bottom + 24

        video_text = self._get_video_source_text()

        source_item = self.panel_canvas.create_text(
            info_x,
            next_y,
            text=video_text,
            fill=COLORS["muted"],
            font=("Arial", 10),
            anchor="nw",
            width=content_width
        )

        source_bbox = self.panel_canvas.bbox(source_item)
        source_bottom = source_bbox[3] if source_bbox else next_y + 24

        buttons_frame = self._build_buttons_frame()

        self.panel_canvas.create_window(
            info_x,
            source_bottom + 28,
            window=buttons_frame,
            anchor="nw"
        )

    def _build_tags_frame(self):
        frame = tk.Frame(
            self.panel_canvas,
            bg="#111111"
        )

        tags = self.movie.get("tags", [])

        for tag in tags:
            label = tk.Label(
                frame,
                text=tag,
                bg="#1b1b1b",
                fg=COLORS["text"],
                font=("Arial", 10, "bold"),
                padx=12,
                pady=6
            )
            label.pack(side="left", padx=(0, 8))

        return frame

    def _build_buttons_frame(self):
        frame = tk.Frame(
            self.panel_canvas,
            bg="#111111"
        )

        PrimaryButton(
            frame,
            text="▶ Watch Now",
            command=self._watch
        ).pack(side="left", padx=(0, 12))

        PrimaryButton(
            frame,
            text="+ My List",
            variant="secondary",
            command=lambda: None
        ).pack(side="left", padx=(0, 12))

        PrimaryButton(
            frame,
            text="Trailer",
            variant="secondary",
            command=lambda: None
        ).pack(side="left")

        return frame

    def _get_video_source_text(self):
        video = self.movie.get("video", {})
        local_path = video.get("local_path", "")
        youtube_url = video.get("youtube_url", "")

        if youtube_url:
            return "Video source: YouTube link configured"

        if local_path:
            return f"Video source: {local_path}"

        return "Video source: Not configured yet"

    def _get_primary_media_path(self):
        return (
            resolve_media_path(self.movie.get("banner"))
            or resolve_media_path(self.movie.get("backdrop"))
            or resolve_media_path(self.movie.get("poster"))
        )

    def _load_page_background_image(self, width, height):
        path = self._get_primary_media_path()

        if path:
            image = Image.open(path).convert("RGB")
        else:
            image = self._placeholder_background(width, height)

        return self._cover_image(image, width, height)

    def _load_panel_background_image(self, width, height):
        path = self._get_primary_media_path()

        if path:
            image = Image.open(path).convert("RGB")
        else:
            image = self._placeholder_background(width, height)

        image = self._cover_image(image, width, height)
        image = image.filter(ImageFilter.GaussianBlur(radius=18))

        return image

    def _load_poster(self):
        path = (
            resolve_media_path(self.movie.get("poster"))
            or resolve_media_path(self.movie.get("banner"))
            or resolve_media_path(self.movie.get("backdrop"))
        )

        if path:
            image = Image.open(path).convert("RGB")
        else:
            image = self._placeholder_poster()

        return self._cover_image(image, 300, 430)

    def _placeholder_poster(self):
        image = Image.new("RGB", (300, 430), "#202020")
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, 300, 430), fill="#202020")
        draw.rectangle((0, 320, 300, 430), fill="#080808")

        draw.text((24, 28), "MBOA FLIX", fill="#E50914")
        draw.text(
            (24, 342),
            self.movie.get("title", "Movie")[:24],
            fill="white"
        )

        return image

    def _placeholder_background(self, width, height):
        image = Image.new("RGB", (width, height), "#111111")
        draw = ImageDraw.Draw(image)

        for y in range(height):
            ratio = y / max(height - 1, 1)
            value = int(40 * (1 - ratio) + 5 * ratio)
            draw.line((0, y, width, y), fill=(value, value, value))

        draw.text(
            (width - 360, 120),
            self.movie.get("title", "Mboa Flix")[:32],
            fill=(80, 80, 80)
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

    def _add_page_overlay(self, image, accent):
        image = image.convert("RGBA")
        width, height = image.size

        black_overlay = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 145)
        )
        image = Image.alpha_composite(image, black_overlay)

        left_gradient = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )
        left_draw = ImageDraw.Draw(left_gradient)

        for x in range(width):
            ratio = x / max(width - 1, 1)
            alpha = int(235 * (1 - ratio))
            left_draw.line(
                (x, 0, x, height),
                fill=(0, 0, 0, alpha)
            )

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

        image = Image.alpha_composite(image, left_gradient)
        image = Image.alpha_composite(image, top_gradient)

        return image.convert("RGB")

    def _add_panel_overlay(self, image):
        image = image.convert("RGBA")
        width, height = image.size

        dark_overlay = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 120)
        )
        image = Image.alpha_composite(image, dark_overlay)

        left_readability = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )
        left_draw = ImageDraw.Draw(left_readability)

        for x in range(width):
            ratio = x / max(width - 1, 1)
            alpha = int(175 * (1 - ratio * 0.85))
            left_draw.line(
                (x, 0, x, height),
                fill=(0, 0, 0, alpha)
            )

        bottom_shadow = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )
        bottom_draw = ImageDraw.Draw(bottom_shadow)

        shadow_height = min(180, height)

        for y in range(height - shadow_height, height):
            ratio = (y - (height - shadow_height)) / shadow_height
            alpha = int(110 * ratio)
            bottom_draw.line(
                (0, y, width, y),
                fill=(0, 0, 0, alpha)
            )

        soft_light = Image.new(
            "RGBA",
            image.size,
            (255, 255, 255, 12)
        )

        image = Image.alpha_composite(image, left_readability)
        image = Image.alpha_composite(image, bottom_shadow)
        image = Image.alpha_composite(image, soft_light)

        return image.convert("RGB")

    def _on_resize(self, _event=None):
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)

        self.resize_after_id = self.after(
            140,
            self._refresh_layout
        )

    def _refresh_layout(self):
        self._render_all()

    def _rgb_to_hex(self, color):
        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    def _back(self):
        if callable(self.on_back):
            self.on_back(self.movie)

    def _watch(self):
        if callable(self.on_watch):
            self.on_watch(self.movie)
        else:
            print(f"Watch requested for: {self.movie.get('title')}")