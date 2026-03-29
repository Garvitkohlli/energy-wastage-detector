# Dependencies Documentation

## Complete List of Dependencies

### Core Web Framework
- **Flask 3.0.0** - Web framework for the application
- **Werkzeug 3.0.0** - WSGI utility library (Flask dependency)
- **Gunicorn 21.2.0** - Production WSGI server

### Machine Learning
- **NumPy 1.24.3** - Numerical computing library
- **scikit-learn 1.3.0** - Machine learning algorithms (Isolation Forest, SVM, LOF)
- **Joblib 1.3.2** - Model serialization and persistence

### Data Processing
- **Pandas 2.0.3** - Data manipulation and analysis

### Visualization
- **Matplotlib 3.7.2** - Plotting library (optional, for future use)

### Utilities
- **python-dateutil 2.8.2** - Date/time utilities

### Built-in Python Modules (No Installation Required)
- **sqlite3** - Database operations
- **os** - Operating system interface
- **sys** - System-specific parameters
- **json** - JSON encoding/decoding
- **threading** - Thread-based parallelism
- **time** - Time access and conversions
- **random** - Random number generation
- **datetime** - Date and time handling
- **collections** - Container datatypes
- **contextlib** - Context manager utilities

## Installation

### Quick Install
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python check_dependencies.py
```

### Complete Setup and Verification
```bash
python setup_and_verify.py
```

## What Each Package Does

### Flask
- Handles HTTP requests and responses
- Renders HTML templates
- Provides routing for API endpoints
- Manages sessions and cookies

### NumPy
- Powers array operations for ML features
- Provides mathematical functions
- Handles numerical computations efficiently

### scikit-learn
- **Isolation Forest** - Anomaly detection algorithm
- **One-Class SVM** - Support Vector Machine for outlier detection
- **Local Outlier Factor** - Density-based anomaly detection
- **StandardScaler** - Feature normalization
- **Metrics** - Model evaluation (accuracy, precision, recall, F1)

### Joblib
- Saves trained ML models to disk
- Loads models for reuse
- Efficient serialization of large numpy arrays

### Pandas
- Data manipulation and analysis
- DataFrame operations (optional, for future enhancements)

### Matplotlib
- Creates charts and visualizations (optional)
- Currently used for potential future features

### Gunicorn
- Production-ready WSGI server
- Handles multiple concurrent requests
- Better performance than Flask's built-in server

### SQLite3 (Built-in)
- Stores all application data
- No separate database server needed
- File-based database (energy_monitor.db)

## Version Compatibility

### Python Version
- **Minimum**: Python 3.8
- **Recommended**: Python 3.10 or higher
- **Tested on**: Python 3.10, 3.11

### Operating Systems
- ✓ Windows
- ✓ Linux
- ✓ macOS

## Troubleshooting

### Common Issues

#### 1. scikit-learn Installation Fails
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Then install scikit-learn
pip install scikit-learn==1.3.0
```

#### 2. NumPy Installation Issues
```bash
# Install NumPy separately first
pip install numpy==1.24.3

# Then install other packages
pip install -r requirements.txt
```

#### 3. Gunicorn Not Available on Windows
Gunicorn doesn't work on Windows. For development on Windows, use:
```bash
python app_advanced.py
```

For production on Windows, use:
```bash
waitress-serve --host=0.0.0.0 --port=5000 app_advanced:app
```

Add to requirements.txt for Windows:
```
waitress==2.1.2
```

#### 4. Permission Errors
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Development vs Production

### Development
```bash
pip install -r requirements.txt
python app_advanced.py
```

### Production (Linux/macOS)
```bash
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 app_advanced:app
```

### Production (Windows)
```bash
pip install -r requirements.txt
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app_advanced:app
```

## Virtual Environment (Recommended)

### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Deactivate
```bash
deactivate
```

## Checking What's Installed

### List All Packages
```bash
pip list
```

### Check Specific Package
```bash
pip show flask
pip show scikit-learn
```

### Export Current Environment
```bash
pip freeze > requirements_current.txt
```

## Updating Dependencies

### Update All Packages
```bash
pip install --upgrade -r requirements.txt
```

### Update Specific Package
```bash
pip install --upgrade flask
```

### Check for Outdated Packages
```bash
pip list --outdated
```

## Minimal Installation (Core Only)

If you want to run with minimal dependencies:

```txt
Flask==3.0.0
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2
```

This excludes:
- Pandas (not currently used)
- Matplotlib (optional visualization)
- Gunicorn (use Flask dev server instead)

## Additional Tools (Optional)

### For Development
```bash
pip install pytest  # Testing
pip install black   # Code formatting
pip install flake8  # Linting
```

### For Database Management
```bash
pip install sqlite-web  # Web-based SQLite browser
```

### For API Testing
```bash
pip install requests  # HTTP library
pip install httpie    # Command-line HTTP client
```

## File Sizes

Approximate download sizes:
- Flask: ~1 MB
- NumPy: ~15 MB
- scikit-learn: ~30 MB
- Pandas: ~40 MB
- Matplotlib: ~50 MB

Total: ~140 MB

## Support

If you encounter any dependency issues:

1. Check Python version: `python --version`
2. Update pip: `python -m pip install --upgrade pip`
3. Use virtual environment
4. Run verification: `python setup_and_verify.py`
5. Check individual imports: `python check_dependencies.py`

## License Information

All dependencies are open-source with permissive licenses:
- Flask: BSD License
- NumPy: BSD License
- scikit-learn: BSD License
- Pandas: BSD License
- Matplotlib: PSF License
