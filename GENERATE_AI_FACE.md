# Generate AI Face for Lip-Sync

**Quick Answer:** Yes, AI-generated faces work MUCH better for lip-sync!

## Why AI Faces Work Better

1. **Clean, uniform lighting** - No shadows or uneven lighting
2. **Front-facing, neutral expressions** - Perfect for Wav2Lip
3. **Consistent facial structure** - No unusual features that confuse alignment
4. **No facial hair** - Mouth is clearly visible
5. **High quality** - Optimized for processing

## Quick Start

### Option 1: Generate a Face (Recommended)

```bash
# Generate a professional male presenter
python -m src.core.face_generator "professional male presenter"

# Or use a description
python -m src.core.face_generator --description "young professional woman"
```

The generated face will be saved to `data/cache/faces/generated_face.png`

### Option 2: Update Config

```yaml
# config.yaml
avatar:
  source_image: "data/cache/faces/generated_face.png"
```

Then create your podcast as normal - the AI-generated face will have much better lip-sync alignment!

## Example Prompts

- `"professional male presenter, headshot"`
- `"young female news anchor, studio lighting"`
- `"middle-aged male podcaster, front-facing"`
- `"professional woman presenter, neutral expression"`

## Technical Details

- **Model:** Stable Diffusion v1.5 (fast, good quality)
- **Resolution:** 512x512 (optimal for lip-sync)
- **Optimizations:** 
  - Front-facing pose
  - Neutral expression
  - Clean lighting
  - No facial hair
  - Symmetrical features

## Next Steps

1. Generate a face using the command above
2. Update `config.yaml` to use the generated face
3. Create your podcast - lip-sync should be much more accurate!

