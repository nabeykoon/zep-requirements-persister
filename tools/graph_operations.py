#!/usr/bin/env python3
"""
Zep Graph Operations Utility

This utility provides simplified operations for Zep knowledge graphs with a focus on:
1. Finding isolated nodes
2. Finding dangling edges
3. Deleting a node by UUID
4. Deleting an edge by UUID
5. Deleting all isolated nodes with confirmation
6. Deleting all dangling edges with confirmation

Usage:
    python -m tools.graph_operations --action find_isolated_nodes [--graph_id <graph_id>]
    python -m tools.graph_operations --action find_isolated_edges [--graph_id <graph_id>]
    python -m tools.graph_operations --action delete_node --uuid <node_uuid> [--graph_id <graph_id>]
    python -m tools.graph_operations --action delete_edge --uuid <edge_uuid> [--graph_id <graph_id>]
    python -m tools.graph_operations --action delete_isolated_nodes [--graph_id <graph_id>]
    python -m tools.graph_operations --action delete_isolated_edges [--graph_id <graph_id>]

Author: Your Organization
License: MIT
"""

#------------------------------------------------------------------------------
# Configuration
#------------------------------------------------------------------------------
# The Zep Graph ID to operate on. This can be:
# 1. Set here as DEFAULT_GRAPH_ID
# 2. Overridden via command line with --graph_id
# 3. Set as an environment variable ZEP_GRAPH_ID
#
# Examples:
# - "pet-store-knowledge" for pet store domain knowledge
# - "jira-requirements" for JIRA requirements
# - "confluence-docs" for Confluence documentation
DEFAULT_GRAPH_ID = "pet-store-knowledge"

# API Authentication:
# The API key should be set in src/.env file as ZEP_API_KEY
# Example .env content:
# ZEP_API_KEY=your_api_key_here
#------------------------------------------------------------------------------

import os
import sys
import logging
import asyncio
import argparse
from datetime import datetime
import json
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get the path to the src/.env file
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
env_path = os.path.join(src_dir, ".env")

from zep_cloud import Zep, AsyncZep

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"zep_graph_operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ZepGraphOperations:
    """
    Utility class for Zep graph operations.
    
    Provides methods to:
    - Find isolated nodes (nodes with no connections)
    - Find dangling edges (edges with missing source or target nodes)
    - Delete a node by UUID
    - Delete an edge by UUID
    - Delete all isolated nodes with confirmation
    - Delete all dangling edges with confirmation
    """
    
    def __init__(self, api_key=None, graph_id=None):
        """
        Initialize the Zep Graph Operations.
        
        Args:
            api_key (str, optional): Zep API key. If None, will be loaded from ZEP_API_KEY env var.
            graph_id (str, optional): Graph ID to operate on. Defaults to DEFAULT_GRAPH_ID.
        """
        # Load environment variables from src/.env file
        load_dotenv(dotenv_path=env_path)
        
        self.api_key = api_key or os.environ.get('ZEP_API_KEY')
        self.graph_id = graph_id or DEFAULT_GRAPH_ID
        
        if not self.api_key:
            raise ValueError(f"Zep API key is required. Set it as ZEP_API_KEY environment variable in {env_path} or pass directly.")
        
        self.client = None
    
    async def connect(self):
        """Connect to Zep API."""
        try:
            self.client = AsyncZep(api_key=self.api_key)
            logger.info(f"Connected to Zep with graph ID: {self.graph_id}")
        except Exception as e:
            logger.error(f"Failed to connect to Zep: {str(e)}")
            raise
    
    async def get_nodes(self):
        """
        Get all nodes in the graph.
        
        Returns:
            list: List of node objects.
        """
        try:
            # Get nodes using the proper v3.4.1 API endpoint
            nodes = await self.client.graph.node.get_by_graph_id(
                graph_id=self.graph_id,
                limit=1000  # Adjust limit as needed
            )
            logger.info(f"Found {len(nodes)} nodes in graph {self.graph_id}")
            
            # Debug: Log some sample node data to verify structure
            if nodes and len(nodes) > 0:
                sample_node = nodes[0]
                logger.debug(f"Sample node data: {json.dumps(sample_node, default=str)}")
                logger.debug(f"Node UUID: {self._get_attr(sample_node, 'uuid')}")
                logger.debug(f"Node has keys: {sample_node.keys() if isinstance(sample_node, dict) else 'Not a dict'}")
            
            return nodes
        except Exception as e:
            logger.error(f"Failed to get nodes: {str(e)}")
            return []
    
    async def get_edges(self):
        """
        Get all edges in the graph.
        
        Returns:
            list: List of edge objects.
        """
        try:
            # Get edges using the proper v3.4.1 API endpoint
            edges = await self.client.graph.edge.get_by_graph_id(
                graph_id=self.graph_id,
                limit=1000  # Adjust limit as needed
            )
            logger.info(f"Found {len(edges)} edges in graph {self.graph_id}")
            
            # Debug: Log some sample edge data to verify structure
            if edges and len(edges) > 0:
                sample_edge = edges[0]
                logger.debug(f"Sample edge data: {json.dumps(sample_edge, default=str)}")
                logger.debug(f"Edge ID: {self._get_attr(sample_edge, 'id')}")
                logger.debug(f"Edge UUID: {self._get_attr(sample_edge, 'uuid')}")
                logger.debug(f"Edge source_node_uuid: {self._get_attr(sample_edge, 'source_node_uuid')}")
                logger.debug(f"Edge target_node_uuid: {self._get_attr(sample_edge, 'target_node_uuid')}")
                logger.debug(f"Edge has keys: {sample_edge.keys() if isinstance(sample_edge, dict) else 'Not a dict'}")
            
            return edges
        except Exception as e:
            logger.error(f"Failed to get edges: {str(e)}")
            return []
    
    async def find_isolated_nodes(self):
        """
        Find nodes that have no connections (isolated nodes).
        A truly isolated node is one that exists in the graph but has no connections to any other nodes.
        
        Returns:
            list: List of isolated node objects.
        """
        try:
            # Get all nodes and edges
            nodes = await self.get_nodes()
            edges = await self.get_edges()
            
            # Create a set of node UUIDs that appear in edges
            nodes_in_edges = set()
            for edge in edges:
                # Extract source and target node UUIDs safely
                source_uuid = self._get_attr(edge, 'source_node_uuid')
                target_uuid = self._get_attr(edge, 'target_node_uuid')
                
                if source_uuid:
                    nodes_in_edges.add(source_uuid)
                if target_uuid:
                    nodes_in_edges.add(target_uuid)
            
            # Find isolated nodes (nodes that exist but don't participate in any edges)
            isolated_nodes = []
            for node in nodes:
                # Extract node UUID safely
                node_uuid = self._get_attr(node, 'uuid')
                
                if node_uuid and node_uuid not in nodes_in_edges:
                    isolated_nodes.append(node)
            
            logger.info(f"Found {len(isolated_nodes)} isolated nodes in graph {self.graph_id}")
            
            # Log isolated node details
            for i, node in enumerate(isolated_nodes):
                node_uuid = self._get_attr(node, 'uuid', 'Unknown')
                node_name = self._get_attr(node, 'name', 'Unknown')
                
                logger.info(f"Isolated Node {i+1}/{len(isolated_nodes)}: UUID={node_uuid}, Name={node_name}")
            
            return isolated_nodes
        except Exception as e:
            logger.error(f"Failed to find isolated nodes: {str(e)}")
            return []
    
    async def find_isolated_edges(self):
        """
        Find dangling edges (edges with missing source or target nodes).
        A dangling edge is one where either the source node or target node (or both) doesn't exist.
        
        Returns:
            list: List of dangling edge objects.
        """
        try:
            # Get all nodes first
            nodes = await self.get_nodes()
            
            # Create a set of all node UUIDs
            node_uuids = set()
            for node in nodes:
                node_uuid = self._get_attr(node, 'uuid')
                if node_uuid:
                    node_uuids.add(node_uuid)
            
            # Get all edges
            edges = await self.get_edges()
            
            # Find dangling edges (edges with missing source or target nodes)
            dangling_edges = []
            for edge in edges:
                source_uuid = self._get_attr(edge, 'source_node_uuid')
                target_uuid = self._get_attr(edge, 'target_node_uuid')
                
                # Check if either source or target node doesn't exist
                source_missing = source_uuid and source_uuid not in node_uuids
                target_missing = target_uuid and target_uuid not in node_uuids
                
                if source_missing or target_missing:
                    dangling_edges.append(edge)
            
            logger.info(f"Found {len(dangling_edges)} dangling edges in graph {self.graph_id}")
            
            # Log dangling edge details
            for i, edge in enumerate(dangling_edges):
                # Try to get edge UUID
                edge_uuid = self._get_attr(edge, 'uuid', 'Unknown')
                edge_name = self._get_attr(edge, 'name', 'Unknown')
                source_uuid = self._get_attr(edge, 'source_node_uuid', 'Unknown')
                target_uuid = self._get_attr(edge, 'target_node_uuid', 'Unknown')
                
                source_exists = source_uuid in node_uuids
                target_exists = target_uuid in node_uuids
                
                logger.info(f"Dangling Edge {i+1}/{len(dangling_edges)}: ID={edge_uuid}, Name={edge_name}")
                logger.info(f"  Source node {source_uuid} exists: {source_exists}")
                logger.info(f"  Target node {target_uuid} exists: {target_exists}")
            
            return dangling_edges
        except Exception as e:
            logger.error(f"Failed to find isolated edges: {str(e)}")
            return []
    
    async def delete_node(self, uuid):
        """
        Delete a node by UUID.
        
        Args:
            uuid (str): UUID of the node to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Check if the node exists first
            try:
                # Try to get the node to verify it exists
                node = await self.client.graph.node.get(uuid_=uuid)
                node_name = self._get_attr(node, 'name', 'Unknown')
                logger.info(f"Found node: UUID={uuid}, Name={node_name}")
            except Exception as e:
                logger.error(f"Node not found: {uuid} - {str(e)}")
                return False
            
            # Delete the node using the v3.4.1 API
            try:
                # Use the raw HTTP request method
                response = await self.client.request(
                    method="DELETE",
                    url=f"api/v2/graph/node/{uuid}",
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200 or response.status_code == 204:
                    logger.info(f"Successfully deleted node: {uuid}")
                    return True
                else:
                    logger.error(f"Failed to delete node {uuid}: {response.status_code}")
                    return False
            except Exception as delete_error:
                logger.error(f"Failed to delete node {uuid}: {str(delete_error)}")
                return False
        except Exception as e:
            logger.error(f"Error in delete_node operation: {str(e)}")
            return False
    
    async def delete_edge(self, uuid):
        """
        Delete an edge by UUID.
        
        Args:
            uuid (str): UUID of the edge to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Check if the edge exists first
            try:
                # Try to get the edge to verify it exists
                edge = await self.client.graph.edge.get(uuid_=uuid)
                edge_name = self._get_attr(edge, 'name', 'Unknown')
                logger.info(f"Found edge: UUID={uuid}, Name={edge_name}")
            except Exception as e:
                logger.error(f"Edge not found: {uuid} - {str(e)}")
                return False
            
            # Delete the edge using the v3.4.1 API
            try:
                # Delete the edge
                await self.client.graph.edge.delete(uuid_=uuid)
                logger.info(f"Successfully deleted edge: {uuid}")
                return True
            except Exception as delete_error:
                logger.error(f"Failed to delete edge {uuid}: {str(delete_error)}")
                return False
        except Exception as e:
            logger.error(f"Error in delete_edge operation: {str(e)}")
            return False
    
    async def delete_isolated_nodes(self, confirm=True):
        """
        Delete all isolated nodes in the graph.
        
        Args:
            confirm (bool): Whether to require confirmation before deletion.
            
        Returns:
            tuple: (deleted_count, failed_count)
        """
        # Find isolated nodes
        isolated_nodes = await self.find_isolated_nodes()
        
        if not isolated_nodes:
            logger.info("No isolated nodes found.")
            return 0, 0
        
        logger.info(f"Found {len(isolated_nodes)} isolated nodes.")
        
        # Get confirmation if required
        if confirm:
            print(f"Found {len(isolated_nodes)} isolated nodes to delete.")
            print("Example nodes:")
            for i, node in enumerate(isolated_nodes[:5]):
                node_uuid = self._get_attr(node, 'uuid', 'Unknown')
                node_name = self._get_attr(node, 'name', 'Unknown')
                print(f"  {i+1}. UUID={node_uuid}, Name={node_name}")
            
            if len(isolated_nodes) > 5:
                print(f"  ... and {len(isolated_nodes) - 5} more")
            
            confirmation = input("Do you want to delete these nodes? (yes/no): ")
            if confirmation.lower() not in ['yes', 'y']:
                logger.info("Node deletion cancelled by user.")
                return 0, 0
        
        # Delete the isolated nodes
        deleted_count = 0
        failed_count = 0
        
        for i, node in enumerate(isolated_nodes):
            node_uuid = self._get_attr(node, 'uuid')
            
            if not node_uuid:
                logger.warning(f"Node {i+1}/{len(isolated_nodes)} has no UUID, skipping.")
                failed_count += 1
                continue
            
            logger.info(f"Deleting isolated node {i+1}/{len(isolated_nodes)}: UUID={node_uuid}")
            
            success = await self.delete_node(node_uuid)
            
            if success:
                deleted_count += 1
                print(f"Deleted node {i+1}/{len(isolated_nodes)}: UUID={node_uuid}")
            else:
                failed_count += 1
        
        logger.info(f"Deleted {deleted_count} isolated nodes. Failed to delete {failed_count} nodes.")
        return deleted_count, failed_count
    
    async def delete_isolated_edges(self, confirm=True):
        """
        Delete all dangling edges in the graph.
        
        Args:
            confirm (bool): Whether to require confirmation before deletion.
            
        Returns:
            tuple: (deleted_count, failed_count)
        """
        # Find dangling edges
        isolated_edges = await self.find_isolated_edges()
        
        if not isolated_edges:
            logger.info("No dangling edges found.")
            return 0, 0
        
        logger.info(f"Found {len(isolated_edges)} dangling edges.")
        
        # Get confirmation if required
        if confirm:
            print(f"Found {len(isolated_edges)} dangling edges to delete.")
            print("Example edges:")
            for i, edge in enumerate(isolated_edges[:5]):
                edge_uuid = self._get_attr(edge, 'uuid', 'Unknown')
                edge_name = self._get_attr(edge, 'name', 'Unknown')
                print(f"  {i+1}. UUID={edge_uuid}, Name={edge_name}")
            
            if len(isolated_edges) > 5:
                print(f"  ... and {len(isolated_edges) - 5} more")
            
            confirmation = input("Do you want to delete these edges? (yes/no): ")
            if confirmation.lower() not in ['yes', 'y']:
                logger.info("Edge deletion cancelled by user.")
                return 0, 0
        
        # Delete the isolated edges
        deleted_count = 0
        failed_count = 0
        
        for i, edge in enumerate(isolated_edges):
            edge_uuid = self._get_attr(edge, 'uuid')
            
            if not edge_uuid:
                logger.warning(f"Edge {i+1}/{len(isolated_edges)} has no UUID, skipping.")
                failed_count += 1
                continue
            
            logger.info(f"Deleting dangling edge {i+1}/{len(isolated_edges)}: UUID={edge_uuid}")
            
            success = await self.delete_edge(edge_uuid)
            
            if success:
                deleted_count += 1
                print(f"Deleted edge {i+1}/{len(isolated_edges)}: UUID={edge_uuid}")
            else:
                failed_count += 1
        
        logger.info(f"Deleted {deleted_count} dangling edges. Failed to delete {failed_count} edges.")
        return deleted_count, failed_count
    
    def _get_attr(self, obj, attr, default=None):
        """
        Safely get an attribute from an object, whether it's a dictionary or an object with attributes.
        Also handles nested attributes with dot notation like 'metadata.name'.
        
        Args:
            obj: The object to get the attribute from.
            attr: The name of the attribute to get.
            default: The default value to return if the attribute is not found.
            
        Returns:
            The attribute value or the default.
        """
        if obj is None:
            return default
        
        # Handle dot notation for nested attributes
        if '.' in attr:
            parts = attr.split('.')
            current = obj
            for part in parts:
                current = self._get_attr(current, part, None)
                if current is None:
                    return default
            return current
        
        # Try dictionary access first
        if isinstance(obj, dict):
            # Direct access
            if attr in obj:
                return obj[attr]
            
            # Try with underscore for uuid -> uuid_
            if attr == 'uuid' and 'uuid_' in obj:
                return obj['uuid_']
            
            # Handle special case for edge UUID
            if attr == 'uuid' and 'id' in obj:
                return obj['id']
                
            return default
        
        # Try attribute access
        try:
            # Direct attribute access
            if hasattr(obj, attr):
                return getattr(obj, attr)
            
            # Try with underscore for uuid -> uuid_
            if attr == 'uuid' and hasattr(obj, 'uuid_'):
                return getattr(obj, 'uuid_')
            
            # Handle special case for edge UUID
            if attr == 'uuid' and hasattr(obj, 'id'):
                return getattr(obj, 'id')
                
            return default
        except:
            return default

async def run(action, uuid=None, graph_id=None, confirm=True, verbose=False):
    """
    Run the graph operations utility.
    
    Args:
        action (str): Action to perform
        uuid (str, optional): UUID of the node or edge to operate on.
        graph_id (str, optional): Graph ID to operate on. If None, uses DEFAULT_GRAPH_ID.
        confirm (bool, optional): Whether to require confirmation before bulk operations.
        verbose (bool, optional): Enable verbose logging.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize graph operations with direct parameters
    ops = ZepGraphOperations(graph_id=graph_id)
    
    # Connect to Zep
    await ops.connect()
    
    # Perform the requested action
    if action == 'find_isolated_nodes':
        isolated_nodes = await ops.find_isolated_nodes()
        print(f"\nFound {len(isolated_nodes)} isolated nodes (nodes with no connections):")
        if isolated_nodes:
            for i, node in enumerate(isolated_nodes):
                node_uuid = ops._get_attr(node, 'uuid', 'Unknown')
                node_name = ops._get_attr(node, 'name', 'Unknown')
                node_type = ops._get_attr(node, 'type', 'Unknown')
                print(f"{i+1}. UUID: {node_uuid}, Type: {node_type}, Name: {node_name}")
        else:
            print("No isolated nodes found in the graph.")
    
    elif action == 'find_isolated_edges':
        # Get all nodes first to avoid repeated API calls
        nodes = await ops.get_nodes()
        node_uuids = {ops._get_attr(node, 'uuid') for node in nodes if ops._get_attr(node, 'uuid')}
        
        dangling_edges = await ops.find_isolated_edges()
        print(f"\nFound {len(dangling_edges)} dangling edges (edges with missing source/target nodes):")
        if dangling_edges:
            for i, edge in enumerate(dangling_edges):
                edge_uuid = ops._get_attr(edge, 'uuid', 'Unknown')
                edge_name = ops._get_attr(edge, 'name', 'Unknown')
                source_uuid = ops._get_attr(edge, 'source_node_uuid', 'Unknown')
                target_uuid = ops._get_attr(edge, 'target_node_uuid', 'Unknown')
                
                # Check if source and target exist
                source_exists = source_uuid in node_uuids
                target_exists = target_uuid in node_uuids
                
                print(f"{i+1}. ID: {edge_uuid}, Name: {edge_name}")
                print(f"   Source: {source_uuid} (Exists: {source_exists})")
                print(f"   Target: {target_uuid} (Exists: {target_exists})")
        else:
            print("No dangling edges found in the graph.")
    
    elif action == 'delete_node':
        if not uuid:
            logger.error("UUID is required for delete_node action")
            return
        success = await ops.delete_node(uuid)
        if success:
            print(f"Successfully deleted node: {uuid}")
        else:
            print(f"Failed to delete node: {uuid}")
    
    elif action == 'delete_edge':
        if not uuid:
            logger.error("UUID is required for delete_edge action")
            return
        success = await ops.delete_edge(uuid)
        if success:
            print(f"Successfully deleted edge: {uuid}")
        else:
            print(f"Failed to delete edge: {uuid}")
    
    elif action == 'delete_isolated_nodes':
        deleted, failed = await ops.delete_isolated_nodes(confirm=confirm)
        print(f"Deleted {deleted} isolated nodes. Failed to delete {failed} nodes.")
    
    elif action == 'delete_isolated_edges':
        deleted, failed = await ops.delete_isolated_edges(confirm=confirm)
        print(f"Deleted {deleted} dangling edges. Failed to delete {failed} edges.")
    
    else:
        logger.error(f"Unknown action: {action}")

def main():
    """Entry point for the script."""
    parser = argparse.ArgumentParser(description="Zep Graph Operations Utility")
    parser.add_argument('--action', choices=[
        'find_isolated_nodes', 
        'find_isolated_edges', 
        'delete_node', 
        'delete_edge', 
        'delete_isolated_nodes', 
        'delete_isolated_edges'
    ], required=True, help='Action to perform')
    parser.add_argument('--uuid', help='UUID of the node or edge to operate on')
    parser.add_argument('--graph_id', help=f'Graph ID to operate on (default: {DEFAULT_GRAPH_ID})')
    parser.add_argument('--no-confirm', dest='confirm', action='store_false', 
                       help='Skip confirmation for bulk operations')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.action in ['delete_node', 'delete_edge'] and not args.uuid:
        parser.error(f"--uuid is required for {args.action} action")
    
    # Run the async main function
    try:
        asyncio.run(run(args.action, args.uuid, args.graph_id, args.confirm, args.verbose))
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
