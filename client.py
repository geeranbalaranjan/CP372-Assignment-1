"""
CP372 - Computer Networks, Spring 2026
Assignment 1: TCP Client-Server Application
File: client.py

Usage:
  python client.py [host] [port]

  host  - Server IP address (default: 127.0.0.1)
  port  - Server port number (default: 5372)

Protocol Commands (type at the prompt):
  LOGIN <username>   - Authenticate with the server
  MSG <text>         - Send a text message to the server
  FILE <filepath>    - Transfer a local file to the server
  QUIT               - Disconnect gracefully from the server
"""

import socket
import os
import sys

# ──────────────────────────────────────────────
# Configuration defaults
# ──────────────────────────────────────────────
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5372
BUFFER_SIZE = 4096


# ──────────────────────────────────────────────
# Helper utilities
# ──────────────────────────────────────────────

def print_banner() -> None:
    print("=" * 50)
    print("  CP372 TCP Client  |  Spring 2026")
    print("=" * 50)
    print("Commands: LOGIN <user>  MSG <text>  FILE <path>  QUIT")
    print("-" * 50)


def receive_response(sock: socket.socket) -> str:
    """
    Receive a newline-terminated response from the server.
    Accumulates chunks until a newline is found.
    Returns the stripped response string, or empty string on failure.
    """
    data = b""
    try:
        while b"\n" not in data:
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                return ""
            data += chunk
    except OSError as e:
        print(f"[ERROR] Failed to receive server response: {e}")
        return ""
    return data.decode("utf-8", errors="replace").strip()


def send_command(sock: socket.socket, command: str) -> None:
    """Send a newline-terminated command string to the server."""
    try:
        sock.sendall((command + "\n").encode("utf-8"))
    except OSError as e:
        print(f"[ERROR] Failed to send command: {e}")


# ──────────────────────────────────────────────
# Command handlers
# ──────────────────────────────────────────────

def do_login(sock: socket.socket, args: str) -> bool:
    """
    Handle LOGIN <username>.
    Returns True if the server accepted the login.
    """
    if not args.strip():
        print("[CLIENT] Usage: LOGIN <username>")
        return False

    send_command(sock, f"LOGIN {args.strip()}")
    response = receive_response(sock)
    print(f"[SERVER] {response}")
    return response.startswith("OK")


def do_msg(sock: socket.socket, args: str) -> None:
    """Handle MSG <text>."""
    if not args.strip():
        print("[CLIENT] Usage: MSG <text>")
        return

    send_command(sock, f"MSG {args.strip()}")
    response = receive_response(sock)
    print(f"[SERVER] {response}")


def do_file(sock: socket.socket, args: str) -> None:
    """
    Handle FILE <filepath>.

    Transfer protocol:
      1. Client sends: FILE <filename>
      2. Server replies: READY
      3. Client sends: SIZE <bytes>
      4. Server replies: OK
      5. Client streams raw file bytes
      6. Server replies with final status
    """
    filepath = args.strip()

    if not filepath:
        print("[CLIENT] Usage: FILE <filepath>")
        return

    if not os.path.exists(filepath):
        print(f"[CLIENT] Error: File not found: '{filepath}'")
        return

    if not os.path.isfile(filepath):
        print(f"[CLIENT] Error: '{filepath}' is not a regular file.")
        return

    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)

    # Step 1 — send FILE command with just the base filename
    send_command(sock, f"FILE {filename}")

    # Step 2 — wait for READY
    response = receive_response(sock)
    if response != "READY":
        print(f"[SERVER] {response}")
        print("[CLIENT] File transfer aborted: server not ready.")
        return

    # Step 3 — send file size
    send_command(sock, f"SIZE {file_size}")

    # Step 4 — wait for OK
    response = receive_response(sock)
    if not response.startswith("OK"):
        print(f"[SERVER] {response}")
        print("[CLIENT] File transfer aborted.")
        return

    # Step 5 — stream file bytes
    print(f"[CLIENT] Sending '{filename}' ({file_size} bytes)...")
    try:
        with open(filepath, "rb") as f:
            bytes_sent = 0
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                sock.sendall(chunk)
                bytes_sent += len(chunk)
        print(f"[CLIENT] Transfer complete ({bytes_sent} bytes sent).")
    except OSError as e:
        print(f"[CLIENT] Error reading/sending file: {e}")
        return

    # Step 6 — receive final server confirmation
    response = receive_response(sock)
    print(f"[SERVER] {response}")


def do_quit(sock: socket.socket) -> None:
    """Handle QUIT — notify server and close the connection."""
    send_command(sock, "QUIT")
    response = receive_response(sock)
    print(f"[SERVER] {response}")


# ──────────────────────────────────────────────
# Main client loop
# ──────────────────────────────────────────────

def run_client(host: str, port: int) -> None:
    """Connect to the server and enter the interactive command loop."""
    print_banner()
    print(f"[CLIENT] Connecting to {host}:{port} ...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"[CLIENT] Error: Connection refused. Is the server running on {host}:{port}?")
        return
    except OSError as e:
        print(f"[CLIENT] Error: Could not connect to {host}:{port} — {e}")
        return

    print(f"[CLIENT] Connected to {host}:{port}")

    # Print the server's greeting
    greeting = receive_response(sock)
    if greeting:
        print(f"[SERVER] {greeting}")

    try:
        while True:
            # Read user input
            try:
                raw = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[CLIENT] Interrupted. Disconnecting...")
                do_quit(sock)
                break

            if not raw:
                continue

            # Parse command and arguments
            parts = raw.split(None, 1)
            command = parts[0].upper()
            args = parts[1] if len(parts) > 1 else ""

            if command == "LOGIN":
                do_login(sock, args)

            elif command == "MSG":
                do_msg(sock, args)

            elif command == "FILE":
                do_file(sock, args)

            elif command == "QUIT":
                do_quit(sock)
                break

            else:
                print(
                    f"[CLIENT] Unknown command '{command}'. "
                    "Valid commands: LOGIN, MSG, FILE, QUIT"
                )

    finally:
        sock.close()
        print("[CLIENT] Connection closed. Goodbye!")


# ──────────────────────────────────────────────
# Entry point — parse optional host/port args
# ──────────────────────────────────────────────

if __name__ == "__main__":
    host = DEFAULT_HOST
    port = DEFAULT_PORT

    if len(sys.argv) >= 2:
        host = sys.argv[1]

    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            print(f"[CLIENT] Error: Invalid port '{sys.argv[2]}'. Must be an integer between 1 and 65535.")
            sys.exit(1)

    run_client(host, port)