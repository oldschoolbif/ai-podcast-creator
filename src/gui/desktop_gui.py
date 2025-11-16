"""
Desktop GUI for AI Podcast Creator using tkinter
Native desktop application
"""

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.audio_mixer import AudioMixer
from src.core.music_generator import MusicGenerator
from src.core.script_parser import ScriptParser
from src.core.tts_engine import TTSEngine
from src.core.video_composer import VideoComposer
from src.gui.desktop_gui_controller import PodcastCreatorController
from src.utils.config import load_config
from src.utils.gpu_utils import get_gpu_manager


class PodcastCreatorGUI:
    """Desktop GUI for AI Podcast Creator."""

    def __init__(self, root):
        self.root = root
        self.root.title("AI Podcast Creator 🎙️")
        self.root.geometry("900x700")

        # Variables
        self.script_file = tk.StringVar()
        self.music_file = tk.StringVar()
        self.music_description = tk.StringVar()
        self.voice_type = tk.StringVar(value="gtts")
        self.avatar_style = tk.StringVar(value="Professional Studio")
        self.video_quality = tk.StringVar(value="Fastest (Testing)")  # Default to fastest for testing
        self.visualize = tk.BooleanVar(value=False)  # Waveform visualization (opt-in)
        self.background = tk.BooleanVar(value=False)  # Background image (opt-in)
        self.avatar = tk.BooleanVar(value=False)  # Avatar/lip-sync (opt-in)
        self.output_name = tk.StringVar()

        # Load config
        self.config = load_config()
        
        # Initialize controller (business logic layer)
        self.controller = PodcastCreatorController(self.config)

        # Create GUI
        self.create_widgets()

        # Check GPU
        self.check_gpu()

    def _run_on_ui_thread(self, func, wait: bool = False):
        """Execute a callable on the Tk main thread."""

        if threading.current_thread() is threading.main_thread():
            func()
            return

        if wait:
            done = threading.Event()

            def wrapper():
                try:
                    func()
                finally:
                    done.set()

            self.root.after(0, wrapper)
            done.wait()
        else:
            self.root.after(0, func)

    def create_widgets(self):
        """Create all GUI widgets."""

        # Title
        title_frame = tk.Frame(self.root, bg="#2196F3", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame, text="🎙️ AI Podcast Creator", font=("Arial", 24, "bold"), bg="#2196F3", fg="white"
        )
        title_label.pack(pady=10)

        # Main container
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left column - Inputs
        left_frame = tk.LabelFrame(main_frame, text="📄 Input Files", font=("Arial", 12, "bold"), padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Script file
        tk.Label(left_frame, text="Script File:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=(0, 5))

        script_entry = tk.Entry(left_frame, textvariable=self.script_file, width=40, state="readonly")
        script_entry.grid(row=1, column=0, pady=(0, 10))

        tk.Button(
            left_frame,
            text="Browse...",
            command=self.browse_script,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
        ).grid(row=1, column=1, padx=(5, 0))

        # Music file
        tk.Label(left_frame, text="Music File (Optional):", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )

        music_entry = tk.Entry(left_frame, textvariable=self.music_file, width=40, state="readonly")
        music_entry.grid(row=3, column=0, pady=(0, 10))

        tk.Button(
            left_frame, text="Browse...", command=self.browse_music, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")
        ).grid(row=3, column=1, padx=(5, 0))

        # Music description
        tk.Label(left_frame, text="Or Describe Music Style:", font=("Arial", 10)).grid(
            row=4, column=0, sticky="w", pady=(0, 5)
        )

        music_desc_entry = tk.Entry(left_frame, textvariable=self.music_description, width=40)
        music_desc_entry.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        # Right column - Settings
        right_frame = tk.LabelFrame(main_frame, text="⚙️ Settings", font=("Arial", 12, "bold"), padx=10, pady=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        # Voice type
        tk.Label(right_frame, text="Voice Engine:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=(0, 5))

        voice_combo = ttk.Combobox(
            right_frame,
            textvariable=self.voice_type,
            values=[
                "gtts (Free, Cloud)",
                "coqui (High Quality, GPU)",
                "elevenlabs (Premium, API)",
                "azure (Good, API)",
            ],
            state="readonly",
            width=30,
        )
        voice_combo.grid(row=1, column=0, pady=(0, 10))

        # Avatar style
        tk.Label(right_frame, text="Avatar Style:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=(0, 5))

        avatar_combo = ttk.Combobox(
            right_frame,
            textvariable=self.avatar_style,
            values=["Professional Studio", "Gradient Background", "News Desk", "Tech Theme", "Minimal"],
            state="readonly",
            width=30,
        )
        avatar_combo.grid(row=3, column=0, pady=(0, 10))

        # Video quality
        tk.Label(right_frame, text="Video Quality:", font=("Arial", 10)).grid(row=4, column=0, sticky="w", pady=(0, 5))

        quality_combo = ttk.Combobox(
            right_frame,
            textvariable=self.video_quality,
            values=["Fastest (Testing)", "Fast (720p)", "Medium (720p)", "High (1080p)"],
            state="readonly",
            width=30,
        )
        quality_combo.grid(row=5, column=0, pady=(0, 10))

        # Video effects checkboxes
        effects_frame = tk.LabelFrame(right_frame, text="🎨 Video Effects (opt-in)", font=("Arial", 10, "bold"), padx=10, pady=10)
        effects_frame.grid(row=6, column=0, sticky="ew", pady=(0, 10))

        visualize_check = tk.Checkbutton(
            effects_frame, text="Waveform Visualization", variable=self.visualize, font=("Arial", 9)
        )
        visualize_check.grid(row=0, column=0, sticky="w", pady=2)

        background_check = tk.Checkbutton(
            effects_frame, text="Static Background Image", variable=self.background, font=("Arial", 9)
        )
        background_check.grid(row=1, column=0, sticky="w", pady=2)

        avatar_check = tk.Checkbutton(
            effects_frame, text="Avatar / Lip-Sync", variable=self.avatar, font=("Arial", 9)
        )
        avatar_check.grid(row=2, column=0, sticky="w", pady=2)

        # Output name
        tk.Label(right_frame, text="Output Name:", font=("Arial", 10)).grid(row=7, column=0, sticky="w", pady=(0, 5))

        output_entry = tk.Entry(right_frame, textvariable=self.output_name, width=33)
        output_entry.grid(row=8, column=0, pady=(0, 10))

        # Bottom section - Log and buttons
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(20, 0))

        # Status label
        self.status_label = tk.Label(bottom_frame, text="Ready", font=("Arial", 10), fg="green")
        self.status_label.pack(anchor="w")

        # Log output
        log_label = tk.Label(bottom_frame, text="📝 Progress Log:", font=("Arial", 10, "bold"))
        log_label.pack(anchor="w", pady=(10, 5))

        self.log_text = scrolledtext.ScrolledText(bottom_frame, height=10, width=100, font=("Courier", 9), bg="#f5f5f5")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = tk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.create_button = tk.Button(
            button_frame,
            text="🚀 Create Podcast",
            command=self.create_podcast,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
        )
        self.create_button.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            button_frame,
            text="📁 Open Output Folder",
            command=self.open_output_folder,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=10,
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=10,
        ).pack(side=tk.LEFT)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)

    def check_gpu(self):
        """Check and display GPU status."""
        gpu_manager = get_gpu_manager()
        if gpu_manager.gpu_available:
            gpu_info = f"⚡ GPU: {gpu_manager.gpu_name} ({gpu_manager.gpu_memory:.1f} GB)"
            self.log(gpu_info, "green")
        else:
            self.log("⚠️ Running on CPU (No GPU detected)", "orange")

    def browse_script(self):
        """Browse for script file."""
        filename = filedialog.askopenfilename(
            title="Select Script File",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")],
        )
        if filename:
            self.script_file.set(filename)
            self.log(f"Script selected: {Path(filename).name}")

    def browse_music(self):
        """Browse for music file."""
        filename = filedialog.askopenfilename(
            title="Select Music File", filetypes=[("Audio files", "*.mp3 *.wav *.m4a"), ("All files", "*.*")]
        )
        if filename:
            self.music_file.set(filename)
            self.log(f"Music selected: {Path(filename).name}")

    def log(self, message, color="black"):
        """Add message to log."""

        def append():
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)

        self._run_on_ui_thread(append)

    def clear_log(self):
        """Clear log text."""
        self.log_text.delete(1.0, tk.END)

    def update_status(self, message, color="black"):
        """Update status label."""
        self._run_on_ui_thread(lambda: self.status_label.config(text=message, fg=color))

    def open_output_folder(self):
        """Open output folder in file explorer."""
        output_dir = Path(self.config["storage"]["outputs_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        import platform
        import subprocess

        if platform.system() == "Windows":
            subprocess.Popen(["explorer", str(output_dir)])
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", str(output_dir)])
        else:  # Linux
            subprocess.Popen(["xdg-open", str(output_dir)])

    def create_podcast(self):
        """Create podcast in separate thread."""
        # Update controller state from GUI
        self.controller.script_file = self.script_file.get()
        self.controller.music_file = self.music_file.get() if self.music_file.get() else None
        self.controller.music_description = self.music_description.get() if self.music_description.get() else None
        self.controller.video_quality = self.video_quality.get()
        self.controller.visualize = self.visualize.get()
        self.controller.background = self.background.get()
        self.controller.avatar = self.avatar.get()
        self.controller.output_name = self.output_name.get() if self.output_name.get() else None
        
        # Validate using controller
        is_valid, error_msg = self.controller.validate_inputs()
        if not is_valid:
            messagebox.showerror("Error", error_msg)
            return

        # Disable button during processing
        self._run_on_ui_thread(lambda: self.create_button.config(state=tk.DISABLED), wait=True)

        # Run in thread to keep GUI responsive
        thread = threading.Thread(target=self._create_podcast_thread)
        thread.daemon = True
        thread.start()

    def _create_podcast_thread(self):
        """Create podcast (runs in separate thread)."""
        try:
            # Use controller to create podcast with callbacks for UI updates
            final_video = self.controller.create_podcast(
                progress_callback=lambda msg, status: self.update_status(msg, status),
                log_callback=lambda msg, color: self.log(msg, color)
            )

            # Show success dialog
            prompt_result = {"value": False}

            def ask_success():
                prompt_result["value"] = messagebox.askyesno(
                    "Success!", f"Podcast created successfully!\n\nSaved to: {final_video}\n\nOpen output folder?"
                )

            self._run_on_ui_thread(ask_success, wait=True)

            if prompt_result["value"]:
                self._run_on_ui_thread(self.open_output_folder)

        except (ValueError, RuntimeError) as e:
            self.log(f"❌ Error: {str(e)}", "red")
            self.update_status("❌ Error", "red")
            self._run_on_ui_thread(
                lambda e=e: messagebox.showerror("Error", f"Failed to create podcast:\n\n{str(e)}"), wait=True
            )

        finally:
            # Re-enable button
            self._run_on_ui_thread(lambda: self.create_button.config(state=tk.NORMAL), wait=True)


def launch_desktop_gui():
    """Launch the desktop GUI."""
    root = tk.Tk()
    _app = PodcastCreatorGUI(root)  # GUI is initialized and bound to root
    root.mainloop()


if __name__ == "__main__":
    launch_desktop_gui()
