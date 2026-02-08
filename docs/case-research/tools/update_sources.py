#!/usr/bin/env python3
"""
Update all case-result.json files to use a single source.

Replaces the sources array in each case-result.json with a single
Annapurna News source.
"""

import json
from pathlib import Path


def update_case_sources(json_file):
    """Update sources in a single case-result.json file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Replace sources with single Annapurna News source
        data['sources'] = [
            {
                'title': 'Annapurna News (2080 Shrawan 9)',
                'url': 'https://annapurnapost.com/epaper/?date=2080-04-09&type=',
                'description': ''
            }
        ]
        
        # Rename event_date to date in timeline
        if 'timeline' in data and isinstance(data['timeline'], list):
            for event in data['timeline']:
                if isinstance(event, dict) and 'event_date' in event:
                    event['date'] = event.pop('event_date')
        
        # Write back
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error processing {json_file}: {e}")
        return False


def main():
    annapurna_path = Path('tmp/annapurna')
    
    if not annapurna_path.exists():
        print(f"Error: Directory not found: {annapurna_path}")
        return
    
    # Find all case-result.json files
    json_files = list(annapurna_path.glob('case*/*/case-result.json'))
    
    if not json_files:
        print(f"No case-result.json files found in {annapurna_path}")
        return
    
    print(f"Found {len(json_files)} case files")
    print("Updating sources...\n")
    
    success_count = 0
    for json_file in sorted(json_files):
        if update_case_sources(json_file):
            success_count += 1
            print(f"✓ {json_file.parent.parent.name}/{json_file.parent.name}")
    
    print(f"\n{'='*60}")
    print(f"Updated {success_count}/{len(json_files)} files")


if __name__ == '__main__':
    main()
