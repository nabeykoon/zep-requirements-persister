import logging
import html2text
import re
from datetime import datetime
from zep_cloud import Message

logger = logging.getLogger(__name__)
h = html2text.HTML2Text()
h.ignore_links = False

def extract_sections(content):
    """Extract sections/headings from content for better structure."""
    if not content:
        return []

    sections = []
    # Look for heading patterns in HTML/markdown
    heading_patterns = [
        r'<h[1-6][^>]*>(.*?)</h[1-6]>',  # HTML headings
        r'^#{1,6}\s+(.*)$',                # Markdown headings
    ]

    for pattern in heading_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        if matches:
            sections.extend(matches)

    return sections[:10]  # Limit to first 10 sections

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

    This function restructures Confluence pages with rich metadata and content structure
    to enhance AI understanding and searchability. Includes space, author, dates, labels,
    version info, and extracted sections for better content organization.

    Args:
        confluence_page (dict): Confluence page data with rich metadata from the connector.

    Returns:
        dict: Zep JSON format with enhanced metadata compatible with Zep Cloud v3.4.1 API.

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

        # Extract rich metadata
        space = confluence_page.get('space', '')
        created_date = confluence_page.get('created_date', '')
        last_modified = confluence_page.get('last_modified', '')
        author = confluence_page.get('author', '')
        labels = confluence_page.get('labels', [])
        version = confluence_page.get('version', '')
        
        # Convert HTML to text if needed
        if content and isinstance(content, str) and ('<' in content and '>' in content):
            content = h.handle(content)
        
        # Extract sections from content for better structure
        sections = extract_sections(content)

        # Structure the data with rich metadata for better AI understanding
        structured_data = {
            "product_documentation": {
                "title": title,
                "content": {
                    "full_text": content,
                    "sections": sections
                },
                "metadata": {
                    "source": "Confluence",
                    "page_id": page_id,
                    "space": space,
                    "url": url,
                    "author": author,
                    "created_date": created_date,
                    "last_modified": last_modified,
                    "version": version,
                    "labels": labels
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
