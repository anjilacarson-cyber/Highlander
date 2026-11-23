import base64
import io
import json
import os
import queue
import re
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

import pyautogui
from PIL import ImageGrab, ImageTk
from google import genai
from google.genai import types
import keyring

APP_NAME = "Gemini Desktop Operator"
APP_VERSION = "1.0.0"
KEYRING_SERVICE = "GeminiDesktopOperator"
KEYRING_USERNAME = "gemini_api_key"
DEFAULT_MODEL = "gemini-3.8-flash"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.03


class OperatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("1120x820")
        self.root.minsize(900, 680)
        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.typing_thread = None
        self.generated_code = ""
        self.last_screenshot = None
        self.client = None
        self.project_dir = tk.StringVar(value=str(Path.home() / "Desktop"))
        self.target_file = tk.StringVar(value="index.html")
        self.mouse_x = tk.StringVar(value="500")
        self.mouse_y = tk.StringVar(value="400")
        self.speed = tk.IntVar(value=5)
        self.model = tk.StringVar(value=DEFAULT_MODEL)
        self.status = tk.StringVar(value="Ready. Add your Gemini API key to get started.")
        self._build()
        self._load_saved_key()
        self.root.after(100, self._poll_events)

    def _build(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Header.TLabel", font=("Segoe UI", 19, "bold"))
        style.configure("Sub.TLabel", foreground="#555555")
        style.configure("Action.TButton", padding=(10, 7))

        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x")
        ttk.Label(header, text="Gemini Desktop Operator", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text=f"v{APP_VERSION}", style="Sub.TLabel").pack(side="right")

        ttk.Label(
            outer,
            text="Generate code, review it, and type it visibly into the application you choose.",
            style="Sub.TLabel"
        ).pack(anchor="w", pady=(3, 12))

        settings = ttk.LabelFrame(outer, text="Gemini connection", padding=10)
        settings.pack(fill="x", pady=(0, 10))
        keyrow = ttk.Frame(settings)
        keyrow.pack(fill="x")
        ttk.Label(keyrow, text="Gemini API key", width=16).pack(side="left")
        self.api_key = tk.StringVar()
        self.key_entry = ttk.Entry(keyrow, textvariable=self.api_key, show="•")
        self.key_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(keyrow, text="Save key securely", command=self.save_key).pack(side="left", padx=(8, 0))
        ttk.Button(keyrow, text="Forget key", command=self.forget_key).pack(side="left", padx=(6, 0))
        modelrow = ttk.Frame(settings)
        modelrow.pack(fill="x", pady=(8, 0))
        ttk.Label(modelrow, text="Model", width=16).pack(side="left")
        ttk.Entry(modelrow, textvariable=self.model, width=30).pack(side="left")
        ttk.Label(modelrow, text="API key is stored in Windows Credential Manager via keyring.",
                  style="Sub.TLabel").pack(side="left", padx=10)

        task = ttk.LabelFrame(outer, text="Task instructions", padding=10)
        task.pack(fill="x", pady=(0, 10))
        self.prompt = tk.Text(task, height=4, wrap="word", font=("Segoe UI", 10))
        self.prompt.pack(fill="x")
        self.prompt.insert(
            "1.0",
            "Create a clean, responsive HTML landing page for a student portfolio. "
            "Use semantic HTML and simple CSS in one file."
        )

        target = ttk.LabelFrame(outer, text="Workspace and typing", padding=10)
        target.pack(fill="x", pady=(0, 10))
        row1 = ttk.Frame(target)
        row1.pack(fill="x")
        ttk.Label(row1, text="Project folder", width=16).pack(side="left")
        ttk.Entry(row1, textvariable=self.project_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(row1, text="Browse…", command=self.browse_folder).pack(side="left", padx=(8, 0))
        row2 = ttk.Frame(target)
        row2.pack(fill="x", pady=(8, 0))
        ttk.Label(row2, text="Target filename", width=16).pack(side="left")
        ttk.Entry(row2, textvariable=self.target_file, width=28).pack(side="left")
        ttk.Button(row2, text="Create/open target file", command=self.create_open_target).pack(side="left", padx=(8, 0))
        ttk.Label(row2, text="Characters per second", padding=(16, 0, 4, 0)).pack(side="left")
        self.speed_scale = ttk.Scale(row2, from_=1, to=10, orient="horizontal",
                                     command=self._on_speed)
        self.speed_scale.set(5)
        self.speed_scale.pack(side="left", fill="x", expand=True, padx=6)
        self.speed_label = ttk.Label(row2, text="5 chars/sec", width=13)
        self.speed_label.pack(side="left")

        mousebox = ttk.LabelFrame(outer, text="Mouse controls", padding=8)
        mousebox.pack(fill="x", pady=(0, 10))
        ttk.Label(mousebox, text="Screen X").pack(side="left")
        ttk.Entry(mousebox, textvariable=self.mouse_x, width=7).pack(side="left", padx=(4, 12))
        ttk.Label(mousebox, text="Screen Y").pack(side="left")
        ttk.Entry(mousebox, textvariable=self.mouse_y, width=7).pack(side="left", padx=(4, 12))
        ttk.Button(mousebox, text="Move pointer", command=self.move_pointer).pack(side="left")
        ttk.Button(mousebox, text="Left click", command=lambda: self.click_pointer("left")).pack(side="left", padx=6)
        ttk.Button(mousebox, text="Right click", command=lambda: self.click_pointer("right")).pack(side="left")

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="Generate with Gemini", style="Action.TButton",
                   command=self.generate).pack(side="left")
        ttk.Button(actions, text="Create/open workspace", style="Action.TButton",
                   command=self.open_workspace).pack(side="left", padx=6)
        ttk.Button(actions, text="Capture screen", style="Action.TButton",
                   command=self.capture_screen).pack(side="left")
        ttk.Button(actions, text="Analyze screen with Gemini", style="Action.TButton",
                   command=self.analyze_screen).pack(side="left", padx=6)
        ttk.Button(actions, text="Type visibly", style="Action.TButton",
                   command=self.start_typing).pack(side="left")
        ttk.Button(actions, text="STOP", style="Action.TButton",
                   command=self.stop_typing).pack(side="right")

        panes = ttk.Panedwindow(outer, orient="horizontal")
        panes.pack(fill="both", expand=True)
        code_frame = ttk.LabelFrame(panes, text="Generated code — review before typing", padding=6)
        log_frame = ttk.LabelFrame(panes, text="Activity log", padding=6)
        panes.add(code_frame, weight=3)
        panes.add(log_frame, weight=1)

        self.code = tk.Text(code_frame, wrap="none", font=("Consolas", 10), undo=True)
        self.code.pack(fill="both", expand=True)
        self.log = tk.Text(log_frame, wrap="word", font=("Segoe UI", 9), state="disabled")
        self.log.pack(fill="both", expand=True)

        ttk.Label(outer, textvariable=self.status, style="Sub.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Label(
            outer,
            text="Safety: generated code is not executed automatically. Review it first. "
                 "Typing starts after a 5-second countdown. Move the mouse to the top-left "
                 "corner for PyAutoGUI's emergency failsafe.",
            style="Sub.TLabel",
            wraplength=1050
        ).pack(anchor="w", pady=(3, 0))

    def _log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_status(self, message):
        self.status.set(message)
        self._log(message)

    def _load_saved_key(self):
        try:
            saved = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if saved:
                self.api_key.set(saved)
                self._set_status("A Gemini key was found in Windows Credential Manager.")
        except Exception:
            self._log("No saved API key found.")

    def save_key(self):
        key = self.api_key.get().strip()
        if not key:
            messagebox.showwarning("Missing key", "Paste your Gemini API key first.")
            return
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, key)
            self._set_status("API key saved in Windows Credential Manager.")
        except Exception as exc:
            messagebox.showerror("Could not save key", str(exc))

    def forget_key(self):
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
        except Exception:
            pass
        self.api_key.set("")
        self._set_status("Saved API key cleared.")

    def _get_client(self):
        key = self.api_key.get().strip()
        if not key:
            raise ValueError("Enter your Gemini API key first.")
        return genai.Client(api_key=key)

    def _on_speed(self, value):
        v = max(1, min(10, round(float(value))))
        self.speed.set(v)
        self.speed_label.configure(text=f"{v} chars/sec")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.project_dir.get() or str(Path.home()))
        if folder:
            self.project_dir.set(folder)

    def open_workspace(self):
        folder = Path(self.project_dir.get()).expanduser()
        try:
            folder.mkdir(parents=True, exist_ok=True)
            os.startfile(str(folder))
            self._set_status(f"Opened workspace folder: {folder}")
        except Exception as exc:
            messagebox.showerror("Workspace error", str(exc))

    def generate(self):
        prompt = self.prompt.get("1.0", "end").strip()
        filename = self.target_file.get().strip()
        if not prompt or not filename:
            messagebox.showwarning("Missing information", "Enter a task and target filename.")
            return
        self._set_status("Sending coding request to Gemini…")
        threading.Thread(target=self._generate_worker, args=(prompt, filename), daemon=True).start()

    def _generate_worker(self, prompt, filename):
        try:
            client = self._get_client()
            instruction = (
                "You are a senior software developer. Generate the complete contents for exactly "
                f"one file named {filename}. Return source code only, without Markdown fences. "
                "Do not include shell commands, secrets, destructive instructions, or code that "
                "attempts to disable security controls. Prefer clear, maintainable code.\n\n"
                f"User task:\n{prompt}"
            )
            response = client.models.generate_content(
                model=self.model.get().strip() or DEFAULT_MODEL,
                contents=instruction
            )
            text = (response.text or "").strip()
            text = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            self.events.put(("generated", text))
        except Exception as exc:
            self.events.put(("error", f"Gemini request failed: {exc}"))


    def _target_path(self):
        folder = Path(self.project_dir.get()).expanduser().resolve()
        name = self.target_file.get().strip()
        if not name or Path(name).name != name or name in {".", ".."}:
            raise ValueError("Target filename must be a simple filename, not a path.")
        folder.mkdir(parents=True, exist_ok=True)
        return folder / name

    def create_open_target(self):
        try:
            target = self._target_path()
            target.touch(exist_ok=True)
            os.startfile(str(target))
            self._set_status(f"Created/opened target file: {target}")
        except Exception as exc:
            messagebox.showerror("Target file error", str(exc))

    def move_pointer(self):
        try:
            x, y = int(self.mouse_x.get()), int(self.mouse_y.get())
            width, height = pyautogui.size()
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"Coordinates must be within this screen: 0–{width-1}, 0–{height-1}.")
            if not messagebox.askyesno("Move mouse", f"Move the pointer to screen position ({x}, {y})?"):
                return
            threading.Thread(target=lambda: pyautogui.moveTo(x, y, duration=0.5), daemon=True).start()
            self._set_status(f"Moving pointer to ({x}, {y}).")
        except Exception as exc:
            messagebox.showerror("Mouse control error", str(exc))

    def click_pointer(self, button):
        if not messagebox.askyesno(
            "Confirm mouse click",
            f"Send a {button} click at the current pointer position? Make sure the intended window is active."
        ):
            return
        threading.Thread(target=lambda: pyautogui.click(button=button), daemon=True).start()
        self._set_status(f"Sent {button} click at current pointer position.")

    def capture_screen(self):
        try:
            self.last_screenshot = ImageGrab.grab()
            self._set_status(f"Captured screen: {self.last_screenshot.width} × {self.last_screenshot.height}")
            preview = tk.Toplevel(self.root)
            preview.title("Screen capture preview")
            preview.geometry("850x600")
            img = self.last_screenshot.copy()
            img.thumbnail((820, 520))
            photo = ImageTk.PhotoImage(img)
            label = ttk.Label(preview, image=photo)
            label.image = photo
            label.pack(padx=10, pady=10)
            ttk.Label(preview, text="This capture stays local unless you choose Analyze screen with Gemini.").pack()
        except Exception as exc:
            messagebox.showerror("Capture failed", str(exc))

    def analyze_screen(self):
        if self.last_screenshot is None:
            messagebox.showinfo("No capture", "Capture the screen first.")
            return
        if not messagebox.askyesno(
            "Send screenshot to Gemini?",
            "This will send the captured screen image to Google's Gemini API. "
            "Make sure it contains no passwords, private messages, or sensitive information."
        ):
            return
        threading.Thread(target=self._analyze_worker, daemon=True).start()

    def _analyze_worker(self):
        try:
            client = self._get_client()
            buf = io.BytesIO()
            self.last_screenshot.save(buf, format="PNG")
            image_part = types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
            response = client.models.generate_content(
                model=self.model.get().strip() or DEFAULT_MODEL,
                contents=[
                    "Describe the visible desktop UI and suggest the next safe user-interface step. "
                    "Do not assume permission to click, type, run commands, or change files.",
                    image_part
                ]
            )
            self.events.put(("analysis", response.text or "No analysis returned."))
        except Exception as exc:
            self.events.put(("error", f"Screen analysis failed: {exc}"))

    def start_typing(self):
        content = self.code.get("1.0", "end-1c")
        if not content:
            messagebox.showwarning("No code", "Generate or paste code into the editor first.")
            return
        if not messagebox.askyesno(
            "Confirm visible typing",
            "Open the intended file in VS Code and click the exact insertion point. "
            "The bot will send visible keystrokes to whichever window is focused after a "
            "5-second countdown. Existing text will not be cleared automatically. Continue?"
        ):
            return
        self.stop_event.clear()
        self.typing_thread = threading.Thread(target=self._typing_worker, args=(content,), daemon=True)
        self.typing_thread.start()

    def _typing_worker(self, content):
        for remaining in range(5, 0, -1):
            if self.stop_event.is_set():
                self.events.put(("status", "Typing cancelled."))
                return
            self.events.put(("status", f"Switch to the target editor — typing starts in {remaining}s"))
            time.sleep(1)
        cps = max(1, min(10, int(self.speed.get())))
        interval = 1.0 / cps
        try:
            for ch in content:
                if self.stop_event.is_set():
                    self.events.put(("status", "Typing stopped by user."))
                    return
                if ch == "\n":
                    pyautogui.press("enter")
                elif ch == "\t":
                    pyautogui.press("tab")
                elif ch == "\r":
                    continue
                else:
                    # write() emits keyboard events; interval is controlled per character below.
                    pyautogui.write(ch, interval=0)
                time.sleep(interval)
            self.events.put(("status", "Typing finished. Save the file in your editor."))
        except pyautogui.FailSafeException:
            self.events.put(("status", "Emergency stop triggered by moving the pointer to the top-left corner."))
        except Exception as exc:
            self.events.put(("error", f"Typing interrupted: {exc}"))

    def stop_typing(self):
        self.stop_event.set()
        self._set_status("Stop requested.")

    def _poll_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "generated":
                    self.code.delete("1.0", "end")
                    self.code.insert("1.0", value)
                    self._set_status(f"Gemini generated {len(value)} characters. Review before typing.")
                elif kind == "analysis":
                    self._set_status("Gemini screen analysis received.")
                    messagebox.showinfo("Gemini screen analysis", value[:12000])
                elif kind == "error":
                    self._set_status("An error occurred.")
                    messagebox.showerror("Operator error", value)
                else:
                    self._set_status(value)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)


def main():
    root = tk.Tk()
    app = OperatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
