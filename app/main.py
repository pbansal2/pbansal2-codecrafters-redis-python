import socket  # noqa: F401
from _thread import start_new_thread
import threading

lock = threading.Lock()

def handle_client(connection):
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                #lock.release()     
                break
            connection.sendall(b"+PONG\r\n")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connection.close()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    try:
        while True:
            connection, _ = server_socket.accept() # wait for client  
            #lock.acquire()
            start_new_thread(handle_client,(connection,))
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()
    try: # respond to multiple PINGs
        while True:
            data = connection.recv(1024)
            if not data:
                break
            connection.sendall(b"+PONG\r\n")
    finally:
        connection.close()



if __name__ == "__main__":
    main()
