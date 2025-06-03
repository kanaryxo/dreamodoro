import customtkinter as ctk
import pygame
from customtkinter import CTkImage
from PIL import Image, ImageTk, ImageSequence
from tkinter import messagebox
import sys
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this at runtime
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Set time intervals
work_time = 30 * 60
short_break = 5 * 60
long_break = 15 * 60


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master, delay=3000):
        super().__init__(master)

        width, height = 320, 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.title("Dreamodoro")
        self.configure(fg_color="#eecbff")
        self.overrideredirect(True)  # removes title bar

        # Label / Logo
        self.label = ctk.CTkLabel(self, text="🌙 Dreamodoro", font=(
            "Helvetica", 22, "bold"), text_color="#999999")
        self.label.pack(pady=(40, 10))

        self.sublabel = ctk.CTkLabel(self, text="Loading your focus...", font=(
            "Helvetica", 12), text_color="#999999")
        self.sublabel.pack()

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, width=200)
        self.progress.pack(pady=20)
        self.progress.set(0)  # start at 0

        # Animate bar
        self.update_progress(delay)

    def update_progress(self, delay):
        steps = 100
        step_delay = delay // steps

        def step(i=0):
            if i <= steps:
                self.progress.set(i / steps)
                self.after(step_delay, lambda: step(i + 1))
            else:
                self.destroy()  # close splash after done

        step()


class PomodoroApp:
    def __init__(self, root):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme(resource_path("mytheme.json"))

        self.root = root
        self.root.configure(fg_color="#e0d6ff")
        self.root.title("Dreamodoro")
        self.root.iconbitmap(resource_path("icon.ico"))

        self.root.update_idletasks()
        width, height = 320, 410
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.deiconify()

        self.container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.container.pack(padx=10, pady=10)

        self.quote_top = ctk.CTkLabel(
            self.container, text="Dreams don’t work", font=("Helvetica", 24, "bold"))
        self.quote_top.pack(pady=(10, 0))

        self.quote_bottom = ctk.CTkLabel(
            self.container, text="unless you do.", font=("Helvetica", 20))
        self.quote_bottom.pack(pady=(0, 10))

        self.timer_label = ctk.CTkLabel(
            self.container, text="00:00", font=("Helvetica", 36, "bold"))
        self.timer_label.pack(pady=30)

        button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        button_frame.pack(pady=5)

        self.start_button = ctk.CTkButton(
            button_frame, text="Start", command=self.on_start_click, corner_radius=50, width=90)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(
            button_frame, text="Stop", command=self.on_stop_click, corner_radius=50, width=90)
        self.stop_button.pack(side="left", padx=5)

        self.reset_button = ctk.CTkButton(
            button_frame, text="Reset", command=self.on_reset_click, corner_radius=50, width=90)
        self.reset_button.pack(side="left", padx=5)

        self.gif_frames = []
        self.current_gif_index = 0
        self.gif_label = ctk.CTkLabel(self.root, text="")
        self.gif_label.place(x=60, y=310)
        self.active_gif_name = ""

        self.work_time, self.break_time = work_time, short_break
        self.is_work_time = True
        self.pomodoros_completed = 0
        self.is_running = False

        self.load_gif(resource_path("study.gif"))
        self.animate_gif()
        self.restart_timer(gif_path="study.gif")

    def on_start_click(self):
        self.play_sound(resource_path("button.mp3"))
        self.start_timer()
        self.load_gif(resource_path("study.gif"))

    def on_stop_click(self):
        self.play_sound(resource_path("button.mp3"))
        self.stop_timer()
        self.load_gif(resource_path("break.gif"))

    def on_reset_click(self):
        self.play_sound(resource_path("button.mp3"))
        self.restart_timer(gif_path="reset.gif")
        self.load_gif(resource_path("reset.gif"))

    def animate_gif(self):
        if not self.gif_frames:
            return

        frame = self.gif_frames[self.gif_index]
        self.gif_label.configure(image=frame)
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.root.after(100, self.animate_gif)

    def load_gif(self, path):
        self.active_gif_name = os.path.basename(path)
        self.gif_frames.clear()
        self.gif_index = 0
        gif = Image.open(path)

        self.gif_label.place(x=80, y=240)

        for frame in ImageSequence.Iterator(gif):
            frame = frame.resize((150, 150))
            self.gif_frames.append(
                CTkImage(light_image=frame, size=(150, 150)))

    def start_timer(self):
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.is_running = True
        self.load_gif(resource_path("study.gif"))
        self.gif_index = 0
        self.update_timer()

    def stop_timer(self):
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.is_running = False
        self.gif_index = 0
        self.load_gif(resource_path("break.gif"))

    def restart_timer(self, gif_path=None):
        self.is_running = False
        self.work_time = 30 * 60
        self.break_time = 5 * 60
        self.is_work_time = True
        self.pomodoros_completed = 0

        if gif_path:
            self.load_gif(resource_path(gif_path))

        minutes, seconds = divmod(self.work_time, 60)
        self.timer_label.configure(
            text="{:02d}:{:02d}".format(minutes, seconds))
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def update_timer(self):
        if self.is_running:
            if self.is_work_time:
                self.work_time -= 1
                if self.work_time == 0:
                    self.is_work_time = False
                    self.pomodoros_completed += 1
                    self.break_time = long_break if self.pomodoros_completed % 4 == 0 else short_break
                    self.play_sound(resource_path("breaktime.mp3"))
                    self.load_gif(resource_path("break.gif"))
                    self.is_running = False
                    self.root.after(100, self.show_break_popup)
            else:
                self.break_time -= 1
                if self.break_time == 0:
                    self.is_work_time = True
                    self.work_time = work_time
                    messagebox.showinfo("Work Time", "Get back to work!")
                    self.load_gif(resource_path("study.gif"))

            minutes, seconds = divmod(
                self.work_time if self.is_work_time else self.break_time, 60)
            self.timer_label.configure(
                text="{:02d}:{:02d}".format(minutes, seconds))
            self.root.after(1000, self.update_timer)

    def show_break_popup(self):
        messagebox.showinfo("Break Time", "Take a break!")
        self.is_running = True
        self.update_timer()

    def play_sound(self, file):
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()

    splash = SplashScreen(root, delay=3000)
    splash.wait_window()

    root.destroy()

    main_root = ctk.CTk()
    app = PomodoroApp(main_root)
    main_root.mainloop()
