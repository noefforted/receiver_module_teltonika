import socket
import os
from dotenv import load_dotenv
import numpy as np
from datetime import datetime , timedelta, timezone

# Load environment variables from .env file
load_dotenv()

def parse_data(avl_data):
    zero_bytes = avl_data[:4]
    data_field_len = avl_data[4:8]
    codec_id = avl_data[8]
    num_of_data_1 = avl_data[9]
    timestamp = datetime.fromtimestamp(
        (int.from_bytes(avl_data[10:18], byteorder='big')/1000),
        timezone(timedelta(hours=7))) # 8 bytes
    priority = avl_data[18]
    longitude = int.from_bytes(avl_data[19:23], byteorder='big')  # 4 bytes
    latitude = int.from_bytes(avl_data[23:27], byteorder='big')   # 4 bytes
    altitude = int.from_bytes(avl_data[27:29], byteorder='big')   # 2 bytes
    angle = int.from_bytes(avl_data[29:31], byteorder='big')      # 2 bytes
    satellites = avl_data[31]
    speed = int.from_bytes(avl_data[32:34], byteorder='big')      # 2 bytes

    print(f"Zero Bytes: {zero_bytes}")
    print(f"Data Field Length: {data_field_len}")
    print(f"Codec ID: {codec_id}")
    print(f"Number of Data 1: {num_of_data_1}")
    print(f"Timestamp: {timestamp}")
    print(f"Priority: {priority}")
    print(f"Longitude: {longitude}")
    print(f"Latitude: {latitude}")
    print(f"Altitude: {altitude}")
    print(f"Angle: {angle}")
    print(f"Satellites: {satellites}")
    print(f"Speed: {speed}")
    
    return num_of_data_1

def start_tcp_receiver():
    # Configuration for host and port
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening for connections on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from: {client_address}")

        try:
            # Step 1: Receive the IMEI
            data = client_socket.recv(17)
            if data.startswith(b'\x00\x0f'):  # 0x000F means 15 bytes for IMEI
                imei = data[2:].decode('utf-8')
                print(f"IMEI Received: {imei}")

                # Send ACK for IMEI (0x01 for accepted)
                client_socket.sendall(b'\x01')
                print("ACK 0x01 sent for IMEI")

                # Step 2: Receive AVL Data
                while True:
                    avl_data = client_socket.recv(4096)
                    if not avl_data:
                        break

                    # Parse and display raw AVL data
                    print(f"AVL Data Received: {avl_data.hex()}")

                    # Parse specific fields based on Codec 8 structure
                    num_of_data_1 = parse_data(avl_data)

                    # Send acknowledgment: number of data records as 4 bytes
                    num_of_data_1_bytes = num_of_data_1.to_bytes(4, byteorder='big')
                    client_socket.sendall(num_of_data_1_bytes)
                    print(f"Data ack: {num_of_data_1_bytes.hex()} sent")

            else:
                print("Invalid IMEI length header received, closing connection.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()
            print("Connection closed.")

if __name__ == "__main__":
    start_tcp_receiver()
