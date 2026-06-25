import ctypes
import os
import sys
import tkinter as tk
from ctypes import wintypes

class OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Overlay App for Writing")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.click_through = False
        self.original_style = None
        self.current_language = "ENG"
        self.image_position = "center"
        self.overlay_alpha = 0.22
        self.image_id = None
        self.hotkey_id = 1

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.image_x = screen_width // 2
        self.image_y = screen_height // 2

        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.config(bg="#00ff00")
        self.root.attributes("-alpha", self.overlay_alpha)
        self.root.attributes("-transparentcolor", "#00ff00")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.images = {
            "ENG": tk.PhotoImage(file=os.path.join(script_dir, "ENG.png")),
            "SPA": tk.PhotoImage(file=os.path.join(script_dir, "ES.png")),
            "RUS": tk.PhotoImage(file=os.path.join(script_dir, "RU.png"))
        }

        self.canvas = tk.Canvas(self.root, bg="#00ff00", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.controls_window = tk.Toplevel(self.root)
        self.controls_window.title("Overlay Controls")
        self.controls_window.attributes("-topmost", True)
        self.controls_window.geometry("760x110+20+20")
        self.controls_window.configure(bg="#222222")
        self.controls_window.protocol("WM_DELETE_WINDOW", lambda: None)

        self.controls_frame = tk.Frame(self.controls_window, bg="#222222", bd=1, relief=tk.RIDGE)
        self.controls_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.create_controls()
        self.update_overlay_image()

        self.root.bind("<Escape>", lambda event: self.close_app())
        self.root.bind("<Control-Shift-o>", lambda event: self.toggle_click_through())
        self.root.bind("<Control-Shift-s>", lambda event: self.open_settings())
        self.root.bind("<Control-Shift-x>", lambda event: self.close_app())
        self.controls_window.bind("<Control-Shift-x>", lambda event: self.close_app())

        self.register_close_hotkey()
        self.set_click_through(True)
        self.open_troubleshoot()

    def create_controls(self):
        tk.Label(self.controls_frame, text="Languages:", fg="white", bg="#222222").pack(side=tk.LEFT, padx=5)

        for language in ["ENG", "SPA", "RUS"]:
            button = tk.Button(
                self.controls_frame,
                text=language,
                command=lambda lang=language: self.select_language(lang),
                width=5
            )
            button.pack(side=tk.LEFT, padx=2, pady=5)

        self.settings_button = tk.Button(self.controls_frame, text="Settings", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        self.troubleshoot_button = tk.Button(self.controls_frame, text="Troubleshoot", command=self.open_troubleshoot)
        self.troubleshoot_button.pack(side=tk.LEFT, padx=5)

        self.click_button = tk.Button(self.controls_frame, text="Enable Click-Through", command=self.toggle_click_through)
        self.click_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.controls_frame, text="Clear Image", command=self.clear_overlay)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.close_button = tk.Button(self.controls_frame, text="Close App", command=self.close_app, bg="#cc3333", fg="white")
        self.close_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.controls_frame, text="Mode: Image Overlay", fg="white", bg="#222222")
        self.status_label.pack(side=tk.LEFT, padx=5)

    def select_language(self, language):
        self.current_language = language
        self.update_overlay_image()

    def clear_overlay(self):
        if self.image_id is not None:
            self.canvas.delete(self.image_id)
            self.image_id = None

    def update_overlay_image(self):
        self.clear_overlay()
        image = self.images.get(self.current_language)
        if not image:
            return

        x, y = self.compute_image_position(image)
        self.image_id = self.canvas.create_image(x, y, image=image, anchor=tk.CENTER)

    def compute_image_position(self, image):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        image_width = image.width()
        image_height = image.height()

        positions = {
            "top-left": (image_width // 2 + 30, image_height // 2 + 30),
            "top-right": (screen_width - image_width // 2 - 30, image_height // 2 + 30),
            "bottom-left": (image_width // 2 + 30, screen_height - image_height // 2 - 30),
            "bottom-right": (screen_width - image_width // 2 - 30, screen_height - image_height // 2 - 30),
            "center": (screen_width // 2, screen_height // 2),
            "custom": (self.image_x, self.image_y),
        }
        return positions.get(self.image_position, positions["center"])

    def toggle_click_through(self):
        self.set_click_through(not self.click_through)

    def set_click_through(self, value: bool):
        self.click_through = value
        if value:
            self.click_button.config(text="Disable Click-Through")
            self.status_label.config(text="Mode: Click-through")
        else:
            self.click_button.config(text="Enable Click-Through")
            self.status_label.config(text="Mode: Image Overlay")

        if sys.platform == "win32":
            hwnd = self.root.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20

            if self.original_style is None:
                self.original_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

            style = self.original_style
            if value:
                style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
                self.root.attributes("-alpha", 1.0)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        else:
            self.root.attributes("-alpha", 0.15 if value else self.overlay_alpha)

        self.controls_window.lift()

    def close_app(self):
        if sys.platform == "win32":
            self.unregister_close_hotkey()
        try:
            self.controls_window.destroy()
        except Exception:
            pass
        self.root.destroy()

    def register_close_hotkey(self):
        if sys.platform != "win32":
            return

        MOD_WIN = 0x0008
        VK_X = 0x58
        ctypes.windll.user32.RegisterHotKey(None, self.hotkey_id, MOD_WIN, VK_X)
        self.check_hotkey()

    def unregister_close_hotkey(self):
        if sys.platform != "win32":
            return
        ctypes.windll.user32.UnregisterHotKey(None, self.hotkey_id)

    def check_hotkey(self):
        if sys.platform != "win32":
            return

        msg = wintypes.MSG()
        PM_REMOVE = 0x0001
        WM_HOTKEY = 0x0312
        user32 = ctypes.windll.user32

        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
            if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                self.close_app()
                return
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        self.root.after(50, self.check_hotkey)

    def open_settings(self):
        settings = tk.Toplevel(self.root)
        settings.title("Overlay Settings")
        settings.geometry("340x300+100+100")
        settings.attributes("-topmost", True)

        tk.Label(settings, text="Select overlay position:", pady=8).pack()

        options = ["center", "top-left", "top-right", "bottom-left", "bottom-right", "custom"]
        position_var = tk.StringVar(value=self.image_position)

        radio_frame = tk.Frame(settings)
        radio_frame.pack(fill=tk.X, padx=10)
        for option in options:
            radio = tk.Radiobutton(
                radio_frame,
                text=option.replace('-', ' ').title(),
                variable=position_var,
                value=option,
                anchor="w",
                width=12
            )
            radio.pack(side=tk.LEFT, padx=2, pady=2)

        tk.Label(settings, text="Image visibility:", pady=8).pack(pady=(10, 0))
        visibility_var = tk.DoubleVar(value=self.overlay_alpha)
        visibility_scale = tk.Scale(
            settings,
            variable=visibility_var,
            from_=0.05,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            length=300
        )
        visibility_scale.pack(padx=10)

        tk.Label(settings, text="Custom X / Y position:", pady=8).pack(pady=(10, 0))
        position_frame = tk.Frame(settings)
        position_frame.pack(fill=tk.X, padx=10)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_var = tk.IntVar(value=self.image_x)
        y_var = tk.IntVar(value=self.image_y)

        tk.Label(position_frame, text="X", width=2).pack(side=tk.LEFT)
        x_scale = tk.Scale(position_frame, variable=x_var, from_=0, to=screen_width, orient=tk.HORIZONTAL, length=150)
        x_scale.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(position_frame, text="Y", width=2).pack(side=tk.LEFT)
        y_scale = tk.Scale(position_frame, variable=y_var, from_=0, to=screen_height, orient=tk.HORIZONTAL, length=150)
        y_scale.pack(side=tk.LEFT)

        tk.Label(settings, text="Tip: If you can still click apps, use AltGr+Tab to switch apps and then disable click-through.", wraplength=320, justify=tk.LEFT, fg="#eeeeee", bg="#222222").pack(padx=10, pady=(10, 0))
        tk.Label(settings, text="Note: pink background is normal; it just makes the overlay transparent.", wraplength=320, justify=tk.LEFT, fg="#ffee88", bg="#222222").pack(padx=10, pady=(5, 10))

        def apply_settings():
            self.image_position = position_var.get()
            self.overlay_alpha = float(visibility_var.get())
            self.image_x = int(x_var.get())
            self.image_y = int(y_var.get())
            if self.click_through and sys.platform == "win32":
                self.root.attributes("-alpha", 1.0)
            else:
                self.root.attributes("-alpha", self.overlay_alpha)
            self.update_overlay_image()
            settings.destroy()

        tk.Button(settings, text="Apply", command=apply_settings).pack(pady=10)

    def open_troubleshoot(self):
        trouble = tk.Toplevel(self.root)
        trouble.title("Troubleshoot")
        trouble.geometry("360x220+120+120")
        trouble.attributes("-topmost", True)

        tk.Label(trouble, text="Troubleshoot", font=("Arial", 12, "bold"), pady=8).pack()
        tk.Label(trouble, text="If your apps are still clickable by default, use AltGr+Tab to switch to the desired app, then disable click-through.", wraplength=340, justify=tk.LEFT, fg="#eeeeee", bg="#333333").pack(padx=10, pady=(0, 10))
        tk.Label(trouble, text="If the screen looks pink, don't worry: this is just the transparent color marker for the overlay.", wraplength=340, justify=tk.LEFT, fg="#ffee88", bg="#333333").pack(padx=10, pady=(0, 10))
        tk.Label(trouble, text="Tip: Close the overlay with Win+X or the Close button if needed.", wraplength=340, justify=tk.LEFT, fg="#aaffaa", bg="#333333").pack(padx=10, pady=(0, 10))
        
        tk.Button(trouble, text="OK", command=trouble.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = OverlayApp(root)
    root.mainloop()