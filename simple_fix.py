#!/usr/bin/env python3
"""Simple script to replace all API URLs with production URL"""

import os
import re

def fix_file(filepath):
    """Replace all API URL patterns with production URL"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Replace various patterns
    patterns = [
        (r'import\.meta\.env\.VITE_API_BASE_URL \|\| \'http://127\.0\.0\.1:8000/api\'', "'https://web-scraper-api-vnue.onrender.com/api'"),
        (r'\$\{import\.meta\.env\.VITE_API_BASE_URL \|\| \'http://127\.0\.0\.1:8000/api\'\}', 'https://web-scraper-api-vnue.onrender.com/api'),
        (r'import\.meta\.env\.VITE_API_BASE_URL\?\?\.replace\(\'/api\', \'\'\) \|\| \'http://127\.0\.0\.1:8000\'', "'https://web-scraper-api-vnue.onrender.com'"),
        (r'\$\{import\.meta\.env\.VITE_API_BASE_URL\?\?\.replace\(\'/api\', \'\'\) \|\| \'http://127\.0\.0\.1:8000\'\}', 'https://web-scraper-api-vnue.onrender.com'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    """Fix all files"""
    svelte_dir = "/Users/user/Desktop/web scraper/svelte-dashboard/src"
    fixed_count = 0

    for root, dirs, files in os.walk(svelte_dir):
        for file in files:
            if file.endswith(('.svelte', '.js', '.ts')):
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    fixed_count += 1

    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main()