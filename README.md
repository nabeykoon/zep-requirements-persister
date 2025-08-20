# Zep Requirements Persister

A Python utility to fetch requirements from JIRA and Confluence and persist them to Zep for AI agent use.

## Overview

This utility helps you:
1. Fetch specific JIRA issues and Confluence pages
2. Transform them into formats compatible with Zep Cloud API v3.4.1
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

Define which JIRA issues and Confluence pages to fetch in the `config/config.yaml` file:

```yaml
# Zep configuration
zep:
  # API key should be in .env file
  session_id: "pet-store-requirements"  # Main session for thread persistence
  user_id: "pet-store-knowledge"        # Graph ID for JSON persistence

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
  project: "requirements"  # Default project name for organizing data
```

## Usage

### Basic Usage

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
