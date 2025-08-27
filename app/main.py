import socket  # noqa: F401
from _thread import start_new_thread
import threading

store = {}
def handle_client(connection):
    try:
        while True:
            data = connection.recv(1024)
            if not data:    
                break
            data:str = data.decode().strip()
            parts = data.split()
            if not parts:
                continue
            command = parts[2].upper()

            if command == "PING":
                connection.sendall(b"+PONG\r\n")
            elif command == "ECHO" and len(parts) > 1: # redis protocol parser - stage 5
                message = " ".join(parts[4:])  # join in case of multiple words
                response = f"${len(message)}\r\n{message}\r\n"
                connection.send(response.encode())
            elif command == "SET" and len(parts) > 3:
                key = parts[3]
                value = " ".join(parts[4])
                store[key] = value 
                response = f"+OK\r\n"
                connection.send(response.encode())      
            elif command == "GET"  and len(parts) > 3:
                key = parts[3]
                if key in store:
                    value = store[key]
                    response = f"${len(value)}\r\n{value}\r\n"
                else:
                    response = "$-1\r\n"
                connection.send(response.encode())
            else:
                connection.send(b"-ERR unknown command\r\n")      
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
