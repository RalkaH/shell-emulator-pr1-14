import argparse
import json
import sys
import os
import getpass
import socket
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    def __init__(self, vfs_path, log_path, script_path=None):
        self.log_path = log_path
        self.script_path = script_path
        self.running = True

        # Загрузка VFS
        if not os.path.isdir(vfs_path):
            print(f"Ошибка: VFS не найден или не является директорией: {vfs_path}", file=sys.stderr)
            sys.exit(1)
        self.vfs_root = os.path.abspath(vfs_path)
        self.current_dir = self.vfs_root  # начальная директория = корень VFS

        # Создаём лог-файл
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

        # Отладочный вывод
        print(f"[DEBUG] VFS root: {self.vfs_root}")
        print(f"[DEBUG] Log file: {self.log_path}")
        print(f"[DEBUG] Script file: {self.script_path}")

        if self.script_path:
            self.run_script()
        else:
            self.run_gui()

    def log_command(self, command, args):
        log_entry = {
            "user": getpass.getuser(),
            "command": command,
            "args": args,
            "timestamp": datetime.now().isoformat()
        }
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log = []
        log.append(log_entry)
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    def safe_path(self, path):
        """Преобразует путь в абсолютный внутри VFS и проверяет, что он не выходит за пределы"""
        if os.path.isabs(path):
            full_path = os.path.abspath(os.path.join(self.vfs_root, path.lstrip('/')))
        else:
            full_path = os.path.abspath(os.path.join(self.current_dir, path))

        # Проверка: путь должен начинаться с self.vfs_root
        if not full_path.startswith(self.vfs_root):
            raise PermissionError("Доступ за пределы VFS запрещён")
        return full_path

    def execute_command(self, user_input, output_callback=None):
        if not user_input.strip():
            return True

        parts = user_input.strip().split()
        if not parts:
            return True

        command = parts[0]
        args = parts[1:]

        self.log_command(command, args)

        if command == "exit":
            if output_callback:
                output_callback("$ exit\nВыход...")
            self.running = False
            return True

        elif command == "ls":
            try:
                target = args[0] if args else "."
                full_path = self.safe_path(target)
                if not os.path.exists(full_path):
                    msg = f"ls: cannot access '{target}': No such file or directory"
                    if output_callback:
                        output_callback(f"$ {user_input}\n{msg}")
                    return False
                if not os.path.isdir(full_path):
                    # Если это файл — просто покажем его имя
                    msg = os.path.basename(full_path)
                else:
                    items = sorted(os.listdir(full_path))
                    msg = "\n".join(items) if items else ""
                if output_callback:
                    output_callback(f"$ {user_input}\n{msg}")
                return True
            except PermissionError as e:
                msg = f"ls: {e}"
                if output_callback:
                    output_callback(f"$ {user_input}\n{msg}")
                return False
            except Exception as e:
                msg = f"ls: error: {e}"
                if output_callback:
                    output_callback(f"$ {user_input}\n{msg}")
                return False

        elif command == "cd":
            if not args:
                # cd без аргументов — в корень VFS
                self.current_dir = self.vfs_root
                if output_callback:
                    output_callback(f"$ {user_input}")
                return True
            try:
                target = args[0]
                full_path = self.safe_path(target)
                if not os.path.exists(full_path):
                    msg = f"cd: {target}: No such file or directory"
                    if output_callback:
                        output_callback(f"$ {user_input}\n{msg}")
                    return False
                if not os.path.isdir(full_path):
                    msg = f"cd: {target}: Not a directory"
                    if output_callback:
                        output_callback(f"$ {user_input}\n{msg}")
                    return False
                self.current_dir = full_path
                if output_callback:
                    output_callback(f"$ {user_input}")
                return True
            except PermissionError as e:
                msg = f"cd: {e}"
                if output_callback:
                    output_callback(f"$ {user_input}\n{msg}")
                return False

        else:
            msg = f"bash: {command}: команда не найдена"
            if output_callback:
                output_callback(f"$ {user_input}\n{msg}")
            return False

    def run_script(self):
        if not os.path.exists(self.script_path):
            print(f"Ошибка: скрипт не найден: {self.script_path}", file=sys.stderr)
            sys.exit(1)

        with open(self.script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Убираем дублирование: не печатаем "$ команда" здесь
            success = self.execute_command(line, output_callback=print)
            if not success:
                print(f"Ошибка в строке {i} скрипта: '{line}'", file=sys.stderr)
                sys.exit(1)

        print("Скрипт выполнен успешно.")

    def run_gui(self):
        root = tk.Tk()
        username = getpass.getuser()
        hostname = socket.gethostname()
        root.title(f"Эмулятор - [{username}@{hostname}]")
        root.geometry("700x500")

        output = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        output.pack(expand=True, fill='both', padx=10, pady=10)

        input_frame = tk.Frame(root)
        input_frame.pack(fill='x', padx=10, pady=(0, 10))

        tk.Label(input_frame, text="$ ").pack(side='left')
        entry = tk.Entry(input_frame, font=("Courier", 10))
        entry.pack(side='left', fill='x', expand=True)
        entry.focus()

        def print_output(text):
            output.config(state='normal')
            output.insert(tk.END, text + "\n")
            output.config(state='disabled')
            output.see(tk.END)

        def on_enter(event=None):
            user_input = entry.get()
            if not user_input:
                return
            entry.delete(0, tk.END)

            success = self.execute_command(user_input, output_callback=print_output)
            if not self.running:
                root.after(100, root.destroy)

        entry.bind("<Return>", on_enter)

        print_output("Добро пожаловать в эмулятор оболочки UNIX!")
        print_output("Поддерживаемые команды: ls, cd, exit")
        root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Эмулятор UNIX-оболочки с VFS")
    parser.add_argument("--vfs", required=True, help="Путь к директории VFS")
    parser.add_argument("--log", required=True, help="Путь к лог-файлу (JSON)")
    parser.add_argument("--script", help="Путь к стартовому скрипту")

    args = parser.parse_args()

    ShellEmulator(vfs_path=args.vfs, log_path=args.log, script_path=args.script)


if __name__ == "__main__":
    main()

