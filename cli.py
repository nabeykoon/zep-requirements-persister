#!/usr/bin/env python3
"""
Zep Requirements Persister CLI

This script provides a command-line interface for the Zep Requirements Persister utility
using the Click library. It replaces the Makefile with a more user-friendly, cross-platform
interface that works the same way on Windows, Linux, and macOS.

Usage:
    python cli.py --help
    python cli.py run main --source jira --json
    python cli.py graph list-nodes
    python cli.py graph delete-node --uuid <node-uuid>
    python cli.py cleanup delete-isolated

Author: Your Organization
Date: August 2025
License: MIT
"""

import os
import sys
import click
import subprocess
from datetime import datetime

# Define path to Python executable in virtual environment
if os.name == 'nt':  # Windows
    PYTHON = os.path.join('zep-env', 'Scripts', 'python')
else:  # Unix/Linux/Mac
    PYTHON = os.path.join('zep-env', 'bin', 'python')


# Main CLI group
@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Zep Requirements Persister CLI.
    
    This tool helps you manage the Zep Requirements Persister utility
    with a simple command-line interface that works across all platforms.
    """
    pass


# Run commands group
@cli.group('run')
def run_commands():
    """Commands for running the main utility."""
    pass


@run_commands.command('main')
@click.option('--source', type=click.Choice(['jira', 'confluence']), help='Source to process')
@click.option('--json', is_flag=True, help='Use JSON format instead of messages')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def run_main(source, json, verbose):
    """Run the main utility with specified options."""
    click.echo("Running main.py...")
    
    # Build command
    cmd = [PYTHON, '-m', 'main']
    if source:
        cmd.extend(['--source', source])
    if json:
        cmd.append('--json')
    if verbose:
        cmd.append('--verbose')
    
    # Execute command
    click.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        click.echo(f"Command failed with exit code {result.returncode}", err=True)
        sys.exit(result.returncode)


# Graph commands group
@cli.group('graph')
def graph_commands():
    """Commands for managing the knowledge graph."""
    pass


@graph_commands.command('find-isolated-nodes')
@click.option('--graph_id', help='Graph ID to operate on')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def find_isolated_nodes(graph_id, verbose):
    """Find nodes with no connections in the knowledge graph."""
    click.echo("Finding isolated nodes in the knowledge graph...")
    
    cmd = [PYTHON, '-m', 'tools.graph_operations', '--action', 'find_isolated_nodes']
    if graph_id:
        cmd.extend(['--graph_id', graph_id])
    if verbose:
        cmd.append('--verbose')
    
    click.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        click.echo(f"Command failed with exit code {result.returncode}", err=True)
        sys.exit(result.returncode)


@graph_commands.command('find-isolated-edges')
@click.option('--graph_id', help='Graph ID to operate on')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def find_isolated_edges(graph_id, verbose):
    """Find dangling edges (edges with missing source or target nodes)."""
    click.echo("Finding dangling edges in the knowledge graph...")
    
    cmd = [PYTHON, '-m', 'tools.graph_operations', '--action', 'find_isolated_edges']
    if graph_id:
        cmd.extend(['--graph_id', graph_id])
    if verbose:
        cmd.append('--verbose')
    
    click.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        click.echo(f"Command failed with exit code {result.returncode}", err=True)
        sys.exit(result.returncode)


@graph_commands.command('delete-node')
@click.option('--uuid', required=True, help='UUID of the node to delete')
@click.option('--graph_id', help='Graph ID to operate on')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def delete_node(uuid, graph_id, verbose):
    """Delete a specific node by UUID."""
    click.echo(f"Deleting node with UUID: {uuid}")
    
    cmd = [PYTHON, '-m', 'tools.graph_operations', '--action', 'delete_node', '--uuid', uuid]
    if graph_id:
        cmd.extend(['--graph_id', graph_id])
    if verbose:
        cmd.append('--verbose')
    
    click.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        click.echo(f"Command failed with exit code {result.returncode}", err=True)
        sys.exit(result.returncode)


@graph_commands.command('delete-edge')
@click.option('--uuid', required=True, help='UUID of the edge to delete')
@click.option('--graph_id', help='Graph ID to operate on')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def delete_edge(uuid, graph_id, verbose):
    """Delete a specific edge by UUID."""
    click.echo(f"Deleting edge with UUID: {uuid}")
    
    cmd = [PYTHON, '-m', 'tools.graph_operations', '--action', 'delete_edge', '--uuid', uuid]
    if graph_id:
        cmd.extend(['--graph_id', graph_id])
    if verbose:
        cmd.append('--verbose')
    
    click.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        click.echo(f"Command failed with exit code {result.returncode}", err=True)
        sys.exit(result.returncode)


# Cleanup commands group
@cli.group('cleanup')
def cleanup_commands():
    """Commands for cleaning up the knowledge graph."""
    pass


@cleanup_commands.command('delete-isolated-nodes')
@click.option('--graph_id', help='Graph ID to operate on')
@click.option('--no-confirm', is_flag=True, help='Skip confirmation prompt')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cleanup_isolated_nodes(graph_id, no_confirm, verbose):
    """Delete all isolated nodes in the knowledge graph."""
    click.echo("Deleting all isolated nodes in the knowledge graph...")
    
    cmd = [PYTHON, '-m', 'tools.graph_operations', '--action', 'delete_isolated_nodes']
    if graph_id:
        cmd.extend(['--graph_id', graph_id])
    if no_confirm:
        cmd.append('--no-confirm')
    if verbose:
        cmd.append('--verbose')
    
    click.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        click.echo(f"Command failed with exit code {result.returncode}", err=True)
        sys.exit(result.returncode)


@cleanup_commands.command('delete-isolated-edges')
@click.option('--graph_id', help='Graph ID to operate on')
@click.option('--no-confirm', is_flag=True, help='Skip confirmation prompt')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cleanup_isolated_edges(graph_id, no_confirm, verbose):
    """Delete all dangling edges in the knowledge graph."""
    click.echo("Deleting all dangling edges in the knowledge graph...")
    
    cmd = [PYTHON, '-m', 'tools.graph_operations', '--action', 'delete_isolated_edges']
    if graph_id:
        cmd.extend(['--graph_id', graph_id])
    if no_confirm:
        cmd.append('--no-confirm')
    if verbose:
        cmd.append('--verbose')
    
    click.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        click.echo(f"Command failed with exit code {result.returncode}", err=True)
        sys.exit(result.returncode)


# Utility commands
@cli.command('venv')
def venv_info():
    """Show information about the virtual environment."""
    venv_path = 'zep-env'
    
    if not os.path.exists(venv_path):
        click.echo("Virtual environment not found. Create it with:")
        click.echo("  python -m venv zep-env")
        return
    
    # Display activation commands
    click.echo("Virtual environment found at: " + os.path.abspath(venv_path))
    click.echo("\nTo activate the virtual environment:")
    
    if os.name == 'nt':  # Windows
        click.echo("  zep-env\\Scripts\\activate.bat    # Command Prompt")
        click.echo("  zep-env\\Scripts\\Activate.ps1   # PowerShell")
        click.echo("  source zep-env/Scripts/activate  # Git Bash")
    else:  # Unix/Linux/Mac
        click.echo("  source zep-env/bin/activate")
    
    # Check if the virtual environment is active
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        click.echo("\nCurrent status: Virtual environment is ACTIVE")
    else:
        click.echo("\nCurrent status: Virtual environment is NOT ACTIVE")


if __name__ == '__main__':
    cli()
