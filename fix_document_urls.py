#!/usr/bin/env python3
"""
Fix document URLs to remove local file paths and replace with proper references
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
DOCUMENTS_DIR = BASE_DIR / "documents"

def fix_url(url):
    """Convert file:// URLs to proper references"""
    if url.startswith("file://"):
        # Extract filename from path
        filename = url.split("/")[-1]

        # Return a reference note instead of broken link
        return f"*[Local document: {filename}]*"
    elif url.startswith("http://") or url.startswith("https://"):
        # Keep web URLs as-is
        return f"[{url}]({url})"
    elif url == "Not available" or url == "#":
        return "*Document URL not available*"
    else:
        # For any other format, treat as unavailable
        return "*Document URL not available*"

def process_document_file(filepath):
    """Process a single document markdown file"""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and replace Access URL lines
    pattern = r'\| \*\*Access URL\*\* \| \[(.*?)\]\((.*?)\) \|'

    def replace_url(match):
        display_text = match.group(1)
        url = match.group(2)

        if url.startswith("file://"):
            # Extract just the filename for display
            filename = url.split("/")[-1]
            return f"| **Access URL** | *Local document: {filename}* |"
        elif url == "#" or display_text == "Not available":
            return "| **Access URL** | *Not publicly available* |"
        else:
            # Keep valid web URLs
            return match.group(0)

    # Replace file URLs
    content = re.sub(pattern, replace_url, content)

    # Also fix any standalone file:// links
    content = re.sub(r'\[([^\]]+)\]\(file://[^\)]+\)', r'*Local document: \1*', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    """Main function to fix all document URLs"""

    print("=" * 50)
    print("Fixing Document URLs")
    print("=" * 50)

    # Process all document markdown files
    fixed_count = 0

    for doc_file in DOCUMENTS_DIR.glob("D*.md"):
        if process_document_file(doc_file):
            print(f"  ✓ Fixed {doc_file.name}")
            fixed_count += 1

    # Also create a reference document explaining document access
    reference_content = """# Document Access Information

## About Document URLs

Many of the documents referenced in this GitBook are from various sources:

### Types of Documents

1. **Publicly Available Documents**
   - These have direct web links that you can click to access
   - Usually from official websites, journals, or repositories

2. **Restricted Access Documents**
   - Academic papers that may require institutional access
   - Government reports with limited distribution
   - Internal organizational documents

3. **Local Reference Documents**
   - Documents that were used in the literature review process
   - Not publicly shareable due to copyright or access restrictions
   - Listed for reference purposes only

### How to Access Documents

For documents marked as "Local document" or "Not publicly available":

1. **Check the citation** - Use the author, title, and year to search for the document
2. **Academic databases** - Try Google Scholar, JSTOR, or institutional libraries
3. **Publisher websites** - Many documents can be found on publisher sites
4. **Contact authors** - Some authors share papers upon request
5. **Institutional access** - Your organization may have subscriptions

### Document Metadata

Even when direct links aren't available, we provide:
- Full citation information
- DOI numbers (when available)
- ISBN/ISSN numbers
- Publication details
- Abstract or summary

This metadata should help you locate the documents through appropriate channels.

---
*Note: This GitBook respects copyright and access restrictions. Documents are referenced for academic and research purposes.*
"""

    reference_file = DOCUMENTS_DIR / "document-access.md"
    with open(reference_file, 'w', encoding='utf-8') as f:
        f.write(reference_content)

    print(f"\n  ✓ Created document-access.md reference file")

    print("\n" + "=" * 50)
    print(f"✨ Fixed {fixed_count} document files")
    print("=" * 50)

if __name__ == "__main__":
    main()