# JS-Leaker Optimization TODO - Make Production-Ready

## Implementation Steps (In Order)

### Phase 1: Logging & Emojis [✅]
- [✅] utils.py: Bulletproof ASCII-only log_print (no dupes/crashes)
- [✅] Remove ALL 22+ emojis from ALL log_print calls (main,collector,downloader,scanner,utils)
- [✅] utils.py: Clean generate_severity_report (no emojis/symbols)

### Phase 2: Collector Fixes [✅]
- [✅] collector.py: Add .js regex fallback for links without script tags
- [✅] Limit total JS stricter; ASCII-safe logs

### Phase 3: Downloader Improvements [✅]
- [✅] downloader.py: Content-hash dupes (data/hashes.json)
- [✅] Strict URL validation (only .js ending)
- [✅] ASCII-safe logs

### Phase 4: Scanner Enhancements [ ]
- [ ] scanner.py: Expand patterns (Stripe,GCP,GitHub,etc.)
- [ ] Fix context/line numbers (proper split)
- [ ] Add threading for file scanning
- [ ] Rescan Base64 decoded fully
- [ ] Improved dedup + sorting

**Status:** Phase 4

**Status:** Phase 2

### Phase 2: Collector Fixes [ ]
- [ ] collector.py: Add .js regex fallback for links without script tags
- [ ] Limit total JS stricter; ASCII-safe logs

### Phase 3: Downloader Improvements [ ]
- [ ] downloader.py: Content-hash dupes (data/hashes.json)
- [ ] Strict URL validation (only .js ending)
- [ ] ASCII-safe logs

### Phase 4: Scanner Enhancements [ ]
- [ ] scanner.py: Expand patterns (Stripe,GCP,GitHub,etc.)
- [ ] Fix context/line numbers (proper split)
- [ ] Add threading for file scanning
- [ ] Rescan Base64 decoded fully
- [ ] Improved dedup + sorting

### Phase 5: Main Flow & Progress [ ]
- [ ] main.py: Progress counters (Collecting X, Downloading Y/Z, Scanning N/M)
- [ ] Pass threads everywhere; graceful no-JS
- [ ] ASCII-safe logs

### Phase 6: Testing & Final [ ]
- [ ] Test full pipeline: `python main.py -u https://httpbin.org/html -t 3`
- [ ] Verify Windows encoding
- [ ] Update README.md if needed
- [ ] Mark complete

**Status:** Phase 1 logging fixed, emojis next

### Phase 2: Collector Fixes [ ]
- [ ] collector.py: Add .js regex fallback for links without script tags
- [ ] Limit total JS stricter; ASCII-safe logs

### Phase 3: Downloader Improvements [ ]
- [ ] downloader.py: Content-hash dupes (data/hashes.json)
- [ ] Strict URL validation (only .js ending)
- [ ] ASCII-safe logs

### Phase 4: Scanner Enhancements [ ]
- [ ] scanner.py: Expand patterns (Stripe,GCP,GitHub,etc.)
- [ ] Fix context/line numbers (proper split)
- [ ] Add threading for file scanning
- [ ] Rescan Base64 decoded fully
- [ ] Improved dedup + sorting

### Phase 5: Main Flow & Progress [ ]
- [ ] main.py: Progress counters (Collecting X, Downloading Y/Z, Scanning N/M)
- [ ] Pass threads everywhere; graceful no-JS
- [ ] ASCII-safe logs

### Phase 6: Testing & Final [ ]
- [ ] Test full pipeline: `python main.py -u https://httpbin.org/html -t 3`
- [ ] Verify Windows encoding
- [ ] Update README.md if needed
- [ ] Mark complete

**Status:** Starting Phase 1
