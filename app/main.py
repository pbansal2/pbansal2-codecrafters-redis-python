import socket  # noqa: F401
from _thread import start_new_thread
import threading

def handle_client(connection):
    try:
        while True:
            data = connection.recv(1024)
            if not data:    
                break
            connection.sendall(b"+PONG\r\n")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connection.close()

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    try:
        while True:
            connection, _ = server_socket.accept() # wait for client  
            start_new_thread(handle_client,(connection,)) # Handle concurrent clients
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()
    '''
    try: # respond to multiple PINGs
        while True:
            data = connection.recv(1024)
            if not data:
                break
            connection.sendall(b"+PONG\r\n")
    finally:
        connection.close()
    '''



if __name__ == "__main__":
    main()
