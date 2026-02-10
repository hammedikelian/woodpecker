#!/usr/bin/env python3
"""Test that all imports work correctly."""


def test_imports():
    try:
        import numpy
        from config import Settings
        from fastapi import FastAPI
        from pydantic import BaseModel
        from vosk import Model

        print("service-vocal: all imports OK")
        return True
    except ImportError as e:
        print(f"service-vocal: import error - {e}")
        return False


if __name__ == "__main__":
    import sys

    sys.exit(0 if test_imports() else 1)
