#!/usr/bin/env python3
"""Test that all imports work correctly."""

def test_imports():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        from config import Settings
        print("service-bdd: all imports OK")
        return True
    except ImportError as e:
        print(f"service-bdd: import error - {e}")
        return False

if __name__ == "__main__":
    import sys
    sys.exit(0 if test_imports() else 1)
