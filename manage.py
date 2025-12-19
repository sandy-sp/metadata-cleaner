#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
import argparse
import platform

# Constants
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def log(msg, color=RESET):
    print(f"{color}{msg}{RESET}")

def run_command(command, cwd=None, exit_on_fail=True):
    """Run a shell command and optionally exit on failure."""
    log(f"🚀 Running: {' '.join(command)}", BOLD)
    try:
        subprocess.check_call(command, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ Command failed: {' '.join(command)}", RED)
        if exit_on_fail:
            sys.exit(e.returncode)
        return False

def check_command_exists(cmd):
    return shutil.which(cmd) is not None

def install():
    """Install dependencies and check system tools."""
    log("📦 Starting installation...", GREEN)
    
    # 1. Check/Install Poetry
    if not check_command_exists("poetry"):
        log("⚠️ Poetry not found. Please install Poetry first: https://python-poetry.org/docs/", YELLOW)
        sys.exit(1)
        # Note: Auto-installing poetry is risky across platforms (win/mac/linux differences), 
        # simpler to ask user to have the package manager installed.
    else:
        log("✅ Poetry is installed.", GREEN)

    # 2. Install Project Dependencies
    log("📥 Installing project dependencies...", GREEN)
    run_command(["poetry", "install"])

    # 3. Check System Dependencies (ffmpeg, exiftool)
    sys_deps = ["ffmpeg", "exiftool"]
    missing = []
    for dep in sys_deps:
        if check_command_exists(dep):
            log(f"✅ System check: {dep} is found.", GREEN)
        else:
            log(f"❌ System check: {dep} is MISSING.", RED)
            missing.append(dep)
    
    if missing:
        log(f"\n⚠️ Missing system tools: {', '.join(missing)}", YELLOW)
        if platform.system() == "Linux":
            log("   Run: sudo apt install " + " ".join(missing), BOLD)
        elif platform.system() == "Darwin":
            log("   Run: brew install " + " ".join(missing), BOLD)
        elif platform.system() == "Windows":
            log("   Install via choco or download binaries.", BOLD)
        log("\nNote: The application may still run, but some features will be disabled.", YELLOW)
    
    log("\n✅ Installation steps completed.", GREEN)

def test():
    """Run tests via pytest."""
    log("🧪 Running tests...", GREEN)
    run_command(["poetry", "run", "pytest"])

def lint():
    """Run linting checks (flake8)."""
    log("🔍 Running linting (flake8)...", GREEN)
    # Check if flake8 is available in project
    run_command(["poetry", "run", "flake8", "m_c"])

def check():
    """Run security checks (pip-audit, safety)."""
    log("🛡️ Running security checks...", GREEN)
    
    # pip-audit
    if run_command(["poetry", "run", "pip-audit"], exit_on_fail=False):
        log("✅ pip-audit passed.", GREEN)
    else:
        log("⚠️ pip-audit issues found.", YELLOW)

    # safety
    # Safety might not be in dev dependencies, checking...
    # Assuming user wants same logic as script
    if run_command(["poetry", "run", "safety", "check"], exit_on_fail=False):
        log("✅ safety check passed.", GREEN)
    else:
         log("⚠️ safety check found issues.", YELLOW)

def clean():
    """Remove temporary build artifacts."""
    log("🧹 Cleaning up...", GREEN)
    patterns = ["build", "dist", "*.egg-info", "__pycache__", ".pytest_cache", ".coverage"]
    
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d in ["build", "dist", "__pycache__", ".pytest_cache"] or d.endswith(".egg-info"):
                path = os.path.join(root, d)
                log(f"   Removing directory: {path}")
                shutil.rmtree(path, ignore_errors=True)
        
        for f in files:
             if f.endswith(".pyc") or f == ".coverage":
                path = os.path.join(root, f)
                log(f"   Removing file: {path}")
                os.remove(path)
    
    log("✅ Clean complete.", GREEN)

def main():
    parser = argparse.ArgumentParser(description="Metadata Cleaner Task Runner")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    subparsers.add_parser("install", help="Install dependencies and check system tools")
    subparsers.add_parser("test", help="Run tests")
    subparsers.add_parser("lint", help="Run code linting")
    subparsers.add_parser("check", help="Run security checks")
    subparsers.add_parser("clean", help="Clean build artifacts")
    
    args = parser.parse_args()
    
    if args.command == "install":
        install()
    elif args.command == "test":
        test()
    elif args.command == "lint":
        lint()
    elif args.command == "check":
        check()
    elif args.command == "clean":
        clean()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
