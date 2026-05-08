import tkinter as tk
from PIL import Image, ImageTk, ImageFilter

from config import COLORS, ASSETS_DIR, APP_NAME
from components.primary_button import PrimaryButton
from components.text_input import TextInput
from services.auth_service import sign_in, sign_up


class LandingPage(tk.Frame):
    def __init__(self, master, on_auth_success=None):
        super().__init__(master, bg=COLORS["background"])

        self.on_auth_success = on_auth_success
        self.background_original = self._load_background()
        self.background_photo = None
        self.logo_photo = None
        self.modal = None
        self.resize_job = None
        self.is_blurred = False

        self.pack(fill="both", expand=True)

        self.background_label = tk.Label(self, bd=0)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.bind("<Configure>", self._on_resize)

        self._render_background(blur=False)
        self._build_landing_content()

    def _load_background(self):
        background_path = ASSETS_DIR / "background.png"

        if background_path.exists():
            return Image.open(background_path).convert("RGB")

        return Image.new("RGB", (1100, 680), "#050505")

    def _load_logo_photo(self):
        logo_path = ASSETS_DIR / "logo.png"

        if not logo_path.exists():
            return None

        image = Image.open(logo_path).convert("RGBA")
        image.thumbnail((230, 230), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def _cover_image(self, image, width, height):
        image_ratio = image.width / image.height
        screen_ratio = width / height

        if screen_ratio > image_ratio:
            new_width = width
            new_height = int(width / image_ratio)
        else:
            new_height = height
            new_width = int(height * image_ratio)

        resized = image.resize((new_width, new_height), Image.LANCZOS)

        left = (new_width - width) // 2
        top = (new_height - height) // 2

        return resized.crop((left, top, left + width, top + height))

    def _render_background(self, blur=False):
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)

        image = self._cover_image(self.background_original, width, height)

        if blur:
            image = image.filter(ImageFilter.GaussianBlur(radius=8))
            dark_overlay = Image.new("RGB", image.size, "#000000")
            image = Image.blend(image, dark_overlay, 0.62)
        else:
            dark_overlay = Image.new("RGB", image.size, "#000000")
            image = Image.blend(image, dark_overlay, 0.42)

        self.background_photo = ImageTk.PhotoImage(image)
        self.background_label.config(image=self.background_photo)
        self.background_label.lower()

    def _on_resize(self, event):
        if self.resize_job:
            self.after_cancel(self.resize_job)

        self.resize_job = self.after(
            120,
            lambda: self._render_background(blur=self.is_blurred)
        )

    def _build_landing_content(self):
        self.content = tk.Frame(self, bg="#000000")
        self.content.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_photo = self._load_logo_photo()

        if self.logo_photo:
            logo = tk.Label(
                self.content,
                image=self.logo_photo,
                bg="#000000"
            )
        else:
            logo = tk.Label(
                self.content,
                text=APP_NAME,
                bg="#000000",
                fg=COLORS["primary"],
                font=("Arial", 40, "bold")
            )

        logo.pack(pady=(25, 10), padx=45)

        title = tk.Label(
            self.content,
            text="Unlimited local movies, stories and entertainment.",
            bg="#000000",
            fg=COLORS["text"],
            font=("Arial", 16, "bold"),
            wraplength=520,
            justify="center"
        )
        title.pack(pady=(0, 10), padx=45)

        subtitle = tk.Label(
            self.content,
            text="Watch Mboa stories your way.",
            bg="#000000",
            fg=COLORS["muted"],
            font=("Arial", 12)
        )
        subtitle.pack(pady=(0, 25))

        buttons = tk.Frame(self.content, bg="#000000")
        buttons.pack(pady=(0, 30))

        PrimaryButton(
            buttons,
            text="Sign In",
            command=lambda: self._open_auth_modal("sign_in")
        ).pack(side="left", padx=8)

        PrimaryButton(
            buttons,
            text="Sign Up",
            variant="secondary",
            command=lambda: self._open_auth_modal("sign_up")
        ).pack(side="left", padx=8)

    def _open_auth_modal(self, mode):
        self.is_blurred = True
        self._render_background(blur=True)

        self.content.place_forget()

        if self.modal:
            self.modal.destroy()

        self.modal = tk.Frame(
            self,
            bg=COLORS["surface"],
            highlightbackground="#333333",
            highlightthickness=1
        )
        self.modal.place(relx=0.5, rely=0.5, anchor="center", width=440, height=430)

        title_text = "Sign In" if mode == "sign_in" else "Create Account"
        button_text = "Continue" if mode == "sign_in" else "Create Account"

        title = tk.Label(
            self.modal,
            text=title_text,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(35, 25))

        form = tk.Frame(self.modal, bg=COLORS["surface"])
        form.pack(fill="x", padx=40)

        email_input = TextInput(form, "Email")
        email_input.pack(fill="x", pady=(0, 18))

        password_input = TextInput(form, "Password", show="*")
        password_input.pack(fill="x", pady=(0, 15))

        message_label = tk.Label(
            form,
            text="",
            bg=COLORS["surface"],
            fg=COLORS["error"],
            font=("Arial", 10),
            wraplength=350,
            justify="left"
        )
        message_label.pack(fill="x", pady=(0, 15))

        def submit():
            email = email_input.get()
            password = password_input.get()

            if mode == "sign_in":
                result = sign_in(email, password)
            else:
                result = sign_up(email, password)

            if not result["success"]:
                message_label.config(
                    text=result["message"],
                    fg=COLORS["error"]
                )
                return

            message_label.config(
                text=result["message"],
                fg=COLORS["success"]
            )

            if self.on_auth_success:
                self.on_auth_success(result["user"])

        buttons = tk.Frame(form, bg=COLORS["surface"])
        buttons.pack(fill="x")

        PrimaryButton(
            buttons,
            text=button_text,
            command=submit
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        PrimaryButton(
            buttons,
            text="Back",
            variant="secondary",
            command=self._close_auth_modal
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

        email_input.focus()

    def _close_auth_modal(self):
        self.is_blurred = False
        self._render_background(blur=False)

        if self.modal:
            self.modal.destroy()
            self.modal = None

        self.content.place(relx=0.5, rely=0.5, anchor="center")