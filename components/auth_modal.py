import tkinter as tk
from PIL import Image, ImageTk, ImageFilter

from config import COLORS, ASSETS_DIR
from components.primary_button import PrimaryButton
from components.text_input import TextInput
from services.auth_service import sign_in, sign_up
from services.movie_service import resolve_media_path


class AuthModal(tk.Frame):
    def __init__(
        self,
        master,
        movie=None,
        initial_mode="sign_in",
        on_success=None,
        on_close=None
    ):
        super().__init__(master, bg="#050505")

        self.movie = movie or {}
        self.mode = initial_mode
        self.on_success = on_success
        self.on_close = on_close

        self.background_photo = None
        self.resize_after_id = None
        self.panel = None

        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.lift()

        self.background_label = tk.Label(self, bd=0)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.bind("<Configure>", self._on_resize)

        self._render_background()
        self._build_panel()

    def _build_panel(self):
        if self.panel:
            self.panel.destroy()

        self.panel = tk.Frame(
            self,
            bg=COLORS["surface"],
            highlightbackground="#444444",
            highlightthickness=1
        )
        self.panel.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=460,
            height=500
        )

        movie_title = self.movie.get("title", "this movie")

        title_text = "Sign In" if self.mode == "sign_in" else "Create Account"
        action_text = "Continue" if self.mode == "sign_in" else "Create Account"

        title = tk.Label(
            self.panel,
            text=title_text,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(34, 8))

        subtitle = tk.Label(
            self.panel,
            text=f"Sign in to watch {movie_title}",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Arial", 11),
            wraplength=360,
            justify="center"
        )
        subtitle.pack(pady=(0, 25))

        form = tk.Frame(self.panel, bg=COLORS["surface"])
        form.pack(fill="x", padx=42)

        self.email_input = TextInput(form, "Email")
        self.email_input.pack(fill="x", pady=(0, 18))

        self.password_input = TextInput(form, "Password", show="*")
        self.password_input.pack(fill="x", pady=(0, 14))

        self.message_label = tk.Label(
            form,
            text="",
            bg=COLORS["surface"],
            fg=COLORS["error"],
            font=("Arial", 10),
            wraplength=360,
            justify="left"
        )
        self.message_label.pack(fill="x", pady=(0, 16))

        PrimaryButton(
            form,
            text=action_text,
            command=self._submit
        ).pack(fill="x", pady=(0, 12))

        switch_text = (
            "New to Mboa Flix? Create an account"
            if self.mode == "sign_in"
            else "Already have an account? Sign in"
        )

        switch_button = tk.Button(
            form,
            text=switch_text,
            command=self._switch_mode,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        switch_button.pack(pady=(0, 12))

        PrimaryButton(
            form,
            text="Back to Home",
            variant="secondary",
            command=self._close
        ).pack(fill="x")

        self.email_input.focus()

        self.panel.lift()

    def _submit(self):
        email = self.email_input.get()
        password = self.password_input.get()

        if self.mode == "sign_in":
            result = sign_in(email, password)
        else:
            result = sign_up(email, password)

        if not result["success"]:
            self.message_label.config(
                text=result["message"],
                fg=COLORS["error"]
            )
            return

        self.message_label.config(
            text=result["message"],
            fg=COLORS["success"]
        )

        if callable(self.on_success):
            self.after(
                400,
                lambda: self.on_success(result["user"])
            )

    def _switch_mode(self):
        self.mode = "sign_up" if self.mode == "sign_in" else "sign_in"
        self._build_panel()

    def _close(self):
        if callable(self.on_close):
            self.on_close()

        self.destroy()

    def _get_background_path(self):
        return (
            resolve_media_path(self.movie.get("banner"))
            or resolve_media_path(self.movie.get("backdrop"))
            or resolve_media_path(self.movie.get("poster"))
            or self._get_default_background()
        )

    def _get_default_background(self):
        path = ASSETS_DIR / "background.png"

        if path.exists():
            return path

        return None

    def _render_background(self):
        width = max(self.winfo_width(), 900)
        height = max(self.winfo_height(), 580)

        path = self._get_background_path()

        if path:
            image = Image.open(path).convert("RGB")
        else:
            image = Image.new("RGB", (width, height), "#050505")

        image = self._cover_image(image, width, height)

        image = image.filter(ImageFilter.GaussianBlur(radius=10))

        dark_overlay = Image.new("RGB", image.size, "#000000")
        image = Image.blend(image, dark_overlay, 0.62)

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

        resized = image.resize(
            (new_width, new_height),
            Image.LANCZOS
        )

        left = (new_width - width) // 2
        top = (new_height - height) // 2

        return resized.crop(
            (left, top, left + width, top + height)
        )

    def _on_resize(self, _event=None):
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)

        self.resize_after_id = self.after(
            120,
            self._render_background
        )