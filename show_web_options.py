#!/usr/bin/env python3
"""
Display all available options for running the web application
"""

import os
import sys
from pathlib import Path

def show_web_app_options():
    """Display all available methods to run the web application"""
    
    print("⚡ Power System State Estimation Web Application")
    print("🌐 Multiple Launch Options Available")
    print("=" * 70)
    
    # Check current directory
    cwd = Path.cwd()
    web_app_path = cwd / "web_ui" / "web_app.py"
    
    if not web_app_path.exists():
        print("❌ Error: web_ui/web_app.py not found in current directory")
        print(f"📍 Current directory: {cwd}")
        print("💡 Make sure you're in the gridsimvk project root directory")
        return False
    
    print(f"✅ Web application found at: {web_app_path}")
    print(f"📍 Working directory: {cwd}")
    print()
    
    # Show all available launch methods
    print("🚀 LAUNCH METHODS:")
    print("-" * 70)
    
    print("1️⃣  PYTHON LAUNCHER (Recommended)")
    print("   📋 Full-featured launcher with options")
    print("   🔧 Commands:")
    print("      python3 run_web_app.py                    # Default settings")
    print("      python3 run_web_app.py --port 5000        # Custom port")
    print("      python3 run_web_app.py --host 0.0.0.0     # Network access")
    print("      python3 run_web_app.py --no-browser       # No auto-open")
    print("      python3 run_web_app.py --check-only       # Dependency check")
    print()
    
    print("2️⃣  SHELL SCRIPT (Unix/Linux/macOS)")
    print("   📋 Quick launcher with auto-setup")
    print("   🔧 Commands:")
    print("      ./launch_web.sh                           # Quick launch")
    print()
    
    print("3️⃣  BATCH FILE (Windows)")
    print("   📋 Windows-compatible launcher")
    print("   🔧 Commands:")
    print("      launch_web.bat                            # Windows launch")
    print()
    
    print("4️⃣  DIRECT FLASK (Manual)")
    print("   📋 Direct Flask development server")
    print("   🔧 Commands:")
    print("      export FLASK_APP=web_ui.web_app")
    print("      export FLASK_ENV=development")
    print("      flask run --host=127.0.0.1 --port=8000 --debug")
    print()
    
    print("5️⃣  PYTHON DIRECT (Advanced)")
    print("   📋 Direct Python execution")
    print("   🔧 Commands:")
    print("      python3 web_ui/web_app.py                 # Direct execution")
    print()
    
    # Show system information
    print("💻 SYSTEM INFORMATION:")
    print("-" * 70)
    print(f"   🐍 Python: {sys.version.split()[0]}")
    print(f"   📁 Working Directory: {cwd}")
    print(f"   🌐 Default URL: http://127.0.0.1:8000")
    print()
    
    # Show virtual environment status
    if 'VIRTUAL_ENV' in os.environ:
        venv_path = os.environ['VIRTUAL_ENV']
        print(f"   ✅ Virtual Environment Active: {venv_path}")
    else:
        venv_dir = cwd / "venv"
        if venv_dir.exists():
            print(f"   ⚠️  Virtual Environment Available but Not Active")
            print(f"      Activate with: source venv/bin/activate")
        else:
            print(f"   ❌ No Virtual Environment Found")
            print(f"      Create with: python3 -m venv venv")
    print()
    
    # Show quick start recommendation
    print("⭐ QUICK START RECOMMENDATION:")
    print("-" * 70)
    
    if 'VIRTUAL_ENV' not in os.environ and (cwd / "venv").exists():
        print("   1. Activate virtual environment:")
        print("      source venv/bin/activate")
        print()
        print("   2. Launch web application:")
        print("      python3 run_web_app.py")
    else:
        print("   🚀 Ready to launch:")
        print("      python3 run_web_app.py")
    
    print()
    print("📖 For detailed information, see: WEB_APP_README.md")
    print("=" * 70)
    
    return True

def main():
    """Main function"""
    if not show_web_app_options():
        sys.exit(1)

if __name__ == "__main__":
    main()