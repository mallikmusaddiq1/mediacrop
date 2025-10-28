#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import webbrowser
import json
import time
import subprocess
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from http_handler import CropHandler
from utils import get_file_info

# Global variables
media_file = None
verbose = False

__version__ = "5.0.0"
DEFAULT_PORT = 8000

def port_type(value):
    """Custom type for argparse to validate port number."""
    try:
        port = int(value)
        if not (1024 <= port <= 65535):
            raise argparse.ArgumentTypeError(f"Port must be between 1024 and 65535. Got {port}.")
        return port
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid port number: {value}")

def parse_arguments():
    """Parses command-line arguments using argparse for robustness."""

    help_epilog = """
Supported Preview Formats:
  Images : JPG, PNG, WEBP, AVIF, GIF, BMP, SVG, ICO
  Videos : MP4, WEBM, MOV, OGV
  Audio  : MP3, WAV, FLAC, OGG, M4A, AAC, OPUS

Author Info:
  Name   : Mallik Mohammad Musaddiq
  GitHub : https://github.com/mallikmusaddiq1/mediacrop
  Email  : mallikmusaddiq1@gmail.com
"""
    
    parser = argparse.ArgumentParser(
        description="""mediacrop - Visual FFmpeg Crop Tool
==================================================
A CLI tool featuring a localhost web interface for visually determining FFmpeg crop coordinates of any media file.""",
        epilog=help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter  # Epilog formatting ko theek rakhta hai
    )
    
    parser.add_argument(
        'media_file',
        metavar='<media_file>',
        type=str,
        help='Path to the video or image file.'
    )
    parser.add_argument(
        '-p', '--port',
        type=port_type,
        default=DEFAULT_PORT,
        help=f'Use a specific port for the server (default: {DEFAULT_PORT}).'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Specify host address (default: 127.0.0.1).'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed server logs.'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'mediacrop {__version__}'
    )
    
    # --help aur --version ab argparse khud handle karega
    return parser.parse_args()


def open_browser_auto(url, verbose=False):
    """
    Attempts to automatically open the URL in the default browser,
    handling various environments and edge cases (Termux, WSL, etc.).
    Returns True on success, False on failure.
    """
    
    # --- Environment 1: Termux (Android) ---
    try:
        if 'com.termux' in os.environ.get('PREFIX', ''):
            if verbose:
                print("Termux environment detected. Using 'termux-open-url'.")
            subprocess.run(
                ['termux-open-url', url], 
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            print(f"Opening {url} in default browser...")
            return True
    except Exception as e:
        if verbose:
            print(f"Termux-open-url failed (falling back): {e}")
            
    # --- Environment 2: WSL (Windows Subsystem for Linux) ---
    try:
        if 'WSL_INTEROP' in os.environ or 'WSL_DISTRO_NAME' in os.environ:
            if verbose:
                print("WSL environment detected. Using 'explorer.exe' to open URL on Windows host.")
            subprocess.run(
                ['explorer.exe', url], 
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            print(f"Opening {url} in default browser...")
            return True
    except Exception as e:
        if verbose:
            print(f"WSL 'explorer.exe' failed (falling back): {e}")

    # --- Environment 3: Standard (Windows, macOS, Graphical Linux) ---
    try:
        if verbose:
            print("Standard environment. Trying 'webbrowser.open()'.")
        
        if webbrowser.open(url):
            print(f"Opening {url} in default browser...")
            return True
        else:
            if verbose:
                print("'webbrowser.open()' returned False. Likely a headless or unsupported environment.")
            return False
    except Exception as e:
        if verbose:
            print(f"'webbrowser.open()' raised an exception: {e}")
        return False

    # --- Failure ---
    if verbose:
        print("All automatic browser opening methods failed.")
    return False

def main():
    # --- Step 1: Perfected Argument Parsing ---
    # Manual sys.argv checks hata diye gaye hain
    args = parse_arguments()

    global media_file, verbose
    media_file = os.path.abspath(args.media_file)
    verbose = args.verbose
    port = args.port
    host = args.host

    if not os.path.exists(media_file):
        print(f"Error: File not found - {media_file}", file=sys.stderr)
        sys.exit(1)

    if not os.access(media_file, os.R_OK):
        print(f"Error: Permission denied - {media_file}", file=sys.stderr)
        sys.exit(1)

    file_info = get_file_info(media_file)
    if file_info:
        file_size_gb = file_info['size'] / (1024 * 1024 * 1024)
        file_size_mb = file_info['size'] / (1024 * 1024)
      
        if file_size_gb >= 1:
            size_str = f"{file_size_gb:.2f} GB"
        else:
            size_str = f"{file_size_mb:.2f} MB"

        print(f"File   : {file_info['name']}")
        print(f"Size   : {size_str}")
        print(f"Format : {file_info['extension'].upper().replace('.', '')}")
  
    server = None
    original_port = port
    max_attempts = 100
    
    for attempt in range(max_attempts):
        try:
            server = HTTPServer((host, port), CropHandler)
            server.media_file = media_file
            server.verbose = verbose
            break  # Port mil gaya, loop se bahar niklo
        except OSError as e:
            if e.errno == 98:
                if attempt == 0:
                    print(f"Port {original_port} is busy, trying next available port...")
                port += 1
            else:
                # Koi aur server error
                print(f"Server error: {e}", file=sys.stderr)
                sys.exit(1)

    if server is None:
        print(f"Error: Could not find an available port starting from {original_port}.", file=sys.stderr)
        sys.exit(1)
  
    url = f"http://{host}:{port}"
    try:
        auto_open_success = open_browser_auto(url, verbose)
        
        if not verbose:
            print(f"Server : {url}")
            if not auto_open_success:
                print(f"Open {url} in browser...") 
            print()
            print("Tips:")
            print("   • Drag crop box to move anywhere")
            print("   • Use arrow keys for precision") 
            print("   • Press 'G' for grid overlay")
            print("   • Press 'C' to center crop")
            print("   • Right-click for more options")
            print()
            print("Click 'Save Coordinates' when ready")
            print("Press Ctrl+C to stop server")
            print("-" * 50)
      
        if verbose:
            print(f"Server running on port {port}")
            print(f"Serving file: {media_file}")
            if not auto_open_success:
                print(f"Open {url} in browser...")
      
        server.serve_forever()
      
    except KeyboardInterrupt:
        print("\nServer stopped")
        if server:
            server.server_close()
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        if server:
            server.server_close()
        sys.exit(1)


if __name__ == "__main__":
    main()