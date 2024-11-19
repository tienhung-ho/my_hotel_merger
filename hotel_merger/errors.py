class SupplierFetchError(Exception):
    """Exception raised when fetching data from a supplier fails."""
    pass

class DataParsingError(Exception):
    """Exception raised when parsing supplier data fails."""
    pass

class MergeError(Exception):
    """Exception raised when merging data fails."""
    pass
