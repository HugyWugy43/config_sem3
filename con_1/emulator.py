import os
import zipfile
import tkinter as tk
import argparse
from tkinter import simpledialog, messagebox

class VirtualFileSystem:
    def __init__(self, zip_file):
        self.zip_file = zip_file
        self.filesystem = self.load_filesystem(zip_file)

    def load_filesystem(self, zip_file):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            files = zip_ref.namelist()
            print("DEBUG: Files in ZIP:", files)  # Отладочный вывод
            return files

        
    def resolve_path(self, current_path, path):
        """Преобразует относительный путь в абсолютный относительно текущей директории."""
        if path.startswith("/"):
            # Абсолютный путь
            normalized_path = os.path.normpath(path)
        else:
            # Относительный путь
            normalized_path = os.path.normpath(os.path.join(current_path, path))
        if not normalized_path.endswith("/"):
            normalized_path += "/"
        return normalized_path

   

    def list_directory(self, path):
        # Проверяем, какие файлы начинаются с данного пути
        files = [f[len(path):].split('/')[0] for f in self.filesystem if f.startswith(path)]
        # Убираем дубли (например, если dir1/dir2/file.txt и dir1/dir2/ существуют)
        return sorted(set(f for f in files if f))  # Убираем пустые строки


    def change_directory(self, args):
        if len(args) > 1:
            # Передаем текущую директорию в resolve_path
            new_path = self.fs.resolve_path(self.current_path, args[1])
            # Проверяем, существует ли директория
            new_path_normalized = new_path.rstrip('/') + '/'
            if any(f.startswith(new_path_normalized) for f in self.fs.filesystem):
                self.current_path = new_path_normalized
            else:
                self.output_area.insert(tk.END, f"Directory not found: {args[1]}\n")
        else:
            self.output_area.insert(tk.END, "Usage: cd <directory>\n")



    def head(self, path, lines=10):
        with zipfile.ZipFile(self.zip_file, 'r') as zip_ref:
            content = zip_ref.read(path).decode()
            return "\n".join(content.splitlines()[:lines])

    def rev(self, path):
        with zipfile.ZipFile(self.zip_file, 'r') as zip_ref:
            content = zip_ref.read(path).decode()
        
            # Разбиваем содержимое на строки
            lines = content.splitlines()
        
            # Переворачиваем каждую строку, но сохраняем порядок
            reversed_lines = [line[::-1] for line in lines]
        
            # Соединяем строки обратно в один текст с сохранением новых строк
            result = '\n'.join(reversed_lines)
            return result   

    def tree(self, path, depth=2):
        path = path.rstrip('/')
        if not path.endswith('/'):
            path += '/'
        return self.tree_recursive(path, depth)


    def tree_recursive(self, path, depth, current_depth=1):
        if current_depth > depth:
            return ""
    
        result = ""
        if path != "/":
            result += f"{'  ' * current_depth}{os.path.basename(path)}/\n"
    
        # Собираем элементы текущего уровня
        current_level = sorted(set(
            f.split('/')[current_depth]  # Текущий уровень пути
            for f in self.filesystem
            if f.startswith(path) and len(f.split('/')) > current_depth
        ))

        print(f"DEBUG: Building tree for path: {path}")
        print(f"DEBUG: Current level: {current_level}")
        print(f"DEBUG: Current depth: {current_depth}, Path: {path}, Current files: {current_level}")
    
        for item in current_level:
            full_path = os.path.join(path, item).rstrip('/')
            if any(f.startswith(full_path + "/") for f in self.filesystem):
                # Рекурсивно обрабатываем директории
                result += self.tree_recursive(full_path, depth, current_depth + 1)
            else:
                # Добавляем файл
                result += f"{'  ' * (current_depth + 1)}{item}\n"
        
        print(f"DEBUG: Checking path: {path}, Current depth: {current_depth}, Max depth: {depth}")
        return result



class ShellEmulator:
    def __init__(self, username, zip_file):
        self.username = username
        self.fs = VirtualFileSystem(zip_file)
        self.current_path = "fs_image/"

        # Инициализация GUI
        self.window = tk.Tk()
        self.window.title(f"Shell Emulator - {self.username}")
        self.output_area = tk.Text(self.window, height=20, width=80)
        self.output_area.pack()

        self.input_entry = tk.Entry(self.window, width=80)
        self.input_entry.pack()
        self.input_entry.bind("<Return>", self.execute_command)

        self.display_prompt()
        self.window.mainloop()

    def display_prompt(self):
        prompt = f"{self.username}@shell:{self.current_path}$ "
        self.output_area.insert(tk.END, prompt)
        self.output_area.yview(tk.END)

    def execute_command(self, event=None):
        command = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.output_area.insert(tk.END, f"{command}\n")
        self.process_command(command)

    def process_command(self, command):
        args = command.split()
        if not args:
            return
        cmd = args[0]

        if cmd == "exit":
            self.window.quit()
        elif cmd == "ls":
            self.list_directory()
        elif cmd == "cd":
            self.change_directory(args)
        elif cmd == "rev":
            self.reverse(args)
        elif cmd == "tree":
            self.display_tree(args)
        elif cmd == "head":
            self.head(args)
        else:
            self.output_area.insert(tk.END, f"Unknown command: {cmd}\n")
        self.display_prompt()

    def list_directory(self):
        files = self.fs.list_directory(self.current_path)
        if files:
            self.output_area.insert(tk.END, "\n".join(files) + "\n")
        else:
            self.output_area.insert(tk.END, "Directory is empty.\n")



    def change_directory(self, args):
        if len(args) > 1:
            new_path = args[1]
            self.current_path = new_path
        else:
            self.output_area.insert(tk.END, "Usage: cd <directory>\n")

    def reverse(self, args):
        if len(args) > 1:
            file_path = args[1]
            reversed_content = self.fs.rev(file_path)
            self.output_area.insert(tk.END, reversed_content + "\n")
        else:
            self.output_area.insert(tk.END, "Usage: rev <file>\n")

    def display_tree(self, args):
        if len(args) > 1:
            path = self.fs.resolve_path(args[1])  # Корректное преобразование пути
        else:
            path = self.current_path  # Используем текущую директорию
        try:
            tree = self.fs.tree(path)  # Строим дерево
            if not tree.strip():
                tree = "No files or directories found.\n"  # Если дерево пустое
        except Exception as e:
            tree = f"Error displaying tree: {e}\n"  # Обработка ошибок
        self.output_area.insert(tk.END, tree + "\n")
        self.output_area.yview(tk.END)  # Автопрокрутка вниз


    def head(self, args):
        if len(args) > 1:
            file_path = args[1]
            lines = 10
            if len(args) > 2:
                lines = int(args[2])
            head_content = self.fs.head(file_path, lines)
            self.output_area.insert(tk.END, head_content + "\n")
        else:
            self.output_area.insert(tk.END, "Usage: head <file> [lines]\n")

def parse_args():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("--user", required=True, help="Имя пользователя для приглашения")
    parser.add_argument("--zip", required=True, help="Путь к архиву виртуальной файловой системы (ZIP)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    emulator = ShellEmulator(args.user, args.zip)
