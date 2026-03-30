import time
import win32evtlog
import datetime
from PyQt6.QtCore import QThread, pyqtSignal

class EventSnifferWorker(QThread):
    log_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        self.running = True
        server = 'localhost'
        logtype = 'System'

        try:
            hand = win32evtlog.OpenEventLog(server, logtype)
            # Read backwards from the newest events
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        except Exception as e:
            self.log_signal.emit("ERROR", f"Win32 Event sniffer failed to attach: {e}")
            return

        self.log_signal.emit("INFO", "Kernel-PnP Sniffer armed. Watching for D2 drops...")

        last_seen_time = datetime.datetime.now()

        while self.running:
            try:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                if events:
                    for event in events:
                        # Convert PyTime to standard datetime
                        event_time = datetime.datetime.fromtimestamp(int(event.TimeGenerated))
                        if event_time <= last_seen_time:
                            continue

                        last_seen_time = max(last_seen_time, event_time)

                        # Check for the dreaded Surprise Removal
                        event_id = event.EventID & 0xFFFF
                        if 'Kernel-PnP' in event.SourceName and event_id == 410:
                            self.log_signal.emit("ERROR", "🚨 CRITICAL: Windows forced a USB Surprise Removal (Event 410)!")
                            self.log_signal.emit("WARNING", "The XHCI controller failed the D2 low-power state transition.")
            except Exception:
                pass # Fail silently if the log rolls over or locks temporarily

            time.sleep(2) # Poll every 2 seconds

        win32evtlog.CloseEventLog(hand)

    def stop(self):
        self.running = False
        self.wait()
