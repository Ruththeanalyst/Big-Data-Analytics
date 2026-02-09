import socket
import json
from IPython.display import clear_output
import statistics
from collections import deque

# --- CONFIGURATION ---
PRODUCER_IP = '127.0.0.1'  # If running on same machine
PORT = 9999

# --- Analytics Engine for Tumbling Window ---
class AnalyticsEngine:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.window = []

    def process(self, temp):
        self.window.append(temp)
        if len(self.window) < self.window_size:
            # Not enough data for a full window yet
            return None
        elif len(self.window) == self.window_size:
            avg = sum(self.window) / self.window_size
            self.window = []  # Clear window for next "tumble"
            return avg

# --- Consumer Logic ---
def start_consumer():
    engine = AnalyticsEngine(window_size=10)
    
    print(f"Connecting to Producer at {PRODUCER_IP}:{PORT}...")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((PRODUCER_IP, PORT))
        print("Connected! Receiving Stream...")
        
        socket_file = s.makefile('r')
        
        for line in socket_file:
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue  # Skip corrupted packets
                
            current_temp = data['temp']
            avg_temp = engine.process(current_temp)
            
            clear_output(wait=True)
            print(f"--- 📡 NETWORK STREAM DASHBOARD ---")
            print(f"Source: {PRODUCER_IP}")
            print(f"Packet ID: {data['id']}")
            print("-" * 30)
            print(f"Incoming Temp: {current_temp} °C")
            if avg_temp is not None:
                print(f"Tumbling Window Avg (10 readings): {avg_temp:.2f} °C")
            else:
                print(f"Tumbling Window Avg: collecting... ({len(engine.window)}/10)")
            
            # Simple visual bar
            print("\nGraph:")
            print("#" * int(current_temp))
            
    except ConnectionRefusedError:
        print("Could not connect. Is the Producer script running?")
    except KeyboardInterrupt:
        print("\nStopped by user.")
        s.close()
    except Exception as e:
        print(f"Error: {e}")
        s.close()

# Start the consumer
start_consumer()
