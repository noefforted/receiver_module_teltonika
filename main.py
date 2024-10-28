import socket
import os
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

def start_tcp_receiver():
    """Mulai server TCP untuk menerima data dari Teltonika FMB920 secara langsung tanpa buffer."""
    # Mengambil konfigurasi langsung dari .env
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))

    # Mendirikan server TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print(f"Menunggu koneksi di {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Koneksi dari: {client_address}")
        try:
            data = client_socket.recv(4096)  # Menerima hingga 4096 byte data per sekali terima
            print(data)
            if not data:
                break
            else:
                # Menampilkan data yang diterima dalam format hexadecimal
                print("Data Diterima:", data)  # hex() untuk menampilkan data mentah sebagai hex
                # Kirim ACK (0x01) setelah menerima IMEI
                ack = b'\x01'
                client_socket.sendall(ack)
                print("ACK Dikirim")
                # Menampilkan data AVL mentah yang diterima
                print("Data AVL Mentah Diterima:", data.hex())
            
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
        finally:
            client_socket.close()
            print("Koneksi ditutup")

if __name__ == "__main__":
    start_tcp_receiver()
