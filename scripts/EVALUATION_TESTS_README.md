# Evaluation Test Suite

## Overview

This evaluation suite runs **47 comprehensive tests** with different waveform configurations, locations, combinations, and permutations - all using the short test script for quick evaluation.

## Test Categories

### Single Position Tests (5 tests)
- `eval_01_bottom_default` - Bottom position
- `eval_02_top_default` - Top position
- `eval_03_middle_default` - Middle position
- `eval_04_left_vertical` - Left side (vertical)
- `eval_05_right_vertical` - Right side (vertical)

### Two Position Combinations (6 tests)
- `eval_06_top_bottom` - Top and bottom
- `eval_07_left_right` - Left and right
- `eval_08_top_left` - Top and left
- `eval_09_top_right` - Top and right
- `eval_10_bottom_left` - Bottom and left
- `eval_11_bottom_right` - Bottom and right

### Three Position Combinations (4 tests)
- `eval_12_top_left_right` - Top, left, right
- `eval_13_bottom_left_right` - Bottom, left, right
- `eval_14_top_bottom_left` - Top, bottom, left
- `eval_15_top_bottom_right` - Top, bottom, right

### Four Position Combinations (1 test)
- `eval_16_all_four_positions` - All four positions

### Different Line Counts (3 tests)
- `eval_17_bottom_1_line` - 1 line
- `eval_18_bottom_5_lines` - 5 lines
- `eval_19_bottom_10_lines` - 10 lines (maximum)

### Different Styles (4 tests)
- `eval_20_bottom_continuous` - Continuous style
- `eval_21_bottom_bars` - Bars style
- `eval_22_bottom_dots` - Dots style
- `eval_23_bottom_filled` - Filled style

### Different Colors (3 tests)
- `eval_24_bottom_neon_green` - Neon green
- `eval_25_bottom_rainbow` - Rainbow colors
- `eval_26_bottom_cyan_magenta` - Cyan and magenta

### Different Thicknesses (3 tests)
- `eval_27_bottom_thick` - Thick lines (20px)
- `eval_28_bottom_thin` - Thin lines (6px)
- `eval_29_bottom_varying_thickness` - Varying thickness per line

### Different Opacities (2 tests)
- `eval_30_bottom_opacity_50` - 50% opacity
- `eval_31_bottom_opacity_75` - 75% opacity

### Different Heights/Widths (4 tests)
- `eval_32_bottom_10_percent` - 10% height
- `eval_33_bottom_50_percent` - 50% height
- `eval_34_left_10_percent` - 10% width
- `eval_35_left_50_percent` - 50% width

### Spacing Tests (3 tests)
- `eval_36_left_spacing_20px` - Left 20px spacing
- `eval_37_right_spacing_20px` - Right 20px spacing
- `eval_38_left_right_spacing_30px` - Both 30px spacing

### Render Quality Tests (3 tests)
- `eval_39_bottom_render_1x` - 1x render scale
- `eval_40_bottom_render_4x` - 4x render scale
- `eval_41_bottom_no_antialias` - No anti-aliasing

### Complex Combinations (5 tests)
- `eval_42_top_bottom_5_lines_rainbow` - Top/bottom, 5 lines, rainbow
- `eval_43_left_right_bars_style` - Left/right, bars style
- `eval_44_all_four_dots_style` - All four, dots style
- `eval_45_top_bottom_filled_rainbow` - Top/bottom, filled, rainbow
- `eval_46_complex_all_features` - All features combined

### Randomized Test (1 test)
- `eval_47_randomized` - Randomized configuration

## Running the Tests

### Run All Tests
```bash
python scripts/run_evaluation_tests.py
```

This will:
1. Run all 47 tests sequentially
2. Use the short test script for each test
3. Generate config overrides for each test
4. Save outputs to `Creations/Outputs/`
5. Display progress and results

### Run Single Test
You can also run individual tests using the CLI:

```bash
python -m src.cli.main create "Creations/Scripts/test_short.txt" --visualize --background --avatar --quality fastest --output eval_01_bottom_default --config "Creations/Configs/evaluation_tests/eval_01_bottom_default_config.yaml"
```

## Output Files

All test outputs are saved to:
- **Videos**: `Creations/MMedia/eval_XX_*.mp4` (correct location per config.yaml)
- **Configs**: `Creations/Configs/evaluation_tests/eval_XX_*_config.yaml`

## Test Naming Convention

Tests are named with:
- `eval_XX` - Sequential number (01-47)
- Descriptive suffix indicating the test configuration

Examples:
- `eval_01_bottom_default` - First test, bottom position, default settings
- `eval_42_top_bottom_5_lines_rainbow` - Top/bottom, 5 lines, rainbow colors
- `eval_46_complex_all_features` - Complex test with all features

## What to Evaluate

When reviewing the test outputs, check:

1. **Visual Quality**
   - Smoothness of lines (no graininess)
   - Clarity and visibility
   - Color accuracy

2. **Position Accuracy**
   - Correct placement
   - No overlap issues
   - Proper spacing

3. **Style Rendering**
   - Continuous lines are smooth
   - Bars are properly rendered
   - Dots are visible and clear
   - Filled areas are complete

4. **Multi-Position Combinations**
   - All positions render correctly
   - No interference between positions
   - Proper sizing for each position

5. **Performance**
   - Rendering time
   - File sizes
   - Memory usage

## Expected Results

- **47 test videos** in `Creations/MMedia/`
- **47 config files** in `Creations/Configs/evaluation_tests/`
- **Summary report** in console output

## Notes

- Each test uses the same short script for consistency
- Tests run sequentially (one at a time)
- Each test has a 10-minute timeout
- Failed tests are reported in the summary

