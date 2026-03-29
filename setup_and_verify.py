"""
Setup and Verification Script
Checks environment and verifies all components are ready
"""
import sys
import os
import subprocess

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_python_version():
    """Check Python version"""
    print_header("PYTHON VERSION CHECK")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        return False
    
    print("✓ Python version is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    print_header("PIP CHECK")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        print(result.stdout.strip())
        print("✓ pip is available")
        return True
    except Exception as e:
        print(f"✗ pip not found: {e}")
        return False

def check_requirements_file():
    """Check if requirements.txt exists"""
    print_header("REQUIREMENTS FILE CHECK")
    if os.path.exists('requirements.txt'):
        print("✓ requirements.txt found")
        with open('requirements.txt', 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
            print(f"\nPackages listed: {len(lines)}")
            for line in lines:
                print(f"  - {line}")
        return True
    else:
        print("✗ requirements.txt not found")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print_header("DEPENDENCY CHECK")
    
    dependencies = {
        'flask': 'Flask',
        'werkzeug': 'Werkzeug',
        'gunicorn': 'Gunicorn',
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn',
        'joblib': 'Joblib',
        'pandas': 'Pandas',
        'matplotlib': 'Matplotlib',
        'dateutil': 'python-dateutil'
    }
    
    missing = []
    installed = []
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name}")
            installed.append(name)
        except ImportError:
            print(f"✗ {name} - NOT INSTALLED")
            missing.append(name)
    
    print(f"\nInstalled: {len(installed)}/{len(dependencies)}")
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        return False
    
    return True

def check_project_files():
    """Check if all required project files exist"""
    print_header("PROJECT FILES CHECK")
    
    required_files = {
        'app_advanced.py': 'Main application',
        'database.py': 'Database module',
        'ml_models.py': 'ML models module',
        'requirements.txt': 'Dependencies list',
        'templates/base.html': 'Base template',
        'templates/index.html': 'Home page',
        'templates/dashboard.html': 'Dashboard page',
        'templates/analytics.html': 'Analytics page',
        'templates/iot_dashboard.html': 'IoT dashboard'
    }
    
    all_exist = True
    
    for file, desc in required_files.items():
        if os.path.exists(file):
            print(f"✓ {file:30} - {desc}")
        else:
            print(f"✗ {file:30} - MISSING")
            all_exist = False
    
    return all_exist

def check_database():
    """Check database initialization"""
    print_header("DATABASE CHECK")
    
    try:
        import database as db
        
        # Check if database file exists
        if os.path.exists('energy_monitor.db'):
            print("✓ Database file exists")
            
            # Try to connect
            import sqlite3
            conn = sqlite3.connect('energy_monitor.db')
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"✓ Database has {len(tables)} tables")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  - {table}: {count} records")
            
            conn.close()
        else:
            print("⚠ Database file not found (will be created on first run)")
        
        return True
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print_header("INSTALLING DEPENDENCIES")
    
    response = input("\nInstall missing dependencies? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            print("\nRunning: pip install -r requirements.txt\n")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            
            if result.returncode == 0:
                print("✓ Dependencies installed successfully")
                return True
            else:
                print(f"✗ Installation failed:\n{result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Installation error: {e}")
            return False
    else:
        print("Skipping installation")
        return False

def main():
    """Main verification routine"""
    print("\n" + "="*70)
    print("  ENERGY MONITOR - SETUP AND VERIFICATION")
    print("="*70)
    
    checks = []
    
    # Run all checks
    checks.append(("Python Version", check_python_version()))
    checks.append(("pip", check_pip()))
    checks.append(("Requirements File", check_requirements_file()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("Project Files", check_project_files()))
    checks.append(("Database", check_database()))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:25} {status}")
    
    print(f"\nPassed: {passed}/{total}")
    
    # Offer to install if dependencies missing
    if not checks[3][1]:  # Dependencies check failed
        if install_dependencies():
            print("\nRe-checking dependencies...")
            if check_dependencies():
                print("✓ All dependencies now installed")
    
    print("\n" + "="*70)
    
    if passed == total:
        print("✓ ALL CHECKS PASSED - SYSTEM READY")
        print("\nTo start the application, run:")
        print("  python app_advanced.py")
    else:
        print("⚠ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the application")
    
    print("="*70 + "\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
