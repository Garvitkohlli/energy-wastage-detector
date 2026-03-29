"""
Dependency Checker
Verifies all required packages are installed
"""
import sys

def check_import(module_name, package_name=None):
    """Try to import a module and report status"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {package_name:30} - OK")
        return True
    except ImportError as e:
        print(f"✗ {package_name:30} - MISSING ({e})")
        return False

def main():
    print("\n" + "="*70)
    print("  DEPENDENCY CHECKER")
    print("="*70 + "\n")
    
    all_ok = True
    
    # Core Python (built-in)
    print("Built-in Python Modules:")
    all_ok &= check_import("sqlite3", "sqlite3 (built-in)")
    all_ok &= check_import("os", "os (built-in)")
    all_ok &= check_import("sys", "sys (built-in)")
    all_ok &= check_import("json", "json (built-in)")
    all_ok &= check_import("threading", "threading (built-in)")
    all_ok &= check_import("time", "time (built-in)")
    all_ok &= check_import("random", "random (built-in)")
    all_ok &= check_import("datetime", "datetime (built-in)")
    all_ok &= check_import("collections", "collections (built-in)")
    all_ok &= check_import("contextlib", "contextlib (built-in)")
    
    print("\nWeb Framework:")
    all_ok &= check_import("flask", "Flask")
    all_ok &= check_import("werkzeug", "Werkzeug")
    all_ok &= check_import("gunicorn", "Gunicorn")
    
    print("\nMachine Learning:")
    all_ok &= check_import("numpy", "NumPy")
    all_ok &= check_import("sklearn", "scikit-learn")
    all_ok &= check_import("joblib", "Joblib")
    
    print("\nData Processing:")
    all_ok &= check_import("pandas", "Pandas")
    
    print("\nVisualization:")
    all_ok &= check_import("matplotlib", "Matplotlib")
    
    print("\nUtilities:")
    all_ok &= check_import("dateutil", "python-dateutil")
    
    print("\n" + "="*70)
    
    if all_ok:
        print("✓ ALL DEPENDENCIES INSTALLED")
        print("="*70 + "\n")
        return 0
    else:
        print("✗ SOME DEPENDENCIES MISSING")
        print("\nTo install missing packages, run:")
        print("  pip install -r requirements.txt")
        print("="*70 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
