from .jira import to_zep_message as jira_to_zep_message
from .jira import to_zep_json as jira_to_zep_json
from .confluence import to_zep_message as confluence_to_zep_message
from .confluence import to_zep_json as confluence_to_zep_json
import logging

logger = logging.getLogger(__name__)

def transform_to_zep_message(item, source_type):
    """
    Transform an item to Zep message format based on source type.

    Args:
        item (dict): The source data item (JIRA issue or Confluence page).
        source_type (str): The type of source ('jira' or 'confluence').

    Returns:
        Message: Zep Message object compatible with the Zep Cloud API v3.4.1.

    Raises:
        ValueError: If source_type is unsupported.
    """
    logger.debug(f"Transforming {source_type} item to Zep message")
    
    if source_type == 'jira':
        return jira_to_zep_message(item)
    elif source_type == 'confluence':
        return confluence_to_zep_message(item)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

def transform_to_zep_json(item, source_type):
    """
    Transform an item to Zep JSON format based on source type.

    Args:
        item (dict): The source data item (JIRA issue or Confluence page).
        source_type (str): The type of source ('jira' or 'confluence').

    Returns:
        dict: Zep JSON format for the item.

    Raises:
        ValueError: If source_type is unsupported.
    """
    logger.debug(f"Transforming {source_type} item to Zep JSON")
    
    if source_type == 'jira':
        return jira_to_zep_json(item)
    elif source_type == 'confluence':
        return confluence_to_zep_json(item)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")
