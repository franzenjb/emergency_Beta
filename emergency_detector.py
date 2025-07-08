from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import os
import getpass
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --------------------------------------------------------------------------
# CONFIGURATION
# Script settings are now primarily loaded from your .env file.
# You can still override them here if needed.
# --------------------------------------------------------------------------

# ArcGIS Online or Enterprise Portal URL. Loaded from .env file.
ARCGIS_PORTAL_URL = os.getenv("ARCGIS_PORTAL_URL", "https://www.arcgis.com")

# The REST services URL of your feature layer view.
FEATURE_LAYER_URL = "https://services.arcgis.com/pGfbNJoYypmNq86F/arcgis/rest/services/survey123_e94edce759494dbc89d3cc0d4368b68a_results/FeatureServer/0"

# The name of the field in your layer that contains the text to be analyzed.
# IMPORTANT: Change this to your actual field name.
NOTES_FIELD = "other_info_provided" 

# The name of the unique identifier field for your features.
OBJECTID_FIELD = "objectid" # This is usually 'objectid' or 'fid'

# The name of the field that will store the AI analysis result.
FLAG_FIELD = "ai_flag"


# --- Analysis Functions --------------------------------------------------

def is_emergency_keyword(text: str) -> bool:
    """
    Checks for specific emergency-related keywords in the provided text.
    This is a simple, fast, and cheap method of analysis.

    Returns True if an emergency keyword is found, False otherwise.
    """
    if not isinstance(text, str):
        return False
    
    emergency_words = [
        "trapped", "unconscious", "fire", "injured", "can't breathe",
        "emergency", "urgent", "help", "attack", "bleeding"
    ]
    
    text_lower = text.lower()
    return any(word in text_lower for word in emergency_words)


def is_emergency_openai(text: str) -> bool:
    """
    Uses OpenAI's GPT model to determine if the text describes an emergency.
    This is a more advanced and accurate method but requires an API key and incurs cost.

    To use this function:
    1. Install the openai library: pip install openai
    2. Set your OpenAI API key as an environment variable named 'OPENAI_API_KEY'.
    
    Returns True for an emergency, False otherwise.
    """
    if not isinstance(text, str) or not text.strip():
        return False
        
    try:
        # Dynamic import to avoid requiring 'openai' if not used
        from openai import OpenAI
    except ImportError:
        print("Error: The 'openai' library is required for this function.")
        print("Please run 'pip install openai' to install it.")
        return False

    # The API key is expected to be in the OPENAI_API_KEY environment variable
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set. Please add it to your .env file.")
        return False

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" for higher accuracy
            messages=[
                {"role": "system", "content": "You are an emergency triage system. Your task is to identify immediate, life-threatening emergencies OR situations requiring urgent medical attention. Respond with the single word 'EMERGENCY' if the text mentions things like being trapped, fire, serious injury, can't breathe, heart attack, stroke, or a critical need for medical equipment/treatment like dialysis or oxygen. For all other cases, respond with the single word 'OK'."},
                {"role": "user", "content": text}
            ],
            max_tokens=10,
            temperature=0,
        )
        result = response.choices[0].message.content.strip().upper()
        return "EMERGENCY" in result
    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        return False

# --------------------------------------------------------------------------
# MAIN SCRIPT LOGIC
# --------------------------------------------------------------------------

def main():
    """
    Main function to connect to ArcGIS, analyze features, and flag emergencies.
    """
    print("--- Starting Emergency Analysis Script ---")

    # --- Step 1: Connect to ArcGIS ---
    print("Connecting to ArcGIS...")
    
    # Get credentials from environment variables (.env file)
    arcgis_client_id = os.getenv("ARCGIS_CLIENT_ID")
    arcgis_client_secret = os.getenv("ARCGIS_CLIENT_SECRET")
    arcgis_username = os.getenv("ARCGIS_USERNAME")
    arcgis_password = os.getenv("ARCGIS_PASSWORD")

    try:
        # Prioritize connecting with Client ID/Secret (for app authentication)
        if arcgis_client_id and arcgis_client_secret:
            print(f"Connecting to {ARCGIS_PORTAL_URL} using Client ID...")
            gis = GIS(ARCGIS_PORTAL_URL, client_id=arcgis_client_id, client_secret=arcgis_client_secret)
        # Else, try username/password
        elif arcgis_username and arcgis_password:
            print(f"Connecting to {ARCGIS_PORTAL_URL} as user '{arcgis_username}'...")
            gis = GIS(ARCGIS_PORTAL_URL, arcgis_username, arcgis_password)
        # Fallback to profile-based login (OAuth, etc.)
        else:
            print("Connecting using default profile (GIS('home'))...")
            gis = GIS("home")

        # After connecting, get the username for the confirmation message.
        # For app logins (client_id), the user is often the app's ID.
        username = gis.users.me.username if gis.users.me else arcgis_client_id
        print(f"Successfully connected to '{gis.properties.portalName}' as '{username}'.")
    except Exception as e:
        print(f"Failed to connect to ArcGIS. Error: {e}")
        print("Please check your credentials in the .env file or your saved profile.")
        return

    # --- Step 2: Access the Feature Layer ---
    if "PASTE_YOUR_FEATURE_LAYER_URL_HERE" in FEATURE_LAYER_URL:
        print("\nERROR: Please update the FEATURE_LAYER_URL in the script configuration.")
        return
        
    print(f"\nAccessing feature layer: {FEATURE_LAYER_URL}")
    try:
        layer = FeatureLayer(FEATURE_LAYER_URL, gis)
        # A quick check to ensure the layer was loaded
        layer_properties = layer.properties
        print(f"Successfully accessed layer: '{layer_properties.get('name')}'")
    except Exception as e:
        print(f"Failed to access the feature layer. Please check the URL and permissions. Error: {e}")
        return


    # --- Step 3: Ensure Flag Field Exists ---
    print(f"\nChecking for '{FLAG_FIELD}' field...")
    field_names = [field['name'] for field in layer_properties.fields]
    print(f"Detected fields: {field_names}") # Diagnostic print
    
    if FLAG_FIELD not in field_names:
        print(f"Field '{FLAG_FIELD}' not found. Adding it to the layer...")
        try:
            layer.manager.add_to_definition({
                "fields": [{
                    "name": FLAG_FIELD,
                    "type": "esriFieldTypeString",
                    "alias": "AI Emergency Flag",
                    "length": 50,
                    "nullable": True,
                    "defaultValue": None
                }]
            })
            print(f"Successfully added '{FLAG_FIELD}' field.")
        except Exception as e:
            print(f"Failed to add field. Please check layer permissions. Error: {e}")
            return
    else:
        print(f"Field '{FLAG_FIELD}' already exists.")


    # --- Step 4: Query and Process Submissions ---
    # Query for features that have not been processed yet.
    query_clause = f"{FLAG_FIELD} IS NULL OR {FLAG_FIELD} = ''"
    print(f"\nQuerying for new submissions with: {query_clause}")
    
    try:
        features_to_process = layer.query(
            where=query_clause,
            out_fields=f"{OBJECTID_FIELD},{NOTES_FIELD}",
            return_geometry=False
        ).features
        print(f"Found {len(features_to_process)} new feature(s) to analyze.")
    except Exception as e:
        print(f"Failed to query features. Please check your field names. Error: {e}")
        return

    if not features_to_process:
        print("No new submissions to process. Exiting.")
        return

    # --- Step 5: Analyze and Prepare Updates ---
    updates = []
    for feature in features_to_process:
        oid = feature.attributes.get(OBJECTID_FIELD)
        text_to_analyze = feature.attributes.get(NOTES_FIELD)
        
        print(f"\nProcessing Feature ID: {oid}")
        print(f"  - Text: '{text_to_analyze}'")
        
        # --- Multi-Stage Analysis for Cost-Efficiency ---
        # Stage 1: Fast, free keyword check for obvious emergencies.
        is_emergency = is_emergency_keyword(text_to_analyze)
        
        # Stage 2: If no keywords found, use the more nuanced AI analysis.
        if not is_emergency:
            print("  - No keywords found. Sending to AI for deeper analysis...")
            is_emergency = is_emergency_openai(text_to_analyze)
        else:
            print("  - Emergency keyword found. Flagging immediately.")
        
        flag = "911_REVIEW" if is_emergency else "OK"
        print(f"  - Analysis Result: {flag}")
        
        # Prepare the feature attribute for the update operation
        feature.attributes[FLAG_FIELD] = flag
        updates.append(feature)

    # --- Step 6: Apply Updates to the Layer ---
    if updates:
        print(f"\nApplying updates for {len(updates)} feature(s)...")
        try:
            result = layer.edit_features(updates=updates)
            print("Update results:", result)
            
            # Check for errors in the update response
            update_errors = [r.get('error') for r in result.get('updateResults', []) if not r.get('success')]
            if update_errors:
                print(f"\nErrors occurred during update: {update_errors}")
            else:
                print("All features updated successfully in the layer.")
        except Exception as e:
            print(f"Failed to apply updates to the layer. Error: {e}")
    else:
        print("No features were flagged for update.")

    print("\n--- Script finished ---")


if __name__ == "__main__":
    main() 