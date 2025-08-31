import socket  # noqa: F401
from _thread import start_new_thread
import threading
import time

store = {}
expiry = {}
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
            elif command == "SET" and len(parts) > 3: # stage LA7 (SET and GET)
                key = parts[3]
                print(f"{key}")
                value = " ".join(parts[6:7])
                print(f"{len(parts)}")
                #print(f"parts[8]=<{parts[7]}>, lower=<{parts[8].lower()}>")
                if len(parts) > 7 and parts[8].lower() == "px": # Stage YZ1 
                    ttl = int(parts[10])
                    expiry[key] = time.time() + ttl / 1000
                    #print(f"{expiry[key]}")
                    # Optional cleanup timers
                    threading.Timer(ttl / 1000, lambda k=key: store.pop(k, None)).start()
                    threading.Timer(ttl / 1000, lambda k=key: expiry.pop(k, None)).start()
                    #threading.Timer(ttl / 1000, store.pop, args=[key]).start()   
                else:
                    expiry.pop(key, None)              
                print(f"{value}")
                store[key] = value 
                response = f"+OK\r\n"
                connection.send(response.encode())
            elif command == "GET"  and len(parts) > 2:
                key = parts[3]      
                print(f"{key}")
                # Check expiration
                if key in expiry and time.time() > expiry[key]:
                    store.pop(key, None)
                    expiry.pop(key, None)
                    value = None
                else:
                    value = store.get(key,None)
                print(f"{value}")
                if value is not None:
                    response = f"${len(value)}\r\n{value}\r\n"
                else:
                    response = "$-1\r\n"
                connection.send(response.encode())
            elif command == "RPUSH" and len(parts) > 2: # lists - MH6
                key = parts[3]
                value = parts[6]
                print(f"{value}")
                if key not in store:
                    store[key] = []
                    store[key].extend(value)
                    response = f":{len(store)}\r\n"
                else:
                    store[key].extend(value)
                    response = f":{len(store[key])}\r\n"
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
