import tkinter as tk
from tkinter import scrolledtext, font
import os
import tarfile
import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime
from typing import List


class ShellEmulator:
    def __init__(self, root: tk.Tk, config_file: str) -> None:
        self.root = root
        self.config = self.load_config(config_file)
        self.cwd = self.extract_tar(self.config["tar_file"])
        self.create_gui()
        self.load_log()

    def load_config(self, config_file: str) -> dict:
        config = {}
        with open(config_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                config = row
        return config

    def extract_tar(self, tar_file: str) -> str:
        extracted_dir = "/tmp/shell_emulator"
        if not os.path.exists(extracted_dir):
            os.makedirs(extracted_dir)
        with tarfile.open(tar_file, "r") as tar:
            tar.extractall(path=extracted_dir)
        return extracted_dir

    def load_log(self) -> None:
        if os.path.exists(self.config["log_file"]):
            os.remove(self.config["log_file"])
        self.root_log = ET.Element("Logs")
        self.save_log()

    def save_log(self) -> None:
        xml_str = ET.tostring(self.root_log, "utf-8")
        parsed_xml = xml.dom.minidom.parseString(xml_str)
        pretty_xml_str = parsed_xml.toprettyxml(indent="  ")
        with open(self.config["log_file"], "w") as log_file:
            log_file.write(pretty_xml_str)

    def create_gui(self) -> None:
        text_font = font.Font(family="Courier", size=12)
        self.root.title("Shell Emulator")
        self.root.configure(bg="#2e3b4e")
        frame = tk.Frame(self.root, bg="#2e3b4e")
        frame.pack(padx=10, pady=10)
        self.output_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=text_font,
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
        )
        self.output_text.pack()
        self.input_text = tk.Entry(
            self.root,
            width=80,
            font=text_font,
            bg="#444444",
            fg="white",
            insertbackground="white",
        )
        self.input_text.pack(pady=5)
        self.input_text.bind("<Return>", self.process_command)
        self.update_prompt()

    def update_prompt(self) -> None:
        self.prompt = f"{self.config['user']}@{self.config['hostname']}:{self.cwd}$ "
        self.output_text.insert(tk.END, self.prompt)
        self.output_text.yview(tk.END)

    def process_command(self, event: tk.Event) -> None:
        command = self.input_text.get()
        self.input_text.delete(0, tk.END)
        self.execute_command(command)

    def execute_command(self, command: str) -> None:
        args = command.split()
        if not args:
            return
        cmd = args[0]
        if cmd == "exit":
            self.root.quit()
        elif cmd == "ls":
            self.ls_command()
        elif cmd == "cd":
            self.cd_command(args)
        elif cmd == "whoami":
            self.whoami_command()
        elif cmd == "tree":
            self.tree_command()
        elif cmd == "find":
            self.find_command(args)
        elif cmd == "clear":
            self.clear_screen()
        else:
            self.output_text.insert(tk.END, f"command not found: {cmd}\n")
            self.log_action(cmd, is_error=True)
        self.update_prompt()

    def ls_command(self) -> None:
        try:
            files = os.listdir(self.cwd)
            for file in files:
                self.output_text.insert(tk.END, f"{file}\n")
            self.log_action("ls")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {e}\n")

    def cd_command(self, args: List[str]) -> None:
        if len(args) > 1:
            new_dir = args[1]
            if new_dir == ".." or new_dir == "../":
                self.cwd = os.path.dirname(self.cwd)
            else:
                new_path = os.path.join(self.cwd, new_dir)
                if os.path.isdir(new_path):
                    self.cwd = new_path
                else:
                    self.output_text.insert(
                        tk.END, f"cd: no such file or directory: {new_dir}\n"
                    )
            self.log_action(f"cd {new_dir}")
        else:
            self.output_text.insert(tk.END, "cd: missing operand\n")

    def whoami_command(self) -> None:
        self.output_text.insert(tk.END, f"{self.config['user']}\n")
        self.log_action("whoami")

    def tree_command(self) -> None:
        self.print_tree(self.cwd)
        self.log_action("tree")

    def print_tree(self, path: str, level: int = 0) -> None:
        try:
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                self.output_text.insert(tk.END, " " * level + f"{file}\n")
                if os.path.isdir(full_path):
                    self.print_tree(full_path, level + 2)
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {e}\n")

    def find_command(self, args: List[str]) -> None:
        if len(args) < 2:
            self.output_text.insert(tk.END, "find: missing operand\n")
        else:
            self.find_files(self.cwd, args[1])
            self.log_action(f"find {args[1]}")

    def find_files(self, path: str, query: str) -> None:
        try:
            for file in os.listdir(path):
                if file == query:
                    full_path = os.path.join(path, file)
                    self.output_text.insert(tk.END, f"Found: {full_path}\n")
                elif os.path.isdir(os.path.join(path, file)):
                    self.find_files(os.path.join(path, file), query)
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {e}\n")

    def clear_screen(self) -> None:
        self.output_text.delete(1.0, tk.END)
        self.log_action("clear")

    def log_action(self, command: str, is_error: bool = False) -> None:
        action = ET.SubElement(self.root_log, "Action")
        if is_error:
            action.set("is_error", "true")
        action.set("user", self.config["user"])
        action.set("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        action.set("command", command)
        self.save_log()


if __name__ == "__main__":
    root = tk.Tk()
    emulator = ShellEmulator(root, "config.csv")
    root.mainloop()
