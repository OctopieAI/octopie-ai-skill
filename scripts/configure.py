#!/usr/bin/env python3
"""
Octopie.AI Token Configuration Tool

Save your Private Token to a local config file for long-term persistence.

Usage:
    # Save token directly (recommended)
    python configure.py --token "your-private-token"
    
    # Persist environment variable to config file
    export OCTOPIE_PRIVATE_TOKEN="your-token"
    python configure.py --from-env
    
    # Check existing configuration
    python configure.py --check

Note:
    If you already have OCTOPIE_PRIVATE_TOKEN environment variable set,
    the API client can use it directly without running configure.
    Use configure only when you want to persist the token to a file.
"""

import os
import json
import sys
import argparse
from pathlib import Path


# Configuration file location
CONFIG_DIR = Path(__file__).parent.parent / ".config"
CONFIG_FILE = CONFIG_DIR / "credentials.json"


def save_token(token: str) -> None:
    """
    Save Private Token to configuration file.
    
    Args:
        token: Your Private Token from www.octopie.ai
    """
    if not token:
        print("Error: Token cannot be empty")
        sys.exit(1)
    
    # Create config directory if not exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save token
    config = {"private_token": token}
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set file permissions (readable only by owner)
    os.chmod(CONFIG_FILE, 0o600)
    
    print(f"✓ Token saved to: {CONFIG_FILE}")
    print("✓ Token will be automatically loaded in future sessions")


def load_token() -> str:
    """
    Load Private Token from configuration file.
    
    Returns:
        Saved Private Token, or None if not configured
    """
    if not CONFIG_FILE.exists():
        return None
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get("private_token")
    except Exception as e:
        print(f"Warning: Failed to load config: {e}")
        return None


def check_existing_token() -> None:
    """Check if token already exists and show status."""
    existing_token = load_token()
    
    if existing_token:
        print("\n" + "=" * 50)
        print("Existing Configuration Found")
        print("=" * 50)
        print(f"Config file: {CONFIG_FILE}")
        print(f"Token: {existing_token[:10]}...{existing_token[-5:]}")
        print("=" * 50 + "\n")
    else:
        print("\n" + "=" * 50)
        print("No Configuration Found")
        print("=" * 50)
        print(f"Config file location: {CONFIG_FILE}")
        print("\nSave your token:")
        print("  python configure.py --token 'your-token'")
        print("\nOr use environment variable (no config needed):")
        print("  export OCTOPIE_PRIVATE_TOKEN='your-token'")
        print("=" * 50 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Save Octopie.AI Private Token to config file for long-term persistence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Save token to config file (recommended)
  python configure.py --token "your-token-here"
  
  # Persist environment variable to config file
  export OCTOPIE_PRIVATE_TOKEN="your-token"
  python configure.py --from-env
  
  # Check saved configuration
  python configure.py --check

Note:
  The API client can read OCTOPIE_PRIVATE_TOKEN from environment directly.
  Use this tool only when you want to persist the token to a file.
        """
    )
    
    parser.add_argument(
        '--token',
        type=str,
        help='Private token to save to config file'
    )
    
    parser.add_argument(
        '--from-env',
        action='store_true',
        help='Save token from OCTOPIE_PRIVATE_TOKEN env var to config file'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check saved configuration'
    )
    
    args = parser.parse_args()
    
    # Mode 1: Check existing configuration
    if args.check:
        check_existing_token()
        return
    
    # Mode 2: Read from environment variable and save to config
    if args.from_env:
        token = os.environ.get("OCTOPIE_PRIVATE_TOKEN")
        if not token:
            print("Error: OCTOPIE_PRIVATE_TOKEN environment variable not set")
            print("Set it with: export OCTOPIE_PRIVATE_TOKEN='your-token'")
            sys.exit(1)
        save_token(token)
        return
    
    # Mode 3: Direct token input and save to config
    if args.token:
        save_token(args.token)
        return
    
    # No arguments provided - show help
    parser.print_help()
    print("\n" + "=" * 60)
    print("Get your Private Token at:")
    print("  https://www.octopie.ai → Account Settings → Generate Private Token")
    print("=" * 60)


if __name__ == "__main__":
    main()
