# Waveform Test Suite

## Overview

This test suite contains 30 comprehensive waveform visualization tests covering all features and configurations.

## Test Categories

### 1. Graininess Fix Tests (Priority 4)
- `test_graininess_opencv_2x` - OpenCV 2x render scale
- `test_graininess_opencv_4x` - OpenCV 4x render scale (maximum smoothness)

### 2. Position Tests - Horizontal (Priority 2)
- `test_position_top` - Waveform at top
- `test_position_bottom` - Waveform at bottom
- `test_position_middle` - Waveform in middle
- `test_position_top_bottom` - Top and bottom simultaneously

### 3. Position Tests - Vertical (Priority 2)
- `test_position_left` - Vertical waveform on left
- `test_position_right` - Vertical waveform on right
- `test_position_left_right` - Left and right with independent spacing
- `test_position_all_three` - Top, left, and right simultaneously

### 4. Line Customization Tests (Priority 3)
- `test_lines_1` - Single line
- `test_lines_5` - Five lines
- `test_lines_10` - Ten lines (maximum)
- `test_thickness_per_line` - Per-line thickness
- `test_colors_per_line` - Per-line colors
- `test_colors_rainbow` - Rainbow colors

### 5. Waveform Style Tests (Priority 1)
- `test_style_continuous` - Continuous style (default)
- `test_style_bars` - Bar-style
- `test_style_dots` - Dots-style
- `test_style_filled` - Filled area

### 6. Advanced Feature Tests
- `test_opacity_50` - 50% opacity
- `test_opacity_75` - 75% opacity
- `test_height_10` - 10% height
- `test_height_50` - 50% height
- `test_width_10` - 10% width
- `test_width_50` - 50% width
- `test_randomized` - Randomized configuration

### 7. Complex Combination Tests
- `test_complex_1` - Top+Bottom, 5 lines, per-line colors, filled style
- `test_complex_2` - Left+Right, per-line thickness, bars style
- `test_complex_3` - All positions, rainbow colors, dots style

## Running Tests

### Generate Test Scripts
```bash
python scripts/generate_waveform_tests.py
```

### Run Single Test
```bash
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_top.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_top_config.yaml"
```

### Run All Tests (Batch Script)
```bash
Creations\Scripts\waveform_tests\run_all_tests.bat
```

### Run QA Suite
```bash
python scripts/qa_waveform_tests.py
```

## CLI Waveform Parameters

All waveform parameters can be overridden via CLI:

```bash
# Position
--waveform-position "top,bottom"

# Number of lines
--waveform-lines 5

# Thickness (single or comma-separated)
--waveform-thickness "15,12,8"

# Colors (RGB tuples separated by colons)
--waveform-colors "0,255,0:0,255,100:0,200,50"

# Style
--waveform-style "bars"

# Opacity
--waveform-opacity 0.75

# Randomization
--waveform-randomize

# Size
--waveform-height 30  # 10-100 (now allows up to 100% for full height)
--waveform-width 25   # 10-100 (now allows up to 100% for full width)

# Spacing
--waveform-left-spacing 20
--waveform-right-spacing 20

# Quality
--waveform-render-scale 2.0
--waveform-anti-alias

# NEW: Advanced Features (Added 2025-01-XX)
--waveform-orientation-offset 50  # 0-100 (0=bottom, 100=top for horizontal)
--waveform-rotation 45            # Rotation angle in degrees
--waveform-amplitude 1.5          # Amplitude multiplier (0.1+, default: 1.0)
--waveform-instances 3            # Number of waveform instances (1-10)
--waveform-instances-offset 10    # Spacing between instances in pixels
--waveform-instances-intersect   # Allow instances to intersect
```

## Example Commands

```bash
# Test with custom position
python -m src.cli.main create script.txt --visualize --waveform-position "top,left,right" --waveform-lines 5

# Test with rainbow colors
python -m src.cli.main create script.txt --visualize --waveform-colors "255,0,0:255,165,0:255,255,0:0,255,0:0,0,255"

# Test with bars style
python -m src.cli.main create script.txt --visualize --waveform-style "bars" --waveform-lines 3

# Test randomized
python -m src.cli.main create script.txt --visualize --waveform-randomize
```

## Output Files

All test outputs are saved to `Creations/Outputs/` with names like:
- `test_position_top_output.mp4`
- `test_graininess_opencv_2x_output.mp4`
- etc.

## Test Manifest

The test manifest (`test_manifest.json`) contains metadata for all tests:
- Test name and description
- Script path
- Config override path
- Expected configuration

## QA Report

After running the QA suite, a report is generated at:
`Creations/Outputs/qa_waveform_report.json`

This includes:
- Pass/fail status for each test
- Video validation results
- Error messages (if any)
- Summary statistics

