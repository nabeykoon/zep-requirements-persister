from atlassian import Confluence
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)

class ConfluenceConnector(BaseConnector):
    """
    Connector for fetching Confluence pages.
    Handles authentication, connection, and data retrieval for Confluence.
    """
    
    def __init__(self, base_url, username=None, api_token=None):
        """
        Initialize Confluence connector.

        Args:
            base_url (str): Confluence instance base URL.
            username (str, optional): Confluence username.
            api_token (str, optional): Confluence API token.
        """
        super().__init__(base_url)
        self.username = username
        self.api_token = api_token
    
    def connect(self):
        """
        Connect to Confluence using provided credentials.
        Sets up the Confluence client for API calls.

        Returns:
            ConfluenceConnector: Self, for chaining.

        Raises:
            Exception: If connection fails.
        """
        logger.info("Connecting to Confluence...")
        try:
            self.client = Confluence(
                url=self.base_url,
                username=self.username,
                password=self.api_token
            )
            logger.info("Successfully connected to Confluence")
        except Exception as e:
            logger.error(f"Failed to connect to Confluence: {e}")
            raise
        return self
    
    async def fetch_data(self, page_configs):
        """
        Fetch specific Confluence pages by ID.

        Args:
            page_configs (list): List of page configuration dicts, each with an 'id' key.
                                Example: [{'id': '123456'}, {'id': '123457', 'title': 'Optional Title'}]

        Returns:
            list: List of dictionaries with comprehensive page details including:
                  - Basic: id, title, content, type, url
                  - Metadata: space, created_date, last_modified, author, labels, version
                  Content is in HTML format as retrieved from Confluence storage format.
                 
        Raises:
            ConnectionError: If not connected to Confluence. Call connect() first.
            Exception: If an error occurs while fetching pages.
        """
        if not self.client:
            raise ConnectionError("Not connected to Confluence. Call connect() first.")
        
        logger.info(f"Fetching {len(page_configs)} Confluence pages...")
        results = []
        
        for page_config in page_configs:
            page_id = page_config.get('id')
            if not page_id:
                logger.warning("Skipping page config without 'id'")
                continue
            
            try:
                logger.info(f"Fetching Confluence page {page_id}")
                
                # Get page content with body in storage format (HTML)
                page = self.client.get_page_by_id(page_id, expand='body.storage')
                
                # Extract comprehensive page information for rich metadata
                result = {
                    'id': page_id,
                    'title': page.get('title', ''),
                    'content': page.get('body', {}).get('storage', {}).get('value', ''),
                    'space': page.get('space', {}).get('name', ''),
                    'created_date': page.get('createdDate', ''),
                    'last_modified': page.get('lastModified', ''),
                    'author': page.get('creator', {}).get('displayName', ''),
                    'labels': [label['name'] for label in page.get('labels', [])],
                    'version': page.get('version', {}).get('number', ''),
                    'type': 'confluence_page',
                    'url': f"{self.base_url}/pages/viewpage.action?pageId={page_id}"
                }
                
                results.append(result)
                logger.info(f"Successfully fetched page {page_id}")
            except Exception as e:
                logger.error(f"Error fetching page {page_id}: {e}")
                # Continue with next item as per requirements
        
        return results
