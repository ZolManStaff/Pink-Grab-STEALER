import os
import platform
import psutil
import socket
import uuid
import getpass

def info_file():
    user_folder = os.path.expanduser("~")
    target_folder = os.path.join(user_folder, "Windows NB")
    os.makedirs(target_folder, exist_ok=True)
    file_path = os.path.join(target_folder, "!INFO!.txt")
    additional_text = """
████████████████████████████████████████████████████████████████████████████████████████████
██                                                                                        ██
██         ██████╗ ██╗███╗   ██╗██╗  ██╗     ██████╗ ██████╗  █████╗ ██████╗              ██
██         ██╔══██╗██║████╗  ██║██║ ██╔╝    ██╔════╝ ██╔══██╗██╔══██╗██╔══██╗             ██
██         ██████╔╝██║██╔██╗ ██║█████╔╝     ██║  ███╗██████╔╝███████║██████╔╝             ██
██         ██╔═══╝ ██║██║╚██╗██║██╔═██╗     ██║   ██║██╔══██╗██╔══██║██╔══██╗             ██
██         ██║     ██║██║ ╚████║██║  ██╗    ╚██████╔╝██║  ██║██║  ██║██████╔╝             ██
██         ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝              ██
██                                                                                        ██
██  CODED BY: @RigOlit |  @Dedulin               CHANNEL: @Rigolit22 | @castles_perehod   ██
████████████████████████████████████████████████████████████████████████████████████████████
    """
    
    system_info = [
        f"▢ Operating System: {platform.system()} {platform.release()}",
        f"▢ Architecture: {platform.architecture()[0]}",
        f"▢ Processor: {platform.processor()}",
        f"▢ CPU Core Count: {psutil.cpu_count(logical=False)}",
        f"▢ Logical Processors: {psutil.cpu_count(logical=True)}",
        f"▢ CPU Frequency: {psutil.cpu_freq().current} MHz",
        f"▢ Total Memory: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        f"▢ Available Memory: {round(psutil.virtual_memory().available / (1024 ** 3), 2)} GB",
        f"▢ Used Memory: {round(psutil.virtual_memory().used / (1024 ** 3), 2)} GB",
        "▢ Disk Space:",
    ]
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            system_info.append(
                f"  - Disk {partition.device}: Total {round(usage.total / (1024 ** 3), 2)} GB, "
                f"Free {round(usage.free / (1024 ** 3), 2)} GB"
            )
        except PermissionError:
            continue
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])
    ip_address = socket.gethostbyname(socket.gethostname())
    username = getpass.getuser()
    computer_name = socket.gethostname()
    system_info.extend([
        f"▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃",
        f"▪ MAC Address: {mac_address}",
        f"▪ IP Address: {ip_address}",
        f"▪ Username: {username}",
        f"▪ Computer Name: {computer_name}",
    ])
    content = f"{additional_text}\n\n" + "\n".join(system_info)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
info_file()
