from jira import JIRA
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)

class JiraConnector(BaseConnector):
    """
    Connector for fetching JIRA issues.
    Handles authentication, connection, and data retrieval for JIRA.
    """
    
    def __init__(self, base_url, username=None, api_token=None):
        """
        Initialize JIRA connector.

        Args:
            base_url (str): JIRA instance base URL.
            username (str, optional): JIRA username.
            api_token (str, optional): JIRA API token.
        """
        super().__init__(base_url)
        self.auth = None
        if username and api_token:
            self.auth = (username, api_token)
    
    def connect(self):
        """
        Connect to JIRA using provided credentials.
        Sets up the JIRA client for API calls.

        Returns:
            JiraConnector: Self, for chaining.

        Raises:
            Exception: If connection fails.
        """
        logger.info("Connecting to JIRA...")
        try:
            self.client = JIRA(server=self.base_url, basic_auth=self.auth)
            logger.info("Successfully connected to JIRA")
        except Exception as e:
            logger.error(f"Failed to connect to JIRA: {e}")
            raise
        return self
    
    async def fetch_data(self, issue_keys):
        """
        Fetch specific JIRA issues by key.

        Args:
            issue_keys (list): List of JIRA issue keys to fetch. Each element can be either:
                              - A string representing the issue key (e.g., 'PROJ-123')
                              - A dictionary with a 'key' field (e.g., {'key': 'PROJ-123'})

        Returns:
            list: List of dictionaries with issue details (key, summary, description, type, url).
                 The result includes only essential information as required by the transformers.
                 
        Raises:
            ConnectionError: If not connected to JIRA. Call connect() first.
            Exception: If an error occurs while fetching issues.
        """
        if not self.client:
            raise ConnectionError("Not connected to JIRA. Call connect() first.")
        
        logger.info(f"Fetching {len(issue_keys)} JIRA issues...")
        results = []
        
        for key in issue_keys:
            try:
                # Handle different formats (dict with 'key' or direct string)
                issue_key = key.get('key', key) if isinstance(key, dict) else key
                
                logger.info(f"Fetching JIRA issue {issue_key}")
                issue = self.client.issue(issue_key)
                
                # Extract only title and description as specified
                result = {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'description': issue.fields.description or '',
                    'type': 'jira_issue',
                    'url': f"{self.base_url}/browse/{issue.key}"
                }
                
                results.append(result)
                logger.info(f"Successfully fetched issue {issue.key}")
            except Exception as e:
                logger.error(f"Error fetching issue {key}: {e}")
                # Continue with next item as per requirements
        
        return results
