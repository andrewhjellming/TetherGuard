import time
import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.lockdown_service import LockdownService
from pymobiledevice3.exceptions import PyMobileDevice3Exception

class HeartbeatWorker(QThread):
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        self.running = True
        # Spin up a dedicated async event loop for this background thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.monitor_loop())
        finally:
            loop.close()

    async def monitor_loop(self):
        while self.running:
            try:
                # 1. Establish lockdown connection (Properly awaited)
                lockdown = await create_using_usbmux()
                self.status_signal.emit(True, f"Connected: {lockdown.short_info}")
                self.log_signal.emit("SUCCESS", f"Device found. UDID: {lockdown.udid}")

                # 2. Pivot to the dedicated heartbeat daemon
                self.log_signal.emit("INFO", "Starting com.apple.mobile.heartbeat service...")

                heartbeat_service = LockdownService(lockdown, "com.apple.mobile.heartbeat")
                self.log_signal.emit("SUCCESS", "Heartbeat service locked in. USB power state: D0.")

                # 3. The Marco/Polo Loop
                while self.running:
                    # Dynamically handle both sync and async reads
                    msg = heartbeat_service.service.recv_plist()
                    if asyncio.iscoroutine(msg):
                        msg = await msg

                    if not msg:
                        self.log_signal.emit("WARNING", "Heartbeat stream ended.")
                        break

                    command = msg.get("Command")
                    if command == "Marco":
                        self.log_signal.emit("INFO", "Received: Marco -> Sending: Polo (Link Active)")

                        # Respond to keep the link alive
                        send_task = heartbeat_service.service.send_plist({"Command": "Polo"})
                        if asyncio.iscoroutine(send_task):
                            await send_task
                    else:
                        self.log_signal.emit("WARNING", f"Unknown heartbeat command: {command}")

            except PyMobileDevice3Exception as e:
                self.log_signal.emit("ERROR", f"Device disconnected or service failed: {e}")
                self.status_signal.emit(False, "Link Lost")
            except Exception as e:
                self.log_signal.emit("ERROR", f"Transport error: {e}")
                self.status_signal.emit(False, "Link Lost")

            # Reconnection backoff
            if self.running:
                self.log_signal.emit("WARNING", "Waiting 5 seconds before scanning for devices...")
                await asyncio.sleep(5)

    def stop(self):
        self.running = False
        self.wait()
