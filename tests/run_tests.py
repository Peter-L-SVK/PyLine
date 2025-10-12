#!/usr/bin/env python3
"""
Enhanced PyLine Test Runner
Provides detailed output with colors and failure information
"""

import unittest
import sys
import os
from pathlib import Path

# Add color support
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def run_all_tests():
    """Run all tests with enhanced output"""
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Discover all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,  # Maximum verbosity
        failfast=False,
        buffer=False
    )
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}🚀 PyLine Test Suite{Colors.END}")
    print(f"{Colors.BLUE}═" * 60 + Colors.END)
    
    result = runner.run(suite)
    
    # Summary with colors
    print(f"\n{Colors.BOLD}📊 TEST SUMMARY:{Colors.END}")
    print(f"{Colors.BLUE}─" * 40 + Colors.END)
    
    if result.wasSuccessful():
        print(f"{Colors.GREEN}✅ ALL TESTS PASSED!{Colors.END}")
        print(f"   Tests run: {result.testsRun}")
        return 0
    else:
        print(f"{Colors.RED}❌ SOME TESTS FAILED:{Colors.END}")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        
        # Show failures in detail
        if result.failures:
            print(f"\n{Colors.YELLOW}🔴 FAILURES:{Colors.END}")
            for test, traceback in result.failures:
                print(f"{Colors.RED}   ✗ {test}{Colors.END}")
                # Extract first line of error message
                error_line = traceback.split('\n')[-2] if len(traceback.split('\n')) > 1 else traceback
                print(f"      {error_line}")
                
        if result.errors:
            print(f"\n{Colors.RED}🚨 ERRORS:{Colors.END}")
            for test, traceback in result.errors:
                print(f"{Colors.RED}   ⚠ {test}{Colors.END}")
                error_line = traceback.split('\n')[-2] if len(traceback.split('\n')) > 1 else traceback
                print(f"      {error_line}")
        
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
