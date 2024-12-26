import psutil

def kill_telegram_process():
    for process in psutil.process_iter(attrs=["pid", "name"]):
        try:
            if "telegram" in process.info["name"].lower():
                print(f"")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

if __name__ == "__main__":
    kill_telegram_process()