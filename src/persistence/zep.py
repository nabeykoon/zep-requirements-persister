import logging
import json
from zep_cloud import Zep, AsyncZep, Message
from .base import BasePersistence

logger = logging.getLogger(__name__)

class ZepPersistence(BasePersistence):
    """
    Implementation of persistence using Zep Cloud API.
    
    This class provides methods to persist both message-style and JSON-formatted
    data to a Zep memory system. It implements the BasePersistence interface
    and handles all Zep-specific API interactions, authentication, and error handling.
    
    For Zep Cloud API v3.4.1, both persistence methods are supported:
    
    1. JSON persistence method (persist_json): Uses the graph API to store structured data.
       This is the recommended approach for most use cases, especially for JIRA and
       Confluence data, due to its reliability and performance.
    
    2. Message persistence method (persist_message): Uses the thread API to store conversational data.
       This has been implemented using thread.add_messages_batch() for compatibility with v3.4.1.
    
    Zep is a long-term memory store designed for AI applications, allowing for
    semantic search and retrieval of stored information.
    """
    
    def __init__(self, config):
        """
        Initialize the Zep persistence implementation.
        
        Sets up the connection details for the Zep API based on the provided
        configuration. Initializes the AsyncZep client with proper authentication.
        
        Args:
            config (dict): Configuration dictionary containing Zep-specific settings:
                          - zep.api_key: API key for authentication (required)
                          - zep.project: Default project/collection name (default: requirements)
                          - zep.session_id: Session ID for organizing thread-based requirements
                          - zep.user_id: Used as graph_id for graph-based product knowledge
        
        Raises:
            ValueError: If required configuration parameters are missing
        """
        super().__init__(config)
        
        # Extract configuration (defaults are already set in config.py)
        zep_config = config.get('zep', {})
        self.api_key = zep_config.get('api_key', '')
        self.project = zep_config.get('project')
        self.session_id = zep_config.get('session_id')
        self.graph_id = zep_config.get('graph_id')
        
        # Validate required configuration
        if not self.api_key:
            raise ValueError("Zep API key is required in configuration")
        
        # Initialize AsyncZep client from Zep Cloud API v3.4.1
        try:
            self.client = AsyncZep(api_key=self.api_key)
            logger.info(f"Initialized Zep persistence with project: {self.project}, session: {self.session_id}, graph: {self.graph_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Zep client: {str(e)}")
            raise ValueError(f"Failed to initialize Zep client: {str(e)}")
    
    async def persist_message(self, message, collection=None):
        """
        Persist a message to Zep using the thread API.
        
        This method stores a Message object in Zep's thread API using add_messages_batch.
        It first ensures that the thread exists, then adds the message to the thread.
        
        Note: This method may return 404 errors with some versions of Zep Cloud API.
        In such cases, use persist_json instead with the --json flag.
        
        Args:
            message (Message or dict): The message to persist, either a Message object or a dictionary 
                                      containing 'role' and 'content'.
            collection (str, optional): Thread ID to use. If None, uses the
                                       session_id from configuration.
            
        Returns:
            bool: True if successful, False otherwise.
            
        Raises:
            Exception: If an error occurs while persisting message to Zep.
        """
        if not collection:
            collection = self.session_id
        
        try:
            # First ensure the thread exists
            thread_exists = await self.ensure_thread_exists(collection)
            if not thread_exists:
                logger.error(f"Cannot persist message - thread {collection} does not exist and could not be created")
                return False
            
            # Handle both Message objects and dictionaries
            try:
                if isinstance(message, Message):
                    zep_message = message
                else:
                    # Create a Zep Message object from dictionary
                    role = message.get('role', 'system')
                    content = message.get('content', '')
                    
                    # Validate role and content
                    if not content:
                        logger.warning("Message content is empty")
                    
                    zep_message = Message(
                        role=role,  # Use role field for Message object
                        content=content
                    )
            except Exception as msg_error:
                logger.error(f"Error creating message object: {str(msg_error)}")
                return False
            
            # Attempt to add message to thread using the batch method for better compatibility
            try:
                await self.client.thread.add_messages_batch(
                    thread_id=collection,
                    messages=[zep_message]
                )
                
                logger.info(f"Successfully persisted message to Zep thread: {collection}")
                return True
            except Exception as add_error:
                error_msg = str(add_error)
                if "thread not found" in error_msg.lower():
                    logger.error(f"Thread exists but message endpoint is not compatible with API v3.4.1")
                else:
                    logger.error(f"Error adding message: {error_msg}")
                raise add_error
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                logger.error(f"Error persisting message to Zep: Endpoint not found (404). Check API version compatibility.")
            elif "401" in error_msg or "403" in error_msg:
                logger.error(f"Error persisting message to Zep: Authentication error. Check API key.")
            else:
                logger.error(f"Error persisting message to Zep: {error_msg}")
            return False
    
    async def persist_json(self, data, collection=None):
        """
        Persist JSON data to Zep using the graph API.
        
        This method sends structured JSON data to Zep's graph API, which is
        designed for non-conversational, structured data like JIRA issues and
        Confluence pages. It first ensures the graph exists, then adds the data.
        
        This is the recommended method for persisting JIRA and Confluence data
        with Zep Cloud API v3.4.1.
        
        Args:
            data (dict): The structured data to persist, typically containing:
                        - name: Name of the memory
                        - episode_body: The actual data content (JIRA issue or Confluence page)
                        - source: Source type (e.g., 'json')
                        - source_description: Description of the source (e.g., 'JIRA Issue')
            collection (str, optional): Graph ID to use. If None, uses the
                                       graph_id from configuration.
            
        Returns:
            bool: True if successful, False otherwise.
            
        Raises:
            Exception: If an error occurs while persisting data to Zep.
        """
        if not collection:
            collection = self.graph_id
        
        try:
            # First ensure the graph exists
            graph_exists = await self.ensure_graph_exists(collection)
            if not graph_exists:
                logger.error(f"Cannot persist data - graph {collection} does not exist and could not be created")
                return False
            
            # Prepare the JSON data - ensure it's properly formatted as a string
            try:
                if isinstance(data.get('episode_body', {}), str):
                    # If it's already a string, validate it's proper JSON
                    json_data = json.loads(data.get('episode_body', '{}'))
                    json_data = json.dumps(json_data)  # Re-serialize to ensure proper format
                else:
                    # Convert dict or other JSON-serializable objects to string
                    json_data = json.dumps(data.get('episode_body', {}))
            except json.JSONDecodeError as json_error:
                logger.error(f"Invalid JSON data: {str(json_error)}")
                return False
                
            # Prepare source description
            source_description = data.get('source_description', '')
            if not source_description and 'name' in data:
                source_description = data.get('name', '')
            
            # Add data to graph using the correct API method in v3.4.1
            await self.client.graph.add(
                data=json_data,
                type="json",
                graph_id=collection,
                source_description=source_description
            )
            
            logger.info(f"Successfully persisted JSON data to Zep graph: {collection}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                logger.error(f"Error persisting JSON data to Zep: Endpoint not found (404). Check API version compatibility.")
            elif "401" in error_msg or "403" in error_msg:
                logger.error(f"Error persisting JSON data to Zep: Authentication error. Check API key.")
            else:
                logger.error(f"Error persisting JSON data to Zep: {error_msg}")
            return False
    
    async def health_check(self):
        """
        Check if the Zep service is available and healthy.
        
        This method performs comprehensive checks on both the graph and thread APIs 
        to verify that the service is operational. It attempts to list graphs and threads
        to confirm API access. If either test fails, the service is considered unhealthy.
        
        Note: Even if one API (thread or graph) fails, you may still be able to use the
        other API successfully.
        
        Returns:
            bool: True if the service is healthy, False otherwise.
            
        Raises:
            Exception: This method handles all exceptions internally and returns False
                      if an error occurs while checking health.
        """
        health_issues = []
        
        # Check Graph API
        try:
            # Attempt to list graphs as a graph API health check
            await self.client.graph.list_all()
            logger.info("Zep Graph API is healthy")
        except Exception as graph_error:
            error_msg = str(graph_error)
            health_issues.append(f"Graph API error: {error_msg}")
            logger.error(f"Zep Graph API health check failed: {error_msg}")
        
        # Check Thread API
        try:
            # Attempt to list threads as a thread API health check
            await self.client.thread.list_all()
            logger.info("Zep Thread API is healthy")
        except Exception as thread_error:
            error_msg = str(thread_error)
            health_issues.append(f"Thread API error: {error_msg}")
            logger.error(f"Zep Thread API health check failed: {error_msg}")
        
        # If we have any health issues, the service is not healthy
        if health_issues:
            logger.error(f"Zep service health check failed with {len(health_issues)} issues: {', '.join(health_issues)}")
            return False
        
        # If we've made it here, all checks passed
        logger.info("Zep service is healthy")
        return True
    
    async def close_client(self):
        """
        Close the Zep client connection properly.
        
        This method ensures that any open connections are properly closed
        before the application exits. For the AsyncZep client in v3.4.1,
        there is no explicit close method, so we just log the operation.
        
        Returns:
            bool: True if the client was closed successfully, False otherwise.
        """
        try:
            # For v3.4.1, there is no close method on the AsyncZep client
            # We just need to ensure the client is properly dereferenced
            logger.info("Zep client closed successfully")
            return True
        except Exception as e:
            logger.error(f"Error closing Zep client: {str(e)}")
            return False
    
    async def ensure_graph_exists(self, graph_id):
        """
        Ensures that a graph with the given ID exists in Zep.
        
        This method attempts to create a graph with the specified ID.
        If the graph already exists, it handles the error gracefully.
        
        Args:
            graph_id (str): The ID of the graph to ensure exists
            
        Returns:
            bool: True if the graph exists or was created, False otherwise
            
        Raises:
            Exception: This method handles all exceptions internally and returns False
                      if an error occurs while ensuring the graph exists
        """
        try:
            # Try to get the graph first to check if it exists
            try:
                await self.client.graph.get(graph_id=graph_id)
                logger.debug(f"Graph {graph_id} already exists")
                return True
            except Exception as e:
                # If error is "not found", create the graph
                if "not found" in str(e).lower() or "404" in str(e):
                    logger.info(f"Graph {graph_id} not found, creating...")
                    try:
                        await self.client.graph.create(
                            graph_id=graph_id,
                            name=f"Graph for {graph_id}",
                            description=f"Auto-created graph for {graph_id}"
                        )
                        logger.info(f"Successfully created graph: {graph_id}")
                        return True
                    except Exception as create_error:
                        # If error is "already exists", graph was created by another process
                        if "already exists" in str(create_error).lower():
                            logger.debug(f"Graph {graph_id} was created by another process")
                            return True
                        logger.error(f"Failed to create graph {graph_id}: {str(create_error)}")
                        return False
                else:
                    logger.error(f"Error checking if graph {graph_id} exists: {str(e)}")
                    return False
        except Exception as e:
            logger.error(f"Unexpected error ensuring graph {graph_id} exists: {str(e)}")
            return False
    
    async def ensure_thread_exists(self, thread_id):
        """
        Ensures that a thread with the given ID exists in Zep.
        
        This method attempts to create a thread with the specified ID.
        If the thread already exists, it handles the error gracefully.
        
        Args:
            thread_id (str): The ID of the thread to ensure exists
            
        Returns:
            bool: True if the thread exists or was created, False otherwise
            
        Raises:
            Exception: This method handles all exceptions internally and returns False
                      if an error occurs while ensuring the thread exists
        """
        try:
            # Try to get the thread first to check if it exists
            try:
                await self.client.thread.get(thread_id=thread_id, limit=1)
                logger.debug(f"Thread {thread_id} already exists")
                return True
            except Exception as e:
                # If error is "not found", create the thread
                if "not found" in str(e).lower() or "404" in str(e):
                    logger.info(f"Thread {thread_id} not found, creating...")
                    try:
                        await self.client.thread.create(
                            thread_id=thread_id,
                            user_id=self.graph_id  # Use configured graph_id
                        )
                        logger.info(f"Successfully created thread: {thread_id}")
                        return True
                    except Exception as create_error:
                        # If error is "already exists", thread was created by another process
                        if "already exists" in str(create_error).lower():
                            logger.debug(f"Thread {thread_id} was created by another process")
                            return True
                        logger.error(f"Failed to create thread {thread_id}: {str(create_error)}")
                        return False
                else:
                    logger.error(f"Error checking if thread {thread_id} exists: {str(e)}")
                    return False
        except Exception as e:
            logger.error(f"Unexpected error ensuring thread {thread_id} exists: {str(e)}")
            return False
