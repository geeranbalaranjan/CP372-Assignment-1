# CP372 Assignment 1 — TCP Client-Server Application
 
**Course:** CP372 – Computer Networks, Spring 2026  
**Assignment:** Group Assignment 1  
 
---
 
## Overview
 
This project implements a TCP-based client-server application using Python's socket API. The server and client communicate over a custom application-layer protocol supporting user login, text messaging, and file transfer.
 
---
 
## Folder Structure
 
```
CP372-Assignment-1/
├── server.py           # TCP server application
├── client.py           # TCP client application
├── users.txt           # List of valid usernames (one per line)
├── received_files/     # Created automatically; stores files sent by clients
└── README.md           # This file
```
 
---
 
## Dependencies
 
- **Python 3.x** (no external packages required)
- Standard library modules only: `socket`, `os`, `sys`, `time`
No `pip install` is needed.
 
---
 
## How to Run
 
### 1. Set Up Users
 
Create a `users.txt` file in the project folder with one valid username per line:
 
```
Alice
Bob
Charlie
```
 
> The server reads this file on startup. If it is missing or unsaved, all logins will be denied.
 
---
 
### 2. Start the Server
 
Open a terminal in the project folder and run:
 
```bash
python server.py
```
 
Expected output:
```
[2026-06-02 18:00:00] Loaded 3 valid user(s) from 'users.txt'.
[2026-06-02 18:00:00] Created directory 'received_files' for received files.
[2026-06-02 18:00:00] Server listening on 0.0.0.0:5372  (Ctrl+C to stop)
[2026-06-02 18:00:00] Waiting for a client connection...
```
 
The server listens on port `5372` and automatically waits for the next client after each session ends.
 
To stop the server, press `Ctrl+C`.
 
---
 
### 3. Start the Client
 
Open a **second terminal** in the project folder and run:
 
```bash
python client.py
```
 
To connect to a specific host or port:
 
```bash
python client.py <host> <port>
```
 
Example:
```bash
python client.py 192.168.1.10 5372
```
 
Default values: `host = 127.0.0.1`, `port = 5372`
 
---
 
## Example Commands
 
Once the client is connected, type commands at the `>` prompt:
 
```
> LOGIN Alice
[SERVER] OK: Welcome, Alice!
 
> MSG Hello, server!
[SERVER] OK: Message received.
 
> FILE report.pdf
[CLIENT] Sending 'report.pdf' (45312 bytes)...
[CLIENT] Transfer complete (45312 bytes sent).
[SERVER] OK: File 'report.pdf' saved (45312 bytes).
 
> QUIT
[SERVER] OK: Goodbye!
```
 
---
 
## Protocol Commands
 
| Command          | Description                                      |
|------------------|--------------------------------------------------|
| `LOGIN <username>` | Authenticate using a name from `users.txt`     |
| `MSG <text>`     | Send a text message to the server                |
| `FILE <filepath>`| Transfer a local file to the server              |
| `QUIT`           | Gracefully disconnect from the server            |
 
> `LOGIN` must be completed before using `MSG` or `FILE`.
 
---
 
## Error Handling
 
The application handles the following error cases:
 
- Invalid or unknown commands
- Login attempts with unrecognized usernames
- `MSG` or `FILE` used before logging in
- Missing or non-existent files on `FILE` transfer
- Empty commands or messages
- Unexpected client disconnection
- Server unavailable on client startup
- File size mismatches during transfer
---
 
## Notes
 
- Only **one client** can connect at a time (by design — multithreading is not required).
- Transferred files are saved to the `received_files/` directory, created automatically on first run.
- The server must be restarted if `users.txt` is modified after startup.
- Both text and binary files are supported for transfer.
