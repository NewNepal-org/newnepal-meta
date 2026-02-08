#!/usr/bin/env python
"""
Clear JawafEntity, DocumentSource, and Case records from the database.

Usage:
    python tmp/clear_database.py
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cases.models import Case, DocumentSource, JawafEntity


def clear_database():
    """Clear all cases, document sources, and jawaf entities."""
    
    # Count before deletion
    case_count = Case.objects.count()
    source_count = DocumentSource.objects.count()
    entity_count = JawafEntity.objects.count()
    
    print(f"Found {case_count} cases, {source_count} document sources, {entity_count} entities")
    
    # Confirm deletion
    confirm = input("Are you sure you want to delete all records? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborted.")
        return
    
    # Delete in order (respecting foreign key constraints)
    print("\nDeleting records...")
    
    # Delete cases first (they reference sources and entities)
    Case.objects.all().delete()
    print(f"✓ Deleted {case_count} cases")
    
    # Delete document sources
    DocumentSource.objects.all().delete()
    print(f"✓ Deleted {source_count} document sources")
    
    # Delete entities
    JawafEntity.objects.all().delete()
    print(f"✓ Deleted {entity_count} entities")
    
    print("\nDatabase cleared successfully!")


if __name__ == '__main__':
    clear_database()
