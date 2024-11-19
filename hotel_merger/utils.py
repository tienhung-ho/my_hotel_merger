import json
import re
from typing import List, Dict, Union, Optional

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

def deduplicate_amenities(amenities: List[str], cutoff: float=0.8) -> List[str]:
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
    }
    
    if country in country_mapping:
        return country_mapping[country]
    
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
        unique = {json.dumps(item, sort_keys=True): item for item in items if item}
        return list(unique.values())
    
    normalized_set = set()
    unique_list = []
    for item in items:
        normalized = normalize_amenity(item)
        if normalized not in normalized_set:
            normalized_set.add(normalized)
            unique_list.append(item)
    return unique_list


