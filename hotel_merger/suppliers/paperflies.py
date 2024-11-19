from typing import List, Dict

from hotel_merger.suppliers.base import BaseSupplier
from hotel_merger.utils import deduplicate_amenities, clean_text, combine_address, standardize_country, standardize_images
from hotel_merger.errors import DataParsingError

class PaperfliesSupplier(BaseSupplier):
    """
    Supplier class for Paperflies.
    Handles fetching and parsing data from the Paperflies supplier.
    """

    def endpoint(self) -> str:
        """
        Returns the API endpoint URL for Paperflies supplier.

        Returns:
            str: The Paperflies supplier's API endpoint.
        """
        return "https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/paperflies"

    def parse(self, data: Dict) -> Dict:
        """
        Parse Paperflies supplier data into standard format.

        Args:
            data (Dict): Raw data from Paperflies.

        Raises:
            DataParsingError: If required fields are missing or invalid.

        Returns:
            Dict: Standardized hotel data.
        """
        try:
            amenities_general = data.get("amenities", {}).get("general", []) or []
            if not isinstance(amenities_general, list):
                amenities_general = []
            amenities_room = data.get("amenities", {}).get("room", []) or []
            if not isinstance(amenities_room, list):
                amenities_room = []
            booking_conditions = data.get("booking_conditions", []) or []
            if not isinstance(booking_conditions, list):
                booking_conditions = []

            standardized_general = deduplicate_amenities(amenities_general)
            standardized_room = deduplicate_amenities(amenities_room)
            standardized_booking = [clean_text(cond.strip()) for cond in booking_conditions if cond]

            return {
                "id": data.get("hotel_id", "").strip(),
                "destination_id": data.get("destination_id"),
                "name": data.get("hotel_name", "").strip(),
                "description": clean_text(data.get("details", "").strip()) if data.get("details") else "",
                "location": {
                    "lat": None,  # Paperflies does not provide lat, lng
                    "lng": None,
                    "address": combine_address(data.get("location", {}).get("address", ""), ""),
                    "city": "",  # No city information from Paperflies
                    "country": standardize_country(data.get("location", {}).get("country", ""))
                },
                "amenities": {
                    "general": standardized_general,
                    "room": standardized_room
                },
                "images": standardize_images(data.get("images")),
                "booking_conditions": standardized_booking
            }
        except Exception as e:
            raise DataParsingError(f"Error parsing Paperflies data: {e}")
