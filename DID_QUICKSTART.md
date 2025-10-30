# 🎬 D-ID Animated Lip-Sync - 5 Minute Setup

## ✅ Ready to Use!

D-ID API integration is **already implemented** in your system! Just add your API key and it works.

---

## 🚀 Setup (5 Minutes)

### Step 1: Get Free D-ID API Key

1. Visit: **https://www.d-id.com/**
2. Click "Start Free" or "Sign Up"
3. Verify your email
4. Go to: **https://studio.d-id.com/account-settings**
5. Copy your API key

**Free Tier**: 20 videos per month (perfect for testing!)

---

### Step 2: Add API Key

```bash
cd /mnt/d/dev/AI_Podcast_Creator

# Add to .env file
echo "DID_API_KEY=your_api_key_here" >> .env
```

Or edit `.env` manually and add:
```
DID_API_KEY=your_actual_api_key_from_step_1
```

---

### Step 3: Update Config

Edit `config.yaml`:

```yaml
avatar:
  engine: "did"  # Change from "wav2lip" to "did"
  source_image: "src/assets/avatars/default_female.jpg"
  did:
    api_key: ""  # Leave empty, it will use .env
```

---

### Step 4: Generate Animated Avatar!

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Test with short demo
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --skip-music \
  -o did_lipsync_test

# Result: Animated lip-sync avatar video!
```

---

## 🎬 Usage Examples

### Simple Animated Avatar

```bash
python3 -m src.cli.main create \
  "Creations/example_tech_news.txt" \
  --avatar \
  -o tech_news_animated
```

### Avatar + Visualization

```bash
python3 -m src.cli.main create \
  "Creations/example_tech_news.txt" \
  --avatar \
  --visualize \
  -o complete_video
```

### Ultimate: Avatar + Viz + Music

```bash
python3 -m src.cli.main create \
  "Creations/example_tech_news.txt" \
  "Creations/skynet-sky-cassette-main-version-41446-01-52.mp3" \
  --avatar \
  --visualize \
  --music-offset 20 \
  -o ultimate_animated
```

---

## 💰 Pricing

| Plan | Videos/Month | Cost | Best For |
|------|--------------|------|----------|
| **Free Trial** | 20 | $0 | Testing |
| **Lite** | 100 | $49/mo | Regular use |
| **Pro** | 300 | $199/mo | Heavy use |

**Each video costs ~$0.10-0.50 depending on duration**

---

## ⚡ What You Get

With D-ID, you get:
- ✅ Perfect lip synchronization
- ✅ Natural head movements
- ✅ Facial expressions
- ✅ Blinking
- ✅ Professional quality
- ✅ Fast generation (~30-60 seconds per video)
- ✅ No GPU needed (cloud-based)
- ✅ No complex setup

---

## 🎯 Verification

After setup, test it works:

```bash
# Check your avatar is configured correctly
cat config.yaml | grep -A 5 "avatar:"

# Should show:
# avatar:
#   engine: "did"
#   ...

# Check your API key is set
cat .env | grep DID_API_KEY

# Should show:
# DID_API_KEY=your_key_here

# Test generation
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --skip-music \
  -o final_test
```

---

## 🐛 Troubleshooting

### Issue: "D-ID API key not found"

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Add key if missing
echo "DID_API_KEY=your_key" >> .env

# Verify
cat .env
```

### Issue: "D-ID API error: 401"

**Solution**: API key is invalid or expired
- Log into D-ID dashboard
- Generate a new API key
- Update `.env` file

### Issue: "D-ID API error: 429"

**Solution**: Rate limit exceeded
- You've used your monthly quota
- Wait for next month
- Or upgrade your plan

### Issue: "D-ID generation timed out"

**Solution**: Video was too long
- Try shorter scripts (< 5 minutes)
- Or check D-ID dashboard for status

---

## 🔄 Switch Back to Static Avatar

If you want to use static avatars (free, instant):

```yaml
# config.yaml
avatar:
  engine: "wav2lip"  # Change back from "did"
```

The system will automatically fall back to static avatar + audio.

---

## 🎨 Custom Avatars

Use your own photo for personalized avatars:

```bash
# Add your photo
cp /path/to/your/photo.jpg src/assets/avatars/my_face.jpg

# Update config
avatar:
  engine: "did"
  source_image: "src/assets/avatars/my_face.jpg"

# Generate with YOUR animated face!
python3 -m src.cli.main create "script.txt" --avatar -o my_podcast
```

**Photo tips**:
- ✅ Frontal face, centered
- ✅ Good lighting
- ✅ Neutral expression
- ✅ High resolution (512x512+)
- ✅ No sunglasses or obstructions

---

## ✨ Summary

**Setup Time**: 5 minutes  
**Cost**: Free trial (20 videos), then ~$0.10-0.50 per video  
**Quality**: ⭐⭐⭐⭐⭐⭐ (Highest)  
**Complexity**: ⭐ (Easiest)

**Best for**: Instant professional results without complex setup!

---

## 🚀 Ready to Go!

1. Get API key: https://www.d-id.com/
2. Add to `.env`: `DID_API_KEY=your_key`
3. Update `config.yaml`: `engine: "did"`
4. Generate: `python3 -m src.cli.main create "script.txt" --avatar -o test`

**Your animated lip-sync avatars are ready!** 🎭✨





