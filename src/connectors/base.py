class BaseConnector:
    """
    Base connector interface for data sources.
    Subclasses should implement connection and data fetching logic for specific sources.
    """
    
    def __init__(self, base_url, **kwargs):
        """
        Initialize with base URL and other common parameters.

        Args:
            base_url (str): The base URL of the data source (JIRA, Confluence, etc).
            **kwargs: Additional parameters for specific connectors.
        """
        self.base_url = base_url
        self.client = None
    
    def connect(self):
        """
        Establish connection to the data source.
        Subclasses must implement this method to set up their client.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError("Subclasses must implement connect()")
    
    def fetch_data(self, items):
        """
        Fetch data based on items configuration.
        Subclasses must implement this method to retrieve data from the source.

        Args:
            items (list): List of item configurations (issue keys, page IDs, etc).

        Returns:
            list: List of data items fetched from the source.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError("Subclasses must implement fetch_data()")
    
    def close(self):
        """
        Close connection to the data source and clean up client.
        """
        self.client = None
