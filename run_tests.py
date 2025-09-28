import subprocess
import sys
import argparse
import shutil
import os
import platform

def ensure_venv():
    #  virtual environment 
    venv_dir = ".venv"
    if not os.path.isdir(venv_dir):
        print("No virtualenv found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("Virtualenv created at .venv")

    # Determine the path to the venv python
    if platform.system() == "Windows":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    # Install reqs
    if os.path.exists("requirements.txt"):
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    return venv_python

def run_pytest(python_exec, args):
    cmd = [python_exec, "-m", "pytest"] + args
    print(f"\n=== Running: {' '.join(cmd)} ===\n")
    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True
        )
        # summary  from stdout
        for line in result.stdout.splitlines():
            if line.strip().startswith("===") or line.strip().startswith("TOTAL") or "coverage" in line.lower() or "passed" in line.lower():
                print(line)
        return True
    except subprocess.CalledProcessError as e:
        print("Tests failed")
        for line in (e.stdout or "").splitlines():
            if line.strip().startswith("===") or line.strip().startswith("TOTAL") or "coverage" in line.lower() or "failed" in line.lower():
                print(line)
        if e.stderr:
            print(e.stderr.splitlines()[-1])  # last error line
        return False

def clean_artifacts():
    for path in [".pytest_cache", "htmlcov", ".coverage", "coverage.xml"]:
        shutil.rmtree(path, ignore_errors=True)
        try: os.remove(path)
        except FileNotFoundError: pass
    print("Cleaned test artifacts")
    return True

def main():
    parser = argparse.ArgumentParser(description="Customer Order API Test Runner")
    parser.add_argument("command", nargs="?", default="all",
                        choices=["all","fast","models","routes","services","init","coverage","clean"],
                        help="Test command to run (default: all)")
    args = parser.parse_args()

    python_exec = ensure_venv()

    pytest_args = {
        "all": ["tests/", "--cov=app", "--cov-report=html", "--cov-report=term-missing", "--cov-fail-under=70", "-q", "--disable-warnings"],
        "fast": ["tests/", "-q", "--disable-warnings"],
        "models": ["tests/test_models.py", "-q", "--disable-warnings"],
        "routes": ["tests/test_routes.py", "-q", "--disable-warnings"],
        "services": ["tests/test_services.py", "-q", "--disable-warnings"],
        "init": ["tests/test_init.py", "-q", "--disable-warnings"],
        "coverage": ["tests/", "--cov=app", "--cov-report=html", "--cov-report=term-missing", "-q", "--disable-warnings"]
    }

    if args.command == "clean":
        success = clean_artifacts()
    else:
        success = run_pytest(python_exec, pytest_args[args.command])

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
