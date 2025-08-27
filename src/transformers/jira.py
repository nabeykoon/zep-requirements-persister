import logging
import html2text
from datetime import datetime
from zep_cloud import Message

logger = logging.getLogger(__name__)
h = html2text.HTML2Text()
h.ignore_links = False

def to_zep_message(jira_issue):
    """
    Transform a JIRA issue to Zep message format.

    Args:
        jira_issue (dict): JIRA issue data, typically as returned by the JIRA API.

    Returns:
        Message: Zep Message object compatible with the current Zep Cloud API.

    Raises:
        Exception: If transformation fails.
    """
    logger.debug(f"Converting JIRA issue {jira_issue.get('key', 'unknown')} to Zep message")
    
    try:
        # Extract relevant fields
        issue_key = jira_issue.get('key', 'unknown')
        summary = jira_issue.get('summary', '')
        description = jira_issue.get('description', '')
        url = jira_issue.get('url', '')
        
        # Convert HTML to text if needed
        if description and isinstance(description, str) and ('<' in description and '>' in description):
            description = h.handle(description)
        
        # Create message content
        message_content = f"JIRA issue {issue_key} - {summary}\n\n{description}\n\nURL: {url}"
        
        # Create a Message object compatible with the Zep Cloud API
        return Message(
            role="assistant",  # Use role field as expected by Message
            content=message_content
        )
    
    except Exception as e:
        logger.error(f"Error converting JIRA issue to Zep message: {str(e)}")
        raise

def to_zep_json(jira_issue):
    """
    Transform a JIRA issue to Zep JSON format for structured data.
    
    This function restructures JIRA issues to focus on the product requirement content
    rather than JIRA-specific metadata. The issue ID is preserved in metadata but
    not as a primary node in the graph.

    Args:
        jira_issue (dict): JIRA issue data, typically as returned by the JIRA API.

    Returns:
        dict: Zep JSON format compatible with the current Zep Cloud API.

    Raises:
        Exception: If transformation fails.
    """
    logger.debug(f"Converting JIRA issue {jira_issue.get('key', 'unknown')} to Zep JSON")
    
    try:
        # Extract relevant fields
        issue_key = jira_issue.get('key', 'unknown')
        summary = jira_issue.get('summary', '')
        description = jira_issue.get('description', '')
        issue_type = jira_issue.get('type', 'Unknown')  # Now contains actual JIRA issue type (e.g., 'Bug', 'Story', 'Task')
        url = jira_issue.get('url', '')
        
        # Convert HTML to text if needed
        if description and isinstance(description, str) and ('<' in description and '>' in description):
            description = h.handle(description)
        
        # Structure the data to focus on requirement content rather than JIRA metadata
        structured_data = {
            "product_requirement": {
                "title": summary,
                "description": description,
                "metadata": {
                    "source": "JIRA",
                    "issue_key": issue_key,
                    "issue_type": issue_type,
                    "url": url
                }
            }
        }
        
        return {
            "name": f"Requirement: {summary}",
            "episode_body": structured_data,
            "source": "json",
            "source_description": f"JIRA Issue {issue_key}"
        }
    
    except Exception as e:
        logger.error(f"Error converting JIRA issue to Zep JSON: {str(e)}")
        raise
