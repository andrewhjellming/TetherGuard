import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QTextEdit, QFrame)
from PyQt6.QtCore import Qt

# Import from our new architecture paths
from tetherguard.services.heartbeat import HeartbeatWorker
from tetherguard.utilities.event_logger import EventSnifferWorker

class TetherGuardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TetherGuard - iOS Connection Stabilizer")
        self.resize(750, 450)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Status Banner
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet("background-color: #2d2d30; border-radius: 6px;")
        status_layout = QHBoxLayout(self.status_frame)

        self.status_indicator = QLabel("🔴")
        self.status_text = QLabel("Status: Disconnected")
        self.status_text.setStyleSheet("font-size: 15px; font-weight: bold;")

        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        layout.addWidget(self.status_frame)

        # Log Terminal
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #000000; color: #cccccc; font-family: Consolas; font-size: 13px;")
        layout.addWidget(self.log_view)

        # Control Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Engage D0 Lock")
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.setStyleSheet("background-color: #0e639c; padding: 12px; border-radius: 4px; font-weight: bold;")
        self.btn_start.clicked.connect(self.toggle_monitor)
        btn_layout.addWidget(self.btn_start)
        layout.addLayout(btn_layout)

        # Initialize Workers
        self.heartbeat_worker = HeartbeatWorker()
        self.heartbeat_worker.log_signal.connect(self.append_log)
        self.heartbeat_worker.status_signal.connect(self.update_status)

        self.sniffer_worker = EventSnifferWorker()
        self.sniffer_worker.log_signal.connect(self.append_log)

        self.append_log("INFO", "TetherGuard Initialized. Ready to engage.")

    def toggle_monitor(self):
        if not self.heartbeat_worker.running:
            self.heartbeat_worker.start()
            self.sniffer_worker.start()
            self.btn_start.setText("Disengage Lock")
            self.btn_start.setStyleSheet("background-color: #c53929; padding: 12px; border-radius: 4px; font-weight: bold;")
        else:
            self.heartbeat_worker.stop()
            self.sniffer_worker.stop()
            self.btn_start.setText("Engage D0 Lock")
            self.btn_start.setStyleSheet("background-color: #0e639c; padding: 12px; border-radius: 4px; font-weight: bold;")
            self.update_status(False, "Monitor Stopped")

    def update_status(self, connected: bool, text: str):
        self.status_indicator.setText("🟢" if connected else "🔴")
        self.status_text.setText(f"Status: {text}")

    def append_log(self, level: str, message: str):
        timestamp = time.strftime('%H:%M:%S')
        color = "#cccccc"
        if level == "ERROR": color = "#f14c4c"
        elif level == "SUCCESS": color = "#3dc56f"
        elif level == "WARNING": color = "#cca700"
        elif level == "INFO": color = "#3794ff"

        html = f'<span style="color: #666666;">[{timestamp}]</span> <span style="color: {color};"><b>[{level}]</b> {message}</span>'
        self.log_view.append(html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TetherGuardApp()
    window.show()
    sys.exit(app.exec())
