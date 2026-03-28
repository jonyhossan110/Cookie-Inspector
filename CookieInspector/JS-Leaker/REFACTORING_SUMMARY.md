# JS-Leaker Refactoring Summary

## Overview
The JS-Leaker tool has been successfully refactored with two major feature additions:

### ✅ FEATURE 1: Enhanced Output File Structure (COMPLETED)
- **Domain-Specific Folder Creation**: JavaScript files are now downloaded and saved in domain-specific folders
- **Path Structure**: `output/[domain_name]/[original_filename].js`
- **Error Handling**: Failed downloads are logged and skipped; scanning continues without interruption
- **Automatic Folder Creation**: The system automatically creates necessary directory structures using `os.makedirs()`

### ✅ FEATURE 2: Professional ASCII Art Dashboard (COMPLETED)
- **Colorized Design**: Multi-color ASCII art logo using CYAN for "JS-" and RED for "LEAKER"
- **Author Attribution**: "Created By" section with author information and LinkedIn profile
- **Cross-Platform Support**: Uses `colorama` for Windows/Mac/Linux compatibility
- **Fallback Display**: Plain ASCII art displays on systems without color support

---

## Files Modified

### 1. **utils.py** ✏️
**New Function Added**: `print_dashboard()`

```python
def print_dashboard():
    """Print a professional colorized ASCII art dashboard for JS-Leaker."""
    # Displays colorized logo with author information
    # Fallback to plain ASCII if colorama unavailable
```

**Features**:
- CYAN colored borders and "JS-" text
- RED colored "LEAKER" text
- YELLOW "JavaScript Secret Scanner & Extractor" tagline
- GREEN borders around author section
- Author: Md. Jony Hassain (HexaCyberLab)
- LinkedIn: https://www.linkedin.com/in/md-jony-hassain/

---

### 2. **main.py** 🔧
**Changes Made**:

#### New Function: `extract_domain_from_url()`
Extracts clean domain names from URLs:
```python
def extract_domain_from_url(url: str) -> str:
    """Extract domain name from URL for folder creation.
    
    Examples:
    - https://example.com -> example.com
    - https://subdomain.example.com -> example.com
    - https://example.co.uk -> example.co.uk
    """
```

#### Updated Function: `download_and_save()`
Now accepts `domain` parameter and saves files to domain-specific folders:
```python
def download_and_save(url: str, target_dir: str, domain: str, 
                      seen_hashes: set, timeout: int = 15) -> str:
    """Download JS and save to: target_dir/[domain]/[filename].js"""
```

**Key Changes**:
- Added `domain` parameter
- Creates domain-specific folder inside `target_dir`
- Maintains duplicate detection with hash tracking
- Error handling for download failures

#### Updated Function: `main()`
Orchestrates the new workflow:

1. **Dashboard Display**: Calls `print_dashboard()` immediately at startup
2. **Domain Extraction**: Extracts domain from target URL
3. **Folder Structure**: Creates output folder for domain-specific JS files
4. **Parallel Downloads**: Downloads external JS to `output/[domain]/` folder
5. **Enhanced Logging**: Shows domain and output folder information
6. **Success Messages**: Confirms JavaScript files saved to domain folder

**New Workflow**:
```
1. Display Dashboard (Colorized ASCII Art)
2. Parse Arguments
3. Extract Domain from URL
4. Create Directory Structure (output/[domain]/)
5. Collect JavaScript Files (Static + Dynamic)
6. Download External JS to output/[domain]/
7. Scan All Files for Secrets
8. Generate Reports
9. Confirm Files Saved
```

#### Removed Function: `print_banner()`
Old simple ASCII banner has been replaced with the professional `print_dashboard()` function

---

### 3. **requirements.txt** ✓
**Status**: No changes required
- `colorama>=0.4.6` already present
- All dependencies are compatible

---

## Usage Instructions

### Running the Tool

```bash
python main.py -u https://example.com -t 6 -o output/scan_report.txt
```

**Command Arguments**:
- `-u, --url`: Target URL (required)
- `-t, --threads`: Number of worker threads (default: 4)
- `-o, --output-file`: Output file for detailed report (default: `output/scan_report.txt`)

### Output Structure

After running with `example.com`:

```
output/
├── example.com/              # Domain-specific folder
│   ├── subdomain__abc123__script.js
│   ├── cdn__def456__jquery.min.js
│   └── ... (all external JS files)
├── scan_report.txt          # Detailed findings report
└── report.txt               # Severity summary
```

---

## Key Improvements

✅ **Organizational**: JavaScript files are grouped by domain for easy management
✅ **Professional**: Eye-catching colorized dashboard on startup
✅ **Robust**: Error handling for download failures doesn't interrupt the scan
✅ **Cross-Platform**: Works on Windows, Mac, and Linux
✅ **Backward Compatible**: Existing reports (`scan_report.txt`, `report.txt`) remain unchanged
✅ **Scalable**: Supports multiple concurrent downloads with configurable thread count

---

## Technical Details

### Dependencies
- `colorama>=0.4.6` for cross-platform color support
- All other dependencies unchanged (requests, beautifulsoup4, playwright, etc.)

### Error Handling
- Failed downloads are logged but don't halt execution
- Scanning continues with downloaded files
- Network timeouts set to 15 seconds per file
- Duplicate files detected and skipped via SHA-1 hashing

### Performance
- Parallel downloading with configurable thread count
- Parallel secret scanning
- Efficient memory management with content hashing

---

## Verification Checklist

- ✅ Dashboard displays with colors on startup
- ✅ Domain extracted correctly from URLs
- ✅ Domain-specific folder created automatically
- ✅ JavaScript files downloaded to `output/[domain]/`
- ✅ Existing reports generated as before
- ✅ Error handling for failed downloads
- ✅ Cross-platform compatibility verified

---

## Questions or Issues?

If you encounter any issues:
1. Verify `colorama` is installed: `pip install -r requirements.txt`
2. Check file permissions in the `output/` directory
3. Ensure the target URL is accessible
4. Review logs in `js-leaker.log`

---

**Refactoring Date**: March 24, 2026
**Status**: ✅ Complete and Ready for Production
