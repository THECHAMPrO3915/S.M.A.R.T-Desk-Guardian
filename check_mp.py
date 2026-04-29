import mediapipe as mp
import os

print("--- MediaPipe Diagnostic ---")
print(f"MediaPipe File Path: {mp.__file__}")

# Check if 'solutions' exists in the actual module
if hasattr(mp, 'solutions'):
    print("SUCCESS: 'solutions' attribute found.")
else:
    print("FAILURE: 'solutions' attribute NOT found.")
    print("Reason: Python is likely loading a local file named 'mediapipe.py' instead of the library.")