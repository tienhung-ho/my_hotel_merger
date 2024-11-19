import argparse
import json
import sys
from typing import List, Dict, Optional

from hotel_merger.suppliers import SUPPLIERS
from hotel_merger.utils import merge_hotel_data
from hotel_merger.errors import SupplierFetchError, DataParsingError, MergeError

# ========================
# MAIN FUNCTION
# ========================

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
    hotels: List[Dict],
    hotel_ids: Optional[set],
    destination_ids: Optional[set]
) -> List[Dict]:
    """
    Filter hotels based on provided hotel_ids and destination_ids.

    Args:
        hotels (List[Dict]): List of hotel data dictionaries.
        hotel_ids (Optional[set]): Set of hotel IDs to filter. If None, do not filter by hotel IDs.
        destination_ids (Optional[set]): Set of destination IDs to filter. If None, do not filter by destination IDs.

    Returns:
        List[Dict]: Filtered list of hotel data dictionaries.
    """
    if not hotel_ids and not destination_ids:
        return hotels  # No filtering needed

    filtered = []
    for hotel in hotels:
        match_hotel = True
        match_destination = True

        if hotel_ids:
            match_hotel = hotel.get("id") in hotel_ids
        if destination_ids:
            match_destination = str(hotel.get("destination_id")) in destination_ids

        if match_hotel and match_destination:
            filtered.append(hotel)
    return filtered

def standardize_output(hotels: List[Dict]) -> List[Dict]:
    """
    Standardize hotel data for output.

    Args:
        hotels (List[Dict]): List of hotel data dictionaries.

    Returns:
        List[Dict]: List of standardized hotel data dictionaries.
    """
    standardized_hotels = []
    for hotel in hotels:
        standardized_hotels.append({
            "id": hotel.get("id", ""),
            "destination_id": hotel.get("destination_id", ""),
            "name": hotel.get("name", ""),
            "location": {
                "lat": hotel["location"].get("lat", 0.0),
                "lng": hotel["location"].get("lng", 0.0),
                "address": hotel["location"].get("address", ""),
                "city": hotel["location"].get("city", ""),
                "country": hotel["location"].get("country", "")
            },
            "description": hotel.get("description", ""),
            "amenities": {
                "general": hotel.get("amenities", {}).get("general", []),
                "room": hotel.get("amenities", {}).get("room", [])
            },
            "images": {
                "rooms": hotel.get("images", {}).get("rooms", []),
                "site": hotel.get("images", {}).get("site", []),
                "amenities": hotel.get("images", {}).get("amenities", [])
            },
            "booking_conditions": hotel.get("booking_conditions", [])
        })
    return standardized_hotels

def main():
    """
    Main function to run the CLI application.
    Parses command-line arguments, fetches and merges hotel data, and outputs the result in JSON format.
    """
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
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file to save the JSON data."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output."
    )

    args = parser.parse_args()

    # Process arguments
    hotel_ids = set(args.hotel_ids.split(",")) if args.hotel_ids.lower() != "none" else None
    destination_ids = set(args.destination_ids.split(",")) if args.destination_ids.lower() != "none" else None

    try:
        # Fetch hotel data
        all_hotels = fetch_hotels_from_suppliers()

        if not all_hotels:
            print("No hotel data fetched from suppliers.", file=sys.stderr)
            sys.exit(1)

        # Merge hotel data
        merged_hotels = merge_hotel_data(all_hotels)

        # Filter hotels
        filtered_hotels = filter_hotels(merged_hotels, hotel_ids, destination_ids)

        if not filtered_hotels:
            print("No hotels matched the provided filters.")
            sys.exit(0)

        # Standardize output
        standardized_hotels = standardize_output(filtered_hotels)

        # Output the data
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(standardized_hotels, f, indent=2, ensure_ascii=False)
            print(f"Data successfully saved to {args.output}")
        else:
            print(json.dumps(standardized_hotels, indent=2, ensure_ascii=False))

    except MergeError as e:
        print(f"Error merging hotel data: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
