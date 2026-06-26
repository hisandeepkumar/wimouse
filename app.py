import sys
import os
import threading
import socket
import qrcode
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Label
import pyautogui
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# ---------- फ्रोजन (exe) के लिए पथ ----------
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------- लोकल IP पता ----------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# ---------- WebSocket इवेंट ----------
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('mouse_move')
def handle_mouse_move(data):
    dx = data.get('dx', 0)
    dy = data.get('dy', 0)
    pyautogui.moveRel(dx, dy)

@socketio.on('mouse_click')
def handle_mouse_click(data):
    button = data.get('button', 'left')
    if button == 'left':
        pyautogui.click()
    elif button == 'right':
        pyautogui.rightClick()

@socketio.on('mouse_scroll')
def handle_mouse_scroll(data):
    delta = data.get('delta', 0)
    pyautogui.scroll(delta)

# ---------- होम पेज ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- सर्वर थ्रेड ----------
def start_server():
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ---------- QR Code दिखाने वाली GUI ----------
def show_qr():
    ip = get_local_ip()
    url = f"http://{ip}:5000"
    qr = qrcode.make(url)
    qr_img = qr.resize((300, 300))
    img_tk = ImageTk.PhotoImage(qr_img)

    root = tk.Tk()
    root.title("Wireless Trackpad")
    root.geometry("400x500")
    root.resizable(False, False)

    label_ip = tk.Label(root, text=f"Connect to: {url}", font=("Arial", 14))
    label_ip.pack(pady=10)

    label_qr = tk.Label(root, image=img_tk)
    label_qr.image = img_tk
    label_qr.pack(pady=10)

    label_info = tk.Label(root, text="Scan QR with mobile\nto use as trackpad", font=("Arial", 12))
    label_info.pack(pady=10)

    root.mainloop()

# ---------- मुख्य ----------
if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    show_qr()
