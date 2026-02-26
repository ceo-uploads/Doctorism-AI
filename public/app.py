from flask import Flask, request, jsonify, render_template
from brain import brain 
import wsgiserver  # Using the Florent Gallaire WSGI server
import socket
import qrcode
import os

app = Flask(__name__)

def get_ip():
    """Dynamically finds the PC's Wi-Fi IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Standard Google DNS IP to trigger local interface lookup
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def index():
    # Logs the connecting device IP to your terminal
    print(f"\n[DEVICE LINKED] Incoming: {request.remote_addr}")
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    msg = data.get('message', '')
    img = data.get('image', None)
    
    # Process through your custom brain logic
    reply_text, data_source = brain(msg, img) 
    
    return jsonify({
        "reply": reply_text, 
        "source": data_source
    })

# --- SERVER CONFIGURATION ---
# Use Port 8080 (often avoids Windows system conflicts better than 80)
USE_PORT = 8080
server = wsgiserver.WSGIServer(app, host='0.0.0.0', port=USE_PORT)

if __name__ == '__main__':
    current_ip = get_ip()
    # FIXED: Ensured the URL includes the correct port for the QR code
    wifi_url = f"http://{current_ip}:{USE_PORT}"
    
    
    print("\n" + "═"*50)
    print("      NEURAL LINK CORE: WSGI SERVER ONLINE")
    print("═"*50)
    print(f" Local Access:  http://127.0.0.1:{USE_PORT}")
    print(f" Network Access: {wifi_url}")
    print("─" * 50)
    
    print("SCAN TO CONNECT (Android/iOS):")
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(wifi_url)
    qr.make(fit=True)
    
    # Displays QR in the terminal (Invert=True for Dark Mode terminals)
    qr.print_ascii(invert=True)

    app.run(host='0.0.0.0', port=5000)
    
    print("─" * 50)
    print("Status: Waiting for mobile connections...")
    
    try:
        server.start()
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Could not start server: {e}")
    except KeyboardInterrupt:
        print("\n[OFFLINE] Stopping Neural Link Server...")
        server.stop()