import os
import shutil
import hashlib
import json
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# 1. SETUP LOGGING (Saves activity to file_organizer.log)
logging.basicConfig(
    filename="file_organizer.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# 2. FILE CATEGORIES
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Audio": [".mp3", ".wav"],
    "Videos": [".mp4", ".mkv"],
    "Archives": [".zip", ".rar"]
}

# --- CORE FUNCTIONS ---

def categorize_files(folder_path):
    """Moves files into categorized folders based on extension."""
    history = []
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        
        # Skip subfolders and the history file
        if os.path.isdir(filepath) or filename == "history.json":
            continue

        # Find extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Find category
        folder_name = "Others"
        for category, extensions in CATEGORIES.items():
            if ext in extensions:
                folder_name = category
                break

        # Create subfolder if missing
        dest_folder = os.path.join(folder_path, folder_name)
        os.makedirs(dest_folder, exist_ok=True)

        # Move file
        dest_path = os.path.join(dest_folder, filename)
        shutil.move(filepath, dest_path)
        
        # Track move for undo & logging
        history.append({"from": dest_path, "to": filepath})
        logging.info(f"Categorized: {filename} -> {folder_name}")

    save_history(folder_path, "categorize", history)
    return len(history)


def find_duplicates(folder_path):
    """Finds duplicate files by comparing content hashes."""
    seen_hashes = {}
    duplicates = []

    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename == "history.json":
                continue

            filepath = os.path.join(root, filename)
            
            # Read file content hash
            with open(filepath, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            if file_hash in seen_hashes:
                duplicates.append(filepath)
            else:
                seen_hashes[file_hash] = filepath

    return duplicates


def batch_rename(folder_path, prefix):
    """Renames files sequentially: prefix_1, prefix_2, etc."""
    history = []
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for index, filename in enumerate(files, start=1):
        if filename == "history.json":
            continue

        ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}_{index}{ext}"

        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_name)

        os.rename(old_path, new_path)
        history.append({"from": new_path, "to": old_path})
        logging.info(f"Renamed: {filename} -> {new_name}")

    save_history(folder_path, "rename", history)
    return len(history)


def save_history(folder_path, action_name, records):
    """Saves the last action to history.json so it can be undone."""
    history_file = os.path.join(folder_path, "history.json")
    data = {"action": action_name, "records": records}
    with open(history_file, "w") as f:
        json.dump(data, f)


def undo_last_operation(folder_path):
    """Restores files to their previous paths before the last action."""
    history_file = os.path.join(folder_path, "history.json")
    if not os.path.exists(history_file):
        return False, "No undo history found."

    with open(history_file, "r") as f:
        data = json.load(f)

    # Move files back
    for record in reversed(data["records"]):
        current_path = record["from"]
        original_path = record["to"]
        if os.path.exists(current_path):
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            shutil.move(current_path, original_path)

    # Clear history after undo
    os.remove(history_file)
    logging.info(f"Undid operation: {data['action']}")
    return True, f"Undid last action: {data['action']}"


# --- SIMPLE GUI (USER INTERFACE) ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple File Organizer")
        self.root.geometry("450x450")
        self.folder_path = ""

        # UI Elements
        tk.Button(root, text="1. Select Folder", command=self.select_folder, bg="lightblue").pack(pady=40)
        self.label = tk.Label(root, text="No folder selected", fg="gray")
        self.label.pack(pady=6)

        tk.Button(root, text="Categorize Files", command=self.run_categorize).pack(fill="x", padx=40, pady=2)
        tk.Button(root, text="Find Duplicates", command=self.run_duplicates).pack(fill="x", padx=40, pady=2)
        tk.Button(root, text="Batch Rename", command=self.run_rename).pack(fill="x", padx=40, pady=2)
        tk.Button(root, text="Undo Last Action", command=self.run_undo, fg="purple").pack(fill="x", padx=40, pady=10)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.label.config(text=self.folder_path, fg="black")

    def run_categorize(self):
        if self.folder_path:
            count = categorize_files(self.folder_path)
            messagebox.showinfo("Done", f"Organized {count} files!")

    def run_duplicates(self):
        if self.folder_path:
            dupes = find_duplicates(self.folder_path)
            if dupes:
                messagebox.showwarning("Duplicates", f"Found {len(dupes)} duplicate files.")
            else:
                messagebox.showinfo("Duplicates", "No duplicates found!")

    def run_rename(self):
        if self.folder_path:
            prefix = simpledialog.askstring("Rename", "Enter name prefix (e.g., Photo):")
            if prefix:
                count = batch_rename(self.folder_path, prefix)
                messagebox.showinfo("Done", f"Renamed {count} files!")

    def run_undo(self):
        if self.folder_path:
            success, msg = undo_last_operation(self.folder_path)
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)

# Launch Application
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()