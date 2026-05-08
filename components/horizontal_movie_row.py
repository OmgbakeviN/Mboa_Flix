import tkinter as tk

from config import COLORS
from components.movie_card import MovieCard


class HorizontalMovieRow(tk.Frame):
    def __init__(
        self,
        master,
        title,
        movies,
        on_movie_hover=None,
        on_movie_click=None
    ):
        super().__init__(master, bg="#070707")

        self.title = title
        self.movies = movies or []
        self.on_movie_hover = on_movie_hover
        self.on_movie_click = on_movie_click

        self._build_ui()

    def _build_ui(self):
        title_label = tk.Label(
            self,
            text=self.title,
            bg="#070707",
            fg=COLORS["text"],
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=4, pady=(0, 12))

        self.canvas = tk.Canvas(
            self,
            bg="#070707",
            highlightthickness=0,
            height=205
        )
        self.canvas.pack(fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg="#070707")

        self.window_id = self.canvas.create_window(
            0,
            0,
            window=self.inner,
            anchor="nw"
        )

        if not self.movies:
            empty_label = tk.Label(
                self.inner,
                text="No movies found.",
                bg="#070707",
                fg=COLORS["muted"],
                font=("Arial", 11)
            )
            empty_label.pack(pady=30)
        else:
            for movie in self.movies:
                card = MovieCard(
                    self.inner,
                    movie=movie,
                    on_hover=self.on_movie_hover,
                    on_click=self.on_movie_click
                )
                card.pack(side="left", padx=(0, 16))

        self.inner.bind("<Configure>", self._update_scroll_region)

        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _update_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bind_mousewheel(self, _event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if getattr(event, "num", None) == 4:
            self.canvas.xview_scroll(-3, "units")
        elif getattr(event, "num", None) == 5:
            self.canvas.xview_scroll(3, "units")
        else:
            self.canvas.xview_scroll(
                int(-1 * (event.delta / 120)) * 3,
                "units"
            )

        return "break"