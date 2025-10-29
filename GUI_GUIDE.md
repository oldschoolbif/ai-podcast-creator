# GUI Guide - AI Podcast Creator

## 🖥️ Two GUI Options Available!

The AI Podcast Creator now has **beautiful graphical interfaces** - no command line needed!

### Option 1: Web Interface (Recommended) 🌐
- Modern, beautiful Gradio interface
- Works in your web browser
- Can be accessed from any device on your network
- Can create public links for remote access
- Perfect for embedding in websites

### Option 2: Desktop GUI 💻
- Native desktop application using tkinter
- Traditional desktop app feel
- No browser needed
- Runs entirely local

## 🚀 Quick Start

### Web Interface:

```bash
# Activate your environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Launch web GUI
python launch_web_gui.py
```

Then open: **http://localhost:7860** in your browser

### Desktop GUI:

```bash
# Activate your environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Launch desktop GUI
python launch_desktop_gui.py
```

Window opens automatically!

## 📦 Installation

### For Web Interface:

```bash
pip install gradio
# or
pip install -r requirements-basic.txt
```

### For Desktop GUI:

Tkinter is included with Python, no extra installation needed!

## 🎨 Web Interface Features

### Main Features:
- ✅ **Drag & Drop** file upload
- ✅ **Live preview** of generated videos
- ✅ **Real-time progress** indicator
- ✅ **Multiple tabs** for organization
- ✅ **Example scripts** included
- ✅ **Settings panel** for configuration
- ✅ **Help & documentation** built-in

### File Uploads:
1. **Script File**: Upload .txt or .md files
2. **Music File**: Upload .mp3, .wav, or .m4a (optional)
3. **Music Description**: Or describe music style in text

### Configuration Options:

**Voice Engine:**
- gTTS (Free, Cloud-based)
- Coqui (High Quality, GPU required)
- ElevenLabs (Premium, API key required)
- Azure (Good Quality, API key required)

**Avatar Style:**
- Professional Studio (Default)
- Gradient Background
- News Desk
- Tech Theme
- Minimal
- Custom (Upload Background)

**Video Quality:**
- High (1080p)
- Medium (720p)
- Low (480p)

### Advanced Options:

```bash
# Create public link (accessible from anywhere)
python launch_web_gui.py --share

# Change port
python launch_web_gui.py --port 8080

# Allow external access
python launch_web_gui.py --host 0.0.0.0

# Add authentication
python launch_web_gui.py --auth username:password

# Combine options
python launch_web_gui.py --share --port 8080 --auth admin:secret123
```

## 🖥️ Desktop GUI Features

### Main Features:
- ✅ **Native desktop** application
- ✅ **File browser** for easy file selection
- ✅ **Live progress log** showing each step
- ✅ **Status indicator** with color coding
- ✅ **Quick access** to output folder
- ✅ **GPU status** display
- ✅ **Clean, intuitive** interface

### Layout:

```
┌─────────────────────────────────────────────────────┐
│  🎙️ AI Podcast Creator                             │
├──────────────────────┬──────────────────────────────┤
│  📄 Input Files      │  ⚙️ Settings                 │
│  • Script File       │  • Voice Engine              │
│  • Music File        │  • Avatar Style              │
│  • Music Description │  • Video Quality             │
│                      │  • Output Name               │
├──────────────────────┴──────────────────────────────┤
│  📝 Progress Log                                    │
│  [Shows real-time progress and status]             │
├─────────────────────────────────────────────────────┤
│  [🚀 Create] [📁 Output] [Clear]                   │
└─────────────────────────────────────────────────────┘
```

### Status Colors:
- 🟢 **Green**: Success / Ready
- 🔵 **Blue**: Processing
- 🟠 **Orange**: Warning / CPU mode
- 🔴 **Red**: Error

## 📝 How to Use

### Step-by-Step (Web Interface):

1. **Open browser** to http://localhost:7860
2. **Upload script** file (or use example)
3. **Add music** (optional):
   - Upload music file, OR
   - Describe music style in text
4. **Configure settings**:
   - Choose voice engine
   - Select avatar style
   - Set video quality
   - Name your output (optional)
5. **Click "Create Podcast"**
6. **Wait for processing** (progress shown)
7. **Watch/Download** your video!

### Step-by-Step (Desktop GUI):

1. **Launch** desktop_gui.py
2. **Browse** for script file
3. **Browse** for music (optional) or describe style
4. **Select** voice and avatar from dropdowns
5. **Choose** video quality
6. **Enter** output name (optional)
7. **Click "Create Podcast"**
8. **Watch progress** in log window
9. **Click "Open Output Folder"** when done!

## 🎯 Example Workflow

### Create Your First Podcast:

1. **Launch Web GUI**:
   ```bash
   python launch_web_gui.py
   ```

2. **Go to Examples tab** and copy the template

3. **Create your script** in a text editor:
   ```markdown
   # My First Podcast
   
   [MUSIC: upbeat intro]
   
   Hello everyone! Welcome to my first AI podcast.
   
   [MUSIC: soft background]
   
   Today I want to share something interesting...
   
   [MUSIC: fade out]
   
   Thank you for listening!
   ```

4. **Save as** `my_podcast.txt`

5. **Upload** to web GUI

6. **Configure**:
   - Voice: gTTS (Free, Cloud-based)
   - Avatar: Professional Studio
   - Quality: High (1080p)

7. **Click** "Create Podcast"

8. **Wait** ~30 seconds

9. **Download** your video!

## 🌐 Embedding in Websites

The Gradio interface can be embedded in your website:

### HTML Embed:

```html
<iframe
    src="http://your-server:7860"
    width="100%"
    height="800px"
    frameborder="0"
></iframe>
```

### Run on Server:

```bash
# On your server
python launch_web_gui.py --host 0.0.0.0 --port 7860

# Access from anywhere
http://your-server-ip:7860
```

### With Nginx Reverse Proxy:

```nginx
server {
    listen 80;
    server_name podcast.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 🔒 Security Options

### Add Authentication:

```bash
python launch_web_gui.py --auth username:password
```

Users must log in before accessing the interface.

### Limit to Local Only:

```bash
python launch_web_gui.py --host 127.0.0.1
```

Only accessible from the same machine.

### Use HTTPS:

Set up SSL certificate with nginx or use Gradio's share feature (automatically uses HTTPS).

## ⚙️ Customization

### Change Theme:

Edit `src/gui/web_interface.py`:

```python
interface = gr.Blocks(
    theme=gr.themes.Soft()  # Change to: Base, Default, Glass, Monochrome
)
```

Available themes:
- `gr.themes.Soft()` - Current (soft colors)
- `gr.themes.Base()` - Clean, minimal
- `gr.themes.Default()` - Standard Gradio
- `gr.themes.Glass()` - Glassmorphism
- `gr.themes.Monochrome()` - Black & white

### Add Custom Backgrounds:

Place images in `src/assets/backgrounds/` and they'll be available in the avatar style dropdown.

### Modify Voice Options:

Edit the voice dropdown list in `web_interface.py` or `desktop_gui.py` to add/remove options.

## 🐛 Troubleshooting

### Web Interface Won't Start:

**Check port availability:**
```bash
# Linux/Mac
lsof -i :7860

# Windows
netstat -ano | findstr :7860
```

**Try different port:**
```bash
python launch_web_gui.py --port 8080
```

### Desktop GUI Won't Open:

**Check tkinter installation:**
```bash
python -c "import tkinter"
```

**On Linux, install tkinter:**
```bash
sudo apt-get install python3-tk
```

### "Gradio not found":

```bash
pip install gradio
```

### Slow Performance:

- Use **Low (480p)** quality for faster processing
- Ensure GPU is detected (check status display)
- Close other applications

### Can't Access from Other Devices:

```bash
# Allow external access
python launch_web_gui.py --host 0.0.0.0

# Or create public link
python launch_web_gui.py --share
```

## 📱 Mobile Access

The web interface is **mobile-responsive**!

Access from phone/tablet:
1. Launch with `--host 0.0.0.0`
2. Find your computer's IP address
3. Open browser on mobile device
4. Navigate to `http://your-ip:7860`

Or use `--share` for automatic public link.

## 🎓 Tips & Best Practices

### Performance:
- Use **gTTS** for fastest results (basic version)
- Upload music files instead of generating (faster)
- Start with **Low quality** for testing
- Use **High quality** for final output

### Scripts:
- Keep scripts under 500 words for quick testing
- Use `[MUSIC: description]` tags for music cues
- Save scripts as `.txt` files with UTF-8 encoding

### Organization:
- Name outputs descriptively
- Use the output folder shortcut to find videos
- Clear the log regularly in desktop GUI

### Sharing:
- Use `--auth` for public deployments
- Use `--share` for temporary sharing
- Set up proper server for permanent web access

## 📊 Feature Comparison

| Feature | Web Interface | Desktop GUI |
|---------|---------------|-------------|
| **Browser-based** | ✅ Yes | ❌ No |
| **Native app** | ❌ No | ✅ Yes |
| **Drag & drop** | ✅ Yes | ❌ No |
| **Live preview** | ✅ Yes | ❌ No |
| **Progress log** | ✅ Yes | ✅ Yes |
| **Mobile access** | ✅ Yes | ❌ No |
| **Embeddable** | ✅ Yes | ❌ No |
| **Offline** | ✅ Yes | ✅ Yes |
| **Authentication** | ✅ Yes | ❌ No |
| **Public sharing** | ✅ Yes | ❌ No |
| **File browser** | ❌ No | ✅ Yes |
| **Status colors** | ⚠️ Limited | ✅ Full |

## 🚀 Which to Use?

### Use Web Interface if:
- ✅ You want a modern, beautiful UI
- ✅ You need remote access
- ✅ You want to embed in a website
- ✅ You prefer browser-based apps
- ✅ You want to share with others

### Use Desktop GUI if:
- ✅ You prefer traditional desktop apps
- ✅ You want offline-only operation
- ✅ You don't want to open a browser
- ✅ You want native file dialogs
- ✅ You need maximum privacy

**Both are fully functional - choose what you prefer!**

## 📚 Additional Resources

- **README.md** - Complete user manual
- **QUICK_START.md** - Command-line usage
- **GPU_OPTIMIZATION_GUIDE.md** - Performance tuning
- **Creations/README.md** - Example scripts

---

**Enjoy creating podcasts with the GUI!** 🎙️✨

No command line needed - just point, click, and create!

