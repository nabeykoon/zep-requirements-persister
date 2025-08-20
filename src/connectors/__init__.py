from .jira import JiraConnector
from .confluence import ConfluenceConnector
import logging

logger = logging.getLogger(__name__)

def get_connector(source_type, config):
    """
    Factory function to get the right connector based on source type.

    Args:
        source_type (str): The type of source ('jira' or 'confluence').
        config (dict): Configuration dictionary containing connection details.
            For JIRA and Confluence, should contain a section with 'base_url', 'username', 'api_token'.

    Returns:
        JiraConnector or ConfluenceConnector: The connector instance for the specified source.

    Raises:
        ValueError: If required config keys are missing or source_type is unsupported.
    """
    logger.info(f"Creating connector for source type: {source_type}")
    
    # Extract credentials from environment variables or config
    import os
    
    if source_type == 'jira':
        source_config = config.get('jira', {})
        base_url = os.environ.get('JIRA_URL', source_config.get('base_url'))
        username = os.environ.get('JIRA_USERNAME', source_config.get('username'))
        api_token = os.environ.get('JIRA_API_TOKEN', source_config.get('api_token'))
        
        if not base_url:
            raise ValueError("JIRA base URL is required in config or JIRA_URL environment variable")
        
        return JiraConnector(
            base_url=base_url,
            username=username,
            api_token=api_token
        )
    elif source_type == 'confluence':
        source_config = config.get('confluence', {})
        base_url = os.environ.get('CONFLUENCE_URL', source_config.get('base_url'))
        username = os.environ.get('CONFLUENCE_USERNAME', source_config.get('username'))
        api_token = os.environ.get('CONFLUENCE_API_TOKEN', source_config.get('api_token'))
        
        if not base_url:
            raise ValueError("Confluence base URL is required in config or CONFLUENCE_URL environment variable")
            
        return ConfluenceConnector(
            base_url=base_url,
            username=username,
            api_token=api_token
        )
    else:
        raise ValueError(f"Unsupported source type: {source_type}")
