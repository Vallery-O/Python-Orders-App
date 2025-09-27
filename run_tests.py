import subprocess
import sys
import os
import argparse

def run_command(command, description):
    print(f"=== {description} ===")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True,capture_output=True, text=True)
        print("SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def run_all_tests():
    # tests with coverage
    return run_command(
        "pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=70 -v",
        "Running all tests with coverage"
    )

def run_fast_tests():
    #Run tests quickly without 
    return run_command(
        "pytest tests/ -v",
        "Running fast tests (no coverage)"
    )

def run_specific_test(test_type):
    """Run specific test category"""
    test_files = {
        'models': 'tests/test_models.py',
        'routes': 'tests/test_routes.py',
        'services': 'tests/test_services.py',
        'init': 'tests/test_init.py'
    }
    
    if test_type in test_files:
        return run_command(
            f"pytest {test_files[test_type]} -v",
            f"Running {test_type} tests"
        )
    else:
        print(f"Unknown test type: {test_type}")
        return False

def run_coverage_only():
    """Run coverage report only"""
    return run_command(
        "pytest tests/ --cov=app --cov-report=html --cov-report=term-missing",
        "Generating coverage report"
    )

def clean_test_artifacts():
    """Clean up test artifacts"""
    return run_command(
        "rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml",
        "Cleaning test artifacts"
    )

def show_status():
    """Show testing environment status"""
    commands = [
        ("python --version", "Python Version"),
        ("pytest --version", "Pytest Version"),
        ("pip list | grep -E '(pytest|cov)'", "Testing Packages")
    ]
    
    print("=== Testing Environment Status ===")
    for cmd, desc in commands:
        run_command(cmd, desc)

def main():
    parser = argparse.ArgumentParser(description="Customer Order API Test Runner")
    parser.add_argument('command', nargs='?', default='all', 
        choices=['all', 'fast', 'models', 'routes', 'services', 'init', 'coverage', 'clean', 'status'], 
        help='Test command to run (default: all)')
    
    args = parser.parse_args()
    
    commands = {
        'all': run_all_tests,
        'fast': run_fast_tests,
        'models': lambda: run_specific_test('models'),
        'routes': lambda: run_specific_test('routes'),
        'services': lambda: run_specific_test('services'),
        'init': lambda: run_specific_test('init'),
        'coverage': run_coverage_only,
        'clean': clean_test_artifacts,
        'status': show_status
    }
    
    success = commands[args.command]()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()