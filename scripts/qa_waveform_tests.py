#!/usr/bin/env python3
"""
QA Testing for Waveform Visualizations
Validates waveform configurations and generates test reports

All test outputs are saved to Creations/MMedia/ with descriptive names matching test names.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np


def validate_video_output(video_path: Path, expected_config: Dict) -> Dict:
    """Validate video output matches expected configuration"""
    if not video_path.exists():
        return {
            "valid": False,
            "error": f"Video file not found: {video_path}",
        }
    
    # Check file size
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    if file_size_mb < 0.1:
        return {
            "valid": False,
            "error": f"Video file too small: {file_size_mb:.2f} MB",
        }
    
    # Try to open video with OpenCV
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return {
                "valid": False,
                "error": "Cannot open video file",
            }
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Read a few frames to check for waveform presence
        waveform_detected = False
        frames_checked = 0
        max_frames_to_check = min(30, frame_count)
        
        for i in range(0, max_frames_to_check, 5):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                frames_checked += 1
                # Check for non-black pixels (waveform should be visible)
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                non_black_pixels = np.sum(gray > 10)  # Threshold for "non-black"
                total_pixels = gray.shape[0] * gray.shape[1]
                non_black_ratio = non_black_pixels / total_pixels
                
                # If more than 1% of pixels are non-black, waveform likely present
                if non_black_ratio > 0.01:
                    waveform_detected = True
                    break
        
        cap.release()
        
        return {
            "valid": True,
            "file_size_mb": file_size_mb,
            "frame_count": frame_count,
            "fps": fps,
            "resolution": f"{width}x{height}",
            "duration_seconds": frame_count / fps if fps > 0 else 0,
            "waveform_detected": waveform_detected,
            "frames_checked": frames_checked,
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Error analyzing video: {str(e)}",
        }


def run_single_test(test_name: str, script_path: Path, config_path: Optional[Path] = None) -> Dict:
    """Run a single waveform test and return results
    
    All outputs are saved to Creations/MMedia/ with descriptive names.
    """
    print(f"\n[TEST] Running: {test_name}")
    
    # Expected output path - ensure all test files go to MMedia
    output_dir = Path("Creations/MMedia")
    output_dir.mkdir(parents=True, exist_ok=True)
    # Use descriptive test name directly (no _output suffix needed)
    output_name = test_name
    
    # Build command
    cmd = [
        "python", "-m", "src.cli.main", "create",
        str(script_path),
        "--visualize",
        "--background",
        "--avatar",
        "--quality", "fastest",
        "--output", output_name,
    ]
    
    if config_path:
        cmd.extend(["--config", str(config_path)])
    
    # Run command
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        
        # Find output video
        output_video = None
        for ext in [".mp4", ".avi", ".mov"]:
            candidate = output_dir / f"{output_name}{ext}"
            if candidate.exists():
                output_video = candidate
                break
        
        validation = None
        if output_video:
            validation = validate_video_output(output_video, {})
        
        return {
            "test_name": test_name,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout[-500:] if result.stdout else "",  # Last 500 chars
            "stderr": result.stderr[-500:] if result.stderr else "",  # Last 500 chars
            "output_video": str(output_video) if output_video else None,
            "validation": validation,
        }
    except subprocess.TimeoutExpired:
        return {
            "test_name": test_name,
            "success": False,
            "error": "Test timed out after 5 minutes",
        }
    except Exception as e:
        return {
            "test_name": test_name,
            "success": False,
            "error": str(e),
        }


def run_qa_suite():
    """Run QA suite for all waveform tests"""
    manifest_path = Path("Creations/Scripts/waveform_tests/test_manifest.json")
    
    if not manifest_path.exists():
        print(f"[ERROR] Test manifest not found: {manifest_path}")
        print("Run scripts/generate_waveform_tests.py first")
        return
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    print(f"[QA] Running {manifest['total_tests']} waveform tests...")
    
    results = []
    for test_info in manifest["tests"]:
        test_name = test_info["name"]
        script_path = Path(test_info["script"])
        config_path = Path(test_info["config"]) if test_info.get("config") else None
        
        if not script_path.exists():
            results.append({
                "test_name": test_name,
                "success": False,
                "error": f"Script not found: {script_path}",
            })
            continue
        
        result = run_single_test(test_name, script_path, config_path)
        results.append(result)
        
        # Print immediate result
        if result.get("success"):
            print(f"[OK] {test_name} passed")
        else:
            print(f"[FAIL] {test_name} failed")
            if "error" in result:
                print(f"      Error: {result['error']}")
    
    # Generate report
    report = {
        "total_tests": len(results),
        "passed": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results,
    }
    
    # Save report
    report_path = Path("Creations/MMedia/qa_waveform_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n[QA SUMMARY]")
    print(f"Total: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Report: {report_path}")
    
    return report


if __name__ == "__main__":
    run_qa_suite()

