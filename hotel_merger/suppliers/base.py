from abc import ABC, abstractmethod
from typing import List, Dict
import requests
import json
from hotel_merger.errors import SupplierFetchError, DataParsingError

class BaseSupplier(ABC):
    """
    Abstract base class for all suppliers.
    Defines the required methods for fetching and parsing data from a supplier.
    """
    
    @abstractmethod
    def endpoint(self) -> str:
        """
        Returns the API endpoint URL for the supplier.

        Raises:
            NotImplementedError: If the method is not overridden.

        Returns:
            str: The supplier's API endpoint.
        """
        raise NotImplementedError("The endpoint() method must be overridden.")
    
    @abstractmethod
    def parse(self, data: Dict) -> Dict:
        """
        Parses and cleans raw data from the supplier into a standard format.

        Args:
            data (Dict): Raw data fetched from the supplier's API.

        Raises:
            DataParsingError: If parsing fails.

        Returns:
            Dict: Standardized hotel data.
        """
        raise NotImplementedError("The parse() method must be overridden.")
    
    def fetch(self) -> List[Dict]:
        """
        Fetches data from the supplier's endpoint and parses it.

        Returns:
            List[Dict]: List of parsed hotel data dictionaries.

        Raises:
            SupplierFetchError: If fetching data fails due to HTTP errors.
            DataParsingError: If parsing the fetched data fails.
        """
        try:
            response = requests.get(self.endpoint())
            response.raise_for_status()
            json_data = response.json()
            if not isinstance(json_data, list):
                raise DataParsingError("Invalid data format received from supplier.")
            return [self.parse(item) for item in json_data]
        except requests.RequestException as e:
            raise SupplierFetchError(f"HTTP error occurred: {e}")
        except json.JSONDecodeError as e:
            raise DataParsingError(f"JSON decode error: {e}")
        except Exception as e:
            raise DataParsingError(f"Unexpected error: {e}")
