#!/usr/bin/env python3
"""
Test Runner Script - Esegue la test suite completa per ATK-Pro v2.0
"""

import subprocess
import sys
from pathlib import Path

def main():
    workspace_root = Path(__file__).parent.parent
    
    print("=" * 80)
    print("ATK-Pro v2.0 - Test Suite Completa")
    print("=" * 80)
    print()
    
    # Esegui i test con unittest
    print("Esecuzione dei test...")
    print("-" * 80)
    
    test_file = workspace_root / 'tests' / 'test_multilingual_support.py'
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=str(workspace_root),
        capture_output=False
    )
    
    print()
    print("=" * 80)
    if result.returncode == 0:
        print("✓ TUTTI I TEST PASSATI CORRETTAMENTE")
    else:
        print("✗ ALCUNI TEST NON HANNO SUPERATO")
    print("=" * 80)
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
