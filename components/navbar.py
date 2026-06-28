import tkinter as tk
from PIL import Image, ImageTk

from config import APP_NAME, ASSETS_DIR, COLORS


class Navbar(tk.Frame):
    def __init__(
        self,
        master,
        user=None,
        on_search=None,
        on_logout=None,
        on_home=None,
        on_food=None,
        on_about=None,
        active_page="home"
    ):
        super().__init__(master, height=82, bg="#050505")

        self.user = user or {}
        self.on_search = on_search
        self.on_logout = on_logout
        self.on_home = on_home
        self.on_food = on_food
        self.on_about = on_about
        self.active_page = active_page

        self.accent_color = "#141414"
        self.gradient_photo = None
        self.logo_photo = None
        self.search_after_id = None

        self.pack_propagate(False)
        self._build_ui()

        self.bind("<Configure>", lambda event: self._render_gradient())
        self.after(100, self._render_gradient)

    def _build_ui(self):
        self.gradient_label = tk.Label(self, bd=0)
        self.gradient_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.gradient_label.lower()

        self.logo_photo = self._load_logo_photo()

        if self.logo_photo:
            self.logo_label = tk.Label(
                self,
                image=self.logo_photo,
                bg="#050505"
            )
        else:
            self.logo_label = tk.Label(
                self,
                text=APP_NAME,
                bg="#050505",
                fg=COLORS["primary"],
                font=("Arial", 15, "bold")
            )

        self.logo_label.place(x=28, y=18)

        self.links_frame = tk.Frame(self, bg="#050505")
        self.links_frame.place(x=175, y=29)

        links = [
            ("Home", "home", self.on_home),
            ("Movies", "movies", self.on_home),
            ("Series", "series", self.on_home),
            ("Food", "food", self.on_food),
            ("About", "about", self.on_about),
        ]

        for text, key, command in links:
            label = tk.Label(
                self.links_frame,
                text=text,
                bg="#050505",
                fg=COLORS["text"] if self.active_page == key else COLORS["muted"],
                font=("Arial", 10, "bold"),
                cursor="hand2"
            )
            label.pack(side="left", padx=(0, 24))

            if callable(command):
                label.bind("<Button-1>", lambda event, callback=command: callback())

        self.search_var = tk.StringVar()

        self.search_entry = tk.Entry(
            self,
            textvariable=self.search_var,
            bg="#1d1d1d",
            fg="#777777",
            insertbackground=COLORS["text"],
            relief="flat",
            font=("Arial", 11)
        )
        self.search_entry.place(
            relx=0.62,
            y=23,
            anchor="n",
            width=300,
            height=36
        )

        if callable(self.on_search):
            self.search_entry.insert(0, "Search")
            self.search_entry.bind("<FocusIn>", self._clear_placeholder)
            self.search_entry.bind("<FocusOut>", self._restore_placeholder)
            self.search_var.trace_add("write", self._schedule_search)
        else:
            self.search_entry.insert(0, "Search available on Home")
            self.search_entry.config(state="disabled", disabledforeground="#777777")

        display_name = self._get_display_name()

        self.user_label = tk.Label(
            self,
            text=display_name,
            bg="#050505",
            fg=COLORS["muted"],
            font=("Arial", 10, "bold")
        )
        self.user_label.place(relx=1.0, x=-240, y=30, anchor="nw")

        if self.user and self.user.get("email"):
            self.logout_button = tk.Button(
                self,
                text="Logout",
                command=self._handle_logout,
                bg=COLORS["primary"],
                fg=COLORS["text"],
                activebackground=COLORS["primary_hover"],
                activeforeground=COLORS["text"],
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Arial", 10, "bold")
            )
            self.logout_button.place(
                relx=1.0,
                x=-112,
                y=22,
                width=84,
                height=36
            )

    def _get_display_name(self):
        email = self.user.get("email") if self.user else None

        if not email:
            return "Guest"

        return email.split("@")[0]

    def _load_logo_photo(self):
        logo_path = ASSETS_DIR / "logo.png"

        if not logo_path.exists():
            return None

        image = Image.open(logo_path).convert("RGBA")
        image.thumbnail((120, 46), Image.LANCZOS)

        return ImageTk.PhotoImage(image)

    def _clear_placeholder(self, _event=None):
        if self.search_entry.get() == "Search":
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg=COLORS["text"])

    def _restore_placeholder(self, _event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search")
            self.search_entry.config(fg="#777777")

    def _schedule_search(self, *_args):
        value = self.search_var.get()

        if value == "Search":
            return

        if self.search_after_id:
            self.after_cancel(self.search_after_id)

        self.search_after_id = self.after(
            250,
            lambda: self._emit_search(value)
        )

    def _emit_search(self, value):
        if callable(self.on_search):
            self.on_search(value)

    def _handle_logout(self):
        if callable(self.on_logout):
            self.on_logout()

    def set_accent_color(self, color):
        self.accent_color = color or "#141414"
        self._render_gradient()

        bg = self._blend_with_black(self.accent_color, 0.72)

        self.configure(bg=bg)
        self.logo_label.configure(bg=bg)
        self.links_frame.configure(bg=bg)
        self.user_label.configure(bg=bg)

        for child in self.links_frame.winfo_children():
            child.configure(bg=bg)

    def _render_gradient(self):
        width = max(self.winfo_width(), 900)
        height = max(self.winfo_height(), 82)

        start = self._hex_to_rgb(self.accent_color)
        end = (5, 5, 5)

        image = Image.new("RGB", (width, height), end)
        pixels = image.load()

        for x in range(width):
            ratio = x / max(width - 1, 1)

            r = int(start[0] * (1 - ratio) + end[0] * ratio)
            g = int(start[1] * (1 - ratio) + end[1] * ratio)
            b = int(start[2] * (1 - ratio) + end[2] * ratio)

            for y in range(height):
                pixels[x, y] = (r, g, b)

        self.gradient_photo = ImageTk.PhotoImage(image)
        self.gradient_label.config(image=self.gradient_photo)
        self.gradient_label.lower()

    def _hex_to_rgb(self, value):
        value = value.lstrip("#")
        return tuple(
            int(value[index:index + 2], 16)
            for index in (0, 2, 4)
        )

    def _blend_with_black(self, color, amount):
        r, g, b = self._hex_to_rgb(color)

        r = int(r * (1 - amount))
        g = int(g * (1 - amount))
        b = int(b * (1 - amount))

        return f"#{r:02x}{g:02x}{b:02x}"