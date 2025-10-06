#!/usr/bin/env python3
"""
GitBook Content Generator for AI in Social Protection Literature Review
Transforms CSV database into structured GitBook markdown pages
"""

import pandas as pd
import os
import re
from pathlib import Path
from datetime import datetime
import json

# Base paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "workingdocs" / "ai-in-social-protection-review" / "data"
OUTPUT_DIR = BASE_DIR

# Category mappings (with numbers as they appear in CSV)
CATEGORY_FOLDERS = {
    "1. AI-enabled Targeting & Eligibility Assessment": "1-ai-enabled-targeting-eligibility-assessment",
    "2. AI-enabled Fraud Detection & Predictive Risk Management": "2-ai-enabled-fraud-detection-predictive-risk-management",
    "3. AI-enabled Communication & Beneficiary Engagement": "3-ai-enabled-communication-beneficiary-engagement",
    "4. AI-enabled Anticipatory Action & Predictive Crisis Response": "4-ai-enabled-anticipatory-action-predictive-crisis-response",
    "5. AI-enabled Program Administration & Process Optimization": "5-ai-enabled-program-administration-process-optimization",
    "6. AI-enabled Job Matching & Career Guidance Systems": "6-ai-enabled-job-matching-career-guidance",
    "7. AI-enabled Policy Design, Simulation & Evaluation": "7-ai-enabled-policy-design-simulation-evaluation"
}

def load_data():
    """Load all CSV data files"""
    try:
        use_cases_df = pd.read_csv(DATA_DIR / "use_cases.csv")
        documents_df = pd.read_csv(DATA_DIR / "documents.csv")
        links_df = pd.read_csv(DATA_DIR / "usecase_document_links.csv")

        print(f"Loaded {len(use_cases_df)} use cases")
        print(f"Loaded {len(documents_df)} documents")
        print(f"Loaded {len(links_df)} document links")

        return use_cases_df, documents_df, links_df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None

def clean_text(text):
    """Clean and format text for markdown"""
    if pd.isna(text):
        return "Not specified"
    text = str(text).strip()
    # Escape special markdown characters if needed
    text = text.replace("|", "\\|")
    return text if text else "Not specified"

def create_badge(text, color="blue"):
    """Create a markdown badge"""
    if pd.isna(text) or text == "Not specified":
        return ""
    text = str(text).replace(" ", "%20")
    return f"![{text}](https://img.shields.io/badge/{text}-{color})"

def generate_use_case_page(use_case, documents_df, links_df):
    """Generate markdown content for a single use case"""

    # Get linked documents
    linked_docs = links_df[links_df['Use_Case_ID'] == use_case['Use_Case_ID']]
    related_documents = []
    if not linked_docs.empty:
        for _, link in linked_docs.iterrows():
            doc = documents_df[documents_df['Document_ID'] == link['Document_ID']]
            if not doc.empty:
                doc = doc.iloc[0]
                related_documents.append(doc)

    # Create badges
    country_badge = create_badge(use_case.get('Country_Region', ''), "green")
    outcome_badge = create_badge(use_case.get('Outcome_Classification', ''),
                                 "red" if use_case.get('Outcome_Classification') == 'Negative' else "blue")
    status_badge = create_badge(use_case.get('Current_Status', ''), "orange")

    # Build markdown content
    content = f"""# {use_case['Use_Case_ID']}: {clean_text(use_case.get('Category_Title', ''))}

{country_badge} {outcome_badge} {status_badge}

## Quick Facts

| Field | Value |
|-------|-------|
| **Country** | {clean_text(use_case.get('Country_Region', ''))} ({clean_text(use_case.get('Income_Group', ''))}) |
| **Category** | {clean_text(use_case.get('Category_Title', ''))} |
| **Sub-Category** | {clean_text(use_case.get('Sub_Category_Title', ''))} |
| **SP Pillar** | {clean_text(use_case.get('SP_Pillar', ''))} |
| **AI Technology** | {clean_text(use_case.get('AI_Technology', ''))} |
| **Implementation Status** | {clean_text(use_case.get('Current_Status', ''))} |
| **Timeline** | {clean_text(use_case.get('Timeline', ''))} |
| **Scale** | {clean_text(use_case.get('Scale', ''))} |

## Overview

{clean_text(use_case.get('AI_Use_Case_Description', ''))}

## Technical Implementation

### AI Technology Stack
- **Primary Technology:** {clean_text(use_case.get('AI_Technology', ''))}
- **Data Inputs:** {clean_text(use_case.get('Data_Inputs', ''))}
- **PII Data Use:** {clean_text(use_case.get('PII_Data_Use', ''))}
- **Implementation Approach:** {clean_text(use_case.get('Implementation_Approach', ''))}

### Institutional Setup
- **Implementing Partners:** {clean_text(use_case.get('Implementing_Agency_Partners', ''))}
- **Funding:** {clean_text(use_case.get('Funding_Donor', ''))}
- **Hosting:** {clean_text(use_case.get('Hosting_Data_Sovereignty', ''))}

## Outcomes and Impact

### Intended Outcomes
{clean_text(use_case.get('Intended_Outcomes', ''))}

### Documented Outcomes
{clean_text(use_case.get('Documented_Outcomes', ''))}

**Outcome Classification:** {clean_text(use_case.get('Outcome_Classification', ''))}

## Risks and Safeguards

### Reported Risks
{clean_text(use_case.get('Risks_Reported', ''))}

### Implemented Safeguards
{clean_text(use_case.get('Safeguards_Reported', ''))}

## Evidence and Documentation

### Evidence Gaps
- **Gap Identified:** {clean_text(use_case.get('Is_Evidence_Gap', ''))}
- **Gap Type:** {clean_text(use_case.get('Gap_Type', ''))}

### DPG Potential
{clean_text(use_case.get('DPG_Potential', ''))}

"""

    # Add related documents section if any exist
    if related_documents:
        content += "\n### Related Documents\n\n"
        for doc in related_documents:
            title = clean_text(doc.get('Document_Report_Title', 'Untitled'))
            doc_id = doc.get('Document_ID', '')
            year = clean_text(doc.get('Year', ''))
            content += f"- [{title} ({year})](../../documents/{doc_id}.md)\n"

    # Add cross-cutting themes if present
    if pd.notna(use_case.get('Gender_Disability_Inclusion_Notes')) or \
       pd.notna(use_case.get('Localization_Language_Considerations')) or \
       pd.notna(use_case.get('Cross_Sectoral_Adjacent_Relevance')):
        content += "\n## Cross-Cutting Themes\n\n"

        if pd.notna(use_case.get('Gender_Disability_Inclusion_Notes')):
            content += f"### Gender & Disability Inclusion\n{clean_text(use_case.get('Gender_Disability_Inclusion_Notes', ''))}\n\n"

        if pd.notna(use_case.get('Localization_Language_Considerations')):
            content += f"### Localization & Language\n{clean_text(use_case.get('Localization_Language_Considerations', ''))}\n\n"

        if pd.notna(use_case.get('Cross_Sectoral_Adjacent_Relevance')):
            content += f"### Cross-Sectoral Relevance\n{clean_text(use_case.get('Cross_Sectoral_Adjacent_Relevance', ''))}\n\n"

    # Add keywords if present
    if pd.notna(use_case.get('Notes_Keywords')):
        content += f"\n## Keywords\n{clean_text(use_case.get('Notes_Keywords', ''))}\n"

    # Add footer
    content += f"\n---\n*Last Updated: {datetime.now().strftime('%Y-%m-%d')}*\n"

    return content

def generate_document_page(document):
    """Generate markdown content for a single document"""

    content = f"""# {document['Document_ID']}: {clean_text(document.get('Document_Report_Title', 'Untitled'))}

## Citation

**{clean_text(document.get('Authors', 'Unknown'))}** ({clean_text(document.get('Year', 'n.d.'))})
*{clean_text(document.get('Document_Report_Title', 'Untitled'))}*
{clean_text(document.get('Publisher', ''))}

## Abstract

{clean_text(document.get('Abstract_Note', 'No abstract available.'))}

## Document Details

| Field | Value |
|-------|-------|
| **Year** | {clean_text(document.get('Year', ''))} |
| **Type** | {clean_text(document.get('Document_Type', ''))} |
| **Evidence Type** | {clean_text(document.get('Evidence_Type', ''))} |
| **Evidence Strength** | {clean_text(document.get('Evidence_Strength', ''))} |
| **Language** | {clean_text(document.get('Language', ''))} |
| **DOI** | {clean_text(document.get('DOI', ''))} |
| **Access URL** | [{clean_text(document.get('Direct_Link_URL', 'Not available'))}]({document.get('Direct_Link_URL', '#')}) |

## Publication Details

- **Container Title:** {clean_text(document.get('Container_Title', ''))}
- **Publisher:** {clean_text(document.get('Publisher', ''))}
- **Place:** {clean_text(document.get('Place', ''))}
- **Volume:** {clean_text(document.get('Volume', ''))}
- **Issue:** {clean_text(document.get('Issue', ''))}
- **Pages:** {clean_text(document.get('Pages', ''))}
- **ISBN:** {clean_text(document.get('ISBN', ''))}
- **ISSN:** {clean_text(document.get('ISSN', ''))}

## Tags

{clean_text(document.get('Tags', 'No tags'))}

---
*Access Date: {clean_text(document.get('Access_Date', datetime.now().strftime('%Y-%m-%d')))}*
"""

    return content

def create_category_readme(category_name, use_cases_df):
    """Create README for each category folder"""

    # Filter use cases for this category
    category_cases = use_cases_df[use_cases_df['Category_Title'] == category_name]

    content = f"""# {category_name}

## Overview

This category contains {len(category_cases)} documented use cases of {category_name.lower()} in social protection systems.

## Use Cases in This Category

| ID | Country | Description | Outcome |
|----|---------|-------------|---------|
"""

    for _, case in category_cases.iterrows():
        case_id = case['Use_Case_ID']
        country = clean_text(case.get('Country_Region', ''))
        desc = clean_text(case.get('AI_Use_Case_Description', ''))[:100] + "..."
        outcome = clean_text(case.get('Outcome_Classification', ''))

        content += f"| [{case_id}]({case_id}.md) | {country} | {desc} | {outcome} |\n"

    # Add statistics
    content += f"\n## Statistics\n\n"
    content += f"- **Total Use Cases:** {len(category_cases)}\n"

    # Count by outcome
    outcome_counts = category_cases['Outcome_Classification'].value_counts()
    content += f"\n### By Outcome:\n"
    for outcome, count in outcome_counts.items():
        content += f"- {outcome}: {count}\n"

    # Count by country
    country_counts = category_cases['Country_Region'].value_counts()
    content += f"\n### By Country:\n"
    for country, count in country_counts.head(5).items():
        content += f"- {country}: {count}\n"

    return content

def main():
    """Main generation function"""

    print("=" * 50)
    print("GitBook Content Generator")
    print("=" * 50)

    # Load data
    use_cases_df, documents_df, links_df = load_data()

    if use_cases_df is None:
        print("Failed to load data. Exiting.")
        return

    # Generate use case pages
    print("\n📝 Generating use case pages...")
    generated_count = 0

    for _, use_case in use_cases_df.iterrows():
        try:
            # Determine category folder
            category = use_case.get('Category_Title', 'Unknown')
            folder_name = CATEGORY_FOLDERS.get(category)

            if not folder_name:
                print(f"  ⚠️  Unknown category for {use_case['Use_Case_ID']}: {category}")
                continue

            # Create directory if needed
            output_path = OUTPUT_DIR / "use-cases-by-category" / folder_name
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate and save content
            content = generate_use_case_page(use_case, documents_df, links_df)
            file_path = output_path / f"{use_case['Use_Case_ID']}.md"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            generated_count += 1
            print(f"  ✓ Generated {use_case['Use_Case_ID']}.md in {folder_name}")

        except Exception as e:
            print(f"  ✗ Error generating {use_case['Use_Case_ID']}: {e}")

    print(f"\n✓ Generated {generated_count} use case pages")

    # Generate category README files
    print("\n📁 Generating category README files...")
    for category, folder_name in CATEGORY_FOLDERS.items():
        try:
            category_cases = use_cases_df[use_cases_df['Category_Title'] == category]
            if not category_cases.empty:
                output_path = OUTPUT_DIR / "use-cases-by-category" / folder_name
                output_path.mkdir(parents=True, exist_ok=True)

                content = create_category_readme(category, use_cases_df)
                file_path = output_path / "README.md"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"  ✓ Generated README for {folder_name}")
        except Exception as e:
            print(f"  ✗ Error generating README for {category}: {e}")

    # Generate document pages
    print("\n📚 Generating document pages...")
    documents_dir = OUTPUT_DIR / "documents"
    documents_dir.mkdir(parents=True, exist_ok=True)

    doc_count = 0
    for _, document in documents_df.iterrows():
        try:
            content = generate_document_page(document)
            file_path = documents_dir / f"{document['Document_ID']}.md"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            doc_count += 1
            print(f"  ✓ Generated {document['Document_ID']}.md")

        except Exception as e:
            print(f"  ✗ Error generating {document['Document_ID']}: {e}")

    print(f"\n✓ Generated {doc_count} document pages")

    # Generate documents index
    print("\n📋 Generating documents index...")
    try:
        docs_index = "# Bibliography\n\n## All Documents\n\n"
        docs_index += "| ID | Title | Year | Type | Evidence Strength |\n"
        docs_index += "|----|-------|------|------|-------------------|\n"

        for _, doc in documents_df.iterrows():
            doc_id = doc['Document_ID']
            title = clean_text(doc.get('Document_Report_Title', ''))[:60] + "..."
            year = clean_text(doc.get('Year', ''))
            doc_type = clean_text(doc.get('Document_Type', ''))
            strength = clean_text(doc.get('Evidence_Strength', ''))

            docs_index += f"| [{doc_id}]({doc_id}.md) | {title} | {year} | {doc_type} | {strength} |\n"

        with open(documents_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(docs_index)

        print("  ✓ Generated documents index")
    except Exception as e:
        print(f"  ✗ Error generating documents index: {e}")

    print("\n" + "=" * 50)
    print("✨ Generation complete!")
    print(f"   - {generated_count} use case pages")
    print(f"   - {len(CATEGORY_FOLDERS)} category READMEs")
    print(f"   - {doc_count} document pages")
    print("=" * 50)

if __name__ == "__main__":
    main()