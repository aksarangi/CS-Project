# frontend/views/splash_screen.py
import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashScreen(tk.Toplevel):
    def __init__(self, root, next_callback):
        """
        root           -> hidden main window
        next_callback  -> function to run after splash (typically open LoginView)
        """
        super().__init__(root)
        self.root = root
        self.next_callback = next_callback

        # Remove title bar
        self.overrideredirect(True)

        # Splash dimensions
        width, height = 480, 320
        self.geometry(f"{width}x{height}+{self.center_x(width)}+{self.center_y(height)}")

        # Main frame
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="both", expand=True)

        # Load Image (App Icon)
        try:
            img_path = os.path.join("assets", "books.jpg")
            img = Image.open(img_path)
            img = img.resize((180, 180), Image.LANCZOS)
            self.icon_img = ImageTk.PhotoImage(img)
            tk.Label(frame, image=self.icon_img, bg="white").pack(pady=(20, 10))
        except Exception as e:
            tk.Label(frame, text="📚", font=("Arial", 80), bg="white").pack(pady=(30, 5))
            print("Error loading splash image:", e)

        # App name
        tk.Label(
            frame,
            text="Book Shop Management",
            font=("Arial", 20, "bold"),
            bg="white"
        ).pack(pady=5)

        # Sanskrit motto (Devanagari)
        tk.Label(
            frame,
            text="विद्या बलं प्रधानम्",
            font=("Nirmala UI", 18, "italic"),
            fg="#444",
            bg="white"
        ).pack(pady=5)

        # Start invisible for fade-in
        self.attributes("-alpha", 0.0)
        self.fade_in()

        # Auto transition after 2.3 seconds
        self.after(5000, self.finish)

    # -----------------------
    # Utility: center screen
    # -----------------------
    def center_x(self, w): return (self.winfo_screenwidth() - w) // 2
    def center_y(self, h): return (self.winfo_screenheight() - h) // 2

    # -----------------------
    # Fade-in animation
    # -----------------------
    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.attributes("-alpha", alpha)
            self.after(30, self.fade_in)

    # -----------------------
    # End splash → start app
    # -----------------------
    def finish(self):
        self.destroy()
        self.next_callback()
