#!/usr/bin/env python3
"""
downloader.py - Concurrent JS file downloader with limits, dupes skip.
"""

import os
import re
import hashlib
import json
import requests
from urllib.parse import urlparse
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import log_print, print_info, print_success, print_warning, print_error, TIMEOUT, MAX_FILE_SIZE_MB, MAX_CONCURRENT

class JSDownloader:
    """
    Concurrent JS downloader with size limits, content-hash dupe skip.
    """
    
    MAX_CONTENT_SIZE = int(MAX_FILE_SIZE_MB * 1024 * 1024)
    HASHES_FILE = 'data/hashes.json'
    
    def __init__(self):
        self.session = requests.Session()
        # Set a common UA to reduce blocks
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; JS-Leaker/1.0)'
        })
    
    def download(self, js_urls: List[str], download_dir: str, max_workers: int = None):
        """
        Concurrent download with limits, dupes.
        """
        os.makedirs(download_dir, exist_ok=True)
        existing_hashes = self._load_hashes()

        workers = MAX_CONCURRENT if not max_workers else max(1, min(max_workers, MAX_CONCURRENT))
        futures = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for url in js_urls:
                future = executor.submit(self._download_single, url, download_dir, existing_hashes)
                futures.append(future)
        
        downloaded = 0
        skipped = 0
        errors = 0
        new_hashes = {}
        for future in as_completed(futures):
            result, hash_val = future.result()
            if result == 'downloaded':
                downloaded += 1
                if hash_val:
                    new_hashes[hash_val] = True
            elif result == 'skipped':
                skipped += 1
            else:
                errors += 1
        
        # Update hashes
        existing_hashes.update(new_hashes)
        self._save_hashes(existing_hashes)
        
        print_success(f'Download complete: {downloaded} new, {skipped} skipped, {errors} errors')
    
    def _download_single(self, url: str, download_dir: str, existing_hashes: Dict[str, bool]) -> tuple:
        """
        Download single file, return (status, hash).
        """
        try:
            # Strict JS URL validation
            if not re.search(r'\.js(?:\?[^\s]*)?$', url, re.I):
                print_warning(f'Skipped non-JS URL: {url[:80]}...')
                return 'skipped', None
            
            parsed = urlparse(url)
            base = os.path.basename(parsed.path) or f'script_{hashlib.sha256(url.encode()).hexdigest()[:8]}.js'
            filepath = os.path.join(download_dir, base)
            
            # Content hash check
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in existing_hashes:
                return 'skipped', None
            
            response = self.session.get(url, timeout=TIMEOUT, stream=True)
            response.raise_for_status()
            
            content_length = int(response.headers.get('content-length', 0))
            if content_length > self.MAX_CONTENT_SIZE:
                print_warning(f'Skipped large file {base} ({content_length//1024//1024}MB)')
                return 'skipped', None
            
            content = response.content
            content_hash = hashlib.md5(content).hexdigest()
            
            # Final dupe check by content
            if content_hash in existing_hashes:
                return 'skipped', None
            
            with open(filepath, 'wb') as f:
                f.write(content)
            
            print_info(f'Downloaded: {base}')
            return 'downloaded', content_hash
            
        except requests.exceptions.Timeout:
            print_warning(f'Timeout: {url[:80]}...')
            return 'error', None
        except requests.exceptions.RequestException as e:
            print_error(f'Request failed: {str(e)[:80]}')
            return 'error', None
        except Exception as e:
            print_error(f'Download error: {str(e)}')
            return 'error', None
    
    def _load_hashes(self) -> Dict[str, bool]:
        """Load existing content hashes."""
        try:
            if os.path.exists(self.HASHES_FILE):
                with open(self.HASHES_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_hashes(self, hashes: Dict[str, bool]):
        """Save content hashes."""
        try:
            dirn = os.path.dirname(self.HASHES_FILE)
            if dirn:
                os.makedirs(dirn, exist_ok=True)
            with open(self.HASHES_FILE, 'w', encoding='utf-8') as f:
                json.dump(hashes, f)
        except Exception as e:
            print_error(f'Hash save error: {e}')

