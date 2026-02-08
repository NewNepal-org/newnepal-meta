"""
Seed 100 contributors to the database and save credentials to CSV.
"""
import os
import sys
import django
import csv
import random
import string
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


def generate_username():
    """Generate a random username using bird and tree names as pseudonyms."""
    birds = [
        'sparrow', 'robin', 'eagle', 'hawk', 'falcon', 'owl', 'crow', 'raven',
        'dove', 'pigeon', 'heron', 'crane', 'swan', 'duck', 'goose', 'pelican',
        'parrot', 'finch', 'wren', 'lark', 'thrush', 'warbler', 'jay', 'magpie',
        'cardinal', 'bluebird', 'oriole', 'tanager', 'swallow', 'swift',
        'hummingbird', 'woodpecker', 'kingfisher', 'peacock', 'pheasant',
        'quail', 'grouse', 'partridge', 'turkey', 'vulture', 'kite', 'osprey'
    ]
    
    trees = [
        'oak', 'pine', 'maple', 'birch', 'willow', 'cedar', 'elm', 'ash',
        'beech', 'spruce', 'fir', 'cypress', 'aspen', 'poplar', 'walnut',
        'cherry', 'apple', 'pear', 'plum', 'peach', 'olive', 'bamboo',
        'palm', 'juniper', 'alder', 'hazel', 'lemon', 'lime', 'orange',
        'fig', 'date', 'mango', 'banana', 'coconut', 'larch', 'yew',
        'holly', 'rowan', 'elder', 'laurel', 'bay', 'boxwood', 'magnolia'
    ]
    
    first = random.choice(birds)
    last = random.choice(trees)
    number = random.randint(1, 999)
    
    return f"{first}_{last}{number}"


def generate_password():
    """Generate a 10-character password with lowercase, numbers, and 1 special char."""
    special_chars = '!@#$%&*'
    
    # 1 special character
    special = random.choice(special_chars)
    
    # 9 characters from lowercase and numbers
    chars = string.ascii_lowercase + string.digits
    remaining = ''.join(random.choices(chars, k=9))
    
    # Combine and shuffle
    password_list = list(remaining + special)
    random.shuffle(password_list)
    
    return ''.join(password_list)


def seed_contributors(count=100):
    """Seed contributors and save to CSV."""
    
    # Confirm deletion
    confirm = input(f"Are you sure you seed {count} contributors? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborted.")
        return

    # Get or create Contributor group
    contributor_group, created = Group.objects.get_or_create(name='Contributor')
    if created:
        print("Created 'Contributor' group")
    
    contributors_data = []
    created_count = 0
    skipped_count = 0
    
    print(f"Seeding {count} contributors...")
    
    for i in range(count):
        # Generate unique username
        max_attempts = 10
        username = None
        
        for attempt in range(max_attempts):
            candidate = generate_username()
            if not User.objects.filter(username=candidate).exists():
                username = candidate
                break
        
        if not username:
            print(f"Warning: Could not generate unique username after {max_attempts} attempts")
            skipped_count += 1
            continue
        
        # Generate password
        password = generate_password()
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f"{username}@example.com"
            )
            user.is_staff = True
            user.save()
            user.groups.add(contributor_group)
            
            contributors_data.append({
                'username': username,
                'password': password,
                'email': user.email
            })
            
            created_count += 1
            
            if (created_count) % 10 == 0:
                print(f"Created {created_count} contributors...")
                
        except Exception as e:
            print(f"Error creating user {username}: {e}")
            skipped_count += 1
    
    # Write to CSV
    csv_path = Path(__file__).parent / 'contributors.csv'
    
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['username', 'password', 'email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(contributors_data)
    
    print(f"\n✓ Created {created_count} contributors")
    if skipped_count > 0:
        print(f"✗ Skipped {skipped_count} due to errors")
    print(f"✓ Credentials saved to: {csv_path}")


if __name__ == '__main__':
    seed_contributors(100)
