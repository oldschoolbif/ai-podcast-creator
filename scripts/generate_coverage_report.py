#!/usr/bin/env python3
"""Generate coverage and metrics report."""
import xml.etree.ElementTree as ET
import os
import sys

def main():
    coverage_file = "coverage.xml"
    if not os.path.exists(coverage_file):
        print("Coverage file not found. Run tests with coverage first.")
        return
    
    tree = ET.parse(coverage_file)
    root = tree.getroot()
    
    line_rate = float(root.attrib['line-rate']) * 100
    branch_rate = float(root.attrib.get('branch-rate', 0)) * 100
    lines_valid = int(root.attrib['lines-valid'])
    lines_covered = int(root.attrib['lines-covered'])
    
    print("=== Coverage Report ===")
    print(f"Line Coverage: {line_rate:.2f}%")
    print(f"Branch Coverage: {branch_rate:.2f}%")
    print(f"Total Lines: {lines_valid:,}")
    print(f"Lines Covered: {lines_covered:,}")
    print(f"Lines Missing: {lines_valid - lines_covered:,}")
    print()
    
    # Coverage by package
    packages = root.findall('.//package')
    if packages:
        print("=== Coverage by Package ===")
        low_coverage = []
        for pkg in packages:
            pkg_rate = float(pkg.attrib['line-rate']) * 100
            pkg_name = pkg.attrib['name']
            if pkg_rate < 100.0:
                low_coverage.append((pkg_name, pkg_rate))
        
        if low_coverage:
            low_coverage.sort(key=lambda x: x[1])
            for name, rate in low_coverage[:10]:  # Top 10 lowest
                print(f"{name}: {rate:.1f}%")
        else:
            print("All packages at 100% coverage!")

if __name__ == "__main__":
    main()

