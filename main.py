#!/usr/bin/env python3
"""
Main script for the Zep Requirements Persister utility.

This utility fetches requirements from JIRA and Confluence and persists them to Zep's
memory system for use by AI agents. It supports both message-style and JSON-formatted
storage, selective processing of sources, and detailed logging.

Usage:
    python -m main [--config CONFIG_FILE] [--json] [--source {jira,confluence}] [--verbose]

Author: Your Organization
Date: August 2025
License: MIT
"""

import os
import sys
import logging
import asyncio
import argparse
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connectors import get_connector
from src.transformers import transform_to_zep_message, transform_to_zep_json
from src.persistence import get_persistence
from src.config import load_config

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"zep_persister_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def process_source(source_type, items, config, persistence, use_json=False):
    """
    Process items from a source and persist them to Zep.
    
    This function iterates through each item from a source (JIRA or Confluence),
    transforms it to the appropriate format (message or JSON), and persists it
    to Zep. It keeps track of successes and failures and handles exceptions for
    individual items.
    
    Args:
        source_type (str): Type of source ('jira' or 'confluence').
        items (list): List of items to process from the source.
        config (dict): Configuration dictionary.
        persistence (BasePersistence): Persistence implementation to use.
        use_json (bool, optional): Whether to use JSON format instead of messages.
                                 Defaults to False.
        
    Returns:
        tuple: (success_count, failure_count) - Counts of successfully processed
               and failed items.
    """
    success = 0
    failure = 0
    
    for item in items:
        try:
            if use_json:
                # Transform to JSON format
                zep_data = transform_to_zep_json(item, source_type)
                result = await persistence.persist_json(zep_data)
            else:
                # Transform to message format
                zep_message = transform_to_zep_message(item, source_type)
                result = await persistence.persist_message(zep_message)
                
            if result:
                success += 1
                item_id = item.get('key', item.get('id', 'unknown'))
                logger.info(f"Successfully persisted {source_type} item {item_id} to Zep")
            else:
                failure += 1
                item_id = item.get('key', item.get('id', 'unknown'))
                logger.error(f"Failed to persist {source_type} item {item_id} to Zep")
                
        except Exception as e:
            failure += 1
            item_id = item.get('key', item.get('id', 'unknown'))
            logger.error(f"Error processing {source_type} item {item_id}: {str(e)}")
    
    return success, failure

async def run(config_file, use_json=False, source_filter=None):
    """
    Main execution function for the Zep Requirements Persister.
    
    This function orchestrates the entire process:
    1. Loads configuration from the specified file
    2. Sets up the persistence mechanism
    3. Checks Zep service health
    4. Processes JIRA issues (if configured and not filtered out):
       - Creates and connects the JIRA connector
       - Fetches issues using configured issue keys
       - Transforms and persists each issue to Zep
    5. Processes Confluence pages (if configured and not filtered out):
       - Creates and connects the Confluence connector
       - Fetches pages using configured page IDs
       - Transforms and persists each page to Zep
    6. Properly closes the Zep client connection
    7. Reports overall results
    
    It handles the connection to each source, fetching data, and persisting it
    to Zep in the specified format, with proper error handling at each step.
    
    Args:
        config_file (str): Path to the configuration file.
        use_json (bool, optional): Whether to use JSON format instead of messages.
                                 Defaults to False.
        source_filter (str, optional): Filter to only process a specific source
                                     ('jira' or 'confluence'). If None, processes
                                     all configured sources. Defaults to None.
    """
    # Load configuration
    config = load_config(config_file)
    
    # Initialize persistence
    persistence = get_persistence(config)
    
    # Check Zep service health
    try:
        is_healthy = await persistence.health_check()
        if not is_healthy:
            logger.error("Zep service is not healthy. Aborting.")
            return
    except Exception as e:
        logger.error(f"Failed to check Zep service health: {str(e)}")
        return
    
    total_success = 0
    total_failure = 0
    
    # Process JIRA issues
    if not source_filter or source_filter.lower() == 'jira':
        if 'jira' in config and 'issues' in config['jira']:
            try:
                jira_config = config.get('jira', {})
                jira_issues_list = jira_config.get('issues', [])
                
                jira_connector = get_connector('jira', config)
                jira_connector.connect()
                jira_issues = await jira_connector.fetch_data(jira_issues_list)
                
                if jira_issues:
                    logger.info(f"Fetched {len(jira_issues)} JIRA issues")
                    jira_success, jira_failure = await process_source('jira', jira_issues, config, persistence, use_json)
                    total_success += jira_success
                    total_failure += jira_failure
                    logger.info(f"Processed JIRA issues: {jira_success} succeeded, {jira_failure} failed")
                else:
                    logger.warning("No JIRA issues fetched")
            except Exception as e:
                logger.error(f"Error processing JIRA issues: {str(e)}")
    
    # Process Confluence pages
    if not source_filter or source_filter.lower() == 'confluence':
        if 'confluence' in config and 'pages' in config['confluence']:
            try:
                confluence_config = config.get('confluence', {})
                confluence_pages_list = confluence_config.get('pages', [])
                
                confluence_connector = get_connector('confluence', config)
                confluence_connector.connect()
                confluence_pages = await confluence_connector.fetch_data(confluence_pages_list)
                
                if confluence_pages:
                    logger.info(f"Fetched {len(confluence_pages)} Confluence pages")
                    conf_success, conf_failure = await process_source('confluence', confluence_pages, config, persistence, use_json)
                    total_success += conf_success
                    total_failure += conf_failure
                    logger.info(f"Processed Confluence pages: {conf_success} succeeded, {conf_failure} failed")
                else:
                    logger.warning("No Confluence pages fetched")
            except Exception as e:
                logger.error(f"Error processing Confluence pages: {str(e)}")
    
    # Make sure to close the Zep client properly
    try:
        await persistence.close_client()
    except Exception as e:
        logger.warning(f"Error closing Zep client: {str(e)}")
        
    logger.info(f"Completed persisting requirements to Zep. Total: {total_success} succeeded, {total_failure} failed")

def main():
    """
    Entry point for the script.
    
    This function:
    1. Parses command-line arguments
    2. Configures logging based on verbosity setting
    3. Runs the main async function
    4. Handles interruptions and unexpected errors
    
    Command-line arguments:
        --config, -c: Path to the configuration file (default: config/config.yaml)
        --json, -j: Use JSON format instead of messages
        --source, -s: Process only a specific source (jira or confluence)
        --verbose, -v: Enable verbose (DEBUG level) logging
    
    Returns:
        None
        
    Exits:
        With code 1 on unhandled exceptions
    """
    parser = argparse.ArgumentParser(description="Persist requirements from JIRA and Confluence to Zep")
    parser.add_argument('--config', '-c', default='config/config.yaml', help='Path to the configuration file')
    parser.add_argument('--json', '-j', action='store_true', help='Use JSON format instead of messages')
    parser.add_argument('--source', '-s', choices=['jira', 'confluence'], help='Process only specific source')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the async main function
    try:
        asyncio.run(run(args.config, args.json, args.source))
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
