#!/usr/bin/env python3
"""
Reorganize use cases into their appropriate subcategory folders
"""

import pandas as pd
import os
import shutil
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "workingdocs" / "ai-in-social-protection-review" / "data"

# Subcategory folder mappings (based on actual CSV data)
SUBCATEGORY_FOLDERS = {
    # Category 1 subcategories
    "1a. Poverty Mapping & Geographic Targeting": "1a-poverty-vulnerability-mapping-geographic",
    "1b. Eligibility Scoring & Prediction (Individual/HH)": "1b-eligibility-scoring-prediction-individual-hh",
    "1c. Multi-stage Targeting Systems": "1c-biometric-identity-verification",  # Using existing folder
    "1d. Proactive Eligibility & Linkage Identification": "1d-proactive-eligibility-linkage-identification",

    # Category 2 subcategories
    "2a. Document Authentication & Verification": "2a-financial-integrity-fraud-detection",
    "2b. Identity Verification & Biometrics": "2b-social-risk-prediction-early-intervention",
    "2c. Compliance & Conditionality Monitoring": "2c-compliance-conditionality-monitoring",

    # Category 3 subcategories
    "3a. Chatbots & Multilingual Assistants": "3a-conversational-ai-chatbots",
    "3b. SMS Targeting & Outreach": "3b-automated-translation-services",
    "3c. Geographic Outreach Optimization": "3c-sentiment-feedback-analysis",

    # Category 4 subcategories
    "4a. Early Warning Systems": "4a-climate-environmental-forecasting",
    "4b. Vulnerability Indices": "4b-displacement-conflict-forecasting",

    # Category 5 subcategories
    "5a. Claims Processing Automation": "5a-document-correspondence-automation",
    "5b. User Experience Enhancement": "5b-workforce-augmentation-productivity-tools",
    "5c. Speech Recognition & Documentation": "5c-operational-resource-forecasting",
    "5d. Caseworker Decision Support": "5d-caseworker-decision-support",

    # Category 6 subcategories
    "6a. Automated Job Posting & Matching": "6a-jobseeker-profiling-risk-assessment",
    "6b. Personalized Career Guidance": "6b-skills-based-job-matching-recommendation",
    "6c. Skills Forecasting & Labor Market Intelligence": "6c-skills-forecasting-labor-market-intelligence",

    # Category 7 subcategories
    "7a. Data Analytics for Policy Insights": "7a-policy-program-simulation",
    "7b. Impact Evaluation & Monitoring": "7b-impact-evaluation-monitoring",
    "7c. Policy Framework Assessment": "7c-policy-framework-assessment",
    "7d. Real-time Monitoring & Adaptive Management": "7d-real-time-monitoring-adaptive-management"
}

# Category folder mappings
CATEGORY_FOLDERS = {
    "1. AI-enabled Targeting & Eligibility Assessment": "1-ai-enabled-targeting-eligibility-assessment",
    "2. AI-enabled Fraud Detection & Predictive Risk Management": "2-ai-enabled-fraud-detection-predictive-risk-management",
    "3. AI-enabled Communication & Beneficiary Engagement": "3-ai-enabled-communication-beneficiary-engagement",
    "4. AI-enabled Anticipatory Action & Predictive Crisis Response": "4-ai-enabled-anticipatory-action-predictive-crisis-response",
    "5. AI-enabled Program Administration & Process Optimization": "5-ai-enabled-program-administration-process-optimization",
    "6. AI-enabled Job Matching & Career Guidance Systems": "6-ai-enabled-job-matching-career-guidance",
    "7. AI-enabled Policy Design, Simulation & Evaluation": "7-ai-enabled-policy-design-simulation-evaluation"
}

def main():
    """Main reorganization function"""

    print("=" * 50)
    print("Reorganizing Use Cases into Subcategories")
    print("=" * 50)

    # Load use cases data
    use_cases_df = pd.read_csv(DATA_DIR / "use_cases.csv")
    print(f"Loaded {len(use_cases_df)} use cases")

    moved_count = 0

    # Process each use case
    for _, use_case in use_cases_df.iterrows():
        use_case_id = use_case['Use_Case_ID']
        category = use_case['Category_Title']
        subcategory = use_case.get('Sub_Category_Title', '')

        # Get category folder
        category_folder = CATEGORY_FOLDERS.get(category)
        if not category_folder:
            print(f"  ⚠️  Unknown category for {use_case_id}: {category}")
            continue

        # Build source path
        source_file = BASE_DIR / "use-cases-by-category" / category_folder / f"{use_case_id}.md"

        if not source_file.exists():
            print(f"  ⚠️  File not found: {source_file}")
            continue

        # Determine target path based on subcategory
        if pd.notna(subcategory) and subcategory in SUBCATEGORY_FOLDERS:
            subcategory_folder = SUBCATEGORY_FOLDERS[subcategory]
            target_dir = BASE_DIR / "use-cases-by-category" / category_folder / subcategory_folder
        else:
            # If no valid subcategory, keep in main category folder
            print(f"  ℹ️  No valid subcategory for {use_case_id}, keeping in main folder")
            continue

        # Create target directory if needed
        target_dir.mkdir(parents=True, exist_ok=True)

        # Move the file
        target_file = target_dir / f"{use_case_id}.md"

        if source_file != target_file:
            shutil.move(str(source_file), str(target_file))
            print(f"  ✓ Moved {use_case_id}.md to {subcategory_folder}")
            moved_count += 1

    # Also create README files for each subcategory folder
    print("\n📁 Creating subcategory README files...")

    for _, use_case_group in use_cases_df.groupby(['Category_Title', 'Sub_Category_Title']):
        if use_case_group.empty:
            continue

        first_row = use_case_group.iloc[0]
        category = first_row['Category_Title']
        subcategory = first_row['Sub_Category_Title']

        if pd.isna(subcategory) or subcategory not in SUBCATEGORY_FOLDERS:
            continue

        category_folder = CATEGORY_FOLDERS.get(category)
        if not category_folder:
            continue

        subcategory_folder = SUBCATEGORY_FOLDERS[subcategory]
        readme_path = BASE_DIR / "use-cases-by-category" / category_folder / subcategory_folder / "README.md"

        # Create subcategory README
        content = f"""# {subcategory}

## Overview

This subcategory contains {len(use_case_group)} documented use cases.

## Use Cases

| ID | Country | Description | Outcome |
|----|---------|-------------|---------|
"""

        for _, case in use_case_group.iterrows():
            case_id = case['Use_Case_ID']
            country = case.get('Country_Region', 'Unknown')
            desc = str(case.get('AI_Use_Case_Description', ''))[:80] + "..."
            outcome = case.get('Outcome_Classification', 'Not specified')

            content += f"| [{case_id}]({case_id}.md) | {country} | {desc} | {outcome} |\n"

        content += f"\n---\n*Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d')}*\n"

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Created README for {subcategory_folder}")

    print("\n" + "=" * 50)
    print(f"✨ Reorganization complete!")
    print(f"   - {moved_count} use cases moved to subcategories")
    print("=" * 50)

if __name__ == "__main__":
    main()