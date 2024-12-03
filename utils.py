import os
import pandas as pd
import datetime  # Import the datetime module
from transformers import pipeline
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Directory and file paths
DATA_DIR = "data"
TICKETS_FILE = os.path.join(DATA_DIR, "issue_tickets.csv")

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Load and Save Functions
def load_issue_tickets():
    """
    Load issue tickets from the CSV file. Skip invalid entries.
    Returns:
        List of valid ticket dictionaries.
    """
    valid_tickets = []
    if os.path.exists(TICKETS_FILE) and os.path.getsize(TICKETS_FILE) > 0:
        all_tickets = pd.read_csv(TICKETS_FILE).to_dict(orient="records")
        for ticket in all_tickets:
            try:
                # Validate required fields
                if isinstance(ticket["date"], str):
                    # Check if the date is ISO 8601 formatted
                    datetime.datetime.fromisoformat(ticket["date"])
                else:
                    continue  # Skip invalid rows

                if isinstance(ticket["name"], str):
                    valid_tickets.append(ticket)
            except (ValueError, KeyError):
                continue  # Skip invalid rows
    return valid_tickets



def save_issue_ticket(issue_data):
    """
    Save an issue ticket or list of tickets to the CSV file.
    Args:
        issue_data: A dictionary (single ticket) or list of dictionaries (multiple tickets).
    """
    if isinstance(issue_data, list):
        # Save the entire list of tickets
        pd.DataFrame(issue_data).to_csv(TICKETS_FILE, index=False)
    elif isinstance(issue_data, dict):
        # Save a single ticket
        issue_data["geo_location"] = str(issue_data.get("geo_location", {}))  # Serialize geo_location
        df = pd.DataFrame([issue_data])
        df.to_csv(TICKETS_FILE, mode="a", header=not os.path.exists(TICKETS_FILE), index=False)
    else:
        raise ValueError("Invalid issue_data format. Expected dict or list.")



# AI Models
def classify_waste(image):
    """
    Classify waste based on the uploaded image.
    Args:
        image: PIL Image or compatible input for the classifier.
    Returns:
        Predicted waste category as a string.
    """
    if image is None:
        return "Unknown"
    try:
        classifier = pipeline("image-classification", model="microsoft/resnet-50")
        predictions = classifier(image)
        return predictions[0]["label"]
    except Exception as e:
        print(f"Error in waste classification: {e}")
        return "Error in Classification"


def classify_issue(description):
    """
    Classify issue type based on its textual description.
    Args:
        description: Text describing the issue.
    Returns:
        Predicted issue type as a string.
    """
    try:
        nlp_classifier = pipeline("text-classification", model="distilbert-base-uncased")
        prediction = nlp_classifier(description)
        return prediction[0]["label"]
    except Exception as e:
        print(f"Error in issue classification: {e}")
        return "Error in Classification"


# Geolocation
def get_address(lat, lon):
    """
    Fetch the address for a given latitude and longitude.
    Args:
        lat: Latitude as a float.
        lon: Longitude as a float.
    Returns:
        Address as a string.
    """
    geolocator = Nominatim(user_agent="geoapi")
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True, timeout=10)
        return location.address if location else "Unknown location"
    except GeocoderTimedOut:
        return "Geolocation service timed out"
    except Exception as e:
        print(f"Error in fetching address: {e}")
        return "Error fetching location"