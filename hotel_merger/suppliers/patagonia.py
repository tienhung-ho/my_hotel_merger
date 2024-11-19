from typing import List, Dict
from hotel_merger.suppliers.base import BaseSupplier
from hotel_merger.utils import deduplicate_amenities, clean_text, combine_address, standardize_country, standardize_images
from hotel_merger.errors import DataParsingError

class PatagoniaSupplier(BaseSupplier):
    """
    Supplier class for Patagonia.
    Handles fetching and parsing data from the Patagonia supplier.
    """

    def endpoint(self) -> str:
        """
        Returns the API endpoint URL for Patagonia supplier.

        Returns:
            str: The Patagonia supplier's API endpoint.
        """
        return "https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/patagonia"

    def parse(self, data: Dict) -> Dict:
        """
        Parse Patagonia supplier data into standard format.

        Args:
            data (Dict): Raw data from Patagonia.

        Raises:
            DataParsingError: If required fields are missing or invalid.

        Returns:
            Dict: Standardized hotel data.
        """
        try:
            amenities = data.get("amenities", []) or []
            if not isinstance(amenities, list):
                amenities = []
            standardized_amenities = deduplicate_amenities(amenities)

            booking_conditions = data.get("booking_conditions", []) or []
            if not isinstance(booking_conditions, list):
                booking_conditions = []

            return {
                "id": data.get("id", "").strip(),
                "destination_id": data.get("destination"),
                "name": data.get("name", "").strip(),
                "description": clean_text(data.get("info", "").strip()) if data.get("info") else "",
                "location": {
                    "lat": data.get("lat") if isinstance(data.get("lat"), (int, float)) else None,
                    "lng": data.get("lng") if isinstance(data.get("lng"), (int, float)) else None,
                    "address": combine_address(data.get("address", ""), ""),
                    "city": data.get("city", "").strip(),
                    "country": standardize_country(data.get("country", ""))
                },
                "amenities": {
                    "general": standardized_amenities,
                    "room": []
                },
                "images": standardize_images(data.get("images")),
                "booking_conditions": [clean_text(cond.strip()) for cond in booking_conditions if cond]
            }
        except Exception as e:
            raise DataParsingError(f"Error parsing Patagonia data: {e}")
