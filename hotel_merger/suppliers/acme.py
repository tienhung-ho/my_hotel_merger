from typing import Dict
from hotel_merger.suppliers.base import BaseSupplier
from hotel_merger.utils import deduplicate_amenities, standardize_country

class AcmeSupplier(BaseSupplier):
    """Supplier class for Acme."""
    def endpoint(self) -> str:
        """
        Returns the API endpoint URL for Acme supplier.

        Returns:
            str: The Acme supplier's API endpoint.
        """
        return "https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/acme"

    def parse(self, data: Dict) -> Dict:
        """
        Parse Acme supplier data into standard format.
        
        Args:
            data (Dict): Raw data from Acme.
        
        Returns:
            Dict: Standardized hotel data.
        """
        try:
            amenities = data.get("Facilities", []) or []
            if not isinstance(amenities, list):
                amenities = []
            standardized_amenities = deduplicate_amenities(amenities)
            return {
                "id": data.get("Id", "").strip(),
                "destination_id": data.get("DestinationId"),
                "name": data.get("Name", "").strip(),
                "description": data.get("Description", "").strip(),
                "location": {
                    "lat": data.get("Latitude") if isinstance(data.get("Latitude"), (int, float)) else None,
                    "lng": data.get("Longitude") if isinstance(data.get("Longitude"), (int, float)) else None,
                    "address": f"{data.get('Address', '').strip()}, {data.get('PostalCode', '').strip()}",
                    "city": data.get("City", "").strip(),
                    "country": standardize_country(data.get("Country", "").strip())
                },
                "amenities": {
                    "general": standardized_amenities
                },
                "images": {
                    "rooms": [],
                    "site": [],
                    "amenities": []
                },
                "booking_conditions": []
            }
        except Exception:
            return {}
