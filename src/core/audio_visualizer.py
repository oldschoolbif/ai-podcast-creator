"""
Audio Visualizer - Generate vibrant backgrounds that react to voice
"""

from pathlib import Path

import librosa
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Optional import - librosa.display requires matplotlib
try:
    import librosa.display  # noqa: F401
except ImportError:
    pass  # librosa.display is optional, only needed for spectrogram visualization


class AudioVisualizer:
    """Generate audio-reactive visualizations"""

    def __init__(self, config: dict):
        self.config = config
        self.viz_config = config.get("visualization", {})
        self.style = self.viz_config.get("style", "waveform")  # waveform, spectrum, circular, particles
        self.resolution = config.get("video", {}).get("resolution", [1920, 1080])
        self.fps = config.get("video", {}).get("fps", 30)

        # Visual settings
        self.primary_color = self.viz_config.get("primary_color", [0, 150, 255])  # Blue
        self.secondary_color = self.viz_config.get("secondary_color", [255, 100, 200])  # Pink
        self.background_color = self.viz_config.get("background_color", [10, 10, 20])  # Dark
        self.blur = self.viz_config.get("blur", 3)
        self.sensitivity = self.viz_config.get("sensitivity", 1.0)

    def generate_visualization(self, audio_path: Path, output_path: Path) -> Path:
        """
        Generate video with audio-reactive visualization

        Args:
            audio_path: Path to audio file
            output_path: Path for output video

        Returns:
            Path to generated video
        """
        print(f"🎨 Generating {self.style} visualization...")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)
        duration = float(librosa.get_duration(y=y, sr=sr))
        sr_int = int(sr)  # Ensure sr is int for type checking

        # Generate frames based on style
        if self.style == "waveform":
            frames = self._generate_waveform_frames(y, sr_int, duration)
        elif self.style == "spectrum":
            frames = self._generate_spectrum_frames(y, sr_int, duration)
        elif self.style == "circular":
            frames = self._generate_circular_frames(y, sr_int, duration)
        elif self.style == "particles":
            frames = self._generate_particle_frames(y, sr_int, duration)
        else:
            # Default to waveform
            frames = self._generate_waveform_frames(y, sr_int, duration)

        # Save frames and create video
        video_path = self._frames_to_video(frames, audio_path, output_path)

        print(f"✓ Visualization generated: {output_path}")
        return video_path

    def _generate_waveform_frames(self, y: np.ndarray, sr: int, duration: float) -> list:
        """Generate waveform visualization frames"""
        num_frames = int(duration * self.fps)
        frames = []

        samples_per_frame = len(y) // num_frames
        width, height = self.resolution

        for i in range(num_frames):
            # Create frame
            img = Image.new("RGB", (width, height), tuple(self.background_color))
            draw = ImageDraw.Draw(img)

            # Get audio chunk for this frame
            start_idx = i * samples_per_frame
            end_idx = start_idx + samples_per_frame
            chunk = y[start_idx:end_idx]

            # Calculate amplitude
            amplitude = np.abs(chunk).mean() * self.sensitivity

            # Draw multiple waveform layers with color gradient
            num_waves = 5
            for wave_idx in range(num_waves):
                points = []
                wave_samples = 200  # Points across the width

                for x_idx in range(wave_samples):
                    x = int(x_idx * width / wave_samples)

                    # Sample audio at this x position
                    sample_idx = int((x_idx / wave_samples) * len(chunk))
                    if sample_idx < len(chunk):
                        sample = chunk[sample_idx]
                    else:
                        sample = 0

                    # Calculate y position with wave effect
                    # Position at bottom of screen (80% down from top)
                    wave_offset = wave_idx * 20
                    y_center = int(height * 0.85) - wave_offset  # Bottom positioning
                    # Increase amplitude significantly (3x more dramatic)
                    y_amplitude = sample * 600 * amplitude * (1 + wave_idx * 0.4)
                    y_pos = int(y_center - abs(y_amplitude))  # Waves go UP from bottom

                    points.append((x, y_pos))

                # Interpolate color between primary and secondary
                t = wave_idx / num_waves
                color = self._interpolate_color(self.primary_color, self.secondary_color, t)

                # Draw wave with glow effect
                if len(points) > 1:
                    draw.line(points, fill=tuple(color), width=3)

            # Add glow effect
            img = img.filter(ImageFilter.GaussianBlur(self.blur))

            frames.append(np.array(img))

        return frames

    def _generate_spectrum_frames(self, y: np.ndarray, sr: int, duration: float) -> list:
        """Generate spectrum analyzer (frequency bars) visualization"""
        num_frames = int(duration * self.fps)
        frames = []

        # Compute spectrogram
        hop_length = len(y) // num_frames
        D = np.abs(librosa.stft(y, hop_length=hop_length))

        width, height = self.resolution
        num_bars = 64  # Number of frequency bars
        bar_width = width // num_bars

        for frame_idx in range(min(num_frames, D.shape[1])):
            # Create frame
            img = Image.new("RGB", (width, height), tuple(self.background_color))
            draw = ImageDraw.Draw(img)

            # Get spectrum for this frame
            spectrum = D[:, frame_idx]

            # Bin into bar groups
            bins = np.array_split(spectrum, num_bars)
            bar_heights = [np.mean(b) for b in bins]

            # Normalize
            max_height = max(bar_heights) if max(bar_heights) > 0 else 1
            bar_heights = [h / max_height for h in bar_heights]

            # Draw bars
            for bar_idx, bar_height in enumerate(bar_heights):
                x = bar_idx * bar_width
                bar_h = int(bar_height * height * 0.8 * self.sensitivity)
                y = height - bar_h

                # Color gradient based on position
                t = bar_idx / num_bars
                color = self._interpolate_color(self.primary_color, self.secondary_color, t)

                # Draw bar with gradient
                for h in range(bar_h):
                    y_pos = height - h
                    alpha = h / bar_h if bar_h > 0 else 1
                    bar_color = tuple([int(c * alpha) for c in color])
                    draw.rectangle([x + 2, y_pos, x + bar_width - 2, y_pos + 1], fill=bar_color)

            # Add glow
            img = img.filter(ImageFilter.GaussianBlur(self.blur))

            frames.append(np.array(img))

        return frames

    def _generate_circular_frames(self, y: np.ndarray, sr: int, duration: float) -> list:
        """Generate circular/radial visualization"""
        num_frames = int(duration * self.fps)
        frames = []

        samples_per_frame = len(y) // num_frames
        width, height = self.resolution
        center_x, center_y = width // 2, height // 2

        for i in range(num_frames):
            # Create frame
            img = Image.new("RGB", (width, height), tuple(self.background_color))
            draw = ImageDraw.Draw(img)

            # Get audio chunk
            start_idx = i * samples_per_frame
            end_idx = start_idx + samples_per_frame
            chunk = y[start_idx:end_idx]

            # Calculate amplitude
            amplitude = np.abs(chunk).mean() * self.sensitivity

            # Draw concentric circles
            num_circles = 8
            base_radius = 100

            for circle_idx in range(num_circles):
                radius = int(base_radius + circle_idx * 50 + amplitude * 300)

                # Color gradient
                t = circle_idx / num_circles
                color = self._interpolate_color(self.primary_color, self.secondary_color, t)
                _alpha = int(255 * (1 - t))  # Reserved for future transparency support

                # Draw circle
                bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
                draw.ellipse(bbox, outline=tuple(color), width=3)

            # Draw radial lines based on frequency
            num_lines = 32
            for line_idx in range(num_lines):
                angle = (line_idx / num_lines) * 2 * np.pi

                # Sample amplitude for this angle
                sample_idx = int((line_idx / num_lines) * len(chunk))
                if sample_idx < len(chunk):
                    line_amplitude = abs(chunk[sample_idx]) * self.sensitivity
                else:
                    line_amplitude = 0

                # Calculate line endpoints
                inner_radius = 50
                outer_radius = int(150 + line_amplitude * 400)

                x1 = int(center_x + inner_radius * np.cos(angle))
                y1 = int(center_y + inner_radius * np.sin(angle))
                x2 = int(center_x + outer_radius * np.cos(angle))
                y2 = int(center_y + outer_radius * np.sin(angle))

                # Color based on position
                t = line_idx / num_lines
                color = self._interpolate_color(self.primary_color, self.secondary_color, t)

                draw.line([x1, y1, x2, y2], fill=tuple(color), width=2)

            # Add glow
            img = img.filter(ImageFilter.GaussianBlur(self.blur))

            frames.append(np.array(img))

        return frames

    def _generate_particle_frames(self, y: np.ndarray, sr: int, duration: float) -> list:
        """Generate particle-based visualization"""
        num_frames = int(duration * self.fps)
        frames = []

        samples_per_frame = len(y) // num_frames
        width, height = self.resolution

        # Initialize particles
        num_particles = 200
        particles = []
        for _ in range(num_particles):
            particles.append(
                {
                    "x": np.random.rand() * width,
                    "y": np.random.rand() * height,
                    "vx": (np.random.rand() - 0.5) * 5,
                    "vy": (np.random.rand() - 0.5) * 5,
                    "size": np.random.rand() * 5 + 2,
                }
            )

        for i in range(num_frames):
            # Create frame
            img = Image.new("RGB", (width, height), tuple(self.background_color))
            draw = ImageDraw.Draw(img)

            # Get audio chunk
            start_idx = i * samples_per_frame
            end_idx = start_idx + samples_per_frame
            chunk = y[start_idx:end_idx]
            amplitude = np.abs(chunk).mean() * self.sensitivity

            # Update and draw particles
            for idx, particle in enumerate(particles):
                # Update position
                particle["x"] += particle["vx"] * (1 + amplitude * 5)
                particle["y"] += particle["vy"] * (1 + amplitude * 5)

                # Wrap around edges
                if particle["x"] < 0:
                    particle["x"] = width
                elif particle["x"] > width:
                    particle["x"] = 0
                if particle["y"] < 0:
                    particle["y"] = height
                elif particle["y"] > height:
                    particle["y"] = 0

                # Color based on position
                t = idx / num_particles
                color = self._interpolate_color(self.primary_color, self.secondary_color, t)

                # Draw particle
                size = int(particle["size"] * (1 + amplitude * 3))
                bbox = [
                    int(particle["x"] - size),
                    int(particle["y"] - size),
                    int(particle["x"] + size),
                    int(particle["y"] + size),
                ]
                draw.ellipse(bbox, fill=tuple(color))

            # Add glow
            img = img.filter(ImageFilter.GaussianBlur(self.blur))

            frames.append(np.array(img))

        return frames

    def _interpolate_color(self, color1: list, color2: list, t: float) -> list:
        """Interpolate between two colors"""
        return [int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3)]

    def _frames_to_video(self, frames: list, audio_path: Path, output_path: Path) -> Path:
        """Convert frames to video with audio"""
        from moviepy.editor import AudioFileClip, ImageSequenceClip

        # Create video from frames
        video_clip = ImageSequenceClip(frames, fps=self.fps)

        # Add audio
        audio_clip = AudioFileClip(str(audio_path))
        video_clip = video_clip.set_audio(audio_clip)

        # Write video
        video_clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            bitrate="2000k",
            logger=None,  # Suppress moviepy output
        )

        return output_path
