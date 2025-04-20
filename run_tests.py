"""
Script to run tests and generate reports in timestamped folders
"""
import os
import sys
import datetime
import subprocess
from pathlib import Path

def create_test_results_dir():
    """Create a timestamped directory for test results"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path("test_results")
    result_dir = base_dir / timestamp
    
    # Create directories
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / "coverage").mkdir(exist_ok=True)
    
    return result_dir

def run_tests(result_dir: Path):
    """Run tests with different reporting options"""
    test_file = "tests/test_config_integration.py"
    
    # Commands to run
    commands = [
        # Basic test with verbose output
        f"python3 -m pytest {test_file} -v --capture=tee-sys > {result_dir}/test_output.txt",
        
        # Generate HTML report
        f"python3 -m pytest {test_file} -v --html={result_dir}/report.html",
        
        # Generate coverage report
        f"python3 -m pytest {test_file} -v --cov=src --cov-report=html:{result_dir}/coverage",
        
        # Generate JUnit XML report
        f"python3 -m pytest {test_file} -v --junitxml={result_dir}/test-results.xml"
    ]
    
    # Run each command
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"Successfully ran: {cmd}")
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {cmd}")
            print(f"Error: {str(e)}")

def main():
    """Main function to run tests and generate reports"""
    print("Starting test run...")
    
    # Create results directory
    result_dir = create_test_results_dir()
    print(f"Created test results directory: {result_dir}")
    
    # Run tests
    run_tests(result_dir)
    
    print(f"\nTest run completed. Results are stored in: {result_dir}")
    print("\nGenerated reports:")
    print(f"- Test output: {result_dir}/test_output.txt")
    print(f"- HTML report: {result_dir}/report.html")
    print(f"- Coverage report: {result_dir}/coverage/index.html")
    print(f"- JUnit XML report: {result_dir}/test-results.xml")

if __name__ == "__main__":
    main() 