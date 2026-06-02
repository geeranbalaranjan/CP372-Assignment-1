# CP372 Assignment 1 — TCP Client-Server Application

**Course:** CP372 – Computer Networks, Spring 2026
**Assignment:** Group Assignment 1

---

## Overview

This project is a TCP client-server application made with Python sockets. The client connects to the server and can log in, send messages, transfer files, and quit properly.

The program uses a simple custom protocol with these commands:

* `LOGIN`
* `MSG`
* `FILE`
* `QUIT`

Only one client connects at a time, which matches the assignment requirement.

---

## Folder Structure

The project folder should look like this:

```text
CP372-Assignment-1/
├── server.py
├── client.py
├── users.txt
├── received_files/
└── README.md
```

## File Descriptions

| File / Folder     | Purpose                                              |
| ----------------- | ---------------------------------------------------- |
| `server.py`       | Runs the TCP server and waits for client connections |
| `client.py`       | Runs the TCP client and lets the user enter commands |
| `users.txt`       | Stores valid usernames for the LOGIN command         |
| `received_files/` | Stores files received from the client                |
| `README.md`       | Explains how to run and test the project             |

---

## Dependencies

This project needs:

* Python 3.x

No external packages are needed.

The program only uses built-in Python libraries such as:

* `socket`
* `os`
* `sys`
* `time`

No `pip install` is required.

To check your Python version, run:

```bash
python --version
```

or:

```bash
python3 --version
```

---

## How to Set Up Users

Before running the server, make sure there is a file called:

```text
users.txt
```

Inside `users.txt`, put one valid username per line.

Example:

```text
Alice
Bob
Charlie
```

The server checks this file when a user tries to log in.

If the username is not in `users.txt`, the login will fail.

---

## How to Run the Server

Open a terminal in the project folder.

Run:

```bash
python server.py
```

or, if your system uses `python3`:

```bash
python3 server.py
```

Expected output should look similar to this:

```text
Loaded 3 valid user(s) from 'users.txt'.
Created directory 'received_files' for received files.
Server listening on 0.0.0.0:5372
Waiting for a client connection...
```

The server listens on port:

```text
5372
```

Keep this terminal open while running the client.

To stop the server, press:

```text
Ctrl + C
```

---

## How to Run the Client

Open a second terminal in the same project folder.

Run:

```bash
python client.py
```

or:

```bash
python3 client.py
```

By default, the client connects to:

```text
127.0.0.1:5372
```

If you want to connect to a specific host and port, use:

```bash
python client.py <host> <port>
```

Example:

```bash
python client.py 127.0.0.1 5372
```

If the connection works, the client will show a prompt where you can type commands.

---

## Example Commands

After the client connects, use these commands:

### 1. Login

```text
LOGIN Alice
```

Expected response:

```text
[SERVER] OK: Welcome, Alice!
```

---

### 2. Send a Message

```text
MSG Hello, server!
```

Expected response:

```text
[SERVER] OK: Message received.
```

---

### 3. Send a File

```text
FILE report.pdf
```

Expected output:

```text
[CLIENT] Sending 'report.pdf'...
[CLIENT] Transfer complete.
[SERVER] OK: File 'report.pdf' saved.
```

The server saves the file inside:

```text
received_files/
```

---

### 4. Quit

```text
QUIT
```

Expected response:

```text
[SERVER] OK: Goodbye!
```

This closes the client connection properly.

---

## Protocol Commands

| Command | Format             | What it does                              |
| ------- | ------------------ | ----------------------------------------- |
| `LOGIN` | `LOGIN <username>` | Logs in using a username from `users.txt` |
| `MSG`   | `MSG <text>`       | Sends a text message to the server        |
| `FILE`  | `FILE <filepath>`  | Sends a local file to the server          |
| `QUIT`  | `QUIT`             | Disconnects from the server properly      |

Important note:

```text
LOGIN must be done before using MSG or FILE.
```

---

## Error Handling

The program handles common errors, such as:

* Invalid commands
* Unknown usernames
* Trying to send a message before logging in
* Trying to send a file before logging in
* Missing files
* Empty commands or messages
* Server not running when the client starts
* Client disconnecting unexpectedly
* File transfer problems

Instead of crashing, the program should show an error message.

---

## Testing Checklist

Before submitting, test these things:

* Server starts correctly
* Client connects to the server
* Valid login works
* Invalid login fails
* Message transfer works
* File transfer works
* File appears in `received_files/`
* Invalid command gives an error
* `QUIT` disconnects properly
* Server keeps waiting after client disconnects

---

