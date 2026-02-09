import socket
import time
import json
import random
import math

# Configuration
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 9999       # The port we will talk through

def generate_sensor_data(tick):
    """Generates a single data point with noise and sine wave drift."""
    base_temp = 20.0
    drift = math.sin(tick * 0.1) * 5
    noise = random.uniform(-1, 1)
    
    # Random anomaly
    spike = random.uniform(10, 20) if random.random() < 0.05 else 0
    
    return {
        "timestamp": time.time(),
        "temp": round(base_temp + drift + noise + spike, 2),
        "id": tick
    }

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"PRODUCER started on port {PORT}. Waiting for Consumer...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            tick = 0
            try:
                while True:
                    data = generate_sensor_data(tick)
                    # Convert to JSON string and add a newline (delimiter)
                    message = json.dumps(data) + "\n"
                    
                    # Send bytes
                    conn.sendall(message.encode('utf-8'))
                    print(f"Sent: {data['temp']}")
                    
                    tick += 1
                    time.sleep(0.5) 
            except (BrokenPipeError, ConnectionResetError):
                print("Client disconnected.")

if __name__ == "__main__":
    start_server()
