# hotel_merger/models.py

from typing import List, Dict, Optional

class AmenityImage:
    """
    Represents an image related to amenities or rooms in a hotel.
    
    Attributes:
        link (str): URL of the image.
        description (str): Description of the image.
    """
    def __init__(self, link: str, description: str):
        self.link = link
        self.description = description

    def to_dict(self) -> Dict[str, str]:
        """
        Converts the AmenityImage instance to a dictionary.

        Returns:
            Dict[str, str]: Dictionary representation of the AmenityImage.
        """
        return {
            "link": self.link,
            "description": self.description
        }

class Location:
    """
    Represents the geographical location of a hotel.
    
    Attributes:
        lat (Optional[float]): Latitude coordinate.
        lng (Optional[float]): Longitude coordinate.
        address (str): Street address.
        city (str): City name.
        country (str): Country name.
    """
    def __init__(self, lat: Optional[float], lng: Optional[float], address: str, city: str, country: str):
        self.lat = lat
        self.lng = lng
        self.address = address
        self.city = city
        self.country = country

    def to_dict(self) -> Dict[str, Optional[float]]:
        """
        Converts the Location instance to a dictionary.

        Returns:
            Dict[str, Optional[float]]: Dictionary representation of the Location.
        """
        return {
            "lat": self.lat,
            "lng": self.lng,
            "address": self.address,
            "city": self.city,
            "country": self.country
        }

class Amenities:
    """
    Represents the amenities available at a hotel.
    
    Attributes:
        general (List[str]): List of general amenities.
        room (List[str]): List of room-specific amenities.
    """
    def __init__(self, general: List[str], room: List[str]):
        self.general = general
        self.room = room

    def to_dict(self) -> Dict[str, List[str]]:
        """
        Converts the Amenities instance to a dictionary.

        Returns:
            Dict[str, List[str]]: Dictionary representation of the Amenities.
        """
        return {
            "general": self.general,
            "room": self.room
        }

class Images:
    """
    Represents various categories of images associated with a hotel.
    
    Attributes:
        rooms (List[AmenityImage]): List of room-related images.
        site (List[AmenityImage]): List of site-related images.
        amenities (List[AmenityImage]): List of amenities-related images.
    """
    def __init__(self, rooms: List[AmenityImage], site: List[AmenityImage], amenities: List[AmenityImage]):
        self.rooms = rooms
        self.site = site
        self.amenities = amenities

    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Converts the Images instance to a dictionary.

        Returns:
            Dict[str, List[Dict[str, str]]]: Dictionary representation of the Images.
        """
        return {
            "rooms": [img.to_dict() for img in self.rooms],
            "site": [img.to_dict() for img in self.site],
            "amenities": [img.to_dict() for img in self.amenities]
        }

class Hotel:
    """
    Represents a hotel with all its details.
    
    Attributes:
        id (str): Unique identifier for the hotel.
        destination_id (int): Identifier for the destination.
        name (str): Name of the hotel.
        location (Location): Location details.
        description (str): Description of the hotel.
        amenities (Amenities): Amenities available at the hotel.
        images (Images): Images related to the hotel.
        booking_conditions (List[str]): List of booking conditions.
    """
    def __init__(self, 
                 id: str,
                 destination_id: int,
                 name: str,
                 location: Location,
                 description: str,
                 amenities: Amenities,
                 images: Images,
                 booking_conditions: List[str]):
        self.id = id
        self.destination_id = destination_id
        self.name = name
        self.location = location
        self.description = description
        self.amenities = amenities
        self.images = images
        self.booking_conditions = booking_conditions

    def to_dict(self) -> Dict:
        """
        Converts the Hotel instance to a dictionary.

        Returns:
            Dict: Dictionary representation of the Hotel.
        """
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "name": self.name,
            "location": self.location.to_dict(),
            "description": self.description,
            "amenities": self.amenities.to_dict(),
            "images": self.images.to_dict(),
            "booking_conditions": self.booking_conditions
        }
