import sys
import subprocess
import pkg_resources

print("Checking installed packages...")
installed = [pkg.key for pkg in pkg_resources.working_set]
print(f"Total packages: {len(installed)}")

# Check for specific packages
for pkg in ['edge-tts', 'pygame', 'streamlit']:
    if pkg in installed:
        print(f"✅ {pkg} is installed")
    else:
        print(f"❌ {pkg} is NOT installed")

# Try to import
print("\nTrying to import packages...")
try:
    import edge_tts
    print("✅ edge_tts imports successfully")
except ImportError as e:
    print(f"❌ edge_tts import failed: {e}")

try:
    import pygame
    print("✅ pygame imports successfully")
except ImportError as e:
    print(f"❌ pygame import failed: {e}")
