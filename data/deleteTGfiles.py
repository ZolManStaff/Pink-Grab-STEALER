import os
import shutil
def delete_tg_files():
    user_folder = os.path.expanduser("~")
    tdata_folder = os.path.join(user_folder, "Windows NB", "tdata")
    items_to_delete = ["dumps", "emoji", "tdummy", "temp", "coutries", "devversion", "prefix", "settings", "usertag", "working"]
    for item in items_to_delete:
        item_path = os.path.join(tdata_folder, item)
        if os.path.exists(item_path):
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"Удален файл: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        else:
            print()