#!/usr/bin/env python3
"""
Post-process translated HTML files to:
1. Update lang attribute
2. Add language suffixes to internal links
3. Update active class in language switcher
"""

import argparse
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

def process_html_file(input_file, target_lang):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # 1. Update HTML lang attribute
    if soup.html and soup.html.has_attr('lang'):
        soup.html['lang'] = target_lang
    
    # 2. Add language suffixes to internal links
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Skip external links and anchors
        if not href.startswith(('http', '#', 'mailto:')) and not href.endswith(('.pdf', '.jpg', '.png', '.jpeg')):
            # Remove existing language suffix if present
            base_href = re.sub(r'-(fr|es|zh|en)\.html$', '.html', href)
            # Add new language suffix
            if base_href.endswith('.html'):
                new_href = base_href.replace('.html', f'-{target_lang}.html')
                link['href'] = new_href
    
    # 3. Update active class in language switcher
    for lang_switcher in soup.find_all(class_='language-switcher'):
        for a in lang_switcher.find_all('a'):
            # Remove active class from all links
            if 'active' in a.get('class', []):
                a['class'].remove('active')
            # Add active class to current language
            if a['href'].endswith(f'-{target_lang}.html'):
                if a.get('class'):
                    a['class'].append('active')
                else:
                    a['class'] = ['active']
    
    # Generate output filename
    input_path = Path(input_file)
    output_filename = f"{input_path.stem.replace('_FR', '')}-{target_lang}.html"
    output_path = input_path.parent / output_filename
    
    # Write the modified content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"Processed file saved as: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Post-process translated HTML files with language-specific adjustments"
    )
    parser.add_argument("--input", required=True, 
                       help="Path to input HTML file (final_deepl_FR.html or final_openai_FR.html)")
    parser.add_argument("--target-lang", required=True,
                       help="Target language code (e.g., 'fr')")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found")
        return
    
    process_html_file(args.input, args.target_lang)

if __name__ == "__main__":
    main()
