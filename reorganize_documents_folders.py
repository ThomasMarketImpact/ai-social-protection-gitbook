#!/usr/bin/env python3
"""
Reorganize documents into folder structure based on categories
"""

import pandas as pd
import shutil
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "workingdocs" / "ai-in-social-protection-review" / "data"
DOCUMENTS_DIR = BASE_DIR / "documents"

def categorize_document(doc_row):
    """Determine which folder a document should go into based on type and evidence"""
    doc_type = doc_row.get('Document_Type', '')
    evidence_type = doc_row.get('Evidence_Type', '')

    # Define category mappings
    if doc_type in ['Research Paper', 'Academic Report'] or evidence_type == 'Peer-reviewed Empirical':
        return 'peer-reviewed-research'
    elif doc_type in ['Policy Report', 'Institutional Report', 'Workshop Report', 'Case Study'] or evidence_type in ['Policy Report', 'Donor Evaluation']:
        return 'policy-institutional-reports'
    elif doc_type in ['Government Report', 'Government Website', 'Press Release'] or evidence_type == 'Government Report':
        return 'government-documents'
    elif doc_type in ['News Article', 'Blog Post'] or evidence_type == 'Media Report':
        return 'media-news'
    else:
        return 'other-documents'

def create_folder_readme(folder_path, folder_name, documents_list):
    """Create a README for each document folder"""

    # Pretty names for folders
    folder_titles = {
        'peer-reviewed-research': 'Peer-Reviewed Research',
        'policy-institutional-reports': 'Policy & Institutional Reports',
        'government-documents': 'Government Documents',
        'media-news': 'Media & News Articles',
        'other-documents': 'Other Documents'
    }

    title = folder_titles.get(folder_name, folder_name.replace('-', ' ').title())

    content = f"""# {title}

## Overview

This folder contains {len(documents_list)} documents categorized as {title.lower()}.

## Documents in This Category

| ID | Title | Year | Evidence Strength |
|----|-------|------|-------------------|
"""

    for doc in documents_list:
        doc_id = doc['Document_ID']
        title = str(doc.get('Document_Report_Title', ''))[:60] + "..."
        year = doc.get('Year', 'N/A')
        strength = doc.get('Evidence_Strength', 'N/A')

        content += f"| [{doc_id}]({doc_id}.md) | {title} | {year} | {strength} |\n"

    # Add statistics
    doc_df = pd.DataFrame(documents_list)

    content += f"\n## Statistics\n\n"
    content += f"- **Total Documents:** {len(documents_list)}\n"

    if not doc_df.empty:
        # Year distribution
        years = doc_df['Year'].value_counts().sort_index()
        content += f"\n### By Year:\n"
        for year, count in years.items():
            if pd.notna(year):
                content += f"- {int(year)}: {count} document{'s' if count > 1 else ''}\n"

        # Evidence strength
        strengths = doc_df['Evidence_Strength'].value_counts()
        content += f"\n### By Evidence Strength:\n"
        for strength, count in strengths.items():
            if pd.notna(strength):
                content += f"- {strength}: {count} document{'s' if count > 1 else ''}\n"

    content += f"\n---\n*Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d')}*\n"

    return content

def update_use_case_references(old_path, new_path):
    """Update document references in use case files"""
    use_cases_dir = BASE_DIR / "use-cases-by-category"

    # Find all use case markdown files
    use_case_files = list(use_cases_dir.glob("**/*.md"))

    updated_count = 0
    for uc_file in use_case_files:
        try:
            with open(uc_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace old path with new path
            if old_path in content:
                content = content.replace(old_path, new_path)

                with open(uc_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                updated_count += 1
        except Exception as e:
            print(f"    ⚠️  Error updating {uc_file.name}: {e}")

    return updated_count

def main():
    """Main reorganization function"""

    print("=" * 50)
    print("Reorganizing Documents into Folders")
    print("=" * 50)

    # Load documents data
    documents_df = pd.read_csv(DATA_DIR / "documents.csv")
    print(f"Loaded {len(documents_df)} documents\n")

    # Create folder structure
    folders = [
        'peer-reviewed-research',
        'policy-institutional-reports',
        'government-documents',
        'media-news',
        'other-documents'
    ]

    print("📁 Creating folder structure...")
    for folder in folders:
        folder_path = DOCUMENTS_DIR / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {folder}/")

    # Categorize and move documents
    print("\n📄 Moving documents to appropriate folders...")

    folder_documents = {folder: [] for folder in folders}
    moved_count = 0

    for _, doc in documents_df.iterrows():
        doc_id = doc['Document_ID']
        category = categorize_document(doc)

        # Source file
        source_file = DOCUMENTS_DIR / f"{doc_id}.md"

        if source_file.exists():
            # Target location
            target_dir = DOCUMENTS_DIR / category
            target_file = target_dir / f"{doc_id}.md"

            # Move the file
            shutil.move(str(source_file), str(target_file))
            print(f"  ✓ Moved {doc_id}.md to {category}/")

            # Track for README generation
            folder_documents[category].append(doc.to_dict())
            moved_count += 1

            # Update references in use cases
            old_ref = f"../../documents/{doc_id}.md"
            new_ref = f"../../documents/{category}/{doc_id}.md"
            update_use_case_references(old_ref, new_ref)
        else:
            print(f"  ⚠️  {doc_id}.md not found")

    print(f"\n✓ Moved {moved_count} documents")

    # Create README for each folder
    print("\n📝 Creating README files for each category...")

    for folder in folders:
        if folder_documents[folder]:
            readme_content = create_folder_readme(
                DOCUMENTS_DIR / folder,
                folder,
                folder_documents[folder]
            )

            readme_path = DOCUMENTS_DIR / folder / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)

            print(f"  ✓ Created {folder}/README.md")

    # Create main documents README
    print("\n📚 Creating main documents index...")

    main_readme = """# Documents Library

## Document Categories

The document library is organized into the following categories:

### 📚 [Peer-Reviewed Research](peer-reviewed-research/)
Academic papers and research studies with rigorous peer review

### 📋 [Policy & Institutional Reports](policy-institutional-reports/)
Reports from international organizations, development agencies, and policy institutions

### 🏛️ [Government Documents](government-documents/)
Official government reports, websites, and press releases

### 📰 [Media & News Articles](media-news/)
News articles and blog posts documenting AI implementations

### 📁 [Other Documents](other-documents/)
Additional reference materials

## Document Statistics

"""

    # Add overall statistics
    main_readme += f"- **Total Documents:** {len(documents_df)}\n"
    main_readme += f"- **Date Range:** {int(documents_df['Year'].min())}-{int(documents_df['Year'].max())}\n\n"

    # Add category counts
    main_readme += "### Documents by Category:\n"
    for folder in folders:
        if folder_documents[folder]:
            folder_titles = {
                'peer-reviewed-research': 'Peer-Reviewed Research',
                'policy-institutional-reports': 'Policy & Institutional Reports',
                'government-documents': 'Government Documents',
                'media-news': 'Media & News Articles',
                'other-documents': 'Other Documents'
            }
            title = folder_titles.get(folder, folder)
            count = len(folder_documents[folder])
            main_readme += f"- {title}: {count} document{'s' if count > 1 else ''}\n"

    main_readme += """

## Navigation

- Browse by category using the folders above
- Each category folder contains its own README with document listings
- Documents include full citations, abstracts, and metadata

## Document Access

See [Document Access Information](document-access.md) for guidance on accessing documents that don't have direct links.

---
*Last updated: """ + pd.Timestamp.now().strftime('%Y-%m-%d') + "*\n"

    with open(DOCUMENTS_DIR / "README.md", 'w', encoding='utf-8') as f:
        f.write(main_readme)

    print("  ✓ Created main README.md")

    # Move document-access.md if it exists in root
    if (DOCUMENTS_DIR / "document-access.md").exists():
        print("  ✓ document-access.md already in place")

    print("\n" + "=" * 50)
    print("✨ Document reorganization complete!")
    print(f"   - Created {len(folders)} category folders")
    print(f"   - Moved {moved_count} documents")
    print(f"   - Updated cross-references in use cases")
    print("=" * 50)

if __name__ == "__main__":
    main()