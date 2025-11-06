"""
Quick setup script for D-ID AI avatar generation
D-ID provides professional-quality talking avatars with natural movements
"""

import os
from pathlib import Path

def setup_did():
    """Set up D-ID API for AI-generated talking avatars."""
    print("=== D-ID Avatar Setup ===\n")
    
    print("D-ID provides professional talking avatars with:")
    print("  ✅ Natural movements and expressions")
    print("  ✅ High-quality lip-sync")
    print("  ✅ Professional appearance")
    print("  ✅ Easy integration (already in code!)\n")
    
    # Check for existing API key
    env_file = Path(".env")
    api_key = None
    
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("DID_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    
    if api_key and api_key not in ["", "your_key_here"]:
        print(f"✅ D-ID API key already configured!\n")
        print("To test:")
        print("  1. Update config.yaml: avatar.engine = 'did'")
        print("  2. Run: python -m src.cli.main create script.txt --avatar -o test_did\n")
        return
    
    print("📝 Setup Steps:\n")
    print("1. Sign up at: https://studio.d-id.com/")
    print("2. Get your API key from the dashboard")
    print("3. Run this command (replace YOUR_KEY):")
    print('   echo "DID_API_KEY=YOUR_KEY" >> .env')
    print("\n4. Update config.yaml:")
    print("   avatar:")
    print("     engine: \"did\"\n")
    
    print("💰 Pricing:")
    print("  - Pay-as-you-go: ~$0.10-$0.50 per video")
    print("  - Subscription plans available")
    print("  - Free tier for testing")
    print("\n  Full pricing: https://studio.d-id.com/pricing\n")
    
    print("🎯 Once set up, D-ID will generate professional talking avatars!")
    print("   Much better than static image + lip-sync.\n")

if __name__ == "__main__":
    setup_did()

