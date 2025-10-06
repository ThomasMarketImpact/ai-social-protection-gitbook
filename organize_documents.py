#!/usr/bin/env python3
"""
Organize documents into a structured hierarchy for better navigation
"""

import pandas as pd
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "workingdocs" / "ai-in-social-protection-review" / "data"
DOCUMENTS_DIR = BASE_DIR / "documents"

# Document organization categories
DOCUMENT_CATEGORIES = {
    "peer-reviewed-research": {
        "title": "Peer-Reviewed Research",
        "types": ["Research Paper", "Academic Report"],
        "evidence": ["Peer-reviewed Empirical"]
    },
    "policy-reports": {
        "title": "Policy & Institutional Reports",
        "types": ["Policy Report", "Institutional Report", "Workshop Report", "Case Study"],
        "evidence": ["Policy Report", "Donor Evaluation"]
    },
    "government-documents": {
        "title": "Government Documents",
        "types": ["Government Report", "Government Website", "Press Release"],
        "evidence": ["Government Report"]
    },
    "media-analysis": {
        "title": "Media & News Analysis",
        "types": ["News Article", "Blog Post"],
        "evidence": ["Media Report"]
    }
}

def categorize_document(doc_row):
    """Determine which category a document belongs to"""
    doc_type = doc_row.get('Document_Type', '')
    evidence_type = doc_row.get('Evidence_Type', '')

    for cat_key, cat_info in DOCUMENT_CATEGORIES.items():
        if doc_type in cat_info['types'] or evidence_type in cat_info['evidence']:
            return cat_key

    return "other"  # Fallback category

def create_category_index(category_key, category_info, documents_df):
    """Create an index page for a document category"""

    # Filter documents for this category
    cat_docs = []
    for _, doc in documents_df.iterrows():
        if categorize_document(doc) == category_key:
            cat_docs.append(doc)

    if not cat_docs:
        return None

    content = f"""# {category_info['title']}

## Overview

This section contains {len(cat_docs)} documents categorized as {category_info['title'].lower()}.

## Documents

| ID | Title | Year | Evidence Strength | Access |
|----|-------|------|-------------------|--------|
"""

    for doc in cat_docs:
        doc_id = doc['Document_ID']
        title = str(doc.get('Document_Report_Title', ''))[:50] + "..."
        year = doc.get('Year', 'N/A')
        strength = doc.get('Evidence_Strength', 'N/A')

        # Check if URL is accessible
        url = doc.get('Direct_Link_URL', '')
        if pd.notna(url) and url.startswith('http'):
            access = "🔗 Online"
        else:
            access = "📄 Reference"

        content += f"| [{doc_id}]({doc_id}.md) | {title} | {year} | {strength} | {access} |\n"

    # Add statistics
    content += f"\n## Statistics\n\n"

    # Count by year
    years = pd.DataFrame(cat_docs)['Year'].value_counts().sort_index()
    content += f"### By Year:\n"
    for year, count in years.items():
        content += f"- {year}: {count} document{'s' if count > 1 else ''}\n"

    # Count by evidence strength
    strengths = pd.DataFrame(cat_docs)['Evidence_Strength'].value_counts()
    content += f"\n### By Evidence Strength:\n"
    for strength, count in strengths.items():
        content += f"- {strength}: {count} document{'s' if count > 1 else ''}\n"

    content += f"\n---\n*Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d')}*\n"

    return content

def create_documents_overview():
    """Create main documents overview page"""

    content = """# Document Library Overview

## Organization

Documents in this library are organized by type and evidence quality to help researchers quickly find relevant materials.

### Document Categories

📚 **[Peer-Reviewed Research](peer-reviewed-research.md)**
Academic papers and research studies with rigorous peer review

📋 **[Policy & Institutional Reports](policy-reports.md)**
Reports from international organizations, development agencies, and policy institutions

🏛️ **[Government Documents](government-documents.md)**
Official government reports, websites, and press releases

📰 **[Media & News Analysis](media-analysis.md)**
News articles and blog posts documenting AI implementations

### Quick Access

- 📖 **[All Documents by ID](all-documents.md)** - Complete alphabetical listing
- 📅 **[Documents by Year](by-year.md)** - Chronological view
- 💪 **[Documents by Evidence Strength](by-evidence.md)** - Quality-based filtering
- 🌍 **[Documents by Country](by-country.md)** - Geographic organization

### Using This Library

1. **Browse by category** to find documents of a specific type
2. **Check evidence strength** to assess document quality
3. **Look for 🔗 Online markers** for directly accessible documents
4. **Use document IDs** for precise citations

---
*See [Document Access Information](document-access.md) for help accessing restricted documents*
"""

    return content

def create_year_index(documents_df):
    """Create index organized by year"""

    content = """# Documents by Year

## Chronological Listing

"""

    # Group by year
    for year in sorted(documents_df['Year'].dropna().unique(), reverse=True):
        year_docs = documents_df[documents_df['Year'] == year]
        content += f"### {int(year)} ({len(year_docs)} documents)\n\n"

        for _, doc in year_docs.iterrows():
            doc_id = doc['Document_ID']
            title = str(doc.get('Document_Report_Title', ''))[:80] + "..."
            content += f"- [{doc_id}]({doc_id}.md): {title}\n"

        content += "\n"

    return content

def create_evidence_index(documents_df):
    """Create index organized by evidence strength"""

    content = """# Documents by Evidence Strength

## Quality Assessment

Documents are rated by evidence strength to help researchers prioritize sources.

"""

    strength_order = ['High', 'Medium', 'Low']

    for strength in strength_order:
        strength_docs = documents_df[documents_df['Evidence_Strength'] == strength]
        if not strength_docs.empty:
            content += f"### {strength} Evidence Strength ({len(strength_docs)} documents)\n\n"

            for _, doc in strength_docs.iterrows():
                doc_id = doc['Document_ID']
                title = str(doc.get('Document_Report_Title', ''))[:60] + "..."
                doc_type = doc.get('Document_Type', 'Unknown')
                content += f"- [{doc_id}]({doc_id}.md): {title} *({doc_type})*\n"

            content += "\n"

    return content

def main():
    """Main organization function"""

    print("=" * 50)
    print("Organizing Document Library")
    print("=" * 50)

    # Load documents data
    documents_df = pd.read_csv(DATA_DIR / "documents.csv")
    print(f"Loaded {len(documents_df)} documents")

    # Create main overview
    print("\n📚 Creating document overview...")
    overview_content = create_documents_overview()
    with open(DOCUMENTS_DIR / "overview.md", 'w', encoding='utf-8') as f:
        f.write(overview_content)
    print("  ✓ Created overview.md")

    # Create category indices
    print("\n📁 Creating category indices...")
    for cat_key, cat_info in DOCUMENT_CATEGORIES.items():
        content = create_category_index(cat_key, cat_info, documents_df)
        if content:
            with open(DOCUMENTS_DIR / f"{cat_key}.md", 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Created {cat_key}.md")

    # Create year index
    print("\n📅 Creating chronological index...")
    year_content = create_year_index(documents_df)
    with open(DOCUMENTS_DIR / "by-year.md", 'w', encoding='utf-8') as f:
        f.write(year_content)
    print("  ✓ Created by-year.md")

    # Create evidence strength index
    print("\n💪 Creating evidence strength index...")
    evidence_content = create_evidence_index(documents_df)
    with open(DOCUMENTS_DIR / "by-evidence.md", 'w', encoding='utf-8') as f:
        f.write(evidence_content)
    print("  ✓ Created by-evidence.md")

    # Rename existing README to all-documents.md
    if (DOCUMENTS_DIR / "README.md").exists():
        shutil.copy(DOCUMENTS_DIR / "README.md", DOCUMENTS_DIR / "all-documents.md")
        print("\n  ✓ Created all-documents.md from README")

    # Update main README to point to overview
    readme_content = """# Documents

Welcome to the document library. This section contains all source documents referenced in the AI in Social Protection literature review.

→ **[Browse Document Library](overview.md)**

### Quick Links

- 📚 [Document Categories](overview.md)
- 📖 [All Documents](all-documents.md)
- 📅 [By Year](by-year.md)
- 💪 [By Evidence Strength](by-evidence.md)
- ℹ️ [Document Access Guide](document-access.md)

---
*This library contains {doc_count} documents from {year_min}-{year_max}*
""".format(
        doc_count=len(documents_df),
        year_min=int(documents_df['Year'].min()),
        year_max=int(documents_df['Year'].max())
    )

    with open(DOCUMENTS_DIR / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("  ✓ Updated main README.md")

    print("\n" + "=" * 50)
    print("✨ Document organization complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()