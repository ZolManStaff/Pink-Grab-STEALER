import pyperclip

def save_clipboard_to_txt(file_name="clipboard.txt"):
        clipboard_content = pyperclip.paste()
        
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(clipboard_content)

save_clipboard_to_txt()
