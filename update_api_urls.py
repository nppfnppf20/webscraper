#!/usr/bin/env python3
"""
Update all hardcoded API URLs in Svelte components to use environment-aware configuration
"""
import os
import re

def update_svelte_files():
    """Update all .svelte files to use API_BASE import"""
    svelte_dir = "svelte-dashboard/src"

    for root, dirs, files in os.walk(svelte_dir):
        for file in files:
            if file.endswith('.svelte'):
                file_path = os.path.join(root, file)
                update_file(file_path)

def update_file(file_path):
    """Update a single file"""
    print(f"Updating {file_path}...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Check if file already has API_BASE import
        has_api_import = 'API_BASE' in content or 'from ../lib/api' in content

        # Replace hardcoded URLs
        content = re.sub(
            r"'http://127\.0\.0\.1:8000(/api[^']*)'",
            r"`${API_BASE}\1`",
            content
        )

        # Replace refresh URLs (without /api prefix)
        content = re.sub(
            r"'http://127\.0\.0\.1:8000(/api/refresh/[^']*)'",
            r"`${API_BASE.replace('/api', '')}\1`",
            content
        )

        # Add API_BASE import if needed and content was changed
        if content != original_content and not has_api_import:
            # Find the import section
            import_match = re.search(r'(<script>\s*\n)', content)
            if import_match:
                # Add API_BASE import after <script>
                import_line = "  import { API_BASE } from '../lib/api.js';\n"
                content = content[:import_match.end()] + import_line + content[import_match.end():]

        # Write updated content
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Updated {file_path}")
        else:
            print(f"  - No changes needed for {file_path}")

    except Exception as e:
        print(f"  ✗ Error updating {file_path}: {e}")

if __name__ == "__main__":
    update_svelte_files()
    print("✓ API URL update complete!")