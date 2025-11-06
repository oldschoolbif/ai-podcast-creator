"""
Audio Visualizer - Generate vibrant backgrounds that react to voice
"""

from pathlib import Path
import subprocess

import librosa
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# OpenCV for smooth, anti-aliased line drawing (fixes graininess)
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("[WARN] OpenCV not available - using PIL for waveform (may have graininess)")

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
        
        # Waveform configuration (NEW - comprehensive controls)
        self.waveform_config = self.viz_config.get("waveform", {})
        self.render_scale = self.waveform_config.get("render_scale", 2.0)  # 2x render for smoothness
        self.anti_alias = self.waveform_config.get("anti_alias", True)
        self.num_lines = max(1, min(10, self.waveform_config.get("num_lines", 1)))  # 1-10 lines
        self.line_thickness = self.waveform_config.get("line_thickness", 12)  # Can be array or single number
        self.line_colors = self.waveform_config.get("line_colors", None)  # Array of RGB colors
        self.position = self.waveform_config.get("position", "bottom")  # top, bottom, left, right, middle, or combinations
        self.orientation = self.waveform_config.get("orientation", "auto")  # auto, horizontal, vertical
        self.height_percent = self.waveform_config.get("height_percent", 25)  # For horizontal waveforms
        self.width_percent = self.waveform_config.get("width_percent", 25)  # For vertical waveforms
        # Orientation offset for horizontal waveforms (0=bottom, 100=top)
        self.orientation_offset = self.waveform_config.get("orientation_offset", None)  # 0-100, None = use position
        # Spacing control for multiple vertical waveforms
        self.left_spacing = self.waveform_config.get("left_spacing", 0)  # Pixels from left edge
        self.right_spacing = self.waveform_config.get("right_spacing", 0)  # Pixels from right edge
        # Rotation (degrees, 0 = no rotation)
        self.rotation = self.waveform_config.get("rotation", 0)  # Rotation angle in degrees
        # Amplitude multiplier (beyond sensitivity)
        self.amplitude_multiplier = self.waveform_config.get("amplitude_multiplier", 1.0)  # Multiplier for wave amplitude
        # Multiple instances
        self.num_instances = max(1, self.waveform_config.get("num_instances", 1))  # Number of waveform instances
        self.instances_offset = self.waveform_config.get("instances_offset", 0)  # Spacing between instances (pixels)
        self.instances_intersect = self.waveform_config.get("instances_intersect", False)  # Allow instances to intersect
        # Advanced features
        self.opacity = self.waveform_config.get("opacity", 1.0)  # 0.0-1.0
        self.blend_mode = self.waveform_config.get("blend_mode", "normal")  # normal, screen, add, overlay
        self.waveform_style = self.waveform_config.get("waveform_style", "continuous")  # continuous, bars, dots, filled
        self.randomize = self.waveform_config.get("randomize", False)  # Randomize per video
        
        # Initialize randomization if enabled
        if self.randomize:
            import random
            self._randomize_config()
    
    def _randomize_config(self):
        """Randomize waveform configuration per video"""
        import random
        
        # Randomize number of lines (1-5)
        self.num_lines = random.randint(1, 5)
        
        # Randomize line thickness (per-line or single)
        if random.random() < 0.5:
            # Per-line thickness
            self.line_thickness = [random.randint(8, 20) for _ in range(self.num_lines)]
        else:
            # Single thickness
            self.line_thickness = random.randint(8, 20)
        
        # Randomize colors (per-line or single)
        if random.random() < 0.5:
            # Per-line colors (neon palette)
            neon_colors = [
                [0, 255, 0],      # Neon green
                [0, 255, 100],    # Lime green
                [0, 255, 255],    # Cyan
                [255, 0, 255],    # Magenta
                [255, 255, 0],    # Yellow
                [255, 100, 0],    # Orange
            ]
            self.line_colors = [random.choice(neon_colors) for _ in range(self.num_lines)]
        else:
            # Single color
            neon_colors = [
                [0, 255, 0],      # Neon green
                [0, 255, 100],    # Lime green
                [0, 255, 255],    # Cyan
                [255, 0, 255],    # Magenta
            ]
            self.primary_color = random.choice(neon_colors)
            self.line_colors = None
        
        # Randomize position
        positions = ["top", "bottom", "left", "right", "middle"]
        if random.random() < 0.3:
            # Multiple positions
            num_positions = random.randint(2, 3)
            selected = random.sample(positions, num_positions)
            self.position = ",".join(selected)
        else:
            # Single position
            self.position = random.choice(positions)
        
        # Randomize height/width percent (10-40%)
        self.height_percent = random.randint(10, 40)
        self.width_percent = random.randint(10, 40)
        
        # Randomize opacity (0.7-1.0)
        self.opacity = random.uniform(0.7, 1.0)
        
        print(f"[WAVEFORM] Randomized config: {self.num_lines} lines, position={self.position}, opacity={self.opacity:.2f}")

    def generate_visualization(self, audio_path: Path, output_path: Path) -> Path:
        """
        Generate video with audio-reactive visualization (STREAMING - memory efficient)
        
        Uses chunked audio loading to minimize RAM usage - only loads small chunks
        of audio at a time instead of the entire file.

        Args:
            audio_path: Path to audio file
            output_path: Path for output video

        Returns:
            Path to generated video
        """
        print(f"[VIZ] Generating {self.style} visualization (streaming mode)...")

        # Get duration using FFmpeg (safer than librosa which can crash with C extensions)
        duration = self._get_audio_duration_ffmpeg(audio_path)
        if duration is None:
            # Fallback: use default duration if FFmpeg fails
            duration = 10.0
        
        # Get sample rate from a small sample (only need it for frame generation)
        y_sample, sr = librosa.load(str(audio_path), sr=None, duration=0.1, offset=0.0)
        sr_int = int(sr)
        del y_sample  # Free sample immediately

        # Generate frames as generator based on style (streaming - no memory accumulation)
        # Pass audio_path instead of loaded array for chunked processing
        if self.style == "waveform":
            frame_generator = self._generate_waveform_frames_streaming_chunked(audio_path, sr_int, duration)
        elif self.style == "spectrum":
            # Spectrum needs full audio for STFT, but we'll use a streaming approach
            frame_generator = self._generate_spectrum_frames_streaming_chunked(audio_path, sr_int, duration)
        elif self.style == "circular":
            frame_generator = self._generate_circular_frames_streaming_chunked(audio_path, sr_int, duration)
        elif self.style == "particles":
            frame_generator = self._generate_particle_frames_streaming_chunked(audio_path, sr_int, duration)
        else:
            # Default to waveform
            frame_generator = self._generate_waveform_frames_streaming_chunked(audio_path, sr_int, duration)

        # Stream frames directly to FFmpeg (no memory accumulation)
        video_path = self._stream_frames_to_video(frame_generator, audio_path, output_path, duration)

        print(f"[OK] Visualization generated: {output_path}")
        return video_path

    def _generate_waveform_frames_streaming(self, y: np.ndarray, sr: int, duration: float):
        """Generate waveform visualization frames as a generator (DEPRECATED - use chunked version)"""
        # This method kept for backward compatibility but should use chunked version
        return self._generate_waveform_frames_streaming_chunked_from_array(y, sr, duration)
    
    def _generate_waveform_frames_streaming_chunked(self, audio_path: Path, sr: int, duration: float):
        """Generate waveform frames using chunked audio loading (RAM efficient - only loads small chunks)"""
        num_frames = int(duration * self.fps)
        width, height = self.resolution
        frame_duration = 1.0 / self.fps  # Duration of each frame in seconds
        
        # Load audio in small chunks (1 frame at a time + small overlap for smooth transitions)
        chunk_overlap = 0.05  # 50ms overlap for smooth transitions
        chunk_duration = frame_duration + chunk_overlap
        
        print(f"  [INFO] Generating {num_frames} waveform frames (chunked loading)...")

        for i in range(num_frames):
            # Progress reporting every 100 frames
            if i > 0 and i % 100 == 0:
                print(f"  [INFO] Generated {i}/{num_frames} frames...", end='\r')
            
            # Calculate time offset for this frame
            frame_time = i * frame_duration
            offset = max(0.0, frame_time - chunk_overlap / 2)
            
            # Load only the chunk needed for this frame (memory efficient!)
            try:
                chunk, _ = librosa.load(
                    str(audio_path),
                    sr=sr,
                    offset=offset,
                    duration=chunk_duration
                )
            except Exception as e:
                # If loading fails (e.g., end of file), use silence
                chunk = np.zeros(int(chunk_duration * sr), dtype=np.float32)
            
            # Calculate amplitude - use peak amplitude for maximum visibility
            chunk_abs = np.abs(chunk)
            if len(chunk_abs) > 0:
                # Use peak amplitude with high boost for very visible waveforms
                peak_amp = chunk_abs.max()
                rms = np.sqrt(np.mean(chunk**2))
                # Calculate amplitude - use sensitivity and multiplier directly without excessive boost
                # This allows amplitude_multiplier to have fine-grained control without clipping
                amplitude = (peak_amp * 0.8 + rms * 0.2) * self.sensitivity * self.amplitude_multiplier
            else:
                amplitude = 0.0

            # Determine positions to render (support multiple positions)
            positions = [p.strip() for p in str(self.position).split(",")]
            
            # Render at 2x scale for smoothness (then scale down)
            render_width = int(width * self.render_scale)
            render_height = int(height * self.render_scale)
            base_thickness = self.line_thickness if isinstance(self.line_thickness, (int, float)) else self.line_thickness[0] if isinstance(self.line_thickness, (list, tuple)) and len(self.line_thickness) > 0 else 12
            render_thickness = int(base_thickness * self.render_scale)
            
            # Create frame at 2x resolution with BLACK background (will be chromakeyed transparent)
            if OPENCV_AVAILABLE and self.anti_alias:
                # Use OpenCV for smooth, anti-aliased rendering
                frame = np.zeros((render_height, render_width, 3), dtype=np.uint8)  # Black background
                
                # Render waveforms at each position
                for pos in positions:
                    self._draw_waveform_opencv(frame, chunk, amplitude, render_width, render_height, pos, render_thickness)
                
                # Scale down from 2x resolution to target resolution (smooths pixelation)
                frame_scaled = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LANCZOS4)
                yield frame_scaled
            else:
                # Fallback to PIL (original method)
                img = Image.new("RGB", (render_width, render_height), (0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                for pos in positions:
                    self._draw_waveform_pil(draw, chunk, amplitude, render_width, render_height, pos, render_thickness)
                
                # Scale down from 2x resolution to target resolution
                img_scaled = img.resize((width, height), Image.Resampling.LANCZOS)
                yield np.array(img_scaled)
            
            # Free chunk memory immediately
            del chunk
    
    def _generate_waveform_frames_streaming_chunked_from_array(self, y: np.ndarray, sr: int, duration: float):
        """Generate waveform frames from array with OpenCV for smooth, anti-aliased rendering (FIXES GRAININESS)"""
        num_frames = int(duration * self.fps)
        samples_per_frame = len(y) // num_frames
        width, height = self.resolution
        
        # Render at 2x scale for smoothness (then scale down)
        render_width = int(width * self.render_scale)
        render_height = int(height * self.render_scale)
        base_thickness = self.line_thickness if isinstance(self.line_thickness, (int, float)) else self.line_thickness[0]
        # Make base thickness thicker for better visibility (minimum 20 pixels)
        base_thickness = max(20, base_thickness)
        render_thickness = int(base_thickness * self.render_scale)
        
        print(f"  [INFO] Generating {num_frames} waveform frames (rendering at {render_width}x{render_height} for smoothness)...")

        for i in range(num_frames):
            # Progress reporting every 100 frames
            if i > 0 and i % 100 == 0:
                print(f"  [INFO] Generated {i}/{num_frames} frames...", end='\r')
            
            # Get audio chunk for this frame
            start_idx = i * samples_per_frame
            end_idx = start_idx + samples_per_frame
            chunk = y[start_idx:end_idx]

            # Calculate amplitude - use peak amplitude for maximum visibility
            chunk_abs = np.abs(chunk)
            if len(chunk_abs) > 0:
                # Use peak amplitude with high boost for very visible waveforms
                peak_amp = chunk_abs.max()
                rms = np.sqrt(np.mean(chunk**2))
                # Calculate amplitude - use sensitivity and multiplier directly without excessive boost
                # This allows amplitude_multiplier to have fine-grained control without clipping
                amplitude = (peak_amp * 0.8 + rms * 0.2) * self.sensitivity * self.amplitude_multiplier  # Apply amplitude multiplier
            else:
                amplitude = 0.0

            # Determine positions to render (support multiple positions)
            positions = [p.strip() for p in str(self.position).split(",")]
            
            # Create frame at 2x resolution with BLACK background (will be chromakeyed transparent)
            if OPENCV_AVAILABLE and self.anti_alias:
                # Use OpenCV for smooth, anti-aliased rendering
                frame = np.zeros((render_height, render_width, 3), dtype=np.uint8)  # Black background
                
                # Render waveforms at each position
                for pos in positions:
                    self._draw_waveform_opencv(frame, chunk, amplitude, render_width, render_height, pos, render_thickness)
                
                # Scale down from 2x resolution to target resolution (smooths pixelation)
                frame_scaled = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LANCZOS4)
                yield frame_scaled
            else:
                # Fallback to PIL (original method)
                img = Image.new("RGB", (render_width, render_height), (0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                for pos in positions:
                    self._draw_waveform_pil(draw, chunk, amplitude, render_width, render_height, pos, render_thickness)
                
                # Scale down from 2x resolution to target resolution
                img_scaled = img.resize((width, height), Image.Resampling.LANCZOS)
                yield np.array(img_scaled)
    
    def _rotate_points(self, points: list, center: tuple, angle_degrees: float) -> list:
        """Rotate points around a center point by angle in degrees"""
        if angle_degrees == 0:
            return points
        
        import math
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        cx, cy = center
        
        rotated = []
        for x, y in points:
            # Translate to origin
            dx = x - cx
            dy = y - cy
            # Rotate
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a
            # Translate back
            rotated.append((int(rx + cx), int(ry + cy)))
        return rotated
    
    def _draw_waveform_opencv(self, frame: np.ndarray, chunk: np.ndarray, amplitude: float, 
                               width: int, height: int, position: str, base_thickness: int):
        """Draw waveform using OpenCV with support for multiple lines, instances, rotation, and orientation offset"""
        # Parse position and determine orientation
        orientation = self._get_orientation(position)
        
        # Calculate waveform region based on position
        if orientation == "horizontal":
            # Horizontal waveform
            region_height = int(height * (self.height_percent / 100))
            
            # Calculate region_y based on orientation_offset if provided, otherwise use position
            if self.orientation_offset is not None:
                # 0 = bottom, 100 = top
                offset_normalized = max(0.0, min(100.0, float(self.orientation_offset))) / 100.0
                region_y = int((height - region_height) * (1.0 - offset_normalized))
            else:
                # Use position-based calculation
                if position == "top":
                    region_y = 0
                elif position == "bottom":
                    region_y = height - region_height
                elif position == "middle":
                    region_y = (height - region_height) // 2
                else:
                    region_y = height - region_height  # Default to bottom
        else:
            # Vertical waveform (for left/right positions)
            region_width = int(width * (self.width_percent / 100))
            if position == "left":
                region_x = int(self.left_spacing * self.render_scale)
            elif position == "right":
                region_x = width - region_width - int(self.right_spacing * self.render_scale)
            else:
                region_x = 0  # Default to left
        
        # Draw multiple instances
        for instance_idx in range(self.num_instances):
            # Calculate instance offset
            instance_offset_x = instance_idx * self.instances_offset if orientation == "horizontal" else 0
            instance_offset_y = instance_idx * self.instances_offset if orientation == "vertical" else 0
            
            # Draw multiple lines
            for line_idx in range(self.num_lines):
                # Get line-specific color
                if self.line_colors and line_idx < len(self.line_colors):
                    line_color = self.line_colors[line_idx]
                else:
                    line_color = self.primary_color
                color = tuple([int(c * self.opacity) for c in line_color])
                
                # Get line-specific thickness
                if isinstance(self.line_thickness, (list, tuple)) and line_idx < len(self.line_thickness):
                    line_thickness_val = self.line_thickness[line_idx]
                else:
                    line_thickness_val = self.line_thickness if isinstance(self.line_thickness, (int, float)) else base_thickness
                line_thickness_val = max(1, int(line_thickness_val * self.render_scale))
                
                # Calculate line spacing for multiple lines
                if orientation == "horizontal":
                    line_spacing = (region_height * 0.9) / max(1, self.num_lines) if self.num_lines > 1 else 0
                    line_y_offset = line_idx * line_spacing - (self.num_lines - 1) * line_spacing / 2
                else:
                    line_spacing = (region_width * 0.9) / max(1, self.num_lines) if self.num_lines > 1 else 0
                    line_x_offset = line_idx * line_spacing - (self.num_lines - 1) * line_spacing / 2
                
                # Generate waveform points
                if orientation == "horizontal":
                    # Sample at reduced resolution and upsample for smoother curves
                    # Too many points can create jagged vertical segments
                    wave_samples = min(width, 500)  # Max 500 points for smoothness
                    raw_samples = []
                    # Determine if waveform should emanate from top (downward), center (both ways), or bottom (upward)
                    # If orientation_offset is exactly 50 (middle), center the waveform
                    # If > 50, emanate from top downward; if < 50, emanate from bottom upward
                    offset_normalized = max(0.0, min(100.0, float(self.orientation_offset if self.orientation_offset is not None else 0))) / 100.0
                    
                    if abs(offset_normalized - 0.5) < 0.01:  # Exactly middle (within 1%)
                        # Center the waveform - use dynamic baseline based on amplitude range
                        is_centered = True
                        # Will calculate y_base after we have raw_samples
                    elif offset_normalized > 0.5:
                        # Top: emanate downward
                        y_base = region_y  # Top of region - peaks extend downward
                        is_centered = False
                    else:
                        # Bottom: emanate upward
                        y_base = region_y + region_height - 1  # Bottom of region - peaks extend upward
                        is_centered = False
                    
                    # First pass: sample audio at reduced resolution
                    for idx in range(wave_samples):
                        # Map index to audio sample
                        audio_idx = int((idx / wave_samples) * len(chunk))
                        
                        # Use wider window for smoother averaging
                        window_size = max(10, len(chunk) // (wave_samples * 2))
                        sample_start = max(0, audio_idx - window_size)
                        sample_end = min(len(chunk), audio_idx + window_size)
                        
                        if sample_end > sample_start:
                            # Use RMS for smoother representation
                            sample_rms = np.sqrt(np.mean(chunk[sample_start:sample_end]**2))
                            sample_value = sample_rms
                        else:
                            sample_value = 0.0
                        
                        raw_samples.append(sample_value)
                    
                    # For centered waveforms, calculate dynamic baseline based on amplitude range
                    if is_centered and len(raw_samples) > 0:
                        # Calculate amplitude middle point: (max + min) / 2
                        max_amp = max(raw_samples)
                        min_amp = min(raw_samples)
                        amplitude_middle = (max_amp + min_amp) / 2.0
                        video_center = height // 2
                        
                        # Convert amplitude middle to pixel position (assuming max amplitude = full height)
                        # This is a normalized position where 1.0 = full height
                        amplitude_middle_normalized = amplitude_middle
                        # Scale to pixel space: if amplitude_middle is 0.5, that's middle of video height
                        amplitude_middle_pixel = amplitude_middle_normalized * height
                        
                        # If amplitude middle is greater than video center, use bottom as baseline
                        # Otherwise, use top as baseline (inverted)
                        if amplitude_middle_pixel > video_center:
                            # Use bottom as baseline, waveform extends upward
                            y_base = height - 1  # Bottom of video
                        else:
                            # Use top as baseline, waveform extends downward (inverted)
                            y_base = 0  # Top of video
                    elif is_centered:
                        # Fallback if no samples
                        y_base = height // 2
                    
                    # Apply multiple passes of smoothing to prevent vertical bars
                    if len(raw_samples) > 3:
                        # First pass: wider smoothing
                        window_size = min(25, len(raw_samples) // 5)
                        if window_size > 1:
                            kernel = np.ones(window_size) / window_size
                            padded = np.pad(raw_samples, (window_size//2, window_size//2), mode='edge')
                            smoothed = np.convolve(padded, kernel, mode='valid')
                            raw_samples = smoothed.tolist()
                        
                        # Second pass: tighter smoothing for extra smoothness
                        window_size = min(15, len(raw_samples) // 10)
                        if window_size > 1:
                            kernel = np.ones(window_size) / window_size
                            padded = np.pad(raw_samples, (window_size//2, window_size//2), mode='edge')
                            smoothed = np.convolve(padded, kernel, mode='valid')
                            raw_samples = smoothed.tolist()
                    
                    # Use fixed reference level instead of normalizing to chunk peak
                    # This prevents everything from hitting the ceiling
                    # RMS values are typically 0-1 range, so use a fixed reference that allows natural dynamics
                    fixed_reference = 0.5  # Fixed reference level (typical RMS is much lower than peak)
                    
                    # Generate points at reduced resolution, then interpolate to full width
                    base_points = []
                    for idx in range(wave_samples):
                        sample_value = raw_samples[idx]
                        
                        # Normalize against fixed reference, not chunk peak
                        # This preserves natural dynamics - only truly loud sounds hit the top
                        if fixed_reference > 0:
                            # Divide by fixed reference to get relative amplitude
                            sample_normalized = sample_value / fixed_reference
                            # Clamp to reasonable range (0-2) before applying curve
                            sample_normalized = min(2.0, max(0.0, sample_normalized))
                        else:
                            sample_normalized = 0.0
                        
                        # Apply amplitude_multiplier FIRST to scale the input signal
                        # This allows fine control: 0.05 = 5% of max, 1.0 = 100%, 3.0 = 300% (will be compressed)
                        scaled_normalized = sample_normalized * self.amplitude_multiplier
                        
                        # Apply power curve to compress high values while preserving low values
                        # This ensures only the loudest peaks reach maximum height
                        # The power curve acts as a soft limiter for high multipliers
                        if scaled_normalized > 0:
                            # Use a more aggressive power curve to prevent ceiling clipping
                            # For values <= 1.0: linear scaling (preserves fine detail)
                            # For values > 1.0: aggressive compression (prevents clipping)
                            if scaled_normalized <= 1.0:
                                # Linear scaling for low values (preserves fine detail)
                                base_scale = scaled_normalized
                            else:
                                # Compressive curve for high values: 1.0 + log(overflow) scaled
                                # At 2.0 -> ~1.3, at 3.0 -> ~1.45, at 4.0 -> ~1.55, at 6.0 -> ~1.65
                                # This ensures even high multipliers don't all hit the ceiling
                                overflow = scaled_normalized - 1.0
                                # Use logarithmic compression: log(1 + overflow) / log(max_expected)
                                # max_expected is about 6.0 (3.0 multiplier * 2.0 max normalized)
                                base_scale = 1.0 + (np.log(1.0 + overflow) / np.log(7.0)) * 0.65
                            scaled_sample = base_scale
                        else:
                            scaled_sample = 0.0
                        
                        # Cap at full height - this ensures only extreme peaks reach maximum
                        scaled_sample = min(1.0, max(0.0, scaled_sample))
                        
                        # Calculate y position
                        # For centered waveforms, use full region height (single line, not symmetric)
                        # For non-centered, use full region height
                        max_offset = region_height - 1
                        
                        y_offset = int(scaled_sample * max_offset)
                        y_offset = min(y_offset, max_offset)
                        
                        # For top position: peaks extend downward (y_base + y_offset)
                        # For bottom position: peaks extend upward (y_base - y_offset)
                        # For middle position: single line, direction based on dynamic baseline
                        if is_centered:
                            # Center waveform: single line, direction based on baseline position
                            # If y_base is at top (0), extend downward; if at bottom (height-1), extend upward
                            if y_base == 0:
                                # Top baseline: extend downward
                                y = y_base + y_offset + instance_offset_y
                            else:
                                # Bottom baseline: extend upward
                                y = y_base - y_offset + instance_offset_y
                            y = max(0, min(height - 1, int(y)))
                            y_bottom_mirrored = None
                        elif offset_normalized > 0.5:
                            # Top: peaks extend downward
                            y = y_base + y_offset + instance_offset_y
                            y = max(y_base, min(region_y + region_height - 1, int(y)))
                            y_bottom_mirrored = None
                        else:
                            # Bottom: peaks extend upward
                            y = y_base - y_offset + instance_offset_y
                            y = max(region_y, min(y_base, int(y)))
                            y_bottom_mirrored = None
                        
                        # X position at reduced resolution
                        x = int((idx / (wave_samples - 1)) * (width - 1)) + instance_offset_x
                        x = max(0, min(width - 1, x))
                        
                        # Store point (single line, no mirroring)
                        base_points.append((x, y))
                    
                    # Interpolate to full width for smooth horizontal line
                    if len(base_points) > 1:
                        points = []
                        for x_idx in range(width):
                            x_target = x_idx + instance_offset_x
                            x_target = max(0, min(width - 1, x_target))
                            
                            # Find surrounding base points
                            if x_target <= base_points[0][0]:
                                y = base_points[0][1]
                            elif x_target >= base_points[-1][0]:
                                y = base_points[-1][1]
                            else:
                                # Linear interpolation between base points
                                for i in range(len(base_points) - 1):
                                    x1 = base_points[i][0]
                                    y1 = base_points[i][1]
                                    x2 = base_points[i + 1][0]
                                    y2 = base_points[i + 1][1]
                                    
                                    if x1 <= x_target <= x2:
                                        # Interpolate
                                        if x2 != x1:
                                            t = (x_target - x1) / (x2 - x1)
                                            y = int(y1 + (y2 - y1) * t)
                                        else:
                                            y = y1
                                        break
                                else:
                                    y = base_points[-1][1]
                            
                            points.append((x_target, y))
                    else:
                        points = [(base_points[0][0], base_points[0][1])]
                    
                    # Apply rotation if needed
                    if self.rotation != 0:
                        center_x = width // 2
                        # For centered waveforms, use center of full video height
                        # For others, use center of region
                        if is_centered:
                            center_y = height // 2
                        else:
                            center_y = region_y + (region_height // 2)
                        points = self._rotate_points(points, (center_x, center_y), self.rotation)
                    
                    # Draw waveform as connected horizontal line (single line for all waveforms)
                    if len(points) > 1:
                        # Ensure points are sorted by X coordinate
                        points = sorted(points, key=lambda p: p[0])
                        
                        # Draw line connecting consecutive points horizontally
                        thickness = max(1, line_thickness_val)
                        for i in range(len(points) - 1):
                            x1, y1 = points[i]
                            x2, y2 = points[i + 1]
                            
                            # Clamp coordinates
                            x1 = max(0, min(width - 1, int(x1)))
                            y1 = max(0, min(height - 1, int(y1)))
                            x2 = max(0, min(width - 1, int(x2)))
                            y2 = max(0, min(height - 1, int(y2)))
                            
                            # Only draw if points are close in X (horizontal connection)
                            if abs(x2 - x1) <= 2:  # Adjacent or very close pixels
                                cv2.line(frame, (x1, y1), (x2, y2), color, thickness, lineType=cv2.LINE_AA)
                            else:
                                # For larger gaps, interpolate intermediate points
                                steps = abs(x2 - x1)
                                for step in range(steps):
                                    t = step / max(1, steps)
                                    x = int(x1 + (x2 - x1) * t)
                                    y = int(y1 + (y2 - y1) * t)
                                    if step < steps - 1:
                                        x_next = int(x1 + (x2 - x1) * ((step + 1) / steps))
                                        y_next = int(y1 + (y2 - y1) * ((step + 1) / steps))
                                        cv2.line(frame, (x, y), (x_next, y_next), color, thickness, lineType=cv2.LINE_AA)
                
                else:
                    # Vertical waveform
                    wave_samples = height
                    points = []
                    x_center = region_x + (region_width // 2) + int(line_x_offset) + instance_offset_x
                    
                    for y_idx in range(wave_samples):
                        y = y_idx + instance_offset_y
                        # Sample audio
                        sample_start = max(0, int((y_idx / wave_samples) * len(chunk)) - 2)
                        sample_end = min(len(chunk), int((y_idx / wave_samples) * len(chunk)) + 2)
                        
                        if sample_end > sample_start:
                            sample_avg = np.abs(chunk[sample_start:sample_end]).mean()
                        else:
                            sample_avg = 0.0
                        
                        # Calculate x position
                        sample_normalized = min(1.0, sample_avg * amplitude)
                        sample_normalized = max(0.1, sample_normalized)  # Minimum 10% width
                        x_offset = int(sample_normalized * (region_width * 0.95))
                        
                        if position == "left":
                            x = x_center + x_offset
                        else:  # right
                            x = x_center - x_offset
                        
                        x = max(region_x + 1, min(region_x + region_width - 2, x))
                        points.append((x, y))
                    
                    # Apply rotation if needed
                    if self.rotation != 0:
                        center_x = region_x + (region_width // 2)
                        center_y = height // 2
                        points = self._rotate_points(points, (center_x, center_y), self.rotation)
                    
                    # Draw waveform
                    if len(points) > 1:
                        valid_points = []
                        for pt in points:
                            x, y = pt
                            x = max(region_x + 1, min(region_x + region_width - 2, x))
                            y = max(0, min(height - 1, y))
                            valid_points.append((x, y))
                        
                        if len(valid_points) > 1:
                            # Draw thin line only (no fill)
                            pts = np.array(valid_points, dtype=np.int32)
                            thickness = max(1, line_thickness_val)
                            cv2.polylines(frame, [pts], isClosed=False, color=color, thickness=thickness, lineType=cv2.LINE_AA)
    
    def _get_orientation(self, position: str) -> str:
        """Determine orientation based on position and config"""
        if self.orientation != "auto":
            return self.orientation
        # Auto-detect: horizontal for top/bottom/middle, vertical for left/right
        if position in ["top", "bottom", "middle"]:
            return "horizontal"
        elif position in ["left", "right"]:
            return "vertical"
        return "horizontal"  # Default
    
    def _draw_waveform_pil(self, draw, chunk: np.ndarray, amplitude: float,
                          width: int, height: int, position: str, base_thickness: int):
        """Fallback: Draw waveform using PIL (original method)"""
        # Simplified PIL version for fallback
        orientation = self._get_orientation(position)
        num_lines = self.num_lines
        
        if orientation == "horizontal":
            region_height = int(height * (self.height_percent / 100))
            if position == "top":
                region_y = 0
            elif position == "bottom":
                region_y = height - region_height
            elif position == "middle":
                region_y = (height - region_height) // 2
            else:
                region_y = height - region_height
            
            for line_idx in range(num_lines):
                points = []
                thickness = base_thickness
                color = tuple(self.primary_color)
                
                for x_idx in range(800):
                    x = int(x_idx * width / 800)
                    sample_idx = int((x_idx / 800) * len(chunk))
                    sample = chunk[sample_idx] if sample_idx < len(chunk) else 0
                    
                    wave_offset = line_idx * (thickness + 5)
                    y_center = region_y + (region_height // 2) - wave_offset
                    y_amplitude = sample * (region_height * 0.3) * amplitude
                    y = int(y_center - abs(y_amplitude))
                    y = max(region_y, min(region_y + region_height - 1, y))
                    points.append((x, y))
                
                if len(points) > 1:
                    draw.line(points, fill=color, width=thickness)

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

            # Yield frame immediately
            yield np.array(img)

    def _generate_spectrum_frames_streaming(self, y: np.ndarray, sr: int, duration: float):
        """Generate spectrum analyzer frames as a generator (streaming - memory efficient)"""
        num_frames = int(duration * self.fps)

        # Compute spectrogram (done once, then we iterate over columns)
        hop_length = len(y) // num_frames
        D = np.abs(librosa.stft(y, hop_length=hop_length))

        width, height = self.resolution
        num_bars = 64
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
            max_height = max(bar_heights) if bar_heights else 1
            bar_heights = [h / max_height for h in bar_heights]

            # Draw bars
            for bar_idx, bar_height in enumerate(bar_heights):
                x = bar_idx * bar_width
                bar_h = int(bar_height * height * 0.8 * self.sensitivity)
                y_pos = height - bar_h

                # Color gradient based on position
                t = bar_idx / num_bars
                color = self._interpolate_color(self.primary_color, self.secondary_color, t)

                # Draw bar with gradient
                for h in range(bar_h):
                    y_pos_draw = height - h
                    alpha = h / bar_h if bar_h > 0 else 1
                    bar_color = tuple([int(c * alpha) for c in color])
                    draw.rectangle([x + 2, y_pos_draw, x + bar_width - 2, y_pos_draw + 1], fill=bar_color)

            # Add glow
            img = img.filter(ImageFilter.GaussianBlur(self.blur))

            # Yield frame immediately
            yield np.array(img)

    def _generate_circular_frames_streaming(self, y: np.ndarray, sr: int, duration: float):
        """Generate circular/radial visualization frames as a generator (streaming - memory efficient)"""
        num_frames = int(duration * self.fps)

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

            # Yield frame immediately
            yield np.array(img)

    def _generate_particle_frames_streaming(self, y: np.ndarray, sr: int, duration: float):
        """Generate particle-based visualization frames as a generator (DEPRECATED - use chunked version)"""
        return self._generate_particle_frames_streaming_chunked_from_array(y, sr, duration)
    
    def _generate_spectrum_frames_streaming_chunked(self, audio_path: Path, sr: int, duration: float):
        """Generate spectrum frames using chunked audio loading (RAM efficient).
        
        Note: Spectrum analysis requires computing STFT on audio chunks.
        We compute STFT on overlapping windows to maintain frequency resolution.
        """
        num_frames = int(duration * self.fps)
        width, height = self.resolution
        frame_duration = 1.0 / self.fps
        num_bars = 64
        bar_width = width // num_bars
        
        # For spectrum, we need a larger chunk for STFT (frequency analysis)
        # Use 0.5 second chunks with 0.1 second overlap for smooth transitions
        chunk_duration = 0.5
        chunk_overlap = 0.1
        
        print(f"  [INFO] Generating {num_frames} spectrum frames (chunked loading)...")
        
        # Track global max for normalization across chunks
        global_max_amplitude = 0.0
        
        for i in range(num_frames):
            frame_time = i * frame_duration
            offset = max(0.0, frame_time - chunk_overlap / 2)
            
            # Load chunk for this frame
            try:
                chunk, _ = librosa.load(
                    str(audio_path),
                    sr=sr,
                    offset=offset,
                    duration=chunk_duration
                )
            except Exception:
                chunk = np.zeros(int(chunk_duration * sr), dtype=np.float32)
            
            # Compute STFT for this chunk
            hop_length = len(chunk) // 32  # Use smaller hop for chunk
            if len(chunk) > hop_length:
                D = np.abs(librosa.stft(chunk, hop_length=max(hop_length, 1)))
                # Use the middle column (most representative of current frame)
                # Handle edge case where STFT returns empty result
                if D.shape[1] == 0:
                    # No time frames in STFT, use magnitude of chunk directly
                    spectrum = np.abs(chunk)
                else:
                    mid_col = D.shape[1] // 2
                    spectrum = D[:, mid_col]
            else:
                spectrum = np.abs(chunk)
            
            # Update global max for normalization
            if len(spectrum) > 0:
                global_max_amplitude = max(global_max_amplitude, np.max(spectrum))
            
            # Create frame
            img = Image.new("RGB", (width, height), tuple(self.background_color))
            draw = ImageDraw.Draw(img)
            
            # Bin spectrum into bars
            if len(spectrum) == 0:
                # Empty spectrum - use zero bars
                bar_heights = [0.0] * num_bars
            elif len(spectrum) >= num_bars:
                bins = np.array_split(spectrum[:num_bars*10], num_bars)  # Use first part for efficiency
                bar_heights = [np.mean(b) for b in bins]
            else:
                # Spectrum too short - use mean of available data
                mean_val = np.mean(spectrum) if len(spectrum) > 0 else 0.0
                bar_heights = [mean_val] * num_bars
            
            # Normalize using global max
            max_height = global_max_amplitude if global_max_amplitude > 0 else 1
            bar_heights = [h / max_height for h in bar_heights]
            
            # Draw bars
            for bar_idx, bar_height in enumerate(bar_heights):
                x = bar_idx * bar_width
                bar_h = int(bar_height * height * 0.8 * self.sensitivity)
                y_pos = height - bar_h
                
                # Color gradient
                t = bar_idx / num_bars
                color = self._interpolate_color(self.primary_color, self.secondary_color, t)
                
                # Draw bar
                for h in range(bar_h):
                    y_pos_draw = height - h
                    alpha = h / bar_h if bar_h > 0 else 1
                    bar_color = tuple([int(c * alpha) for c in color])
                    draw.rectangle([x + 2, y_pos_draw, x + bar_width - 2, y_pos_draw + 1], fill=bar_color)
            
            # Free chunk memory
            del chunk
            
            # Add glow
            img = img.filter(ImageFilter.GaussianBlur(self.blur))
            
            # Yield frame immediately
            yield np.array(img)
    
    def _generate_circular_frames_streaming_chunked(self, audio_path: Path, sr: int, duration: float):
        """Generate circular frames using chunked audio loading (RAM efficient)"""
        num_frames = int(duration * self.fps)
        width, height = self.resolution
        frame_duration = 1.0 / self.fps
        center_x, center_y = width // 2, height // 2
        
        chunk_overlap = 0.05
        chunk_duration = frame_duration + chunk_overlap
        
        print(f"  [INFO] Generating {num_frames} circular frames (chunked loading)...")
        
        for i in range(num_frames):
            frame_time = i * frame_duration
            offset = max(0.0, frame_time - chunk_overlap / 2)
            
            # Load chunk for this frame
            try:
                chunk, _ = librosa.load(
                    str(audio_path),
                    sr=sr,
                    offset=offset,
                    duration=chunk_duration
                )
            except Exception:
                chunk = np.zeros(int(chunk_duration * sr), dtype=np.float32)
            
            # Create frame
            img = Image.new("RGB", (width, height), tuple(self.background_color))
            draw = ImageDraw.Draw(img)
            
            # Calculate amplitude
            amplitude = np.abs(chunk).mean() * self.sensitivity if len(chunk) > 0 else 0.0
            
            # Draw concentric circles
            num_circles = 8
            base_radius = 100
            
            for circle_idx in range(num_circles):
                radius = int(base_radius + circle_idx * 50 + amplitude * 300)
                
                # Color gradient
                t = circle_idx / num_circles
                color = self._interpolate_color(self.primary_color, self.secondary_color, t)
                
                # Draw circle
                bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
                draw.ellipse(bbox, outline=tuple(color), width=3)
            
            # Draw radial lines
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
            
            # Free chunk memory
            del chunk
            
            # Add glow
            img = img.filter(ImageFilter.GaussianBlur(self.blur))
            
            # Yield frame immediately
            yield np.array(img)
    
    def _generate_particle_frames_streaming_chunked(self, audio_path: Path, sr: int, duration: float):
        """Generate particle frames using chunked audio loading (RAM efficient)"""
        num_frames = int(duration * self.fps)
        width, height = self.resolution
        frame_duration = 1.0 / self.fps
        
        chunk_overlap = 0.05
        chunk_duration = frame_duration + chunk_overlap
        
        # Initialize particles (state maintained across frames)
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
        
        print(f"  [INFO] Generating {num_frames} particle frames (chunked loading)...")
        
        for i in range(num_frames):
            frame_time = i * frame_duration
            offset = max(0.0, frame_time - chunk_overlap / 2)
            
            # Load chunk for this frame
            try:
                chunk, _ = librosa.load(
                    str(audio_path),
                    sr=sr,
                    offset=offset,
                    duration=chunk_duration
                )
            except Exception:
                chunk = np.zeros(int(chunk_duration * sr), dtype=np.float32)
            
            amplitude = np.abs(chunk).mean() * self.sensitivity if len(chunk) > 0 else 0.0
            
            # Create frame
            img = Image.new("RGB", (width, height), tuple(self.background_color))
            draw = ImageDraw.Draw(img)
            
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
            
            # Free chunk memory
            del chunk
            
            # Add glow
            img = img.filter(ImageFilter.GaussianBlur(self.blur))
            
            # Yield frame immediately
            yield np.array(img)
    
    def _generate_particle_frames_streaming_chunked_from_array(self, y: np.ndarray, sr: int, duration: float):
        """Generate particle frames from array (backward compatibility)"""
        num_frames = int(duration * self.fps)
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

            # Yield frame immediately
            yield np.array(img)

    def _interpolate_color(self, color1: list, color2: list, t: float) -> list:
        """Interpolate between two colors"""
        return [int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3)]

    def _cleanup_ffmpeg_process(self, process, timeout=2.0):
        """Properly cleanup FFmpeg process and close all file handles.
        
        This ensures FFmpeg releases file handles to output files, preventing
        "File In Use" errors when trying to delete or overwrite files.
        
        Args:
            process: subprocess.Popen instance
            timeout: Seconds to wait for graceful termination before force kill
        """
        if process is None:
            return
        
        # Close all file handles first (critical for releasing file locks)
        try:
            if hasattr(process, 'stdin') and process.stdin and not process.stdin.closed:
                process.stdin.close()
        except Exception:
            pass
        try:
            if hasattr(process, 'stderr') and process.stderr and not process.stderr.closed:
                process.stderr.close()
        except Exception:
            pass
        try:
            if hasattr(process, 'stdout') and process.stdout and not process.stdout.closed:
                process.stdout.close()
        except Exception:
            pass
        
        # Terminate gracefully first
        if process.poll() is None:  # Process still running
            try:
                process.terminate()
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Force kill if graceful termination fails
                try:
                    process.kill()
                    process.wait(timeout=1.0)
                except Exception:
                    pass
            except Exception:
                # If terminate fails, try kill directly
                try:
                    process.kill()
                    process.wait(timeout=1.0)
                except Exception:
                    pass
    
    def _stream_frames_to_video(self, frame_generator, audio_path: Path, output_path: Path, duration: float) -> Path:
        """Stream frames directly to FFmpeg via pipe (memory efficient - no frame accumulation)."""
        import subprocess
        
        # Ensure output directory exists before writing
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        width, height = self.resolution
        num_frames = int(duration * self.fps)
        
        # Try GPU acceleration first
        try:
            from src.utils.gpu_utils import get_gpu_manager
            gpu_manager = get_gpu_manager()
            
            nvenc_check = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True
            )
            use_nvenc = gpu_manager.gpu_available and "h264_nvenc" in nvenc_check.stdout
            
        except Exception:
            use_nvenc = False
        
        # Build FFmpeg command to read raw video from stdin
        if use_nvenc:
            print("[GPU] Using NVENC for visualization encoding (streaming)")
            cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo",
                "-vcodec", "rawvideo",
                "-s", f"{width}x{height}",
                "-pix_fmt", "rgb24",  # RGB format (black background will be chromakeyed)
                "-r", str(self.fps),
                "-i", "-",  # Read from stdin
                "-i", str(audio_path),
                "-c:v", "h264_nvenc",
                "-preset", "p7",
                "-tune", "1",
                "-rc", "vbr",
                "-cq", "26",
                "-b:v", "3M",
                "-maxrate", "4M",
                "-bufsize", "8M",
                "-g", "30",
                "-keyint_min", "30",
                "-sc_threshold", "0",
                "-c:a", "aac",
                "-b:a", "192k",
                "-ar", "44100",
                "-ac", "2",
                "-pix_fmt", "yuv420p",  # H.264 output (no alpha support, but we'll use chromakey in overlay)
                "-shortest",
                "-f", "mp4",
                "-movflags", "+faststart",
                str(output_path)
            ]
        else:
            print("[CPU] Using libx264 for visualization encoding (streaming)")
            cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo",
                "-vcodec", "rawvideo",
                "-s", f"{width}x{height}",
                "-pix_fmt", "rgb24",  # RGB format (black background will be chromakeyed)
                "-r", str(self.fps),
                "-i", "-",  # Read from stdin
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-profile:v", "baseline",
                "-level", "3.1",
                "-preset", "faster",
                "-tune", "stillimage",
                "-crf", "23",
                "-g", "30",
                "-keyint_min", "30",
                "-sc_threshold", "0",
                "-pix_fmt", "yuv420p",  # H.264 output (no alpha support, but we'll use chromakey in overlay)
                "-c:a", "aac",
                "-b:a", "192k",
                "-ar", "44100",
                "-ac", "2",
                "-shortest",
                "-f", "mp4",
                "-movflags", "+faststart",
                str(output_path)
            ]
        
        # Start file monitoring to detect stalls
        from src.utils.file_monitor import FileMonitor
        monitor = FileMonitor(
            output_path,
            update_callback=lambda size, rate, warning: None,  # Silent during streaming
            check_interval=2.0
        )
        monitor.start()
        
        # Start FFmpeg process with stdin pipe
        # Note: stderr is where FFmpeg outputs progress/errors
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=0  # Unbuffered for immediate feedback
        )
        
        # Start thread to read FFmpeg stderr for errors
        import threading
        ffmpeg_stderr_data = []
        ffmpeg_stderr_done = threading.Event()
        
        def _read_ffmpeg_stderr():
            """Read FFmpeg stderr to detect errors."""
            try:
                for line in iter(process.stderr.readline, b''):
                    if not line:
                        break
                    line_str = line.decode('utf-8', errors='replace').strip()
                    ffmpeg_stderr_data.append(line_str)
                    # Check for critical errors
                    if any(keyword in line_str.lower() for keyword in ['error', 'failed', 'cannot', 'unable']):
                        print(f"  [ERROR] FFmpeg: {line_str}")
            except Exception as e:
                print(f"  [ERROR] Error reading FFmpeg stderr: {e}")
            finally:
                ffmpeg_stderr_done.set()
        
        stderr_thread = threading.Thread(target=_read_ffmpeg_stderr, daemon=True)
        stderr_thread.start()
        
        import time
        start_time = time.time()
        last_file_check = start_time
        last_frame_time = start_time
        last_file_size = 0.0
        max_stall_time = 30.0  # Abort if no progress for 30 seconds
        max_frame_stall_time = 15.0  # Abort if no frame for 15 seconds
        max_total_time = 600.0  # Abort if total time exceeds 10 minutes
        
        try:
            # Stream frames directly to FFmpeg
            frame_count = 0
            print(f"  [INFO] Starting frame streaming (expecting ~{num_frames} frames)...")
            
            # Use timeout wrapper to detect if generator hangs before yielding
            import threading
            from collections import deque
            from src.utils.ram_monitor import RAMMonitor
            
            # Initialize RAM monitor (45GB max, warn at 35GB - accounts for baseline system usage)
            ram_monitor = RAMMonitor(max_ram_gb=45.0, warning_threshold_gb=35.0)
            
            # Bounded queue - max 100 frames in memory (~600MB at 1920x1080)
            # This prevents unbounded memory growth if FFmpeg can't keep up
            MAX_QUEUE_SIZE = 100
            frame_queue = deque(maxlen=MAX_QUEUE_SIZE)  # Use deque with maxlen for automatic bounds
            generator_exception = []
            generator_done = threading.Event()
            queue_full_warnings = 0
            
            def _generator_wrapper():
                """Wrapper to run generator in thread and catch exceptions."""
                nonlocal queue_full_warnings
                generator_start = time.time()
                max_generator_time = 300.0  # 5 minute max for generator
                try:
                    for frame in frame_generator:
                        # Check total generator time
                        if time.time() - generator_start > max_generator_time:
                            raise Exception(f"Frame generator exceeded maximum time ({max_generator_time}s)")
                        
                        # Check if queue is full (backpressure)
                        if len(frame_queue) >= MAX_QUEUE_SIZE:
                            queue_full_warnings += 1
                            if queue_full_warnings <= 3:  # Only warn first 3 times
                                print(f"  [WARN] Frame queue full ({len(frame_queue)} frames). "
                                      f"FFmpeg may be slow. Waiting for space...")
                            # Wait a bit for queue to drain, but don't wait forever
                            wait_count = 0
                            max_wait = 50  # Max 5 seconds waiting for queue space
                            while len(frame_queue) >= MAX_QUEUE_SIZE and wait_count < max_wait:
                                time.sleep(0.1)
                                wait_count += 1
                                # Check RAM before continuing
                                is_over, msg = ram_monitor.check_ram_limit()
                                if is_over:
                                    raise Exception(f"RAM limit exceeded: {msg}")
                            
                            if wait_count >= max_wait:
                                raise Exception(f"Frame queue full for {max_wait * 0.1}s - FFmpeg may be hung")
                            continue
                        
                        frame_queue.append(frame)
                        if generator_done.is_set():
                            break
                except Exception as e:
                    generator_exception.append(e)
                finally:
                    generator_done.set()
            
            # Start generator in separate thread
            gen_thread = threading.Thread(target=_generator_wrapper, daemon=True)
            gen_thread.start()
            
            # Wait for first frame with aggressive timeout (check every 0.5s)
            first_frame_timeout = 5.0
            start_wait = time.time()
            last_ram_check = start_wait
            while len(frame_queue) == 0 and not generator_done.is_set():
                elapsed_wait = time.time() - start_wait
                
                # Check RAM every 2 seconds
                if time.time() - last_ram_check > 2.0:
                    is_over, msg = ram_monitor.check_ram_limit()
                    if is_over:
                        print(f"\n[ERROR] {msg}")
                        try:
                            process.kill()
                        except:
                            pass
                        try:
                            monitor.stop()
                        except:
                            pass
                        raise Exception(msg)
                    elif msg:
                        print(f"  [WARN] {msg}")
                    last_ram_check = time.time()
                
                if elapsed_wait > first_frame_timeout:
                    # No frames after timeout - kill everything
                    print(f"\n[ERROR] Frame generator hung - no frames after {elapsed_wait:.1f}s. Aborting...")
                    self._cleanup_ffmpeg_process(process)
                    try:
                        monitor.stop()
                    except:
                        pass
                    # Check if generator thread is stuck
                    if gen_thread.is_alive():
                        print(f"[ERROR] Generator thread still alive but not producing frames - likely hung in blocking operation")
                    raise Exception(f"Frame generator hung - no frames produced after {first_frame_timeout}s. Thread alive: {gen_thread.is_alive()}")
                
                # Also check file size - if FFmpeg started but file isn't growing, abort faster
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    if file_size == 0 and elapsed_wait > 3.0:
                        # File exists but zero size after 3s - FFmpeg likely hung
                        print(f"\n[ERROR] Output file exists but zero size after {elapsed_wait:.1f}s. FFmpeg may be hung.")
                        self._cleanup_ffmpeg_process(process)
                        try:
                            monitor.stop()
                        except:
                            pass
                        raise Exception(f"FFmpeg output file zero size after {elapsed_wait:.1f}s - process may be hung")
                
                time.sleep(0.5)  # Check every 0.5 seconds
            
            # Check for exceptions
            if generator_exception:
                self._cleanup_ffmpeg_process(process)
                monitor.stop()
                raise Exception(f"Frame generator error: {generator_exception[0]}")
            
            # Process frames from queue with timeout detection
            while not generator_done.is_set() or len(frame_queue) > 0:
                # Wait for next frame with timeout
                if len(frame_queue) == 0:
                    # Wait for frame with aggressive timeout check
                    wait_start = time.time()
                    while len(frame_queue) == 0 and not generator_done.is_set():
                        time.sleep(0.5)  # Check every 0.5 seconds
                        current_time = time.time()
                        time_since_last_frame = current_time - last_frame_time
                        elapsed = current_time - start_time
                        wait_elapsed = current_time - wait_start
                        
                        # Check for total timeout
                        if elapsed > max_total_time:
                            print(f"\n[ERROR] Total timeout exceeded ({elapsed:.1f}s)")
                            self._cleanup_ffmpeg_process(process)
                            try:
                                monitor.stop()
                            except:
                                pass
                            raise Exception(f"FFmpeg streaming exceeded maximum time ({max_total_time}s)")
                        
                        # Check for stall timeout (more aggressive - 10s instead of 15s)
                        if frame_count > 0 and time_since_last_frame > 10.0:
                            print(f"\n[ERROR] Frame generation stalled - no frame for {time_since_last_frame:.1f}s")
                            self._cleanup_ffmpeg_process(process)
                            try:
                                monitor.stop()
                            except:
                                pass
                            raise Exception(f"Frame generation stalled - no frame for {time_since_last_frame:.1f}s (frame {frame_count}/{num_frames})")
                        
                        # Check if file is zero size and we've been waiting
                        if output_path.exists() and wait_elapsed > 5.0:
                            file_size = output_path.stat().st_size
                            if file_size == 0:
                                print(f"\n[ERROR] File zero size after {wait_elapsed:.1f}s wait - aborting")
                                self._cleanup_ffmpeg_process(process)
                                try:
                                    monitor.stop()
                                except:
                                    pass
                                raise Exception(f"Output file zero size after {wait_elapsed:.1f}s - process likely hung")
                    
                    # Generator done, check if any frames left
                    if generator_done.is_set() and len(frame_queue) == 0:
                        break
                
                # Check RAM before processing frame
                if frame_count % 30 == 0:  # Check every 30 frames (~1 second at 30fps)
                    is_over, msg = ram_monitor.check_ram_limit()
                    if is_over:
                        print(f"\n[ERROR] {msg}")
                        self._cleanup_ffmpeg_process(process)
                        try:
                            monitor.stop()
                        except:
                            pass
                        raise Exception(msg)
                    elif msg:
                        print(f"  [WARN] {msg}")
                
                # Get frame from queue (deque uses popleft for FIFO)
                if len(frame_queue) == 0:
                    continue  # Shouldn't happen due to loop logic, but safety check
                frame = frame_queue.popleft()
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Update last frame time
                last_frame_time = current_time
                
                # Check if process is still alive
                if process.poll() is not None:
                    # Process died - wait for stderr to finish reading
                    ffmpeg_stderr_done.wait(timeout=2.0)
                    error_msg = '\n'.join(ffmpeg_stderr_data[-10:]) if ffmpeg_stderr_data else "Process died unexpectedly"
                    monitor.stop()
                    raise Exception(f"FFmpeg process died: {error_msg[:500]}")
                
                # Check for FFmpeg errors in stderr (every 10 frames)
                if frame_count % 10 == 0 and ffmpeg_stderr_data:
                    last_error = ffmpeg_stderr_data[-1]
                    if any(keyword in last_error.lower() for keyword in ['error', 'failed', 'cannot open', 'no such file']):
                        print(f"\n[ERROR] FFmpeg error detected: {last_error}")
                        self._cleanup_ffmpeg_process(process)
                        try:
                            monitor.stop()
                        except:
                            pass
                        raise Exception(f"FFmpeg error: {last_error[:200]}")
                
                # Check for total timeout
                if elapsed > max_total_time:
                    self._cleanup_ffmpeg_process(process)
                    monitor.stop()
                    raise Exception(f"FFmpeg streaming exceeded maximum time ({max_total_time}s)")
                
                # Check for stalls (every 5 seconds)
                if current_time - last_file_check > 5.0:
                    if output_path.exists():
                        current_size = output_path.stat().st_size / (1024 * 1024)  # MB
                        if current_size <= last_file_size + 0.01:  # Less than 0.01 MB growth
                            stall_time = current_time - last_file_check
                            if stall_time > max_stall_time:
                                self._cleanup_ffmpeg_process(process)
                                monitor.stop()
                                raise Exception(f"FFmpeg streaming stalled - no file growth for {stall_time:.1f}s. File size: {current_size:.2f} MB")
                        last_file_size = current_size
                    last_file_check = current_time
                
                # Convert frame to bytes (RGB24 format: width * height * 3 bytes)
                frame_bytes = frame.tobytes()
                try:
                    process.stdin.write(frame_bytes)
                    process.stdin.flush()  # Ensure data is sent
                except BrokenPipeError:
                    # FFmpeg closed stdin
                    monitor.stop()
                    stdout, stderr = process.communicate()
                    error_msg = stderr.decode('utf-8', errors='replace') if stderr else "FFmpeg closed input"
                    raise Exception(f"FFmpeg closed input: {error_msg[:500]}")
                
                frame_count += 1
                
                # Progress update every 100 frames
                if frame_count % 100 == 0:
                    current_size = monitor.get_current_size_mb()
                    elapsed_str = f"{elapsed:.1f}s" if elapsed < 60 else f"{elapsed/60:.1f}min"
                    print(f"  [PROGRESS] Frame {frame_count}/{num_frames} ({current_size:.1f} MB, {elapsed_str})", end='\r')
            
            # Close stdin to signal end of input
            try:
                process.stdin.close()
            except Exception:
                pass  # May already be closed
            
            # Wait for FFmpeg to finish with timeout
            try:
                stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout for final encoding
            except subprocess.TimeoutExpired:
                # Use helper function for proper cleanup
                self._cleanup_ffmpeg_process(process)
                monitor.stop()
                raise Exception("FFmpeg final encoding timed out after frame streaming completed")
            
            monitor.stop()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace') if isinstance(stderr, bytes) else (stderr or "Unknown error")
                print(f"\n[ERROR] FFmpeg streaming failed (code {process.returncode}):")
                print(f"  {error_msg[:1000]}")
                raise Exception(f"FFmpeg streaming failed with code {process.returncode}")
            
            final_size = monitor.get_current_size_mb()
            print(f"\n[OK] Visualization video encoded with {'NVENC' if use_nvenc else 'libx264'} (streamed {frame_count} frames, {final_size:.1f} MB)")
            
        except subprocess.TimeoutExpired:
            self._cleanup_ffmpeg_process(process)
            monitor.stop()
            raise Exception("FFmpeg streaming timed out")
        except Exception as e:
            # Use helper function for proper cleanup
            self._cleanup_ffmpeg_process(process)
            
            try:
                monitor.stop()
            except Exception:
                pass
            
            # Log full error for troubleshooting
            print(f"\n[ERROR] Streaming failed: {str(e)}")
            if output_path.exists():
                print(f"  Output file size: {output_path.stat().st_size / (1024*1024):.2f} MB")
            raise
        finally:
            # GUARANTEED cleanup - ensure all handles are closed even if exception occurs
            try:
                if 'process' in locals():
                    self._cleanup_ffmpeg_process(process)
            except Exception:
                pass
        
        return output_path

    def _frames_to_video(self, frames: list, audio_path: Path, output_path: Path) -> Path:
        """Legacy method - kept for compatibility. Use _stream_frames_to_video for new code."""
        """Convert frames to video with audio using FFmpeg with GPU acceleration."""
        import subprocess
        import tempfile
        
        # Try GPU acceleration first
        try:
            from src.utils.gpu_utils import get_gpu_manager
            gpu_manager = get_gpu_manager()
            
            # Check if NVENC is available
            nvenc_check = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True
            )
            use_nvenc = gpu_manager.gpu_available and "h264_nvenc" in nvenc_check.stdout
            
        except Exception:
            use_nvenc = False
        
        # Save frames as temporary image sequence
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Write frames as PNG files
            frame_paths = []
            for i, frame in enumerate(frames):
                frame_path = temp_dir / f"frame_{i:06d}.png"
                Image.fromarray(frame).save(frame_path)
                frame_paths.append(frame_path)
            
            # Build FFmpeg command
            if use_nvenc:
                print("[GPU] Using NVENC for visualization encoding")
                # Use GPU-accelerated encoding
                cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(self.fps),
                    "-i", str(temp_dir / "frame_%06d.png"),
                    "-i", str(audio_path),
                    "-c:v", "h264_nvenc",
                    "-profile:v", "baseline",
                    "-level", "3.1",
                    "-preset", "p7",  # Fastest NVENC preset
                    "-tune", "1",
                    "-rc", "vbr",
                    "-cq", "26",
                    "-b:v", "3M",
                    "-maxrate", "4M",
                    "-bufsize", "8M",
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-ar", "44100",
                    "-ac", "2",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    "-f", "mp4",
                    "-movflags", "+faststart",
                    "-r", str(self.fps),
                    str(output_path)
                ]
            else:
                print("[CPU] Using libx264 for visualization encoding (MoviePy fallback available)")
                # Use CPU encoding (faster preset for visualization)
                cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(self.fps),
                    "-i", str(temp_dir / "frame_%06d.png"),
                    "-i", str(audio_path),
                    "-c:v", "libx264",
                    "-profile:v", "baseline",
                    "-level", "3.1",
                    "-preset", "faster",
                    "-tune", "stillimage",
                    "-crf", "23",
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-ar", "44100",
                    "-ac", "2",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    "-f", "mp4",
                    "-movflags", "+faststart",
                    "-r", str(self.fps),
                    str(output_path)
                ]
            
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                errors='replace',
                timeout=3600
            )
            
            if result.returncode != 0:
                # Fallback to MoviePy if FFmpeg fails
                print(f"[WARN] FFmpeg failed: {result.stderr[:200]}, falling back to MoviePy")
                from moviepy.editor import AudioFileClip, ImageSequenceClip
                video_clip = ImageSequenceClip(frames, fps=self.fps)
                audio_clip = AudioFileClip(str(audio_path))
                video_clip = video_clip.set_audio(audio_clip)
                video_clip.write_videofile(
                    str(output_path),
                    fps=self.fps,
                    codec="libx264",
                    audio_codec="aac",
                    preset="medium",
                    bitrate="2000k",
                    logger=None,
                )
            else:
                print(f"[OK] Visualization video encoded with {'NVENC' if use_nvenc else 'libx264'}")
                
        finally:
            # Cleanup temporary frames
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

        return output_path
