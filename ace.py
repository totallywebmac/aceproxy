import socket
import threading

def print_splash_screen():
    print(r"""
     _    ____  _____ 
    / \  |  __\| ____|
   / _ \ | |   |  _|  
  / ___ \| |__ | |___ 
 /_/   \_\____/|_____|
    """)

def get_target_server():
    server_ip = input("Enter the target server IP: ")
    server_port = int(input("Enter the target server port: "))
    return server_ip, server_port

def hexify(data):
    return " ".join(f"{byte:02x}" for byte in data)

def dehexify(data):
    return bytes.fromhex(data.replace(" ", ""))

def ascii_encode(data):
    try:
        return data.decode('ascii')
    except UnicodeDecodeError:
        return None

def unicode_encode(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return "<non-printable data>"

def handle_client(client_socket, server_socket):
    try:
        while True:
            # Receive data from client
            data = client_socket.recv(4096)
            if not data:
                break

            # Display and possibly modify packet data
            data = modify_packet(data, direction="Client to Server")

            # Send modified or original data to the server
            server_socket.send(data)
            
            # Receive response from server
            response = server_socket.recv(4096)
            if not response:
                break

            # Display and possibly modify packet data
            response = modify_packet(response, direction="Server to Client")

            # Send modified or original response to the client
            client_socket.send(response)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        server_socket.close()

def modify_packet(packet, direction):
    hex_data = hexify(packet)
    ascii_data = ascii_encode(packet)
    if ascii_data is None:
        ascii_data = "<non-ASCII data>"
        unicode_data = unicode_encode(packet)
    else:
        unicode_data = ascii_data
    
    print(f"\n{direction} Packet Data (hex): {hex_data}")
    print(f"{direction} Packet Data (ASCII/Unicode): {unicode_data}")
    print("Do you want to modify this packet? (yes/no): ", end="")
    choice = input().strip().lower()
    if choice == "yes":
        print("Enter new packet data (hex): ", end="")
        new_data = input().strip()
        packet = dehexify(new_data)
    return packet

def start_proxy(server_ip, server_port):
    # Proxy details
    PROXY_IP = '127.0.0.1'
    PROXY_PORT = 25566

    # Create a socket to listen for client connections
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((PROXY_IP, PROXY_PORT))
    proxy_socket.listen(5)
    
    print(f"Proxy listening on {PROXY_IP}:{PROXY_PORT}")
    
    while True:
        # Accept a connection from the client
        client_socket, addr = proxy_socket.accept()
        print(f"Accepted connection from {addr}")
        
        # Connect to the actual Minecraft server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.connect((server_ip, server_port))
        except socket.error as e:
            print(f"Failed to connect to the Minecraft server at {server_ip}:{server_port}: {e}")
            client_socket.close()
            continue
        
        # Start a thread to handle the client-server communication
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket, server_socket)
        )
        client_handler.start()

if __name__ == "__main__":
    print_splash_screen()
    server_ip, server_port = get_target_server()
    start_proxy(server_ip, server_port)
