"""
Web-based GUI for AI Podcast Creator using Gradio
Works locally and can be embedded in websites
"""

import gradio as gr
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config import load_config
from src.utils.gpu_utils import get_gpu_manager
from src.core.script_parser import ScriptParser
from src.core.tts_engine import TTSEngine
from src.core.music_generator import MusicGenerator
from src.core.audio_mixer import AudioMixer
from src.core.video_composer import VideoComposer


def get_gpu_status():
    """Get GPU status for display."""
    gpu_manager = get_gpu_manager()
    if gpu_manager.gpu_available:
        return f"✅ GPU: {gpu_manager.gpu_name} ({gpu_manager.gpu_memory:.1f} GB)"
    return "⚠️ CPU Mode (No GPU detected)"


def create_podcast(
    script_file,
    music_file,
    music_description,
    avatar_style,
    voice_type,
    voice_speed,
    video_quality,
    output_name,
    progress=gr.Progress()
):
    """Create podcast with progress updates."""
    
    try:
        # Load configuration
        config = load_config()
        
        # Update config based on user selections
        if voice_type:
            config['tts']['engine'] = voice_type
        
        progress(0.1, desc="Reading script...")
        
        # Read script
        if script_file is None:
            return None, "❌ Please upload a script file"
        
        script_path = Path(script_file.name)
        with open(script_path, 'r', encoding='utf-8') as f:
            script_text = f.read()
        
        progress(0.2, desc="Parsing script...")
        
        # Parse script
        parser = ScriptParser(config)
        parsed_data = parser.parse(script_text)
        
        progress(0.3, desc="Generating speech...")
        
        # Generate TTS
        tts_engine = TTSEngine(config)
        audio_path = tts_engine.generate(parsed_data['text'])
        
        progress(0.5, desc="Processing music...")
        
        # Handle music
        music_path = None
        if music_file:
            music_path = Path(music_file.name)
        elif music_description:
            music_gen = MusicGenerator(config)
            music_path = music_gen.generate(music_description)
        elif parsed_data.get('music_cues'):
            music_gen = MusicGenerator(config)
            music_path = music_gen.generate(parsed_data['music_cues'])
        
        progress(0.6, desc="Mixing audio...")
        
        # Mix audio
        mixer = AudioMixer(config)
        mixed_audio = mixer.mix(audio_path, music_path)
        
        progress(0.8, desc="Creating video...")
        
        # Create video
        composer = VideoComposer(config)
        
        # Set video quality
        if video_quality == "High (1080p)":
            config['video']['resolution'] = [1920, 1080]
        elif video_quality == "Medium (720p)":
            config['video']['resolution'] = [1280, 720]
        else:  # Low 480p
            config['video']['resolution'] = [854, 480]
        
        final_video = composer.compose(
            mixed_audio,
            output_name=output_name or script_path.stem
        )
        
        progress(1.0, desc="Complete!")
        
        return str(final_video), f"✅ Podcast created successfully!\n\nSaved to: {final_video}"
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def create_gradio_interface():
    """Create and configure the Gradio interface."""
    
    # Custom CSS for styling
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .output-class {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 10px;
    }
    """
    
    with gr.Blocks(
        title="AI Podcast Creator",
        theme=gr.themes.Soft(),
        css=custom_css
    ) as interface:
        
        gr.Markdown(
            """
            # 🎙️ AI Podcast Creator
            
            Transform your scripts into professional video podcasts with AI narration, music, and effects!
            """
        )
        
        # GPU Status
        gpu_status = gr.Markdown(get_gpu_status())
        
        with gr.Tabs():
            
            # Main Creation Tab
            with gr.Tab("Create Podcast"):
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📄 Script & Audio")
                        
                        script_file = gr.File(
                            label="Upload Script File (.txt, .md)",
                            file_types=[".txt", ".md"],
                            type="filepath"
                        )
                        
                        music_file = gr.File(
                            label="Upload Music File (Optional)",
                            file_types=[".mp3", ".wav", ".m4a"],
                            type="filepath"
                        )
                        
                        music_description = gr.Textbox(
                            label="Or Describe Music Style",
                            placeholder="e.g., upbeat electronic intro, calm ambient background",
                            lines=2
                        )
                        
                        gr.Markdown("---")
                        gr.Markdown("### 🎭 Voice & Avatar")
                        
                        voice_type = gr.Dropdown(
                            label="Voice Engine",
                            choices=[
                                "gtts (Free, Cloud-based)",
                                "coqui (High Quality, GPU required)",
                                "elevenlabs (Premium, API key required)",
                                "azure (Good Quality, API key required)"
                            ],
                            value="gtts (Free, Cloud-based)"
                        )
                        
                        voice_speed = gr.Slider(
                            label="Voice Speed",
                            minimum=0.5,
                            maximum=2.0,
                            value=1.0,
                            step=0.1
                        )
                        
                        avatar_style = gr.Dropdown(
                            label="Avatar Style",
                            choices=[
                                "Professional Studio (Default)",
                                "Gradient Background",
                                "News Desk",
                                "Tech Theme",
                                "Minimal",
                                "Custom (Upload Background)"
                            ],
                            value="Professional Studio (Default)"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ Video Settings")
                        
                        video_quality = gr.Dropdown(
                            label="Video Quality",
                            choices=[
                                "High (1080p)",
                                "Medium (720p)",
                                "Low (480p)"
                            ],
                            value="High (1080p)"
                        )
                        
                        output_name = gr.Textbox(
                            label="Output Video Name",
                            placeholder="my_podcast (optional)",
                            lines=1
                        )
                        
                        gr.Markdown("---")
                        
                        create_btn = gr.Button(
                            "🚀 Create Podcast",
                            variant="primary",
                            size="lg"
                        )
                        
                        gr.Markdown("---")
                        gr.Markdown("### 📹 Output")
                        
                        output_video = gr.Video(
                            label="Generated Video"
                        )
                        
                        output_message = gr.Textbox(
                            label="Status",
                            lines=3,
                            interactive=False
                        )
                
                # Create button action
                create_btn.click(
                    fn=create_podcast,
                    inputs=[
                        script_file,
                        music_file,
                        music_description,
                        avatar_style,
                        voice_type,
                        voice_speed,
                        video_quality,
                        output_name
                    ],
                    outputs=[output_video, output_message]
                )
            
            # Examples Tab
            with gr.Tab("Examples"):
                gr.Markdown(
                    """
                    ## 📚 Example Scripts
                    
                    Try these example scripts to get started:
                    
                    - `Creations/example_welcome.txt` - Welcome message
                    - `Creations/example_tech_news.txt` - Tech news format
                    - `Creations/example_educational.txt` - Educational content
                    - `Creations/example_storytelling.txt` - Story format
                    - `Creations/example_meditation.txt` - Meditation guide
                    
                    ### Script Format:
                    
                    ```markdown
                    # Episode Title
                    
                    [MUSIC: upbeat intro, energetic]
                    
                    Your podcast content goes here...
                    
                    [MUSIC: soft ambient background]
                    
                    More content...
                    
                    [MUSIC: fade out]
                    ```
                    """
                )
                
                with gr.Row():
                    example_script = gr.Textbox(
                        label="Quick Script Template",
                        value="""# My First Podcast

[MUSIC: upbeat intro]

Hello and welcome to my podcast!

[MUSIC: calm background]

Today we're talking about something interesting...

[MUSIC: fade out]

Thank you for listening!""",
                        lines=15
                    )
            
            # Settings Tab
            with gr.Tab("Settings & Help"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown(
                            """
                            ## ⚙️ Configuration
                            
                            ### Voice Engines:
                            
                            - **gTTS**: Free, cloud-based, British accent
                            - **Coqui**: High quality, requires GPU, local
                            - **ElevenLabs**: Premium quality, requires API key
                            - **Azure**: Good quality, requires API key
                            
                            ### Avatar Styles:
                            
                            - **Professional Studio**: Default with character name
                            - **Gradient Background**: Smooth color gradient
                            - **News Desk**: News-style presentation
                            - **Tech Theme**: Technology-themed background
                            - **Minimal**: Simple, clean look
                            
                            ### Video Quality:
                            
                            - **High (1080p)**: Best quality, larger file
                            - **Medium (720p)**: Good quality, medium file
                            - **Low (480p)**: Fast processing, small file
                            """
                        )
                    
                    with gr.Column():
                        gr.Markdown(
                            """
                            ## 🆘 Help & Tips
                            
                            ### Getting Started:
                            
                            1. Upload your script (.txt file)
                            2. Optionally add music or describe music style
                            3. Choose voice and avatar settings
                            4. Click "Create Podcast"
                            5. Wait for processing (30s - 5min depending on GPU)
                            6. Download your video!
                            
                            ### Tips:
                            
                            - Use `[MUSIC: description]` tags in your script
                            - Keep scripts clear and well-paced
                            - Test with short scripts first
                            - GPU significantly speeds up processing
                            - Basic version (gTTS) works without GPU
                            
                            ### System Info:
                            
                            - Python: 3.10+
                            - FFmpeg: Required
                            - GPU: Optional but recommended
                            - Storage: ~1GB per 5-minute video
                            
                            ### Need Help?
                            
                            Check the documentation files:
                            - README.md
                            - QUICK_START.md
                            - GPU_OPTIMIZATION_GUIDE.md
                            """
                        )
        
        gr.Markdown(
            """
            ---
            
            Made with ❤️ by AI Podcast Creator | [Documentation](../README.md) | [GitHub](https://github.com)
            """
        )
    
    return interface


def launch_web_interface(
    share=False,
    server_name="127.0.0.1",
    server_port=7860,
    auth=None
):
    """
    Launch the web interface.
    
    Args:
        share: Create public link (via Gradio)
        server_name: Server address (0.0.0.0 for external access)
        server_port: Port number
        auth: Tuple of (username, password) for authentication
    """
    interface = create_gradio_interface()
    
    interface.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        auth=auth,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    # Launch with default settings
    print("🎙️ Starting AI Podcast Creator Web Interface...")
    print("📍 Access at: http://localhost:7860")
    print("🌐 Press Ctrl+C to stop")
    
    launch_web_interface()

