import argparse
import json
import sys
from typing import List, Dict, Optional

from hotel_merger.utils import deduplicate_amenities, deduplicate_list, capitalize_first_letter

from hotel_merger.models import Hotel
from hotel_merger.suppliers import SUPPLIERS
from hotel_merger.errors import SupplierFetchError, DataParsingError, MergeError
from hotel_merger.models import Hotel

def fetch_hotels_from_suppliers() -> List[Dict]:
    """
    Fetch hotel data from all registered suppliers.

    Returns:
        List[Dict]: A list of hotel data dictionaries fetched from suppliers.

    Raises:
        SupplierFetchError: If fetching data from any supplier fails.
        DataParsingError: If parsing data from any supplier fails.
    """
    
    suppliers = [cls() for cls in SUPPLIERS.values()]
    all_hotels = []
    for supplier in suppliers:
        try:
            hotels = supplier.fetch()
            all_hotels.extend(hotels)
            
        except SupplierFetchError as e:
            print(f"Error fetching data from {supplier.__class__.__name__}: {e}", file=sys.stderr)
        except DataParsingError as e:
            print(f"Error parsing data from {supplier.__class__.__name__}: {e}", file=sys.stderr)
    return all_hotels

def filter_hotels(
    hotels: List[Hotel],
    hotel_ids: Optional[set],
    destination_ids: Optional[set]
) -> List[Hotel]:
    """
    Filter hotels based on provided hotel_ids and destination_ids.

    Args:
        hotels (List[Hotel]): List of Hotel instances.
        hotel_ids (Optional[set]): Set of hotel IDs to filter. If None, do not filter by hotel IDs.
        destination_ids (Optional[set]): Set of destination IDs to filter. If None, do not filter by destination IDs.

    Returns:
        List[Hotel]: Filtered list of Hotel instances.
    """

    if not hotel_ids and not destination_ids:
        print("No filtering required.")
        return hotels  # No filtering needed

    filtered = []
    for hotel in hotels:
        
        match_hotel = True
        match_destination = True

        if hotel_ids:
            match_hotel = hotel.id in hotel_ids
        if destination_ids:
            match_destination = str(hotel.destination_id) in destination_ids

        if match_hotel and match_destination:
            filtered.append(hotel)
    
    return filtered

def standardize_output(hotels: List[Hotel]) -> List[Dict]:
    """
    Standardize hotel data for output.

    Args:
        hotels (List[Hotel]): List of Hotel instances.

    Returns:
        List[Dict]: List of standardized hotel data dictionaries.
    """
    
    standardized_hotels = [hotel.to_dict() for hotel in hotels]
    return standardized_hotels


def merge_hotel_data(hotels: List[Dict]) -> List[Hotel]:
    """
    Merge hotel data from multiple suppliers based on `id` and create Hotel instances.
    
    Args:
        hotels (List[Dict]): List of hotels from suppliers.
    
    Returns:
        List[Hotel]: Merged list of Hotel instances.
    """
    merged = {}
    for hotel in hotels:
        hotel_id = hotel.get("id")
        
        if not hotel_id:
            continue 

        if hotel_id not in merged:
            merged[hotel_id] = hotel
        else:
           
            existing = merged[hotel_id]

            if isinstance(existing, Hotel):
                existing = existing.to_dict()

            existing_description = existing.get("description", "")
            new_description = hotel.get("description", "")
            if not existing_description and new_description:
                merged_description = new_description
            elif existing_description and new_description:
                merged_description = (
                    existing_description
                    if len(existing_description) >= len(new_description)
                    else new_description
                )
            else:
                merged_description = existing_description or new_description
 
            merged_address = existing["location"].get("address") or hotel["location"].get("address")
            merged_country = existing["location"].get("country") or hotel["location"].get("country")

            existing_general = existing.get("amenities", {}).get("general", [])
            new_general = hotel.get("amenities", {}).get("general", [])
            merged_general = deduplicate_amenities(existing_general + new_general)

            existing_room = existing.get("amenities", {}).get("room", [])
            new_room = hotel.get("amenities", {}).get("room", [])
            merged_room = deduplicate_amenities(existing_room + new_room)

            existing_images = existing.get("images", {})
            new_images = hotel.get("images", {})
            merged_rooms = deduplicate_list(existing_images.get("rooms", []) + new_images.get("rooms", []))
            merged_site = deduplicate_list(existing_images.get("site", []) + new_images.get("site", []))
            merged_amenities_images = deduplicate_list(existing_images.get("amenities", []) + new_images.get("amenities", []))
            
            existing_booking = existing.get("booking_conditions", [])
            new_booking = hotel.get("booking_conditions", [])
            merged_booking = deduplicate_amenities(existing_booking + new_booking)

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
                "booking_conditions": deduplicate_amenities(merged_booking)
            }
    return [Hotel.from_merged_dict(data) for data in merged.values()]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and merge hotel data from suppliers.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "hotel_ids",
        type=str,
        help="Hotel IDs (comma-separated or 'none')"
    )
    parser.add_argument(
        "destination_ids",
        type=str,
        help="Destination IDs (comma-separated or 'none')"
    )

    args = parser.parse_args()

    hotel_ids = set(args.hotel_ids.split(",")) if args.hotel_ids.lower() != "none" else None
    destination_ids = set(args.destination_ids.split(",")) if args.destination_ids.lower() != "none" else None

    try:
        all_hotels = fetch_hotels_from_suppliers()

        if not all_hotels:
            print("No hotel data fetched from suppliers.", file=sys.stderr)
            sys.exit(1)

        merged_hotels = merge_hotel_data(all_hotels)

        filtered_hotels = filter_hotels(merged_hotels, hotel_ids, destination_ids)

        if not filtered_hotels:
            print("No hotels matched the provided filters.")
            sys.exit(0)

        standardized_hotels = standardize_output(filtered_hotels)

        # In this version, we no longer have the output file option, so we only print the result
        print(json.dumps(standardized_hotels, indent=2, ensure_ascii=False))

    except MergeError as e:
        print(f"Error merging hotel data: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
