# Zep Requirements Persister

A Python utility to fetch requirements from JIRA and Confluence and persist them to Zep for AI agent use.

## Overview

This utility helps you:
1. Fetch specific JIRA issues and Confluence pages
2. Transform them into formats compatible w### Graph Operations Utility

The `tools/graph_operations.py` script provides a simplified, focused approach to managing Zep graphs:

1. **Find isolated nodes**: Finds nodes with no connections to other nodes
2. **Find dangling edges**: Finds edges with missing source or target nodes
3. **Delete node by UUID**: Deletes a specific node by its UUID
4. **Delete edge by UUID**: Deletes a specific edge by its UUID
5. **Delete all isolated nodes**: Batch deletion with confirmation prompt
6. **Delete all dangling edges**: Batch deletion with confirmation prompt

This utility is fully compatible with Zep Cloud API v3.4.1 and uses direct parameter configuration rather than relying on project-level configs.

#### Important Terminology Change

In v3.4.1, we've updated the terminology to be more accurate:

- **Isolated Nodes**: Nodes that have no connections to any other nodes
- **Dangling Edges**: Edges that are "dangling" because they refer to source or target nodes that don't exist

This change makes the terminology more accurate and consistent with graph theory terminology.d API v3.4.1
3. Persist the data to Zep's memory system (graph API for JSON or thread API for messages)
4. Make them available for your AI agents to use for tasks like coding and testing

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/zep-requirements-persister.git
   cd zep-requirements-persister
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and edit it with your credentials:
   ```bash
   cp .env.example .env
   ```

## Version Information

This project uses Zep Cloud SDK v3.4.1 or later. If you're upgrading from an older version, note that the API has changed significantly:

- The SDK now uses a client-based approach (`AsyncZep` client)
- Message format has been simplified
- Authentication is handled automatically by the client
- Thread and graph APIs have new methods and parameters

### API Compatibility Note

In Zep Cloud API v3.4.1, we've implemented two persistence methods:

1. **JSON Persistence (Recommended)**: Stores structured data in Zep's graph API. This is the recommended 
   approach for most use cases as it provides the best compatibility and performance. Use the `--json` flag 
   to enable this mode. Product requirements like JIRA issues are well-suited for this approach.

2. **Message Persistence**: Stores conversational-style messages in Zep's thread API. This implementation 
   uses the thread.add_messages_batch() method for compatibility with v3.4.1.

For production use cases, we recommend using JSON persistence (`--json` flag) as it provides the most
reliable operation with the current API version.

## Configuration

### Environment Variables (.env)

Set up your API keys and credentials in the `.env` file:

```
# JIRA Settings
JIRA_BASE_URL=https://your-jira-instance.com
JIRA_USERNAME=your-jira-username
JIRA_API_TOKEN=your-jira-api-token

# Confluence Settings
CONFLUENCE_BASE_URL=https://your-confluence-instance.com
CONFLUENCE_USERNAME=your-confluence-username
CONFLUENCE_API_TOKEN=your-confluence-api-token

# Zep Settings
ZEP_API_KEY=your-zep-api-key
```

### Configuration File (config.yaml)

Define your configuration settings in the `config/config.yaml` file:

```yaml
# Zep configuration
zep:
  # API key should be in .env file
  project: "pet-store"                  # Project/application name
  session_id: "pet-store-requirements"  # Thread ID for message-based requirements
  user_id: "pet-store-knowledge"        # User ID for JSON-based knowledge persistence
  graph_id: "pet-store-knowledge"       # Graph ID for data organization (defaults to user_id)

# JIRA configuration
jira:
  # Credentials should be in .env file
  issues:
    - PS-1
    - PS-2
    - PS-3
    - PS-4

# Confluence configuration
confluence:
  # Credentials should be in .env file
  pages:
    - id: "123456"
      title: "Product Requirements Document"  # Optional, for reference
    - id: "123457"
      title: "API Documentation"
```

### Zep Configuration Details

The Zep configuration section contains several key settings:

- **project**: Identifies the project or application name. Used as a namespace for organizing your data in Zep. Default value: `pet-store`.

- **session_id**: The thread ID used for message-based persistence. This is used when storing requirements as conversational messages in Zep's thread system. Default value: `pet-store-requirements`.

- **user_id**: The user ID used for JSON-based knowledge persistence. In Zep v3.4.1, this maps to the graph_id used for structured data storage. Default value: `pet-store-knowledge`.

- **graph_id**: The graph ID for organizing knowledge data in Zep's graph system. If not specified, it defaults to the same value as `user_id`. This field was added for clarity in configuration but refers to the same underlying value. Default value: Same as `user_id`.

All Zep configuration values have sensible defaults if not specified in the config file. The defaults are:
```
project: "pet-store"
session_id: "pet-store-requirements"
user_id: "pet-store-knowledge"
graph_id: Same as user_id
```

#### Environment Variables and Configuration Precedence

The configuration system follows these precedence rules:

1. Command-line arguments (highest priority)
2. Environment variables from `.env` file
3. Config file values (`config.yaml`)
4. Default values (lowest priority)

While the `.env` file is primarily for credentials and API keys, you can also use environment variables to override configuration values for special use cases without modifying the config file:

```
# Override Zep configuration temporarily
ZEP_PROJECT=special-project
ZEP_SESSION_ID=temporary-session
ZEP_USER_ID=custom-graph
```

## Usage

### Using the CLI Tool (Recommended)

We provide a convenient CLI tool based on Click that makes it easy to run commands without having to remember all the parameters:

```bash
# Show help and available commands
python cli.py --help

# Run the main utility with JIRA source and JSON format
python cli.py run main --source jira --json

# Run with verbose logging
python cli.py run main --verbose

# Run with a specific configuration file
python main.py --config custom_config.yaml

# List all nodes in the knowledge graph
python cli.py graph list-nodes

# List nodes for a specific graph
python cli.py graph list-nodes --graph_id custom-graph-id

# Delete a specific node by UUID
python cli.py graph delete-node --uuid your-node-uuid-here

# Delete all isolated nodes
python cli.py cleanup delete-isolated

# Export the graph to a JSON file
python cli.py cleanup export --output graph_backup.json
```

The CLI is organized into logical command groups:
- `run`: Commands for running the main utility
- `graph`: Commands for managing the knowledge graph
- `cleanup`: Commands for cleaning up the knowledge graph

### Basic Usage (Legacy Method)

```bash
python main.py
```

This will fetch all configured JIRA issues and Confluence pages and persist them to Zep.

### Options

- `--config` or `-c`: Specify a custom config file path (default: `config/config.yaml`)
- `--json` or `-j`: Use JSON format instead of messages for Zep persistence (recommended for v3.4.1)
- `--source` or `-s`: Process only a specific source (`jira` or `confluence`)
- `--verbose` or `-v`: Enable verbose logging

### Examples

Process only JIRA issues with JSON format (recommended):
```bash
python -m main --source jira --json
```

Process only Confluence pages with JSON format:
```bash
python -m main --source confluence --json
```

Use a different config file:
```bash
python -m main --config path/to/custom_config.yaml --json
```

### Using Makefile Commands

The project includes a Makefile with common commands for easier operation:

```bash
# Run the main script with JIRA JSON persistence
make run-main

# Run with verbose logging
make run-main-verbose

# List all nodes in the knowledge graph
make graph-list-nodes

# List all edges in the knowledge graph
make graph-list-edges

# List isolated nodes (nodes with no connections)
make graph-list-isolated

# Delete a specific node by UUID
make delete-node UUID=your-node-uuid-here

# Delete a specific edge by UUID
make delete-edge UUID=your-edge-uuid-here
```

## Zep Cloud API Compatibility

The utility has been updated to ensure compatibility with Zep Cloud API v3.4.1. Key changes include:

1. **API Path Structure**: All API calls now use the correct namespace hierarchy:
   - `client.graph.node.delete` instead of `client.graph.delete_node`
   - `client.graph.edge.delete` instead of `client.graph.delete_edge`

2. **Parameter Naming**: All API calls use the correct parameter names:
   - `uuid_` instead of `uuid` for node and edge deletion
   - `graph_id` for all graph-related operations

3. **Fallback Mechanisms**: Added fallback mechanisms for operations that might not be fully supported:
   - Node deletion with fallback to removing all connected edges
   - Proper handling of different API response formats

4. **Thread API Changes**: Updated thread operations to use the batch method for better compatibility
   - `add_messages_batch()` is now used for persisting messages

5. **Error Handling**: Enhanced error handling to properly identify API compatibility issues:
   - Specific handling for 404 errors that might indicate API endpoint changes
   - Better logging of authentication and authorization issues

## Graph Management Tools

The utility includes tools for managing and maintaining your Zep knowledge graph located in the `tools` directory.

### Graph Operations Utility

The `tools/graph_operations.py` script provides a simplified, focused approach to managing Zep graphs:

1. **Find isolated nodes**: Finds nodes with no connections to other nodes
2. **Find dangling edges**: Finds edges with missing source or target nodes (previously called "isolated edges")
3. **Delete node by UUID**: Deletes a specific node by its UUID
4. **Delete edge by UUID**: Deletes a specific edge by its UUID
5. **Delete all isolated nodes**: Batch deletion with confirmation prompt
6. **Delete all dangling edges**: Batch deletion with confirmation prompt

This utility is fully compatible with Zep Cloud API v3.4.1 and uses direct parameter configuration rather than relying on project-level configs.

#### Important Terminology Change

In v3.4.1, we've updated the terminology to be more accurate:

- **Isolated Nodes**: Nodes that have no connections to any other nodes
- **Dangling Edges**: Edges that are "dangling" because they refer to source or target nodes that don't exist

This change makes the terminology more accurate and consistent with graph theory terminology.

#### Usage

```bash
# Find isolated nodes
python -m tools.graph_operations --action find_isolated_nodes --graph_id my-graph

# Find dangling edges
python -m tools.graph_operations --action find_isolated_edges --graph_id my-graph

# Delete a specific node
python -m tools.graph_operations --action delete_node --uuid your-node-uuid --graph_id my-graph

# Delete a specific edge
python -m tools.graph_operations --action delete_edge --uuid your-edge-uuid --graph_id my-graph

# Delete all isolated nodes (with confirmation)
python -m tools.graph_operations --action delete_isolated_nodes --graph_id my-graph

# Delete all dangling edges (with confirmation)
python -m tools.graph_operations --action delete_isolated_edges --graph_id my-graph

# Skip confirmation for bulk operations
python -m tools.graph_operations --action delete_isolated_nodes --no-confirm --graph_id my-graph

# Enable verbose logging
python -m tools.graph_operations --action find_isolated_nodes --verbose
```

#### Example Usage

We've included an example script in `examples/graph_cleanup.py` that demonstrates how to use the GraphOperations class to:

1. Find isolated nodes and dangling edges in your knowledge graph
2. Display information about them
3. Optionally delete them

This is a good starting point for understanding how to use the GraphOperations class in your own code:

```bash
python -m examples.graph_cleanup
```

The utility reads the Zep API key from the `src/.env` file and uses reasonable defaults for graph IDs.

#### Key Features

- **Better object handling**: Safely handles both dictionary objects and objects with attributes
- **Confirmation for bulk operations**: Requires user confirmation before deleting multiple items
- **Proper src/.env usage**: Uses the src/.env file for API key configuration
- **Simplified interface**: Focused on the most important graph operations
- **Improved error handling**: Better error messages and logging
- **Example display**: Shows examples of items before confirmation

#### Makefile Shortcuts for Graph Operations

```bash
# Find isolated nodes
make find-isolated-nodes

# Find dangling edges
make find-dangling-edges

# Delete a specific node by UUID
make delete-node UUID=your-node-uuid-here

# Delete all isolated nodes with confirmation
make delete-isolated-nodes

# Delete all dangling edges with confirmation
make delete-dangling-edges

# Export the graph to a JSON file
make export-graph OUTPUT=graph_backup.json
```

### When to Use Graph Management Tools

- **After bulk imports**: Clean up any isolated nodes or dangling edges that might have been created
- **During troubleshooting**: Identify graph structure issues
- **For graph maintenance**: Remove outdated or incorrect information
- **When updating node structures**: Clean up old structure nodes after migrating to new formats
- **Before major changes**: Export the graph for backup
- **Pattern-based cleanup**: Remove all nodes from a specific source or type

## Architecture

The utility follows a modular architecture:

- **Connectors**: Fetch data from source systems (JIRA, Confluence)
- **Transformers**: Convert source data to Zep-compatible formats (message or JSON)
- **Persistence**: Store data in Zep's memory system (thread API or graph API)

### Data Flow

1. The main script loads configuration and parses command-line arguments
2. Connectors retrieve data from configured sources (JIRA issues, Confluence pages)
3. Transformers convert each source item to the appropriate Zep format
4. The Zep persistence layer sends the data to Zep Cloud API
5. Results and logs are generated for monitoring and troubleshooting

### Error Handling

The application implements comprehensive error handling:
- Connection failures to JIRA, Confluence, or Zep are caught and logged
- Individual item processing errors don't stop the entire pipeline
- Health checks ensure Zep services are available before proceeding
- Proper cleanup with client connection closure to prevent resource leaks

## Logging

Logs are stored in the `logs` directory with timestamps for easy tracking and troubleshooting. The log format includes timestamp, module name, log level, and message. You can enable verbose logging with the `--verbose` or `-v` flag.

## Best Practices

1. **Use JSON Persistence**: For structured data like JIRA issues and Confluence pages, JSON persistence (using the `--json` flag) provides better reliability and performance with Zep Cloud API v3.4.1.

2. **Environment Variables**: Keep sensitive information like API keys in the `.env` file, which is not committed to version control.

3. **Regular Updates**: Run the utility on a schedule to keep your AI agents' knowledge base up-to-date with the latest requirements.

4. **Selective Processing**: Use the `--source` flag to process only the sources you need, especially when testing or when only one source has been updated.

## Troubleshooting

### Common Issues

1. **Authentication Failures**: If you see 401 or 403 errors, check your API credentials in the `.env` file.

2. **Connection Errors**: Ensure you have network access to the JIRA, Confluence, and Zep servers.

3. **Missing Dependencies**: Run `pip install -r requirements.txt` to ensure all dependencies are installed.

4. **Compatibility Issues**: This utility is designed for Zep Cloud API v3.4.1. If you're using a different version, you may need to modify the code.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
