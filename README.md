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
