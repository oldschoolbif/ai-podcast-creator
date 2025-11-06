#!/usr/bin/env python3
"""
Waveform Test Suite Generator
Generates test scripts with identifiable names for all waveform configurations
"""

import json
from pathlib import Path
from typing import Dict, List

# Test script template
TEST_SCRIPT_TEMPLATE = """Welcome to the AI Podcast Creator waveform test suite.

This is a short test script to verify waveform visualization features.

The waveform should be clearly visible and match the configuration parameters.
"""

# All test configurations
TEST_CONFIGS = [
    # Priority 1: Graininess Fix Tests
    {
        "name": "test_graininess_opencv_2x",
        "description": "OpenCV 2x render scale - should be smooth",
        "waveform": {
            "render_scale": 2.0,
            "anti_alias": True,
            "position": "bottom",
            "num_lines": 3,
            "line_thickness": 12,
            "waveform_style": "continuous",
        }
    },
    {
        "name": "test_graininess_opencv_4x",
        "description": "OpenCV 4x render scale - maximum smoothness",
        "waveform": {
            "render_scale": 4.0,
            "anti_alias": True,
            "position": "bottom",
            "num_lines": 3,
            "line_thickness": 12,
            "waveform_style": "continuous",
        }
    },
    
    # Priority 2: Position Tests (Horizontal)
    {
        "name": "test_position_top",
        "description": "Waveform at top of screen",
        "waveform": {
            "position": "top",
            "num_lines": 3,
            "height_percent": 25,
        }
    },
    {
        "name": "test_position_bottom",
        "description": "Waveform at bottom of screen",
        "waveform": {
            "position": "bottom",
            "num_lines": 3,
            "height_percent": 25,
        }
    },
    {
        "name": "test_position_middle",
        "description": "Waveform in middle of screen",
        "waveform": {
            "position": "middle",
            "num_lines": 3,
            "height_percent": 25,
        }
    },
    {
        "name": "test_position_top_bottom",
        "description": "Waveforms at top and bottom simultaneously",
        "waveform": {
            "position": "top,bottom",
            "num_lines": 3,
            "height_percent": 20,
        }
    },
    
    # Priority 2: Position Tests (Vertical)
    {
        "name": "test_position_left",
        "description": "Vertical waveform on left side",
        "waveform": {
            "position": "left",
            "num_lines": 3,
            "width_percent": 25,
        }
    },
    {
        "name": "test_position_right",
        "description": "Vertical waveform on right side",
        "waveform": {
            "position": "right",
            "num_lines": 3,
            "width_percent": 25,
        }
    },
    {
        "name": "test_position_left_right",
        "description": "Vertical waveforms on left and right with independent spacing",
        "waveform": {
            "position": "left,right",
            "num_lines": 3,
            "width_percent": 25,
            "left_spacing": 20,
            "right_spacing": 20,
        }
    },
    {
        "name": "test_position_all_three",
        "description": "All three positions: top, left, right",
        "waveform": {
            "position": "top,left,right",
            "num_lines": 2,
            "height_percent": 20,
            "width_percent": 20,
        }
    },
    
    # Priority 3: Line Customization Tests
    {
        "name": "test_lines_1",
        "description": "Single waveform line",
        "waveform": {
            "num_lines": 1,
            "line_thickness": 15,
            "position": "bottom",
        }
    },
    {
        "name": "test_lines_5",
        "description": "Five waveform lines",
        "waveform": {
            "num_lines": 5,
            "line_thickness": 10,
            "position": "bottom",
        }
    },
    {
        "name": "test_lines_10",
        "description": "Ten waveform lines (maximum)",
        "waveform": {
            "num_lines": 10,
            "line_thickness": 8,
            "position": "bottom",
        }
    },
    {
        "name": "test_thickness_per_line",
        "description": "Per-line thickness: [15, 12, 8]",
        "waveform": {
            "num_lines": 3,
            "line_thickness": [15, 12, 8],
            "position": "bottom",
        }
    },
    {
        "name": "test_colors_per_line",
        "description": "Per-line colors: green, cyan, magenta",
        "waveform": {
            "num_lines": 3,
            "line_colors": [
                [0, 255, 0],      # Neon green
                [0, 255, 255],    # Cyan
                [255, 0, 255],    # Magenta
            ],
            "position": "bottom",
        }
    },
    {
        "name": "test_colors_rainbow",
        "description": "Rainbow colors per line",
        "waveform": {
            "num_lines": 5,
            "line_colors": [
                [255, 0, 0],      # Red
                [255, 165, 0],    # Orange
                [255, 255, 0],    # Yellow
                [0, 255, 0],      # Green
                [0, 0, 255],     # Blue
            ],
            "position": "bottom",
        }
    },
    
    # Priority 1: Advanced Features (Waveform Styles)
    {
        "name": "test_style_continuous",
        "description": "Continuous waveform style (default)",
        "waveform": {
            "waveform_style": "continuous",
            "num_lines": 3,
            "position": "bottom",
        }
    },
    {
        "name": "test_style_bars",
        "description": "Bar-style waveform (vertical bars)",
        "waveform": {
            "waveform_style": "bars",
            "num_lines": 3,
            "position": "bottom",
        }
    },
    {
        "name": "test_style_dots",
        "description": "Dots-style waveform",
        "waveform": {
            "waveform_style": "dots",
            "num_lines": 3,
            "position": "bottom",
        }
    },
    {
        "name": "test_style_filled",
        "description": "Filled area under waveform",
        "waveform": {
            "waveform_style": "filled",
            "num_lines": 3,
            "position": "bottom",
        }
    },
    
    # Advanced Features
    {
        "name": "test_opacity_50",
        "description": "50% opacity waveform",
        "waveform": {
            "opacity": 0.5,
            "num_lines": 3,
            "position": "bottom",
        }
    },
    {
        "name": "test_opacity_75",
        "description": "75% opacity waveform",
        "waveform": {
            "opacity": 0.75,
            "num_lines": 3,
            "position": "bottom",
        }
    },
    {
        "name": "test_height_10",
        "description": "10% height (horizontal waveform)",
        "waveform": {
            "height_percent": 10,
            "position": "bottom",
        }
    },
    {
        "name": "test_height_50",
        "description": "50% height (horizontal waveform)",
        "waveform": {
            "height_percent": 50,
            "position": "bottom",
        }
    },
    {
        "name": "test_width_10",
        "description": "10% width (vertical waveform)",
        "waveform": {
            "width_percent": 10,
            "position": "left",
        }
    },
    {
        "name": "test_width_50",
        "description": "50% width (vertical waveform)",
        "waveform": {
            "width_percent": 50,
            "position": "left",
        }
    },
    
    # Randomization Test
    {
        "name": "test_randomized",
        "description": "Randomized configuration per video",
        "waveform": {
            "randomize": True,
        }
    },
    
    # Complex Combinations
    {
        "name": "test_complex_1",
        "description": "Complex: Top+Bottom, 5 lines, per-line colors, filled style",
        "waveform": {
            "position": "top,bottom",
            "num_lines": 5,
            "line_colors": [
                [0, 255, 0],
                [0, 255, 100],
                [0, 255, 255],
                [255, 0, 255],
                [255, 255, 0],
            ],
            "waveform_style": "filled",
            "height_percent": 20,
        }
    },
    {
        "name": "test_complex_2",
        "description": "Complex: Left+Right, per-line thickness, bars style",
        "waveform": {
            "position": "left,right",
            "num_lines": 4,
            "line_thickness": [18, 15, 12, 10],
            "waveform_style": "bars",
            "width_percent": 25,
            "left_spacing": 30,
            "right_spacing": 30,
        }
    },
    {
        "name": "test_complex_3",
        "description": "Complex: All positions, rainbow colors, dots style",
        "waveform": {
            "position": "top,left,right",
            "num_lines": 6,
            "line_colors": [
                [255, 0, 0],      # Red
                [255, 127, 0],   # Orange
                [255, 255, 0],   # Yellow
                [0, 255, 0],     # Green
                [0, 0, 255],     # Blue
                [127, 0, 255],   # Violet
            ],
            "waveform_style": "dots",
            "height_percent": 15,
            "width_percent": 15,
        }
    },
]


def generate_test_scripts():
    """Generate test scripts and config files for all waveform configurations"""
    scripts_dir = Path("Creations/Scripts/waveform_tests")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    configs_dir = Path("Creations/Configs/waveform_tests")
    configs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[INFO] Generating {len(TEST_CONFIGS)} test configurations...")
    
    for i, test_config in enumerate(TEST_CONFIGS, 1):
        test_name = test_config["name"]
        description = test_config["description"]
        
        # Create test script
        script_path = scripts_dir / f"{test_name}.txt"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(f"{description}\n\n")
            f.write(TEST_SCRIPT_TEMPLATE)
        
        # Create config override
        config_override = {
            "visualization": {
                "style": "waveform",
                "waveform": test_config["waveform"]
            }
        }
        
        config_path = configs_dir / f"{test_name}_config.yaml"
        import yaml
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_override, f, default_flow_style=False, sort_keys=False)
        
        print(f"  [{i:2d}/{len(TEST_CONFIGS)}] {test_name}: {description}")
    
    # Create batch test script
    batch_script = scripts_dir / "run_all_tests.bat"
    with open(batch_script, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("echo Running all waveform tests...\n\n")
        for test_config in TEST_CONFIGS:
            test_name = test_config["name"]
            f.write(f"echo Running {test_name}...\n")
            f.write(f'python -m src.cli.main create "Creations/Scripts/waveform_tests/{test_name}.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/{test_name}_config.yaml"\n')
            f.write("if errorlevel 1 (\n")
            f.write(f"    echo ERROR: {test_name} failed!\n")
            f.write("    pause\n")
            f.write("    exit /b 1\n")
            f.write(")\n")
            f.write("echo.\n")
        f.write("echo All tests completed successfully!\n")
        f.write("pause\n")
    
    # Create test manifest
    manifest = {
        "total_tests": len(TEST_CONFIGS),
        "tests": [
            {
                "name": tc["name"],
                "description": tc["description"],
                "script": f"Creations/Scripts/waveform_tests/{tc['name']}.txt",
                "config": f"Creations/Configs/waveform_tests/{tc['name']}_config.yaml",
            }
            for tc in TEST_CONFIGS
        ]
    }
    
    manifest_path = scripts_dir / "test_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n[OK] Generated {len(TEST_CONFIGS)} test scripts")
    print(f"[OK] Test scripts: {scripts_dir}")
    print(f"[OK] Config overrides: {configs_dir}")
    print(f"[OK] Batch script: {batch_script}")
    print(f"[OK] Manifest: {manifest_path}")


if __name__ == "__main__":
    generate_test_scripts()

