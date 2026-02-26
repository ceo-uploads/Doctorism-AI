from flask import Flask, request, jsonify, render_template
from brain import brain 
import socket
import qrcode
import os

app = Flask(__name__)

def get_ip():
    """Dynamically finds the PC's Wi-Fi IP address for local testing."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def index():
    # Logs the connecting device IP to the console
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

# --- LOCAL SERVER CONFIGURATION ---
# This block only runs on your PC. Render ignores this entirely.
if __name__ == '__main__':
    USE_PORT = 8080
    current_ip = get_ip()
    wifi_url = f"http://{current_ip}:{USE_PORT}"
    
    print("\n" + "═"*50)
    print("      NEURAL LINK CORE: LOCAL SERVER MODE")
    print("═"*50)
    print(f" Local Access:   http://127.0.0.1:{USE_PORT}")
    print(f" Network Access: {wifi_url}")
    print("─" * 50)
    
    print("SCAN TO CONNECT (Android/iOS):")
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(wifi_url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    
    print("─" * 50)
    print("Status: Waiting for connections...")

    try:
        # We import wsgiserver only here so Render doesn't see it
        import wsgiserver
        server = wsgiserver.WSGIServer(app, host='0.0.0.0', port=USE_PORT)
        server.start()
    except ImportError:
        # Fallback to standard Flask if wsgiserver isn't installed
        print("wsgiserver not found, using default Flask server...")
        app.run(host='0.0.0.0', port=USE_PORT)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
    except KeyboardInterrupt:
        print("\n[OFFLINE] Stopping Neural Link Server...")
