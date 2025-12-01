#!/usr/bin/env python3
"""
Power System State Estimation Web Application Launcher
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import matplotlib
        import numpy
        import pandas
        import pandapower
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Please install requirements: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment for web application"""
    # Set Flask app environment variables
    os.environ['FLASK_APP'] = 'web_ui.web_app'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Ensure matplotlib uses non-interactive backend
    os.environ['MPLBACKEND'] = 'Agg'
    
    print("✅ Environment configured")

def check_web_app_exists():
    """Check if web app file exists"""
    web_app_path = Path("web_ui/web_app.py")
    if web_app_path.exists():
        print(f"✅ Web app found at: {web_app_path}")
        return True
    else:
        print(f"❌ Web app not found at: {web_app_path}")
        return False

def run_web_app(host="127.0.0.1", port=8000, auto_open=True):
    """Run the Flask web application"""
    
    print("\n🚀 Starting Power System State Estimation Web App")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check if web app exists
    if not check_web_app_exists():
        return False
    
    # Setup environment
    setup_environment()
    
    # Print startup information
    print(f"\n📊 Power System Web Interface")
    print(f"🌐 Host: {host}")
    print(f"🔗 Port: {port}")
    print(f"📍 URL: http://{host}:{port}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print()
    
    # Auto-open browser
    if auto_open:
        print("🔍 Opening web browser in 3 seconds...")
        def open_browser():
            time.sleep(3)
            webbrowser.open(f"http://{host}:{port}")
        
        import threading
        threading.Timer(0, open_browser).start()
    
    try:
        print("🚀 Starting Flask development server...")
        print("   Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the Flask app directly
        from web_ui.web_app import app
        app.run(host=host, port=port, debug=True, use_reloader=True)
        
    except ImportError:
        print("❌ Failed to import web app. Trying alternative method...")
        
        # Alternative: Run via flask command
        try:
            cmd = [
                sys.executable, "-m", "flask", "run",
                "--host", host,
                "--port", str(port),
                "--debug"
            ]
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start web app: {e}")
            return False
            
    except KeyboardInterrupt:
        print("\n\n🛑 Web application stopped by user")
        return True
        
    except Exception as e:
        print(f"❌ Web application error: {e}")
        return False
    
    return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Launch Power System State Estimation Web Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_web_app.py                    # Run on localhost:8000
  python run_web_app.py --port 5000        # Run on port 5000
  python run_web_app.py --host 0.0.0.0     # Listen on all interfaces
  python run_web_app.py --no-browser       # Don't auto-open browser
        """
    )
    
    parser.add_argument(
        "--host", 
        default="127.0.0.1", 
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--no-browser", 
        action="store_true", 
        help="Don't automatically open web browser"
    )
    
    parser.add_argument(
        "--check-only", 
        action="store_true", 
        help="Only check dependencies and exit"
    )
    
    args = parser.parse_args()
    
    # Header
    print("⚡ Power System State Estimation Web Application")
    print("🔬 Advanced Grid Analysis and Visualization Platform")
    print()
    
    if args.check_only:
        print("🔍 Checking dependencies only...")
        if check_dependencies() and check_web_app_exists():
            print("✅ All checks passed - ready to run!")
            return True
        else:
            print("❌ Some checks failed")
            return False
    
    # Run the web application
    success = run_web_app(
        host=args.host,
        port=args.port,
        auto_open=not args.no_browser
    )
    
    if success:
        print("\n✅ Web application session completed")
    else:
        print("\n❌ Web application failed to start")
        sys.exit(1)

if __name__ == "__main__":
    main()