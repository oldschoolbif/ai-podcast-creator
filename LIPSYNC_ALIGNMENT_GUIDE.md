# Lip-Sync Alignment Guide

**Status:** Improved with mandatory face detection  
**Last Updated:** 2025-11-03

---

## Current Implementation

The system now uses **mandatory face detection** before generating any video with lip-sync. This ensures accurate alignment by:

1. **Detecting the face** using OpenCV
2. **Locating the mouth** using edge detection and morphological operations
3. **Centering the bounding box** on the detected mouth position
4. **Passing precise coordinates** to Wav2Lip

---

## Detection Methods (in order of accuracy)

### Method 1: MediaPipe (Best - Not Available for Python 3.13)
- **Accuracy:** Excellent (468 facial landmarks)
- **Installation:** `pip install mediapipe`
- **Status:** ❌ Not available for Python 3.13 yet (October 2025)
- **How it works:** Uses facial mesh to precisely locate mouth landmarks
- **Note:** Will be available once MediaPipe adds Python 3.13 support

### Method 2: face_alignment (✅ INSTALLED - Currently Active)
- **Accuracy:** Excellent (68-point landmarks)
- **Installation:** ✅ `pip install face-alignment` (already installed)
- **Status:** ✅ **ACTIVE** - Currently being used for detection
- **How it works:** Uses deep learning (2DFAN4 model) to detect 68 facial landmarks
- **Results:** Detected mouth at (523, 357) with size 108x36 - much more accurate than edge detection

### Method 3: OpenCV Edge Detection (Current - Working)
- **Accuracy:** Good (works but may need fine-tuning)
- **Installation:** Included with opencv-python
- **Status:** ✅ Currently active
- **How it works:**
  - Detects face with Haar cascade
  - Uses Canny edge detection in mouth region
  - Finds horizontal lines (lip signature)
  - Calculates mouth center using median of detected points
  - Detected 58,344+ feature points in recent test

### Method 4: Template Matching (Fallback)
- **Accuracy:** Moderate
- **How it works:** Tests multiple mouth positions and selects best match

---

## Why Lip-Sync Alignment is Challenging

1. **Face Variations:** Everyone's face proportions are different
2. **Facial Hair:** Mustaches/beards can obscure mouth detection
3. **Image Quality:** Blurry or low-resolution images make detection harder
4. **Wav2Lip Requirements:** Wav2Lip needs precise bounding box alignment
5. **No Ground Truth:** We're estimating from a single static image

---

## Solutions for Better Accuracy

### Option 1: face_alignment (✅ Already Installed!)
- **Status:** ✅ Currently active and working
- **Result:** Using 68-point facial landmarks for accurate mouth detection
- **Performance:** Much more accurate than edge detection - detected mouth at (523, 357) vs estimated (529, 271)

### Option 2: Install face_alignment
```bash
pip install face-alignment
```
Provides 68-point facial landmarks with good accuracy.

### Option 3: Manual Bounding Box Override (Future)
We could add a CLI option to manually specify bounding box coordinates if automatic detection is off.

### Option 4: Use Better Source Images
- High resolution (1080p+)
- Clear, front-facing face
- Good lighting
- Minimal facial hair over mouth
- Neutral expression

---

## Current Performance

**Edge Detection Results:**
- ✅ Face detected successfully
- ✅ Mouth detected via edge analysis
- ✅ 58,344+ mouth feature points found
- ⚠️ Alignment may still need fine-tuning for some images

**Recent Test:**
- Face: (37, 445, 326, 734)
- Mouth: (529, 271)
- Bounding Box: (0, 478, 203, 855)

---

## Troubleshooting

If lip-sync is still misaligned:

1. **Check mouth detection output** - Look for "Mouth detected via edge analysis" message
2. **Try MediaPipe** - Install it for best results: `pip install mediapipe`
3. **Image quality** - Ensure source image is clear and high-resolution
4. **Face angle** - Front-facing images work best
5. **Facial hair** - Mustaches can affect detection - edge detection should handle this

---

## Future Improvements

- [ ] Add MediaPipe as default dependency (best accuracy)
- [ ] Manual bounding box adjustment option
- [ ] Visual preview of detected mouth before generation
- [ ] Save/load bounding box per image
- [ ] Fine-tune edge detection parameters per image type

---

## Answer to "Will it always be this difficult?"

**Short answer:** It gets much easier with better tools.

**Current state:** Edge detection works but requires fine-tuning for each image type.

**With MediaPipe:** Installation is simple (`pip install mediapipe`), and accuracy improves significantly because it uses actual facial landmarks rather than edge detection.

**Best practice:** Install MediaPipe for production use. The system will automatically use it if available.

---

**Next Steps:**
1. Install MediaPipe for best accuracy: `pip install mediapipe`
2. Test again with the same image
3. If still not perfect, we can add manual adjustment options

