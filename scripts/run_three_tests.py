#!/usr/bin/env python3
"""
Run 3 specific waveform position tests: bottom, middle, top
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_evaluation_tests import (
    run_evaluation_test,
    TEST_SCRIPT,
    create_config_file,
    console,
    RICH_AVAILABLE
)

if RICH_AVAILABLE and console:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

# Only the 3 tests we want
THREE_TESTS = [
    {
        "name": "eval_01_bottom_default",
        "description": "Bottom position - default settings",
        "waveform": {
            "position": "bottom",
        }
    },
    {
        "name": "eval_03_middle_default",
        "description": "Middle position - default settings",
        "waveform": {
            "position": "middle",
        }
    },
    {
        "name": "eval_02_top_default",
        "description": "Top position - default settings",
        "waveform": {
            "position": "top",
        }
    },
]

def main():
    """Run the 3 requested tests"""
    if not TEST_SCRIPT.exists():
        print(f"[ERROR] Test script not found: {TEST_SCRIPT}")
        return
    
    print(f"\n[TEST] Running 3 waveform position tests")
    print(f"Test script: {TEST_SCRIPT}\n")
    
    results = []
    
    if RICH_AVAILABLE and console:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            expand=True
        ) as progress:
            overall_task = progress.add_task("[bold cyan]Overall Progress", total=len(THREE_TESTS))
            
            for i, test_config in enumerate(THREE_TESTS, 1):
                test_task = progress.add_task(f"[{i}/{len(THREE_TESTS)}] {test_config['name']}", total=100)
                
                success = run_evaluation_test(test_config, i, len(THREE_TESTS), progress, test_task)
                results.append({
                    "test": test_config["name"],
                    "description": test_config["description"],
                    "success": success,
                })
                
                progress.update(overall_task, advance=1)
                progress.remove_task(test_task)
                
                # Stop on first failure
                if not success:
                    console.print(f"\n[bold red]TEST FAILED - STOPPING[/bold red]")
                    console.print(f"[bold]Failed test:[/bold] {test_config['name']}")
                    break
    else:
        # Fallback output
        for i, test_config in enumerate(THREE_TESTS, 1):
            print(f"\n[{i}/{len(THREE_TESTS)}] {test_config['name']}")
            success = run_evaluation_test(test_config, i, len(THREE_TESTS))
            results.append({
                "test": test_config["name"],
                "description": test_config["description"],
                "success": success,
            })
            
            if not success:
                print(f"\n[STOP] Test failed - stopping")
                break
    
    # Summary
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    print(f"\n{'='*70}")
    print(f"Test Results Summary")
    print(f"{'='*70}")
    print(f"Total: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print(f"\nFailed Tests:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['test']}: {r['description']}")
    
    print(f"\nOutput files: Creations/MMedia/")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()

