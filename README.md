# TetherGuard: iOS USB Connection Stabilizer for Windows

**TetherGuard** is a lightweight, open-source Windows utility that permanently fixes the dreaded "~60-second disconnect loop" when tethering iOS devices or doing forensic USB analysis over the native XHCI controller.

## The Problem: The "Event 410" Drop
If you are doing iOS reverse engineering, forensic analysis, or heavy tethering on Windows 11, you have likely experienced your iPhone dropping its connection exactly every 60 seconds.

**This is not a bad cable.** It is a forced OS reset triggered by a driver power-mapping flaw:
1. Windows detects a micro-idle on the USB-C port.
2. The OS attempts to transition the port from an **S1** to a **D2 (Low Power)** state to save energy.
3. Apple's native `netaapl.sys` Windows driver fails the wake-up handshake.
4. Windows panics, drops the connection, and logs a **Kernel-PnP Event 410** (Surprise Removal).

## The Solution
TetherGuard runs a silent, asynchronous `lockdownd` heartbeat every 30 seconds. By querying a lightweight, read-only system property on the device, it forces the Windows XHCI controller to register continuous bus activity.

This completely bypasses the Windows Power Manager, locking the port in a **D0 (Full Power)** state and maintaining an unbreakable bridge.

## Installation & Usage

```bash
git clone [https://github.com/andrewhjellming/TetherGuard.git](https://github.com/andrewhjellming/TetherGuard.git)
cd TetherGuard
pip install -r requirements.txt
python -m tetherguard.main
```

Alternatively, Windows users can just run the start_tetherguard.bat script.

## Features

D0 State Lock: Prevents Windows micro-idles from killing your session.

Kernel Event Sniffer: Actively monitors the Windows Event API for Kernel-PnP drops to help diagnose unstable host hardware.

Non-Intrusive: Uses standard pymobiledevice3 bindings. Does not interfere with standard iTunes/Apple Devices communication or AFC data transfers.

🚀 Background & The Future of iOS Tooling
TetherGuard was born out of deep-dive USB transport research for LibIMobile.

Currently in development, LibIMobile is a massive, high-performance C++23 rewrite of the entire iOS tooling stack (replacing legacy libimobiledevice, pymobiledevice3, and fragmented jailbreak/forensic tools). It features asynchronous zero-copy architecture, native GPU acceleration, and comprehensive support for iOS 17+ CoreDevice QUIC tunnels.

If you are interested in the future of commercial-grade iOS forensics, protocol analysis, and hardware-level device management, follow my GitHub to be notified when LibIMobile goes live.
