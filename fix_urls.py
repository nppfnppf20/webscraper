#!/usr/bin/env python3
"""Script to fix all hardcoded localhost URLs in Svelte files"""

import os
import re

def fix_file(filepath):
    """Fix hardcoded URLs in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Replace hardcoded localhost URLs with environment variable
    content = re.sub(
        r"'http://127\.0\.0\.1:8000/api([^']*)'",
        r"`${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'}\1`",
        content
    )

    # Replace fetch calls to localhost
    content = re.sub(
        r'fetch\(\'http://127\.0\.0\.1:8000([^\']*)\'\)',
        r"fetch(`${import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://127.0.0.1:8000'}\1`)",
        content
    )

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    """Fix all Svelte files"""
    svelte_dir = "/Users/user/Desktop/web scraper/svelte-dashboard/src"
    fixed_count = 0

    for root, dirs, files in os.walk(svelte_dir):
        for file in files:
            if file.endswith('.svelte'):
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    fixed_count += 1

    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main()