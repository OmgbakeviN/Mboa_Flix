import tkinter as tk
from tkinter import messagebox

from config import APP_NAME, WINDOW_SIZE, COLORS
from pages.loading_page import LoadingPage
from pages.home_page import HomePage
from pages.movie_details_page import MovieDetailsPage
from pages.about_page import AboutPage
from pages.food_page import FoodPage


class MboaFlixApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(900, 580)
        self.configure(bg=COLORS["background"])

        self.current_page = None
        self.current_user = None

        self.pending_movie = None
        self.pending_action = None

        self.show_home_page()

    def clear_page(self):
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None

    def show_home_page(self, selected_movie=None):
        self.clear_page()

        self.current_page = HomePage(
            self,
            user=self.current_user,
            selected_movie=selected_movie,
            on_logout=self.logout,
            on_auth_success=self.handle_auth_success,
            on_open_details=self.show_movie_details_page,
            on_watch=self.show_movie_details_page
        )

    def show_movie_details_page(self, movie):
        self.clear_page()

        self.current_page = MovieDetailsPage(
            self,
            movie=movie,
            user=self.current_user,
            on_back=self.show_home_page,
            on_logout=self.logout,
            on_watch=self.handle_watch_request
        )

    def show_about_page(self):
        self.clear_page()

        self.current_page = AboutPage(
            self,
            user=self.current_user,
            on_home=self.show_home_page,
            on_food=self.show_food_page,
            on_about=self.show_about_page,
            on_logout=self.logout
        )

    def show_food_page(self):
        self.clear_page()

        self.current_page = FoodPage(
            self,
            user=self.current_user,
            on_home=self.show_home_page,
            on_food=self.show_food_page,
            on_about=self.show_about_page,
            on_logout=self.logout
        )

    def handle_auth_success(self, user, movie=None, action=None):
        self.current_user = user
        self.pending_movie = movie
        self.pending_action = action

        self.show_loading_page()

    def show_loading_page(self):
        self.clear_page()

        self.current_page = LoadingPage(
            self,
            on_finish=self.finish_loading
        )

    def finish_loading(self):
        movie = self.pending_movie
        action = self.pending_action

        self.pending_movie = None
        self.pending_action = None

        if movie and action in ["details", "watch"]:
            self.show_movie_details_page(movie)
            return

        self.show_home_page(selected_movie=movie)

    def handle_watch_request(self, movie):
        messagebox.showinfo(
            "Mboa Flix",
            f"Video player is coming next.\n\nMovie: {movie.get('title')}"
        )

    def logout(self):
        self.current_user = None
        self.pending_movie = None
        self.pending_action = None

        self.show_home_page()


if __name__ == "__main__":
    app = MboaFlixApp()
    app.mainloop()