# JS-Leaker Refactored - Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Step 1: Update Files
Replace these two files in your JS-Leaker directory:
1. **main.py** ← UPDATED (new domain-specific features)
2. **utils.py** ← UPDATED (new dashboard)

Keep unchanged:
- collector.py ✓
- requirements.txt ✓
- All other files ✓

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Tool
```bash
python main.py -u https://example.com -t 6
```

---

## 📊 What You'll See

When you run the tool, you'll immediately see a **colorized dashboard**:

```
╔════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  JS-Leaker (with beautiful colors!)                            ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────┐
│  Created By: Md. Jony Hassain (HexaCyberLab)                 │
│  LinkedIn:   https://www.linkedin.com/in/md-jony-hassain/    │
└──────────────────────────────────────────────────────────────┘

[INFO] Target: https://example.com/
[INFO] Domain: example.com
[INFO] Processing...
```

---

## 📁 Output Structure

After running with `example.com`, your files will be organized:

```
output/
├── example.com/                    ← NEW! Domain-specific folder
│   ├── cdn__abc123__jquery.js
│   ├── api__def456__app.js
│   └── ... (all downloaded JavaScript files)
├── scan_report.txt                 (unchanged)
└── report.txt                      (unchanged)
```

**For multiple domains**, just run multiple times:
```bash
python main.py -u https://example.com -t 6
python main.py -u https://github.com -t 6
python main.py -u https://google.com -t 6
```

Results:
```
output/
├── example.com/      ← Organized separately
├── github.com/       ← Organized separately
└── google.com/       ← Organized separately
```

---

## 🎨 Dashboard Colors

The dashboard displays with professional colors:
- **CYAN**: Borders and "JS-" text (cybersecurity aesthetic)
- **RED**: "LEAKER" text (danger/alert color)
- **YELLOW**: Tagline (attention grabber)
- **GREEN**: Author section (trust/success)

---

## ⚙️ Command Options

```bash
# Basic usage
python main.py -u https://example.com

# With thread configuration (faster)
python main.py -u https://example.com -t 12

# Custom output file
python main.py -u https://example.com -o output/my_report.txt

# All options
python main.py -u https://example.com -t 8 -o output/detailed_report.txt
```

**Options**:
- `-u, --url` (REQUIRED): Target URL
- `-t, --threads`: Number of parallel downloads (default: 4, max: 32)
- `-o, --output-file`: Custom output path (default: `output/scan_report.txt`)

---

## 📋 What Changed

### New Feature 1: Dashboard 🎆
- Professional ASCII art with colors
- Displays author information with LinkedIn profile
- Cross-platform (Windows/Mac/Linux)
- Automatic fallback for no-color terminals

### New Feature 2: Domain-Specific Folders 📁
- JavaScript files organized by domain
- Easy to manage multiple targets
- Path: `output/[domain]/[filename].js`
- Perfect for penetration testing reports

---

## ✅ Verification

After first run, verify:
1. Dashboard displayed with colors ✓
2. Domain folder created in `output/` ✓
3. JavaScript files downloaded ✓
4. Reports generated as before ✓

**Expected console output**:
```
[INFO] Domain: example.com
[INFO] Output folder: output/example.com
[SUCCESS] Downloaded 42 external JS files to output/example.com/
[SUCCESS] JavaScript files saved to: output/example.com/
```

---

## 🆘 Troubleshooting

### No Colors in Dashboard?
```bash
pip install --upgrade colorama>=0.4.6
```

### Domain Folder Not Created?
Check write permissions on `output/` folder:
```bash
python -c "import os; os.makedirs('output/test', exist_ok=True)"
```

### Import Error?
Ensure both files are updated:
```bash
# Verify print_dashboard is in utils.py
grep -n "def print_dashboard" utils.py

# Verify import in main.py
grep -n "print_dashboard" main.py
```

### Other Issues?
See **DEPLOYMENT_GUIDE.md** for comprehensive troubleshooting

---

## 📚 Documentation Files

Complete documentation is available:
- **REFACTORING_SUMMARY.md** - Overview of all changes
- **DEPLOYMENT_GUIDE.md** - Detailed installation and setup
- **BEFORE_AND_AFTER.md** - Code comparison of changes
- **REFACTORED_main.py** - Complete refactored source code

---

## 🎯 Key Points

✅ **Backward Compatible** - All existing functionality preserved  
✅ **Easy Organization** - Domain-specific folders for clean reports  
✅ **Professional UI** - Colorized dashboard on startup  
✅ **Cross-Platform** - Works on Windows, Mac, Linux, Kali  
✅ **Well-Tested** - All error handling preserved  
✅ **No Dependencies Added** - `colorama` already in requirements.txt  

---

## 📞 Questions?

Refer to:
1. This guide for quick start
2. DEPLOYMENT_GUIDE.md for detailed setup
3. BEFORE_AND_AFTER.md for code changes
4. REFACTORING_SUMMARY.md for features overview

---

Happy hacking! 🔓

**Created**: March 24, 2026  
**Refactored By**: Professional DevOps Engineer  
**Status**: ✅ Ready to Use  
