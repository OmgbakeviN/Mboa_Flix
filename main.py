import tkinter as tk

from config import APP_NAME, WINDOW_SIZE, COLORS
from pages.landing_page import LandingPage
from pages.loading_page import LoadingPage
from pages.home_page import HomePage


class MboaFlixApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(900, 580)
        self.configure(bg=COLORS["background"])

        self.current_page = None
        self.current_user = None

        self.show_landing_page()

    def clear_page(self):
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None

    def show_landing_page(self):
        self.clear_page()
        self.current_page = LandingPage(
            self,
            on_auth_success=self.handle_auth_success
        )

    def handle_auth_success(self, user):
        self.current_user = user
        self.show_loading_page()

    def show_loading_page(self):
        self.clear_page()
        self.current_page = LoadingPage(
            self,
            on_finish=self.show_home_page
        )

    def show_home_page(self):
        self.clear_page()
        self.current_page = HomePage(
            self,
            user=self.current_user,
            on_logout=self.logout
        )

    def logout(self):
        self.current_user = None
        self.show_landing_page()


if __name__ == "__main__":
    app = MboaFlixApp()
    app.mainloop()