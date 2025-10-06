#!/usr/bin/env python3
"""
S3 Document Manager for AI Social Protection GitBook
Manages document uploads to S3 and updates GitBook links
"""

import boto3
import pandas as pd
import json
import os
from pathlib import Path
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / "workingdocs" / ".env"
load_dotenv(env_path)

BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "workingdocs" / "ai-in-social-protection-review" / "data"
DOCUMENTS_DIR = BASE_DIR / "documents"

# S3 Configuration
S3_BUCKET_NAME = "devmarketimpact"  # Your bucket
S3_REGION = "eu-north-1"  # Your region
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com"

# Document source directory (where your PDFs are stored locally)
LOCAL_DOCS_DIR = Path("/Users/tb_mi_m4air_home/dev/ai-sp-litreview/source_documents")

class S3DocumentManager:
    def __init__(self, bucket_name=S3_BUCKET_NAME, region=S3_REGION):
        """Initialize S3 client"""
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = None
        self.document_mapping = {}

    def setup_s3_client(self):
        """Setup S3 client with credentials"""
        try:
            # Use credentials from environment variables
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✓ Connected to S3 bucket: {self.bucket_name}")
            return True
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure:")
            print("   1. Run: aws configure")
            print("   2. Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
            return False
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"❌ Bucket {self.bucket_name} not found. Creating bucket...")
                return self.create_bucket()
            else:
                print(f"❌ Error connecting to S3: {e}")
                return False

    def create_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )

            # Enable public read for documents (optional - remove if you want private)
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                }]
            }

            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )

            print(f"✓ Created bucket: {self.bucket_name}")
            return True
        except Exception as e:
            print(f"❌ Error creating bucket: {e}")
            return False

    def upload_document(self, local_path, document_id):
        """Upload a document to S3"""
        try:
            # Create S3 key (path in bucket)
            file_extension = Path(local_path).suffix
            s3_key = f"documents/{document_id}{file_extension}"

            # Upload file
            with open(local_path, 'rb') as f:
                self.s3_client.upload_file(
                    local_path,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': 'application/pdf',
                        'ContentDisposition': f'inline; filename="{document_id}{file_extension}"'
                    }
                )

            # Generate public URL
            s3_url = f"{S3_BASE_URL}/{s3_key}"
            print(f"  ✓ Uploaded {document_id} -> {s3_url}")

            # Store mapping
            self.document_mapping[document_id] = {
                'local_path': str(local_path),
                's3_key': s3_key,
                's3_url': s3_url
            }

            return s3_url

        except Exception as e:
            print(f"  ✗ Error uploading {document_id}: {e}")
            return None

    def update_document_urls(self):
        """Update all document markdown files with S3 URLs"""
        updated_count = 0

        for folder in DOCUMENTS_DIR.iterdir():
            if folder.is_dir() and folder.name != '.git':
                for doc_file in folder.glob("D*.md"):
                    doc_id = doc_file.stem

                    if doc_id in self.document_mapping:
                        s3_url = self.document_mapping[doc_id]['s3_url']

                        # Read current content
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Replace the Access URL line
                        import re
                        pattern = r'\| \*\*Access URL\*\* \|.*?\|'
                        replacement = f'| **Access URL** | [📥 Download PDF]({s3_url}) |'
                        new_content = re.sub(pattern, replacement, content)

                        # Write updated content
                        if content != new_content:
                            with open(doc_file, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"  ✓ Updated {doc_id}.md with S3 URL")
                            updated_count += 1

        return updated_count

    def save_mapping(self):
        """Save document mapping to JSON file"""
        mapping_file = BASE_DIR / "workingdocs" / "s3_document_mapping.json"
        mapping_file.parent.mkdir(exist_ok=True)

        with open(mapping_file, 'w') as f:
            json.dump(self.document_mapping, f, indent=2)

        print(f"✓ Saved mapping to {mapping_file}")

    def load_mapping(self):
        """Load existing document mapping"""
        mapping_file = BASE_DIR / "workingdocs" / "s3_document_mapping.json"

        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                self.document_mapping = json.load(f)
            print(f"✓ Loaded existing mapping with {len(self.document_mapping)} documents")
            return True
        return False

def main():
    """Main function to upload documents and update links"""

    print("=" * 50)
    print("S3 Document Manager for GitBook")
    print("=" * 50)

    # Initialize manager
    manager = S3DocumentManager()

    # Setup S3 client
    if not manager.setup_s3_client():
        print("\n⚠️  Please configure AWS credentials and try again")
        print("\nOption 1: Run 'aws configure' and enter your credentials")
        print("Option 2: Set environment variables:")
        print("  export AWS_ACCESS_KEY_ID=your_key_id")
        print("  export AWS_SECRET_ACCESS_KEY=your_secret_key")
        return

    # Load document metadata
    documents_df = pd.read_csv(DATA_DIR / "documents.csv")
    print(f"\n📚 Found {len(documents_df)} documents in database")

    # Check for existing mapping
    if manager.load_mapping():
        print("  Using existing S3 mapping")
    else:
        print("\n📤 Uploading documents to S3...")
        print("  Note: This demo shows the structure. You'll need to:")
        print("  1. Place your PDF files in the source directory")
        print("  2. Update the LOCAL_DOCS_DIR path")
        print("  3. Map Document_IDs to actual filenames")

        # Example mapping of document IDs to local files
        # You'll need to update this with your actual file mappings
        document_file_mapping = {
            'D001': 'Face_identification_Ehsaas.pdf',
            'D002': 'Social_Registries_Pakistan_Case.pdf',
            'D003': 'AI_in_social_protection_now_and_tomorrow_DCI.pdf',
            'D004': 'Social_Registries_Pakistan_Case_ASP_Rome_Course.pdf',
            'D005': 'High_resolution_flood_susceptibility_mapping_Pakistan_AI_ML_framework.pdf',
            # Add more mappings as needed
        }

        # Upload documents
        for _, doc in documents_df.iterrows():
            doc_id = doc['Document_ID']

            # Check if we have a file mapping for this document
            if doc_id in document_file_mapping:
                local_filename = document_file_mapping[doc_id]
                local_path = LOCAL_DOCS_DIR / "_processed" / local_filename

                if local_path.exists():
                    s3_url = manager.upload_document(local_path, doc_id)
                else:
                    print(f"  ⚠️  File not found for {doc_id}: {local_path}")

                # For documents with direct web URLs, we can keep those
                direct_url = doc.get('Direct_Link_URL', '')
                if pd.notna(direct_url) and direct_url.startswith('http'):
                    manager.document_mapping[doc_id] = {
                        'local_path': 'web',
                        's3_key': None,
                        's3_url': direct_url
                    }

        # Save mapping for future use
        manager.save_mapping()

    # Update document markdown files
    print("\n📝 Updating document links in GitBook...")
    updated = manager.update_document_urls()
    print(f"✓ Updated {updated} document files")

    # Create a reference file with all S3 links
    print("\n📋 Creating S3 document reference...")
    create_s3_reference(manager.document_mapping)

    print("\n" + "=" * 50)
    print("✨ S3 integration complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Review the updated document links")
    print("2. Commit and push changes to GitHub")
    print("3. Verify links work in GitBook")

def create_s3_reference(mapping):
    """Create a reference file with all S3 document links"""

    content = """# S3 Document Links

## Available Documents

The following documents are available for download from our S3 repository:

| Document ID | Download Link | Type |
|-------------|---------------|------|
"""

    for doc_id, info in sorted(mapping.items()):
        if info['s3_url']:
            link_type = "Web" if info['local_path'] == 'web' else "S3"
            content += f"| {doc_id} | [Download]({info['s3_url']}) | {link_type} |\n"

    content += """

## Access Information

- Documents hosted on AWS S3 are freely accessible
- Click the download link to access the PDF
- For citation purposes, use the Document ID

---
*Last updated: """ + pd.Timestamp.now().strftime('%Y-%m-%d') + "*\n"

    ref_file = DOCUMENTS_DIR / "s3-document-links.md"
    with open(ref_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✓ Created {ref_file.name}")

if __name__ == "__main__":
    # Check if AWS CLI is available
    import subprocess
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        print(f"AWS CLI: {result.stdout.strip()}")
    except:
        print("⚠️  AWS CLI not found. Install with: pip install awscli")

    main()