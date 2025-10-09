#!/usr/bin/env python3
"""Script to replace import.meta.env calls with centralized config import"""

import os
import re

def fix_file(filepath):
    """Fix import.meta.env calls in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Check if file already imports config
    has_config_import = 'from \'../lib/config.js\'' in content or 'from "./config.js"' in content

    # Replace import.meta.env patterns
    content = re.sub(
        r'\$\{import\.meta\.env\.VITE_API_BASE_URL \|\| \'http://127\.0\.0\.1:8000/api\'\}',
        '${API_BASE_URL}',
        content
    )

    # If we made replacements and don't have config import, add it
    if content != original_content and not has_config_import:
        # Add import after other imports
        import_pattern = r'(import.*from.*[\'"][^\'"]*.js[\'"];?\s*\n)'
        if re.search(import_pattern, content):
            # Add after last import
            content = re.sub(
                r'(import.*from.*[\'"][^\'"]*.js[\'"];?\s*\n)(?!.*import)',
                r'\1  import { API_BASE_URL } from \'../lib/config.js\';\n',
                content
            )
        else:
            # Add at beginning of script
            content = re.sub(
                r'(<script>\s*\n)',
                r'\1  import { API_BASE_URL } from \'../lib/config.js\';\n',
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