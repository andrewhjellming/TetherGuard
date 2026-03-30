import os
import sys
import subprocess
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for Windows terminal support
init(autoreset=True)

def setup_logging():
    """Creates the daily log directory and timestamped log file."""
    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H-%M-%S")

    log_dir = os.path.join("logs", date_str)
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{time_str}.log")
    return log_file

def write_log(file_path, level, message):
    """Appends a formatted line to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")

def main():
    log_file = setup_logging()

    print(Fore.CYAN + Style.BRIGHT + "========================================")
    print(Fore.CYAN + Style.BRIGHT + "  TetherGuard Application Monitor")
    print(Fore.CYAN + Style.BRIGHT + "========================================")
    print(Fore.GREEN + f"[*] Session log started at: {log_file}")
    write_log(log_file, "SYSTEM", "TetherGuard Application Monitor Boot Sequence Initiated.")

    # Command to run the actual PyQt6 application
    cmd = [sys.executable, "-m", "tetherguard.main"]

    print(Fore.YELLOW + "[*] Launching target process: " + " ".join(cmd))
    write_log(log_file, "SYSTEM", "Spawning child process...")

    try:
        # Start the process, piping stdout and stderr for capture
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1, # Line buffered for real-time output
            universal_newlines=True
        )

        # Monitor loop: Read standard output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                print(Fore.LIGHTWHITE_EX + f"[APP] {line}")
                write_log(log_file, "APP_STDOUT", line)

        # Capture any remaining errors (Crashes, Tracebacks)
        err_output = process.stderr.read()
        if err_output:
            for line in err_output.splitlines():
                if line.strip():
                    print(Fore.RED + Style.BRIGHT + f"[ERROR] {line.strip()}")
                    write_log(log_file, "APP_STDERR", line.strip())

        rc = process.poll()
        if rc == 0:
            print(Fore.GREEN + f"[*] Process exited cleanly (Code: {rc})")
            write_log(log_file, "SYSTEM", f"Process exited cleanly (Code: {rc})")
        else:
            print(Fore.RED + Style.BRIGHT + f"[!] Process crashed or exited with error code: {rc}")
            write_log(log_file, "CRASH", f"Process terminated abnormally with exit code: {rc}")

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[*] Monitor caught KeyboardInterrupt. Shutting down...")
        write_log(log_file, "SYSTEM", "User aborted via KeyboardInterrupt.")
        process.terminate()
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"[!] Monitor Fatal Error: {e}")
        write_log(log_file, "MONITOR_ERROR", str(e))

if __name__ == "__main__":
    main()
