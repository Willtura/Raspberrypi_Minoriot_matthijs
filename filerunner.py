import subprocess
import time

web_path = "web.py"
usb_path = "mqttscreener.py"
app_path = "app.py"

try:
    # Start het web.py-script
    web_process = subprocess.Popen(["python", web_path])
    time.sleep(5)  # Geef het web.py-script de tijd om te starten
    app_process = subprocess.Popen(["python", app_path])
    time.sleep(5)
    # Start het mqttscreener.py-script tweemaal na elkaar
    usb_process = subprocess.Popen(["python", usb_path])
    print("Alle applicaties en servers zijn opgestart!")
except KeyboardInterrupt:
    # Stop alle scripts als Ctrl+C wordt ingedrukt
    web_process.kill()
    app_process.kill()
    usb_process.kill()
    print("Alle applicaties en servers zijn gestopt!")










