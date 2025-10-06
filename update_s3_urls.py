#!/usr/bin/env python3
"""
Simple S3 URL updater for GitBook documents
Updates document markdown files with S3 URLs
"""

import pandas as pd
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "workingdocs" / "ai-in-social-protection-review" / "data"
DOCUMENTS_DIR = BASE_DIR / "documents"

# S3 Configuration (from your .env)
S3_BUCKET_NAME = "devmarketimpact"
S3_REGION = "eu-north-1"
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com"

# Mapping of Document IDs to S3 paths
# Update this mapping based on your actual uploaded files
DOCUMENT_S3_MAPPING = {
    # Example mappings - update with your actual S3 paths
    'D001': 'ai-social-protection/documents/D001_Face_identification_Ehsaas.pdf',
    'D002': 'ai-social-protection/documents/D002_Social_Registries_Pakistan.pdf',
    'D003': 'ai-social-protection/documents/D003_AI_social_protection_DCI.pdf',
    'D004': 'ai-social-protection/documents/D004_Social_Registries_ASP_Rome.pdf',
    'D005': 'ai-social-protection/documents/D005_Flood_susceptibility_Pakistan.pdf',
    'D006': 'ai-social-protection/documents/D006_Flood_Mapping_Policy_Design.pdf',
    'D007': 'ai-social-protection/documents/D007_Pakistan_Ethical_AI.pdf',
    'D008': 'ai-social-protection/documents/D008_NADRA_Face_Recognition.pdf',
    'D009': 'ai-social-protection/documents/D009_Pakistan_BISP_Budget.pdf',
    'D011': 'ai-social-protection/documents/D011_Big_Data_Nigeria_Poor.pdf',
    'D012': 'ai-social-protection/documents/D012_Nigeria_AI_Identify_Poor.pdf',
    'D013': 'ai-social-protection/documents/D013_Scaling_Social_Assistance.pdf',
    'D014': 'ai-social-protection/documents/D014_Alerta_Infancia_Chile.pdf',
    'D015': 'ai-social-protection/documents/D015_Sistema_Alerta_Ninez.pdf',
    'D016': 'ai-social-protection/documents/D016_DDHH_UDP_Chile.pdf',
    'D017': 'ai-social-protection/documents/D017_German_Digital_Day_BA.pdf',
    'D018': 'ai-social-protection/documents/D018_Tina_Argentina.pdf',
    'D019': 'ai-social-protection/documents/D019_DWP_Age_of_AI.pdf',
}

def update_document_urls():
    """Update document markdown files with S3 URLs"""

    print("=" * 50)
    print("Updating Document URLs to S3")
    print("=" * 50)

    # Load documents metadata
    documents_df = pd.read_csv(DATA_DIR / "documents.csv")
    print(f"\n📚 Found {len(documents_df)} documents in database")

    updated_count = 0
    s3_urls = {}

    # Process each document
    for folder in DOCUMENTS_DIR.iterdir():
        if folder.is_dir() and folder.name != '.git':
            for doc_file in folder.glob("D*.md"):
                doc_id = doc_file.stem

                # Get document metadata
                doc_info = documents_df[documents_df['Document_ID'] == doc_id]

                if not doc_info.empty:
                    doc_info = doc_info.iloc[0]

                    # Check if document has a web URL
                    direct_url = doc_info.get('Direct_Link_URL', '')

                    if pd.notna(direct_url) and direct_url.startswith('http') and not direct_url.startswith('file://'):
                        # Keep existing web URL
                        print(f"  ℹ️  {doc_id}: Keeping existing web URL")
                        continue

                    # Check if we have S3 mapping for this document
                    if doc_id in DOCUMENT_S3_MAPPING:
                        s3_path = DOCUMENT_S3_MAPPING[doc_id]
                        s3_url = f"{S3_BASE_URL}/{s3_path}"
                        s3_urls[doc_id] = s3_url

                        # Read current content
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Replace the Access URL line
                        pattern = r'\| \*\*Access URL\*\* \|.*?\|'
                        replacement = f'| **Access URL** | [📥 Download PDF]({s3_url}) |'
                        new_content = re.sub(pattern, replacement, content)

                        # Write updated content if changed
                        if content != new_content:
                            with open(doc_file, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"  ✓ Updated {doc_id}.md with S3 URL")
                            updated_count += 1
                        else:
                            print(f"  ℹ️  {doc_id}: Already has correct URL")
                    else:
                        print(f"  ⚠️  {doc_id}: No S3 mapping defined")

    print(f"\n✓ Updated {updated_count} document files")

    # Save S3 URL mapping
    if s3_urls:
        mapping_file = BASE_DIR / "workingdocs" / "s3_url_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(s3_urls, f, indent=2)
        print(f"✓ Saved S3 URL mapping to {mapping_file.name}")

    # Create upload instructions
    create_upload_instructions()

    return updated_count

def create_upload_instructions():
    """Create instructions for manual S3 upload"""

    instructions = """# S3 Upload Instructions

## AWS CLI Commands for Document Upload

To upload documents to your S3 bucket, use these AWS CLI commands:

### 1. Configure AWS CLI (if not already done)
```bash
# Set your AWS credentials (from .env file)
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=eu-north-1
```

### 2. Create folder structure in S3
```bash
# Create the documents folder
aws s3api put-object --bucket devmarketimpact --key ai-social-protection/documents/
```

### 3. Upload documents
```bash
# Example upload commands for each document
# Replace /path/to/local/file.pdf with actual file paths

"""

    for doc_id, s3_path in DOCUMENT_S3_MAPPING.items():
        instructions += f"# {doc_id}\n"
        instructions += f"aws s3 cp /path/to/{doc_id}.pdf s3://devmarketimpact/{s3_path} --acl public-read\n\n"

    instructions += """
### 4. Verify uploads
```bash
# List all uploaded documents
aws s3 ls s3://devmarketimpact/ai-social-protection/documents/
```

### 5. Test URLs
After uploading, test the URLs are accessible:
"""

    for doc_id, s3_path in DOCUMENT_S3_MAPPING.items():
        url = f"{S3_BASE_URL}/{s3_path}"
        instructions += f"- {doc_id}: {url}\n"

    instructions += """

## Alternative: S3 Console Upload

1. Go to https://console.aws.amazon.com/s3/
2. Navigate to the 'devmarketimpact' bucket
3. Create folder: ai-social-protection/documents/
4. Upload PDFs with the naming convention: D###_Description.pdf
5. Set permissions to public read

---
*Generated: """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M') + "*\n"

    instructions_file = BASE_DIR / "workingdocs" / "S3_UPLOAD_INSTRUCTIONS.md"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)

    print(f"\n📝 Created upload instructions: {instructions_file.name}")

def main():
    """Main function"""
    update_document_urls()

    print("\n" + "=" * 50)
    print("✨ URL update complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Upload PDFs to S3 using the instructions in workingdocs/S3_UPLOAD_INSTRUCTIONS.md")
    print("2. Verify S3 URLs are accessible")
    print("3. Commit and push changes to GitHub")
    print("4. Check GitBook to ensure links work")

if __name__ == "__main__":
    main()