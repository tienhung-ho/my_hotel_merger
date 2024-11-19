# hotel_merger/utils.py

import json
import re
from typing import List, Dict, Union, Optional

from hotel_merger.models import Hotel, AmenityImage

# ========================
# UTILITY FUNCTIONS
# ========================

def normalize_amenity(amenity: str) -> str:
    """
    Normalize amenity by converting to lowercase and removing non-alphanumeric characters.
    
    Args:
        amenity (str): The amenity to normalize.
    
    Returns:
        str: The normalized amenity.
    """
    return re.sub(r'[^a-z0-9]', '', amenity.lower())

def string_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity between two strings using a simple ratio of matching characters.
    
    Args:
        str1 (str): First string.
        str2 (str): Second string.
    
    Returns:
        float: Similarity ratio between 0 and 1.
    """
    matches = sum(1 for a, b in zip(str1, str2) if a == b)
    return matches / max(len(str1), len(str2)) if max(len(str1), len(str2)) > 0 else 0

def deduplicate_amenities_fuzzy(amenities: List[str], cutoff: float=0.8) -> List[str]:
    """
    Deduplicate amenities by grouping similar amenities using fuzzy matching.
    
    Args:
        amenities (List[str]): List of amenities to process.
        cutoff (float): Similarity threshold for considering two amenities as duplicates.
    
    Returns:
        List[str]: List of unique, deduplicated amenities.
    """
    unique = []
    normalized_unique = []
    for amenity in amenities:
        amenity_normalized = normalize_amenity(amenity)
        match_found = False
        for idx, unique_norm in enumerate(normalized_unique):
            similarity = string_similarity(amenity_normalized, unique_norm)
            if similarity >= cutoff:
                match_found = True
                # Prefer the longer name for more detailed description
                if len(amenity.strip()) > len(unique[idx]):
                    unique[idx] = amenity.strip()
                    normalized_unique[idx] = amenity_normalized
                break
        if not match_found:
            unique.append(amenity.strip())
            normalized_unique.append(amenity_normalized)
    return unique

def combine_address(address: Optional[str], postal_code: Optional[str]) -> str:
    """
    Combine address and postal code.
    
    Args:
        address (Optional[str]): The address.
        postal_code (Optional[str]): The postal code.
    
    Returns:
        str: The combined address.
    """
    address = address.strip() if address else ""
    postal_code = postal_code.strip() if postal_code else ""
    if postal_code:
        return f"{address}, {postal_code}"
    return address

def standardize_country(country: Optional[str]) -> str:
    """
    Standardize country names manually by matching common names and abbreviations.
    
    Args:
        country (Optional[str]): The country name or code.
    
    Returns:
        str: The standardized country name.
    """
    if not country:
        return ""
    
    country = country.strip().upper()
    
    country_mapping = {
        "US": "United States",
        "USA": "United States",
        "UNITED STATES OF AMERICA": "United States",
        "UK": "United Kingdom",
        "GB": "United Kingdom",
        "GREAT BRITAIN": "United Kingdom",
        "CAN": "Canada",
        "CA": "Canada",
        "CANADA": "Canada",
        "AUS": "Australia",
        "AU": "Australia",
        "AUSTRALIA": "Australia",
        "SG": "Singapore",
        "SIN": "Singapore",
        "SINGAPORE": "Singapore",
        "JP": "Japan",
        "JPN": "Japan"
        # Add more countries as needed
    }
    
    # Check if the country is in the mapping
    if country in country_mapping:
        return country_mapping[country]
    
    # If not found, return the original input
    return country.capitalize()

def capitalize_first_letter(text: str) -> str:
    """
    Capitalize the first letter of each sentence in the text.
    
    Args:
        text (str): The text to process.
    
    Returns:
        str: The text with each sentence starting with a capital letter.
    """
    sentences = re.split('(?<=[.!?]) +', text)
    capitalized_sentences = [s.strip().capitalize() for s in sentences if s]
    return ' '.join(capitalized_sentences)

def capitalize_booking_conditions(conditions: List[str]) -> List[str]:
    """
    Capitalize the first letter of each booking condition.
    
    Args:
        conditions (List[str]): List of booking conditions.
    
    Returns:
        List[str]: List of capitalized booking conditions.
    """
    return [capitalize_first_letter(cond) for cond in conditions if cond]

def standardize_images(images: Union[Dict, None]) -> Dict:
    """
    Standardize image fields to have 'link' and 'description'.
    
    Args:
        images (Union[Dict, None]): Image data from the supplier.
    
    Returns:
        Dict: Standardized image data.
    """
    standardized = {"rooms": [], "site": [], "amenities": []}
    if not isinstance(images, dict):
        return standardized
    for category in ["rooms", "site", "amenities"]:
        for img in images.get(category, []):
            if not isinstance(img, dict):
                continue  # Skip if img is not a dict
            link = img.get("link") or img.get("url")
            description = img.get("description") or img.get("caption") or ""
            if link:
                standardized[category].append({
                    "link": link.strip(),
                    "description": capitalize_first_letter(description.strip())
                })
    return standardized

def clean_text(text: str) -> str:
    """
    Cleans a text string by removing extra whitespace and capitalizing the first letter.
    
    Args:
        text (str): The text to clean.
    
    Returns:
        str: The cleaned text.
    """
    return ' '.join(text.split()).capitalize()

def deduplicate_list(items: List[Union[str, Dict]]) -> List:
    """
    Remove duplicates and clean extra whitespace.
    
    Args:
        items (List[Union[str, Dict]]): List of items to process.
    
    Returns:
        List: List of unique, deduplicated items.
    """
    if not items:
        return []
    if isinstance(items[0], dict):
        # Convert dict to JSON string for deduplication
        unique = {json.dumps(item, sort_keys=True): item for item in items if item}
        return list(unique.values())
    # Normalize and deduplicate
    normalized_set = set()
    unique_list = []
    for item in items:
        normalized = normalize_amenity(item)
        if normalized not in normalized_set:
            normalized_set.add(normalized)
            unique_list.append(item)
    return unique_list

def merge_hotel_data(hotels: List[Dict]) -> List[Dict]:
    """
    Merge hotel data from multiple suppliers based on `id`.
    
    Args:
        hotels (List[Dict]): List of hotels from suppliers.
    
    Returns:
        List[Dict]: Merged list of hotels.
    """
    merged = {}
    for hotel in hotels:
        hotel_id = hotel.get("id")
        if not hotel_id:
            continue  # Skip if no ID
        if hotel_id not in merged:
            merged[hotel_id] = hotel
        else:
            existing = merged[hotel_id]
            # Select main description: prefer the existing one or choose the longer one
            existing_description = existing.get("description", "")
            new_description = hotel.get("description", "")
            if not existing_description and new_description:
                merged_description = new_description
            elif existing_description and new_description:
                merged_description = existing_description if len(existing_description) >= len(new_description) else new_description
            else:
                merged_description = existing_description or new_description

            # Merge address and country
            merged_address = existing["location"].get("address") or hotel["location"].get("address")
            merged_country = existing["location"].get("country") or hotel["location"].get("country")

            # Merge amenities
            existing_general = existing.get("amenities", {}).get("general", [])
            new_general = hotel.get("amenities", {}).get("general", [])
            merged_general = deduplicate_amenities_fuzzy(existing_general + new_general)

            existing_room = existing.get("amenities", {}).get("room", [])
            new_room = hotel.get("amenities", {}).get("room", [])
            merged_room = deduplicate_amenities_fuzzy(existing_room + new_room)

            # Merge images
            existing_images = existing.get("images", {})
            new_images = hotel.get("images", {})
            merged_rooms = deduplicate_list(existing_images.get("rooms", []) + new_images.get("rooms", []))
            merged_site = deduplicate_list(existing_images.get("site", []) + new_images.get("site", []))
            merged_amenities_images = deduplicate_list(existing_images.get("amenities", []) + new_images.get("amenities", []))

            # Merge booking conditions
            existing_booking = existing.get("booking_conditions", [])
            new_booking = hotel.get("booking_conditions", [])
            merged_booking = existing_booking + new_booking  # Already standardized and capitalized in parse

            # Update merged data
            merged[hotel_id] = {
                "id": hotel_id,
                "destination_id": existing.get("destination_id") or hotel.get("destination_id"),
                "name": existing.get("name") or hotel.get("name"),
                "description": capitalize_first_letter(merged_description),
                "location": {
                    "lat": existing["location"].get("lat") or hotel["location"].get("lat"),
                    "lng": existing["location"].get("lng") or hotel["location"].get("lng"),
                    "address": merged_address,
                    "city": existing["location"].get("city") or hotel["location"].get("city"),
                    "country": merged_country
                },
                "amenities": {
                    "general": merged_general,
                    "room": merged_room
                },
                "images": {
                    "rooms": merged_rooms,
                    "site": merged_site,
                    "amenities": merged_amenities_images
                },
                "booking_conditions": deduplicate_amenities_fuzzy(merged_booking)
            }
    return list(merged.values())
