import logging
import html2text
from datetime import datetime
from zep_cloud import Message

logger = logging.getLogger(__name__)
h = html2text.HTML2Text()
h.ignore_links = False

def to_zep_message(confluence_page):
    """
    Transform a Confluence page to Zep message format.

    Args:
        confluence_page (dict): Confluence page data, typically as returned by the Confluence API.

    Returns:
        Message: Zep Message object compatible with the current Zep Cloud API.

    Raises:
        Exception: If transformation fails.
    """
    logger.debug(f"Converting Confluence page {confluence_page.get('id', 'unknown')} to Zep message")
    
    try:
        # Extract relevant fields
        page_id = confluence_page.get('id', 'unknown')
        title = confluence_page.get('title', 'Untitled')
        content = confluence_page.get('content', '')
        url = confluence_page.get('url', '')
        
        # Convert HTML to text if needed
        if content and isinstance(content, str) and ('<' in content and '>' in content):
            content = h.handle(content)
        
        # Create message content
        message_content = f"Confluence page: {title}\n\n{content}\n\nURL: {url}"
        
        # Create a Message object compatible with the Zep Cloud API
        return Message(
            role="assistant",  # Use role field as expected by Message
            content=message_content
        )
    
    except Exception as e:
        logger.error(f"Error converting Confluence page to Zep message: {str(e)}")
        raise

def to_zep_json(confluence_page):
    """
    Transform a Confluence page to Zep JSON format for structured data.
    
    This function restructures Confluence pages to focus on the documentation content
    rather than Confluence-specific metadata. The page ID is preserved in metadata but
    not as a primary node in the graph.

    Args:
        confluence_page (dict): Confluence page data, typically as returned by the Confluence API.

    Returns:
        dict: Zep JSON format compatible with the current Zep Cloud API.

    Raises:
        Exception: If transformation fails.
    """
    logger.debug(f"Converting Confluence page {confluence_page.get('id', 'unknown')} to Zep JSON")
    
    try:
        # Extract relevant fields
        page_id = confluence_page.get('id', 'unknown')
        title = confluence_page.get('title', 'Untitled')
        content = confluence_page.get('content', '')
        url = confluence_page.get('url', '')
        
        # Convert HTML to text if needed
        if content and isinstance(content, str) and ('<' in content and '>' in content):
            content = h.handle(content)
        
        # Structure the data to focus on documentation content rather than Confluence metadata
        structured_data = {
            "product_documentation": {
                "title": title,
                "content": content,
                "metadata": {
                    "source": "Confluence",
                    "page_id": page_id,
                    "url": url
                }
            }
        }
        
        return {
            "name": f"Documentation: {title}",
            "episode_body": structured_data,
            "source": "json",
            "source_description": f"Confluence Page {page_id}"
        }
    
    except Exception as e:
        logger.error(f"Error converting Confluence page to Zep JSON: {str(e)}")
        raise
