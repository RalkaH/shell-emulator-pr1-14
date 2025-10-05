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
        self.vfs_path = vfs_path
        self.log_path = log_path
        self.script_path = script_path
        self.running = True

        # Создаём лог-файл, если не существует
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

        # Отладочный вывод параметров
        print(f"[DEBUG] VFS path: {self.vfs_path}")
        print(f"[DEBUG] Log file: {self.log_path}")
        print(f"[DEBUG] Script file: {self.script_path}")

        # Запуск GUI или скрипта
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
        # Прочитать текущий лог
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log = []
        # Добавить новую запись
        log.append(log_entry)
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    def execute_command(self, user_input, output_callback=None):
        if not user_input.strip():
            return True  # пустая строка — не ошибка

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
            return True  # exit — успешная команда!

        elif command in ["ls", "cd"]:
            msg = f"{command}: {' '.join(args)}"
            if output_callback:
                output_callback(f"$ {user_input}\n{msg}")
            return True

        else:
            msg = f"bash: {command}: команда не найдена"
            if output_callback:
                output_callback(f"$ {user_input}\n{msg}")
            return False  # только неизвестная команда — ошибка

    def run_script(self):
        """Выполняет команды из скрипта"""
        if not os.path.exists(self.script_path):
            print(f"Ошибка: скрипт не найден: {self.script_path}", file=sys.stderr)
            sys.exit(1)

        with open(self.script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            print(f"$ {line}")  # имитация ввода
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

            # Парсим команду для проверки
            parts = user_input.strip().split()
            command = parts[0] if parts else ""

            success = self.execute_command(user_input, output_callback=print_output)
            if not self.running:
                root.after(100, root.destroy)

        entry.bind("<Return>", on_enter)

        print_output("Добро пожаловать в эмулятор оболочки UNIX!")
        print_output("Поддерживаемые команды: ls, cd, exit")
        root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Эмулятор UNIX-оболочки")
    parser.add_argument("--vfs", required=True, help="Путь к виртуальной ФС (VFS)")
    parser.add_argument("--log", required=True, help="Путь к лог-файлу (JSON)")
    parser.add_argument("--script", help="Путь к стартовому скрипту")

    args = parser.parse_args()

    ShellEmulator(vfs_path=args.vfs, log_path=args.log, script_path=args.script)


if __name__ == "__main__":
    main()
