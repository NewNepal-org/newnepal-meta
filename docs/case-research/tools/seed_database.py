#!/usr/bin/env python3
"""
Seed database from case-result.json files.

Imports case data from scraped JSON files into Django models:
- JawafEntity (with deduplication)
- DocumentSource (with deduplication)
- Case

Usage:
    python tmp/seed_database.py [--dry-run]
"""

import os
import sys
import json
import django
from pathlib import Path
from datetime import datetime

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from cases.models import Case, DocumentSource, JawafEntity, CaseType, CaseState


class CaseImporter:
    """Import cases from JSON files with deduplication."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.stats = {
            'cases_processed': 0,
            'cases_created': 0,
            'cases_skipped': 0,
            'entities_created': 0,
            'entities_reused': 0,
            'sources_created': 0,
            'sources_reused': 0,
            'errors': []
        }
        
        # Cache for entity deduplication
        self.entity_cache = {}
    
    def get_or_create_entity(self, name):
        """Get or create JawafEntity with deduplication."""
        if not name or not name.strip():
            return None
        
        name = name.strip()
        
        # Check cache first
        if name in self.entity_cache:
            return self.entity_cache[name]
        
        # Try to find existing entity by display_name
        entity = JawafEntity.objects.filter(display_name=name).first()
        
        if entity:
            self.stats['entities_reused'] += 1
        else:
            if not self.dry_run:
                entity = JawafEntity.objects.create(display_name=name)
            else:
                entity = JawafEntity(display_name=name)
            self.stats['entities_created'] += 1
        
        self.entity_cache[name] = entity
        return entity
    
    def get_or_create_source(self, source_data):
        """Get or create DocumentSource with deduplication by URL."""
        url = source_data.get('url', '').strip()
        title = source_data.get('title', '').strip()
        description = source_data.get('description', '').strip()
        
        if not title:
            return None
        
        # Try to find existing source by URL (if provided)
        if url:
            source = DocumentSource.objects.filter(url=url).first()
            if source:
                self.stats['sources_reused'] += 1
                return source
        
        # Try to find by title
        source = DocumentSource.objects.filter(title=title).first()
        if source:
            self.stats['sources_reused'] += 1
            return source
        
        # Create new source
        if not self.dry_run:
            source = DocumentSource.objects.create(
                title=title,
                description=description,
                url=url if url else None
            )
        else:
            source = DocumentSource(title=title, description=description, url=url if url else None)
        
        self.stats['sources_created'] += 1
        return source
    
    def parse_date(self, date_str):
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    
    def import_case(self, json_file):
        """Import a single case from JSON file."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Replace sources with single Annapurna News source
            data['sources'] = [
                {
                    'title': 'Annapurna News (2080 Shrawan 9)',
                    'url': 'https://annapurnapost.com/epaper/?date=2080-04-09&type=',
                    'description': f'Annapurna epaper'
                }
            ]
            
            # Rename event_date to date in timeline
            if 'timeline' in data and isinstance(data['timeline'], list):
                for event in data['timeline']:
                    if isinstance(event, dict) and 'event_date' in event:
                        event['date'] = event.pop('event_date')
            
            self.stats['cases_processed'] += 1
            
            # Check if case already exists by title
            title = data.get('title', '').strip()
            if not title:
                self.stats['errors'].append(f"{json_file}: Missing title")
                self.stats['cases_skipped'] += 1
                return
            
            existing_case = Case.objects.filter(title=title).first()
            if existing_case:
                print(f"  Skipping: {title} (already exists)")
                self.stats['cases_skipped'] += 1
                return
            
            print(f"  Importing: {title}")
            
            # Process entities (for stats in dry-run)
            # Add alleged entities
            for entity_name in data.get('alleged_entities', []):
                self.get_or_create_entity(entity_name)
            
            # Add related entities
            for entity_name in data.get('related_entities', []):
                self.get_or_create_entity(entity_name)
            
            # Add locations (handle both string and dict formats)
            for location in data.get('locations', []):
                if isinstance(location, str):
                    self.get_or_create_entity(location)
                elif isinstance(location, dict):
                    # Extract location name from dict
                    location_name = location.get('other') or location.get('district') or location.get('municipality')
                    self.get_or_create_entity(location_name)
            
            # Get source from data (already replaced above)
            source = self.get_or_create_source(data['sources'][0])
            
            if self.dry_run:
                self.stats['cases_created'] += 1
                return
            
            # Create case with transaction
            with transaction.atomic():
                # Create case (timeline already processed above)
                case = Case(
                    case_type=CaseType.CORRUPTION,
                    state=CaseState.DRAFT,
                    title=title,
                    description=data.get('description', ''),
                    case_start_date=self.parse_date(data.get('case_start_date')),
                    case_end_date=self.parse_date(data.get('case_end_date')),
                    tags=data.get('tags', []),
                    key_allegations=data.get('key_allegations', []),
                    timeline=data.get('timeline', []),
                )
                case.save()
                
                # Add alleged entities
                for entity_name in data.get('alleged_entities', []):
                    entity = self.get_or_create_entity(entity_name)
                    if entity:
                        case.alleged_entities.add(entity)
                
                # Add related entities
                for entity_name in data.get('related_entities', []):
                    entity = self.get_or_create_entity(entity_name)
                    if entity:
                        case.related_entities.add(entity)
                
                # Add locations (handle both string and dict formats)
                for location in data.get('locations', []):
                    if isinstance(location, str):
                        entity = self.get_or_create_entity(location)
                    elif isinstance(location, dict):
                        # Extract location name from dict
                        location_name = location.get('other') or location.get('district') or location.get('municipality')
                        entity = self.get_or_create_entity(location_name)
                    else:
                        continue
                    
                    if entity:
                        case.locations.add(entity)
                
                case_no = json_file.parent.parent.stem.replace("case", "")

                # Build evidence list with single source (already fetched above)
                evidence = []
                if source:
                    evidence.append({
                        'source_id': source.source_id,
                        'description': f'Case no. {case_no}'
                    })
                
                case.evidence = evidence
                case.save()
                
                self.stats['cases_created'] += 1
                
        except Exception as e:
            self.stats['errors'].append(f"{json_file}: {str(e)}")
            print(f"  ERROR: {str(e)}")
    
    def import_all(self, annapurna_dir):
        """Import all cases from annapurna directory."""
        annapurna_path = Path(annapurna_dir)
        
        if not annapurna_path.exists():
            print(f"Error: Directory not found: {annapurna_dir}")
            return
        
        # Find all case-result.json files
        json_files = list(annapurna_path.glob('case*/*/case-result.json'))
        
        if not json_files:
            print(f"No case-result.json files found in {annapurna_dir}")
            return
        
        print(f"Found {len(json_files)} case files")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE IMPORT'}\n")
        
        for json_file in sorted(json_files):
            self.import_case(json_file)
        
        self.print_summary()
    
    def print_summary(self):
        """Print import summary."""
        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)
        print(f"Cases processed:  {self.stats['cases_processed']}")
        print(f"Cases created:    {self.stats['cases_created']}")
        print(f"Cases skipped:    {self.stats['cases_skipped']}")
        print(f"Entities created: {self.stats['entities_created']}")
        print(f"Entities reused:  {self.stats['entities_reused']}")
        print(f"Sources created:  {self.stats['sources_created']}")
        print(f"Sources reused:   {self.stats['sources_reused']}")
        
        if self.stats['errors']:
            print(f"\nErrors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed database from case-result.json files')
    parser.add_argument('--dry-run', action='store_true', help='Run without making changes')
    parser.add_argument('--dir', default='tmp/annapurna', help='Annapurna directory path')
    
    args = parser.parse_args()
    
    importer = CaseImporter(dry_run=args.dry_run)
    importer.import_all(args.dir)


if __name__ == '__main__':
    main()
