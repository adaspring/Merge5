#!/usr/bin/env python3
"""
Enhanced HTML post-processor with:
1. Better link handling
2. Error resilience
3. Cleaner output formatting
"""

import argparse
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

def process_html_file(input_file, target_lang):
    try:
        # Validate input file
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file {input_file} not found")
        
        # Read with explicit UTF-8 encoding and error handling
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Parse with html.parser for consistency
        soup = BeautifulSoup(content, 'html.parser')
        
        # 1. Update HTML lang attribute
        if soup.html:
            soup.html['lang'] = target_lang
        
        # 2. Process internal links
        link_pattern = re.compile(r'^(?!http|#|mailto:).*\.html$')
        for link in soup.find_all('a', href=link_pattern):
            href = link['href']
            # Preserve query strings and fragments
            base, *extra = href.split('?')
            base = re.sub(r'-(fr|es|zh|en)(?=\.html)', '', base)
            new_href = base.replace('.html', f'-{target_lang}.html')
            if extra:
                new_href += '?' + '?'.join(extra)
            link['href'] = new_href
        
        # 3. Update language switcher
        for switcher in soup.find_all(class_='language-switcher'):
            for link in switcher.find_all('a'):
                classes = link.get('class', [])
                if 'active' in classes:
                    classes.remove('active')
                if link['href'].endswith(f'-{target_lang}.html'):
                    classes.append('active')
                    link['class'] = classes
        
        # Generate output path
        output_path = input_path.with_name(
            input_path.stem.replace('_FR', '') + f'-{target_lang}.html'
        )
        
        # Write output with proper formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        print(f"✓ Successfully created: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {input_file}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Post-process translated HTML files"
    )
    parser.add_argument("--input", required=True,
                      help="Input HTML file path")
    parser.add_argument("--target-lang", required=True,
                      choices=['fr', 'es', 'zh', 'en'],
                      help="Target language code")
    
    args = parser.parse_args()
    
    if not process_html_file(args.input, args.target_lang):
        exit(1)

if __name__ == "__main__":
    main()
