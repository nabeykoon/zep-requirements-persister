import os
import yaml
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_config(config_path):
    """Load configuration from YAML file and environment variables."""
    # Load environment variables from .env file
    load_dotenv()
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load YAML config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    # Ensure sections exist
    if 'zep' not in config:
        config['zep'] = {}
    if 'jira' not in config:
        config['jira'] = {}
    if 'confluence' not in config:
        config['confluence'] = {}
    
    # Override with environment variables
    config['zep']['api_key'] = os.environ.get('ZEP_API_KEY')
    
    config['jira']['base_url'] = os.environ.get('JIRA_BASE_URL')
    config['jira']['username'] = os.environ.get('JIRA_USERNAME')
    config['jira']['api_token'] = os.environ.get('JIRA_API_TOKEN')
    
    config['confluence']['base_url'] = os.environ.get('CONFLUENCE_BASE_URL')
    config['confluence']['username'] = os.environ.get('CONFLUENCE_USERNAME')
    config['confluence']['api_token'] = os.environ.get('CONFLUENCE_API_TOKEN')
    
    # Set default values for Zep configuration if not provided
    if 'project' not in config['zep']:
        config['zep']['project'] = 'pet-store'
    if 'session_id' not in config['zep']:
        config['zep']['session_id'] = 'pet-store-requirements'
    if 'user_id' not in config['zep']:
        config['zep']['user_id'] = 'pet-store-knowledge'
    if 'graph_id' not in config['zep']:
        config['zep']['graph_id'] = config['zep']['user_id']  # Use user_id as graph_id by default
    
    # Basic validation
    if not config['zep'].get('api_key'):
        raise ValueError("Zep API key is required in .env file")
    
    logger.info(f"Loaded configuration from {config_path}")
    return config
