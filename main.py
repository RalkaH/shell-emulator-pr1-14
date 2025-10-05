import tkinter as tk
from tkinter import scrolledtext
import getpass
import socket


class ShellEmulator:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        username = getpass.getuser()
        hostname = socket.gethostname()
        self.root.title(f"Эмулятор - [{username}@{hostname}]")
        self.root.geometry("700x500")

    def create_widgets(self):
        # Поле вывода
        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled')
        self.output.pack(expand=True, fill='both', padx=10, pady=10)

        # Поле ввода
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.prompt_label = tk.Label(self.input_frame, text="$ ")
        self.prompt_label.pack(side='left')

        self.entry = tk.Entry(self.input_frame, font=("Courier", 10))
        self.entry.pack(side='left', fill='x', expand=True)
        self.entry.bind("<Return>", self.execute_command)
        self.entry.focus()

    def print_output(self, text):
        self.output.config(state='normal')
        self.output.insert(tk.END, text + "\n")
        self.output.config(state='disabled')
        self.output.see(tk.END)

    def execute_command(self, event=None):
        user_input = self.entry.get().strip()
        if not user_input:
            return

        self.print_output(f"$ {user_input}")
        self.entry.delete(0, tk.END)

        parts = user_input.split()
        if not parts:
            return

        command = parts[0]
        args = parts[1:]

        if command == "exit":
            self.root.quit()
        elif command in ["ls", "cd"]:
            self.print_output(f"{command}: {' '.join(args)}")
        else:
            self.print_output(f"bash: {command}: команда не найдена")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShellEmulator(root)
    app.print_output("Добро пожаловать в эмулятор оболочки UNIX!")
    app.print_output("Поддерживаемые команды: ls, cd, exit")
    root.mainloop()
