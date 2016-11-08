# Multithreaded python socket server with Thread Pooling
## Yasir Mohamed - 13318246
A basic multithreaded python server that handles certains messages, sends a default response for others.

## Dependencies
* python3
* bash

## Run Server
```bash
./start.sh -p $portnumber
```
A `compile.sh` script has been provided, but is completely unnecessary.

## Usage

### Server
The server recognizes one command line argument, `-p`, which is used to specify a port it should listen on. You don't need to worry about this if you're just going to use the `start.sh` script.

The server implements threadpooling using python3's `multiprocessing.pool` library, where you can initialise a pool of threads to be used by the server. I have set the number of threads available in the pool to be 10. The server's socket also accepts a max of 15 connections in it's backlog. The general workflow of the server is:
* Start a pool of 10 worker threads
* Start a socket and listen on the specified port
* On a new connection, pass the client socket and address objects to a worker thread
* If no workers are available, hold the client in the backlog till a thread is available
* Once worker completes action, closes client socket connection, returns to pool

### Client
To run the client, execute:
```bash
python3 client.py -p $serverPortNumber -m 'HELO text'
```
where `-p` is the server port number, and `-m` is the message to be sent. This defaults to 'HELO text'.

## Communicating with the server
Please note, messages to the server must be of the format:
```
msg_length::message
```
where `msg_length` is the number of bytes in `message`. This is so the server can track exactly how many bytes it should be receiving without the need for timeouts.
