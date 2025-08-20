from .zep import ZepPersistence
import logging

logger = logging.getLogger(__name__)

def get_persistence(config, persistence_type='zep'):
    """
    Factory function to get the persistence implementation.
    
    This function creates and returns the appropriate persistence implementation
    based on the specified type. Currently only supports Zep persistence using
    the Zep Cloud API v3.4.1.
    
    Args:
        config (dict): Configuration dictionary containing all settings needed
                      for the persistence implementation, including API URLs and keys.
        persistence_type (str, optional): Type of persistence to use. 
                                         Defaults to 'zep'.
        
    Returns:
        BasePersistence: Concrete implementation of the persistence interface.
        
    Raises:
        ValueError: If an unsupported persistence type is specified.
        
    Example:
        >>> config = load_config('config.yaml')
        >>> persistence = get_persistence(config)
        >>> await persistence.persist_message(message_data)
    """
    logger.debug(f"Getting persistence implementation for type: {persistence_type}")
    
    if persistence_type == 'zep':
        return ZepPersistence(config)
    else:
        raise ValueError(f"Unsupported persistence type: {persistence_type}")
