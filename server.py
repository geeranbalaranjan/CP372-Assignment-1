"""
CP372 - Computer Networks
Assignment 1: TCP Client-Server Application
File: server.py

Protocol Commands:
  LOGIN <username>   - Authenticate using users.txt
  MSG <text>         - Send a text message to the server
  FILE <filename>    - Transfer a file to the server
  QUIT               - Gracefully disconnect from the server
"""

import socket
import os
import time


# Configuration

HOST = "0.0.0.0"       # Listen on all available interfaces
PORT = 5372             # Port number for this assignment
BUFFER_SIZE = 4096      # Buffer size for receiving data
USERS_FILE = "users.txt"           # File containing valid usernames
FILES_DIR = "received_files"       # Directory to store received files


# Helper utilities


def log(message: str) -> None:
    """Print a timestamped status message to the console."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def load_valid_users(filepath: str) -> set:
    """Load valid usernames from a file. Returns an empty set if file not found."""
    if not os.path.exists(filepath):
        log(f"WARNING: '{filepath}' not found. No users will be able to log in.")
        return set()
    with open(filepath, "r") as f:
        users = {line.strip() for line in f if line.strip()}
    log(f"Loaded {len(users)} valid user(s) from '{filepath}'.")
    return users


def ensure_files_dir(directory: str) -> None:
    """Create the directory for received files if it does not exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        log(f"Created directory '{directory}' for received files.")


def send_response(conn: socket.socket, message: str) -> None:
    """Send a newline-terminated response string to the client."""
    try:
        conn.sendall((message + "\n").encode("utf-8"))
    except OSError as e:
        log(f"ERROR: Failed to send response: {e}")


# ──────────────────────────────────────────────
# Command handlers
# ──────────────────────────────────────────────

def handle_login(args: str, valid_users: set, session: dict) -> str:
    """
    Handle LOGIN <username>.
    A client must log in before using MSG or FILE.
    """
    if not args:
        return "ERROR: LOGIN requires a username. Usage: LOGIN <username>"

    username = args.strip()

    if session["logged_in"]:
        return f"ERROR: Already logged in as '{session['username']}'. Use QUIT to disconnect."

    if username not in valid_users:
        log(f"Failed login attempt for unknown user '{username}'.")
        return f"ERROR: Unknown user '{username}'. Access denied."

    session["logged_in"] = True
    session["username"] = username
    log(f"User '{username}' logged in successfully.")
    return f"OK: Welcome, {username}!"


def handle_msg(args: str, session: dict) -> str:
    """
    Handle MSG <text>.
    Displays the message server-side and acknowledges it to the client.
    """
    if not session["logged_in"]:
        return "ERROR: You must LOGIN before sending messages."

    if not args:
        return "ERROR: MSG requires a message body. Usage: MSG <text>"

    log(f"Message from '{session['username']}': {args}")
    return f"OK: Message received."


def handle_file(args: str, conn: socket.socket, session: dict) -> str:
    """
    Handle FILE <filename>.

    Transfer protocol:
      1. Client sends: FILE <filename>
      2. Server replies: READY
      3. Client sends: SIZE <bytes>
      4. Server replies: OK
      5. Client sends raw file bytes
      6. Server replies: OK: File '<filename>' saved (<bytes> bytes).
    """
    if not session["logged_in"]:
        return "ERROR: You must LOGIN before transferring files."

    if not args:
        return "ERROR: FILE requires a filename. Usage: FILE <filename>"

    filename = os.path.basename(args.strip())   # Strip any path traversal
    if not filename:
        return "ERROR: Invalid filename."

    # Signal readiness to receive
    send_response(conn, "READY")

    # Expect SIZE <bytes>
    try:
        size_line = conn.recv(BUFFER_SIZE).decode("utf-8").strip()
    except OSError as e:
        return f"ERROR: Failed to receive file size: {e}"

    if not size_line.upper().startswith("SIZE"):
        return "ERROR: Expected SIZE <bytes> after READY."

    size_parts = size_line.split(None, 1)
    if len(size_parts) != 2 or not size_parts[1].isdigit():
        return "ERROR: Invalid SIZE format. Expected: SIZE <integer>"

    file_size = int(size_parts[1])
    send_response(conn, "OK")

    # Receive file content
    received = b""
    try:
        while len(received) < file_size:
            chunk = conn.recv(min(BUFFER_SIZE, file_size - len(received)))
            if not chunk:
                return "ERROR: Connection lost during file transfer."
            received += chunk
    except OSError as e:
        return f"ERROR: File transfer interrupted: {e}"

    if len(received) != file_size:
        return (
            f"ERROR: Size mismatch — expected {file_size} bytes, "
            f"received {len(received)} bytes."
        )

    # Save the file
    save_path = os.path.join(FILES_DIR, filename)
    try:
        with open(save_path, "wb") as f:
            f.write(received)
    except OSError as e:
        return f"ERROR: Could not save file: {e}"

    log(f"File '{filename}' received from '{session['username']}' ({file_size} bytes) → '{save_path}'.")
    return f"OK: File '{filename}' saved ({file_size} bytes)."


def handle_quit(session: dict, addr: tuple) -> str:
    """Handle QUIT — log the disconnect and signal the loop to exit."""
    username = session["username"] if session["logged_in"] else "unauthenticated client"
    log(f"{username} ({addr[0]}:{addr[1]}) disconnected gracefully.")
    session["active"] = False
    return "OK: Goodbye!"



# Per-client session loop


def handle_client(conn: socket.socket, addr: tuple, valid_users: set) -> None:
    """Manage the full lifecycle of one connected client."""
    log(f"Client connected: {addr[0]}:{addr[1]}")
    send_response(conn, "OK: Connected to CP372 Server. Please LOGIN.")

    session = {
        "active": True,
        "logged_in": False,
        "username": None,
    }

    try:
        while session["active"]:
            # Receive one command line
            try:
                data = conn.recv(BUFFER_SIZE)
            except OSError as e:
                log(f"ERROR: Receive error from {addr}: {e}")
                break

            if not data:
                # Client closed connection without QUIT
                user = session["username"] or "unauthenticated client"
                log(f"{user} ({addr[0]}:{addr[1]}) disconnected unexpectedly.")
                break

            raw = data.decode("utf-8", errors="replace").strip()
            if not raw:
                send_response(conn, "ERROR: Empty command received.")
                continue

            log(f"Received from {addr[0]}:{addr[1]} → {raw!r}")

            # Parse command and optional arguments
            parts = raw.split(None, 1)
            command = parts[0].upper()
            args = parts[1] if len(parts) > 1 else ""

            # Dispatch
            if command == "LOGIN":
                response = handle_login(args, valid_users, session)
                send_response(conn, response)

            elif command == "MSG":
                response = handle_msg(args, session)
                send_response(conn, response)

            elif command == "FILE":
                response = handle_file(args, conn, session)
                send_response(conn, response)

            elif command == "QUIT":
                response = handle_quit(session, addr)
                send_response(conn, response)

            else:
                send_response(
                    conn,
                    f"ERROR: Unknown command '{command}'. "
                    "Valid commands: LOGIN, MSG, FILE, QUIT"
                )

    finally:
        conn.close()
        log(f"Connection with {addr[0]}:{addr[1]} closed.")



# Main server loop

def start_server() -> None:
    """Initialise and run the TCP server indefinitely."""
    valid_users = load_valid_users(USERS_FILE)
    ensure_files_dir(FILES_DIR)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        # Allow quick restart without "Address already in use" errors
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_sock.bind((HOST, PORT))
        except OSError as e:
            print(f"FATAL: Could not bind to {HOST}:{PORT} — {e}")
            return

        server_sock.listen(1)   # Queue up to 1 pending connection (single-client design)
        log(f"Server listening on {HOST}:{PORT}  (Ctrl+C to stop)")

        try:
            while True:
                log("Waiting for a client connection...")
                try:
                    conn, addr = server_sock.accept()
                except OSError as e:
                    log(f"ERROR: Accept failed: {e}")
                    continue

                handle_client(conn, addr, valid_users)
                log("Session ended. Ready for next client.\n" + "─" * 50)

        except KeyboardInterrupt:
            log("Server shutting down (KeyboardInterrupt).")



# Entry point


if __name__ == "__main__":
    start_server()