#!/usr/bin/env python3
"""Test that all imports work correctly."""

def test_imports():
    try:
        import numpy
        from vosk import Model
        from fastapi import FastAPI
        from pydantic import BaseModel
        from config import Settings
        print("service-vocal: all imports OK")
        return True
    except ImportError as e:
        print(f"service-vocal: import error - {e}")
        return False

if __name__ == "__main__":
    import sys
    sys.exit(0 if test_imports() else 1)
