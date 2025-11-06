@echo off
echo Running all waveform tests...

echo Running test_graininess_opencv_2x...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_graininess_opencv_2x.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_graininess_opencv_2x_config.yaml"
if errorlevel 1 (
    echo ERROR: test_graininess_opencv_2x failed!
    pause
    exit /b 1
)
echo.
echo Running test_graininess_opencv_4x...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_graininess_opencv_4x.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_graininess_opencv_4x_config.yaml"
if errorlevel 1 (
    echo ERROR: test_graininess_opencv_4x failed!
    pause
    exit /b 1
)
echo.
echo Running test_position_top...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_top.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_top_config.yaml"
if errorlevel 1 (
    echo ERROR: test_position_top failed!
    pause
    exit /b 1
)
echo.
echo Running test_position_bottom...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_bottom.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_bottom_config.yaml"
if errorlevel 1 (
    echo ERROR: test_position_bottom failed!
    pause
    exit /b 1
)
echo.
echo Running test_position_middle...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_middle.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_middle_config.yaml"
if errorlevel 1 (
    echo ERROR: test_position_middle failed!
    pause
    exit /b 1
)
echo.
echo Running test_position_top_bottom...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_top_bottom.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_top_bottom_config.yaml"
if errorlevel 1 (
    echo ERROR: test_position_top_bottom failed!
    pause
    exit /b 1
)
echo.
echo Running test_position_left...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_left.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_left_config.yaml"
if errorlevel 1 (
    echo ERROR: test_position_left failed!
    pause
    exit /b 1
)
echo.
echo Running test_position_right...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_right.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_right_config.yaml"
if errorlevel 1 (
    echo ERROR: test_position_right failed!
    pause
    exit /b 1
)
echo.
echo Running test_position_left_right...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_left_right.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_left_right_config.yaml"
if errorlevel 1 (
    echo ERROR: test_position_left_right failed!
    pause
    exit /b 1
)
echo.
echo Running test_position_all_three...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_position_all_three.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_position_all_three_config.yaml"
if errorlevel 1 (
    echo ERROR: test_position_all_three failed!
    pause
    exit /b 1
)
echo.
echo Running test_lines_1...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_lines_1.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_lines_1_config.yaml"
if errorlevel 1 (
    echo ERROR: test_lines_1 failed!
    pause
    exit /b 1
)
echo.
echo Running test_lines_5...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_lines_5.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_lines_5_config.yaml"
if errorlevel 1 (
    echo ERROR: test_lines_5 failed!
    pause
    exit /b 1
)
echo.
echo Running test_lines_10...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_lines_10.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_lines_10_config.yaml"
if errorlevel 1 (
    echo ERROR: test_lines_10 failed!
    pause
    exit /b 1
)
echo.
echo Running test_thickness_per_line...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_thickness_per_line.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_thickness_per_line_config.yaml"
if errorlevel 1 (
    echo ERROR: test_thickness_per_line failed!
    pause
    exit /b 1
)
echo.
echo Running test_colors_per_line...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_colors_per_line.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_colors_per_line_config.yaml"
if errorlevel 1 (
    echo ERROR: test_colors_per_line failed!
    pause
    exit /b 1
)
echo.
echo Running test_colors_rainbow...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_colors_rainbow.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_colors_rainbow_config.yaml"
if errorlevel 1 (
    echo ERROR: test_colors_rainbow failed!
    pause
    exit /b 1
)
echo.
echo Running test_style_continuous...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_style_continuous.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_style_continuous_config.yaml"
if errorlevel 1 (
    echo ERROR: test_style_continuous failed!
    pause
    exit /b 1
)
echo.
echo Running test_style_bars...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_style_bars.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_style_bars_config.yaml"
if errorlevel 1 (
    echo ERROR: test_style_bars failed!
    pause
    exit /b 1
)
echo.
echo Running test_style_dots...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_style_dots.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_style_dots_config.yaml"
if errorlevel 1 (
    echo ERROR: test_style_dots failed!
    pause
    exit /b 1
)
echo.
echo Running test_style_filled...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_style_filled.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_style_filled_config.yaml"
if errorlevel 1 (
    echo ERROR: test_style_filled failed!
    pause
    exit /b 1
)
echo.
echo Running test_opacity_50...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_opacity_50.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_opacity_50_config.yaml"
if errorlevel 1 (
    echo ERROR: test_opacity_50 failed!
    pause
    exit /b 1
)
echo.
echo Running test_opacity_75...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_opacity_75.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_opacity_75_config.yaml"
if errorlevel 1 (
    echo ERROR: test_opacity_75 failed!
    pause
    exit /b 1
)
echo.
echo Running test_height_10...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_height_10.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_height_10_config.yaml"
if errorlevel 1 (
    echo ERROR: test_height_10 failed!
    pause
    exit /b 1
)
echo.
echo Running test_height_50...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_height_50.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_height_50_config.yaml"
if errorlevel 1 (
    echo ERROR: test_height_50 failed!
    pause
    exit /b 1
)
echo.
echo Running test_width_10...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_width_10.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_width_10_config.yaml"
if errorlevel 1 (
    echo ERROR: test_width_10 failed!
    pause
    exit /b 1
)
echo.
echo Running test_width_50...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_width_50.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_width_50_config.yaml"
if errorlevel 1 (
    echo ERROR: test_width_50 failed!
    pause
    exit /b 1
)
echo.
echo Running test_randomized...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_randomized.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_randomized_config.yaml"
if errorlevel 1 (
    echo ERROR: test_randomized failed!
    pause
    exit /b 1
)
echo.
echo Running test_complex_1...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_complex_1.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_complex_1_config.yaml"
if errorlevel 1 (
    echo ERROR: test_complex_1 failed!
    pause
    exit /b 1
)
echo.
echo Running test_complex_2...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_complex_2.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_complex_2_config.yaml"
if errorlevel 1 (
    echo ERROR: test_complex_2 failed!
    pause
    exit /b 1
)
echo.
echo Running test_complex_3...
python -m src.cli.main create "Creations/Scripts/waveform_tests/test_complex_3.txt" --visualize --background --avatar --quality fastest --config "Creations/Configs/waveform_tests/test_complex_3_config.yaml"
if errorlevel 1 (
    echo ERROR: test_complex_3 failed!
    pause
    exit /b 1
)
echo.
echo All tests completed successfully!
pause
