# main.py

import tkinter as tk
from backend.initialize import Backend
from backend.utils.logger import logger

from frontend.views.login_view import LoginView
from frontend.views.home_search_view import HomeSearchView
from frontend.splash_screen import SplashScreen


# Initialize backend
try:
    backend_system = Backend()
    logger.info("Backend initialized successfully.")
except Exception:
    logger.exception("Backend initialization failed.")
    raise SystemExit("Cannot start app without backend.")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Book Shop Management")
        self.geometry("1024x700")
        self.minsize(800, 600)

        # Container for all views
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.current_frame = None
        self.user_info = None

        # Start invisible → show splash first
        self.withdraw()
        self.after(50, self.start_splash)

    def start_splash(self):
        """
        Start the splash screen. It will call show_login() after 5 seconds.
        """
        SplashScreen(self, next_callback=self.show_login)

    # ---------------------------
    # FRAME SWITCHING
    # ---------------------------
    def _swap_frame(self, frame_class, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()

        frame = frame_class(self.container, **kwargs)
        frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame = frame

    # ---------------------------
    # VIEWS
    # ---------------------------
    def show_login(self):
        """Called after splash screen finishes."""
        self.deiconify()  # Show main window
        self._swap_frame(LoginView, on_success=self.on_login_success)

    def on_login_success(self, user_data):
        """
        Called from LoginView after successful login.
        user_data should contain 'role' and 'full_name'.
        """
        role = user_data.get("role", "customer")
        full_name = user_data.get("full_name") or "Customer"
        self.show_home(role, full_name)


    def show_home(self, role, username):
        """Called after login view internally determines success."""
        self.title(f"Book Shop Management — {username}")

        # Map LoginView conventions to HomeSearchView parameters
        user_role = "staff" if role.lower() in ["staff", "admin"] else "customer"

        self._swap_frame(
            HomeSearchView,
            user_role=user_role,
            username=username
        )


# ---------------------------
# MAIN ENTRY
# ---------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
