#!/usr/bin/env python3
"""
PDF to Markdown Converter
Converts all PDF files in the source directory to Markdown files in the output directory.
"""

import os
import sys
from pathlib import Path
import subprocess
import re

def install_packages():
    """Install required packages if not already installed"""
    packages = ['pymupdf', 'python-docx']
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def sanitize_filename(filename):
    """Sanitize filename for filesystem compatibility"""
    # Replace problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and special chars at start/end
    sanitized = sanitized.strip(' .!()')
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized

def convert_pdf_to_markdown(pdf_path, output_path):
    """Convert a single PDF to Markdown using PyMuPDF"""
    try:
        import fitz  # PyMuPDF
        
        # Open PDF
        doc = fitz.open(pdf_path)
        
        markdown_content = []
        markdown_content.append(f"# {Path(pdf_path).stem}\n\n")
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Clean up text and convert to markdown
            if text.strip():
                markdown_content.append(f"## Page {page_num + 1}\n\n")
                markdown_content.append(text)
                markdown_content.append("\n\n---\n\n")
        
        doc.close()
        
        # Write markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))
        
        return True, f"Successfully converted {Path(pdf_path).name}"
        
    except Exception as e:
        return False, f"Error converting {Path(pdf_path).name}: {str(e)}"

def main():
    """Main conversion function"""
    source_dir = Path(r"C:\Users\Derek Angell\Desktop\CONEXUS_REPO\FE & ECP PDFs")
    output_dir = source_dir / "converted_markdown"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Install required packages
    print("Installing required packages...")
    install_packages()
    
    # Find all PDF files
    pdf_files = list(source_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the source directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF files to convert...")
    
    # Convert each PDF
    success_count = 0
    error_count = 0
    
    for pdf_file in pdf_files:
        # Generate output filename
        sanitized_name = sanitize_filename(pdf_file.stem)
        md_filename = f"{sanitized_name}.md"
        output_path = output_dir / md_filename
        
        print(f"Converting: {pdf_file.name} -> {md_filename}")
        
        success, message = convert_pdf_to_markdown(pdf_file, output_path)
        
        if success:
            success_count += 1
            print(f"✅ {message}")
        else:
            error_count += 1
            print(f"❌ {message}")
    
    print(f"\nConversion complete!")
    print(f"✅ Successfully converted: {success_count} files")
    print(f"❌ Errors: {error_count} files")
    print(f"📁 Output directory: {output_dir}")

if __name__ == "__main__":
    main()
