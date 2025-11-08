# Waveform Visualization Features

## Overview

The waveform visualization system provides a comprehensive set of features for creating audio-reactive visual effects that respond to your podcast's audio in real-time.

## Core Features

### Basic Configuration

- **Position**: Place waveforms at top, bottom, left, right, middle, or combinations
- **Lines**: Configure 1-10 independent waveform lines
- **Colors**: Custom RGB colors per line or gradient effects
- **Thickness**: Adjustable line thickness (1-50 pixels)
- **Opacity**: Transparency control (0.0-1.0)

### Advanced Features (New)

#### 1. Orientation Offset
- **Parameter**: `orientation_offset` (0-100)
- **Description**: Fine-grained vertical positioning for horizontal waveforms
- **Usage**: 
  - `0` = Bottom-most position
  - `50` = Middle (with dynamic baseline)
  - `100` = Top-most position
- **Example**: `--waveform-orientation-offset 25` (quarter-way up from bottom)

#### 2. Rotation
- **Parameter**: `rotation` (degrees)
- **Description**: Rotate the entire waveform by any angle
- **Usage**: 
  - `0` = No rotation (horizontal/vertical)
  - `45` = Diagonal
  - `90` = Perpendicular
- **Example**: `--waveform-rotation 30` (30-degree rotation)

#### 3. Amplitude Multiplier
- **Parameter**: `amplitude_multiplier` (0.1+)
- **Description**: Fine-grained control over waveform height/response
- **Usage**:
  - `0.05-0.5` = Very subtle, low amplitude
  - `1.0` = Normal (default)
  - `1.5-3.0` = High amplitude (with compression to prevent clipping)
- **Features**:
  - Linear scaling for low values (preserves fine detail)
  - Logarithmic compression for high values (prevents ceiling clipping)
  - Only extreme peaks reach maximum height
- **Example**: `--waveform-amplitude 0.1` (very subtle) or `--waveform-amplitude 2.5` (high)

#### 4. Multiple Instances
- **Parameter**: `num_instances` (1-10)
- **Description**: Create multiple waveform instances for complex visual effects
- **Usage**:
  - `1` = Single waveform (default)
  - `2-5` = Multiple layers
  - `6-10` = Complex multi-layer effects
- **Example**: `--waveform-instances 3` (three overlapping waveforms)

#### 5. Instance Spacing
- **Parameter**: `instances_offset` (pixels)
- **Description**: Control spacing between multiple instances
- **Usage**:
  - `0` = Overlapping instances
  - `10-50` = Spaced instances
- **Example**: `--waveform-instances-offset 20` (20-pixel spacing)

#### 6. Instance Intersection
- **Parameter**: `instances_intersect` (boolean)
- **Description**: Allow waveform instances to visually intersect/overlap
- **Usage**: 
  - `false` = Instances don't overlap (default)
  - `true` = Instances can overlap creating depth effect
- **Example**: `--waveform-instances-intersect`

## Dynamic Baseline Positioning

For middle-positioned waveforms (`orientation_offset=50`), the system uses **dynamic baseline positioning**:

1. Calculates the amplitude midpoint: `(max_amplitude + min_amplitude) / 2`
2. Compares to video center: `video_height / 2`
3. Sets baseline automatically:
   - If amplitude midpoint > video center → Use bottom as baseline (waveform extends upward)
   - If amplitude midpoint ≤ video center → Use top as baseline (waveform extends downward)

This ensures the waveform always appears centered relative to the audio's natural dynamics.

## Amplitude Scaling Algorithm

The amplitude calculation uses a sophisticated compression curve:

1. **Normalize** audio sample against fixed reference (0.5)
2. **Apply multiplier** first: `scaled = normalized * amplitude_multiplier`
3. **Apply compression curve**:
   - Values ≤ 1.0: Linear scaling (preserves fine detail)
   - Values > 1.0: Logarithmic compression (prevents clipping)
4. **Cap at maximum**: Only extreme peaks reach full height

This ensures:
- Low amplitudes (0.05-0.5) scale proportionally
- High amplitudes (1.5-3.0) compress naturally without all hitting the ceiling
- Only truly loud sounds reach maximum height

## CLI Examples

### Basic Usage
```bash
# Single line, bottom position, medium amplitude
python scripts/generate_waveform_only.py "script.txt" \
  --output test_basic \
  --waveform-lines 1 \
  --waveform-position bottom \
  --waveform-amplitude 1.5
```

### Advanced Configuration
```bash
# Three instances, rotated, high amplitude
python scripts/generate_waveform_only.py "script.txt" \
  --output test_advanced \
  --waveform-lines 1 \
  --waveform-position bottom \
  --waveform-orientation-offset 0 \
  --waveform-rotation 15 \
  --waveform-amplitude 2.5 \
  --waveform-instances 3 \
  --waveform-instances-offset 15 \
  --waveform-thickness 2
```

### Testing Different Amplitudes
```bash
# Very low amplitude (10% of normal)
python scripts/generate_waveform_only.py "script.txt" \
  --output test_low_amp \
  --waveform-amplitude 0.05

# High amplitude (will compress naturally)
python scripts/generate_waveform_only.py "script.txt" \
  --output test_high_amp \
  --waveform-amplitude 3.0
```

### Middle Position with Dynamic Baseline
```bash
# Middle position - automatically adjusts baseline
python scripts/generate_waveform_only.py "script.txt" \
  --output test_middle \
  --waveform-position middle \
  --waveform-orientation-offset 50 \
  --waveform-amplitude 1.5
```

## Configuration File

All parameters can also be set in `config.yaml`:

```yaml
visualization:
  waveform:
    # Basic settings
    position: "bottom"
    num_lines: 1
    line_thickness: 2
    
    # Advanced features
    orientation_offset: null  # 0-100 (null = use position)
    rotation: 0               # Degrees
    amplitude_multiplier: 1.0  # 0.1+
    num_instances: 1          # 1-10
    instances_offset: 0       # Pixels
    instances_intersect: false  # Boolean
```

## Testing

Use the standalone waveform generator for quick testing:

```bash
# Generate waveform-only video (no avatar, no background)
python scripts/generate_waveform_only.py "Creations/Scripts/test_short_duration.txt" \
  --output test_waveform \
  --waveform-lines 1 \
  --waveform-position bottom \
  --waveform-orientation-offset 0 \
  --waveform-height 100 \
  --waveform-amplitude 1.5 \
  --waveform-rotation 0 \
  --waveform-thickness 2 \
  --waveform-instances 1
```

Output will be saved to `Creations/MMedia/test_waveform.mp4` for review.

## Performance Notes

- **Amplitude scaling** is CPU-efficient (simple math operations)
- **Rotation** uses matrix math (negligible overhead)
- **Multiple instances** scale linearly (each instance adds ~5% render time)
- **Compression curve** prevents clipping without performance impact

## Known Limitations

- Maximum 10 lines per waveform
- Maximum 10 instances per waveform
- Rotation works best for angles ≤ 45 degrees
- Very high amplitudes (>5.0) may still show some compression artifacts

## Future Enhancements

- Per-line amplitude control
- Animated amplitude transitions
- Frequency-based amplitude mapping
- Caching for repeated operations (see TODO)

