import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BasePersistence(ABC):
    """
    Base class for all persistence implementations.
    
    This abstract class defines the interface that all persistence implementations
    must adhere to. It provides methods for persisting both message-style and
    JSON-formatted data to a storage system, as well as health checking.
    
    Implementations should handle connection details, authentication, and
    error handling specific to their target storage system.
    """
    
    def __init__(self, config):
        """
        Initialize with configuration.
        
        Args:
            config (dict): Configuration dictionary containing all necessary
                          settings for the persistence implementation.
        """
        self.config = config
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    async def persist_message(self, message, collection=None):
        """
        Persist a message to storage.
        
        This method should save a conversation-style message to the storage system.
        The message format should be compatible with the target storage system's
        requirements for conversation data.
        
        Args:
            message (dict): The message to persist, typically containing keys like
                           'role', 'content', 'timestamp', etc.
            collection (str, optional): Collection/memory name to store the message in.
                                       If None, a default collection should be used.
            
        Returns:
            bool: Success status - True if the message was persisted successfully,
                 False otherwise.
                 
        Raises:
            Exception: Implementation-specific exceptions may be raised.
        """
        pass
    
    @abstractmethod
    async def persist_json(self, data, collection=None):
        """
        Persist JSON data to storage.
        
        This method should save structured JSON data to the storage system.
        The data format should be compatible with the target storage system's
        requirements for structured data.
        
        Args:
            data (dict): The structured data to persist, formatted according to
                        the requirements of the target storage system.
            collection (str, optional): Collection/memory name to store the data in.
                                       If None, a default collection should be used.
            
        Returns:
            bool: Success status - True if the data was persisted successfully,
                 False otherwise.
                 
        Raises:
            Exception: Implementation-specific exceptions may be raised.
        """
        pass
    
    @abstractmethod
    async def health_check(self):
        """
        Check if the persistence service is available and healthy.
        
        This method should perform a lightweight check to verify that the
        target storage system is accessible and operational.
        
        Returns:
            bool: True if service is available and healthy, False otherwise.
            
        Raises:
            Exception: Implementation-specific exceptions may be raised.
        """
        pass
        
    @abstractmethod
    async def close_client(self):
        """
        Close any open connections to the persistence service.
        
        This method should be called before the application exits to ensure
        that all connections are properly closed.
        
        Returns:
            bool: True if connections were closed successfully, False otherwise.
            
        Raises:
            Exception: Implementation-specific exceptions may be raised.
        """
        pass
