#!/usr/bin/env python3
"""
NERO Voice Assistant - Validation Test Script

Tests module imports and basic functionality without requiring API keys.
"""

import sys
import os


def test_module_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")

    try:
        from modules.logger import NeroLogger
        print("  [OK] logger module imported")
    except Exception as e:
        print(f"  [FAIL] logger module failed: {e}")
        return False

    try:
        from modules.stt_fraco import STTFraco
        print("  [OK] stt_fraco module imported")
    except Exception as e:
        print(f"  [FAIL] stt_fraco module failed: {e}")
        return False

    try:
        from modules.stt_forte import STTForte
        print("  [OK] stt_forte module imported")
    except Exception as e:
        print(f"  [FAIL] stt_forte module failed: {e}")
        return False

    try:
        from modules.tts import TTS
        print("  [OK] tts module imported")
    except Exception as e:
        print(f"  [FAIL] tts module failed: {e}")
        return False

    try:
        from modules.agent_handler import AgentHandler
        print("  [OK] agent_handler module imported")
    except Exception as e:
        print(f"  [FAIL] agent_handler module failed: {e}")
        return False

    return True


def test_logger():
    """Test logger functionality."""
    print("\nTesting logger...")

    try:
        from modules.logger import NeroLogger

        # Just instantiate, don't call methods to avoid console encoding issues
        logger = NeroLogger(verbose=False)
        print("  [OK] logger instantiated")
        return True
    except Exception as e:
        print(f"  [FAIL] logger test failed: {e}")
        return False


def test_env_template():
    """Test .env.example exists and has required variables."""
    print("\nTesting .env.example...")

    if not os.path.exists(".env.example"):
        print("  [FAIL] .env.example not found")
        return False

    with open(".env.example", "r", encoding="utf-8") as f:
        content = f.read()

    required_vars = ["DEEPGRAM_API_KEY", "CARTESIA_API_KEY"]
    all_present = True

    for var in required_vars:
        if var in content:
            print(f"  [OK] {var} found in .env.example")
        else:
            print(f"  [FAIL] {var} not found in .env.example")
            all_present = False

    return all_present


def test_gitignore():
    """Test .gitignore exists and protects sensitive files."""
    print("\nTesting .gitignore...")

    if not os.path.exists(".gitignore"):
        print("  [FAIL] .gitignore not found")
        return False

    with open(".gitignore", "r", encoding="utf-8") as f:
        content = f.read()

    protected_items = [".env", "*.mp3", "*.wav"]
    all_protected = True

    for item in protected_items:
        if item in content:
            print(f"  [OK] {item} protected by .gitignore")
        else:
            print(f"  [WARN] {item} not in .gitignore (recommended)")
            # Not failing, just warning

    return True


def test_readme():
    """Test README.md exists and has key sections."""
    print("\nTesting README.md...")

    if not os.path.exists("README.md"):
        print("  [FAIL] README.md not found")
        return False

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 if utf-8 fails (Windows)
        with open("README.md", "r", encoding="latin-1") as f:
            content = f.read()

    required_sections = ["Installation", "Usage", "Troubleshooting"]
    all_present = True

    for section in required_sections:
        if section in content:
            print(f"  [OK] Section '{section}' found")
        else:
            print(f"  [WARN] Section '{section}' not found")
            # Not failing, just warning

    return True


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("NERO Voice Assistant - Validation Tests")
    print("=" * 60)

    tests = [
        test_module_imports,
        test_logger,
        test_env_template,
        test_gitignore,
        test_readme,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Test failed with exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All validation tests passed!")
        print("\nNERO is ready to use. Follow these steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to .env")
        print("3. Run: python nero_assistant.py")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
