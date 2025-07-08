import csv
import random
from faker import Faker

# --- CONFIGURATION ---
NUM_ROWS = 100
OUTPUT_FILE = 'test_data.csv'

# Bounding box for Pinellas County, FL (approximate)
PINELLAS_BOUNDS = {
    "lat_min": 27.70,
    "lat_max": 28.16,
    "lon_min": -82.85,
    "lon_max": -82.60,
}

# --- DATA POOLS ---
# Use Faker for generating some data
fake = Faker()

# Scenarios for the 'other_info_provided' field
EMERGENCY_SCENARIOS = [
    "My house is on fire! The address is {}. Please send help!",
    "I smell gas in my apartment building, I think there is a leak.",
    "A tree fell on our car and my husband is trapped inside and injured.",
    "My father is having a heart attack, he can't breathe.",
    "We are trapped by rising floodwaters on the first floor.",
    "There's been a multi-car pile-up on the highway, many people are hurt.",
]

URGENT_SUPPLY_SCENARIOS = [
    "We have run out of my son's asthma medication.",
    "My mother is on oxygen and her tanks are almost empty.",
    "We have a newborn and are completely out of baby formula.",
    "I am a diabetic and I have no insulin left.",
]

NON_URGENT_SCENARIOS = [
    "Where can we find clean drinking water?",
    "Is there a shelter open near us at {}?",
    "When will the power be back on in our neighborhood?",
    "A large tree branch fell in my yard, but everyone is okay and it's not blocking the road.",
    "I'd like to report a downed power line.",
    "My street is flooded, but the water is not in my house.",
]

# Data for other fields in the survey
URGENCY_LEVELS = ['Urgency_ASAP', 'Urgency_Urgent', 'Urgency_Within24Hours']
ASSISTANCE_TYPES = ['Water', 'Shelter', 'Food', 'Financial_Assistance', 'Medical', 'Reunification']


def generate_scenario():
    """Generates a full row of fake data."""
    
    scenario_type = random.choices(['emergency', 'urgent', 'non-urgent'], weights=[0.2, 0.2, 0.6], k=1)[0]
    
    address = fake.street_address()
    other_info = ""
    urgency = ""
    assistance = []

    if scenario_type == 'emergency':
        other_info = random.choice(EMERGENCY_SCENARIOS).format(address)
        urgency = 'Urgency_Urgent'
        assistance.append('Medical')
    elif scenario_type == 'urgent':
        other_info = random.choice(URGENT_SUPPLY_SCENARIOS)
        urgency = 'Urgency_ASAP'
        assistance.append('Medical')
    else:
        other_info = random.choice(NON_URGENT_SCENARIOS).format(address)
        urgency = random.choice(['Urgency_ASAP', 'Urgency_Within24Hours'])

    # Add some other random assistance requests
    if random.random() > 0.4:
        assistance.append(random.choice(ASSISTANCE_TYPES))
    if random.random() > 0.7:
        assistance.append(random.choice(ASSISTANCE_TYPES))
        
    return {
        'x': round(random.uniform(PINELLAS_BOUNDS['lon_min'], PINELLAS_BOUNDS['lon_max']), 6),
        'y': round(random.uniform(PINELLAS_BOUNDS['lat_min'], PINELLAS_BOUNDS['lat_max']), 6),
        'Urgency': urgency,
        'assistance_requested': ",".join(list(set(assistance))), # Join unique values
        'assistance_requested_other': '', # Leave blank for this generator
        'zip_code_provided': fake.zipcode_in_state(state_abbr='FL'),
        'seniors_at_this_location': random.randint(0, 4),
        'youth_at_this_location': random.randint(0, 5),
        'disabled_or_mobility_challenged': random.randint(0, 3),
        'other_info_provided': other_info,
        'ai_flag': '' # Leave blank for the script to process
    }

def main():
    """Main function to generate the CSV file."""
    
    print(f"Generating {NUM_ROWS} fictitious entries...")
    
    fieldnames = [
        'x', 'y', 'Urgency', 'assistance_requested', 'assistance_requested_other',
        'zip_code_provided', 'seniors_at_this_location', 'youth_at_this_location',
        'disabled_or_mobility_challenged', 'other_info_provided', 'ai_flag'
    ]
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i in range(NUM_ROWS):
            writer.writerow(generate_scenario())
            
    print(f"\nSuccessfully created '{OUTPUT_FILE}'.")
    print("You can now upload this file to your ArcGIS Hosted Feature Layer.")

if __name__ == '__main__':
    main() 