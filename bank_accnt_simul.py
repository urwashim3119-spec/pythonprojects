
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from datetime import datetime
import json
import csv
import os

# Store data in files
FILE = "bank_data.json"

if os.path.exists(FILE):
    with open(FILE, "r") as f:
        accounts = json.load(f)
else:
    accounts = {}

current = None


def save():
    with open(FILE, "w") as f:
        json.dump(accounts, f, indent=4)


def log(action, amount, details=""):
    accounts[current]["history"].append([
        datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        action, amount, details
    ])
    save()
    show_history()


def create_account():
    name = simpledialog.askstring("Account", "Enter your name:")
    if not name:
        return

    pin = simpledialog.askstring("PIN", "Create a 4-digit PIN:", show="*")
    if not pin or len(pin) != 4 or not pin.isdigit():
        messagebox.showerror("Error", "PIN must be 4 digits")
        return

    kind = simpledialog.askstring(
        "Account Type", "Enter Savings or Current:"
    )
    if not kind or kind.title() not in ["Savings", "Current"]:
        messagebox.showerror("Error", "Invalid account type")
        return

    number = str(max([int(x) for x in accounts] + [10000]) + 1)

    accounts[number] = {
        "name": name,
        "pin": pin,
        "type": kind.title(),
        "balance": 0,
        "history": []
    }
    save()

    messagebox.showinfo(
        "Success", f"Account created!\nAccount Number: {number}"
    )


def login():
    global current

    number = simpledialog.askstring("Login", "Enter account number:")
    pin = simpledialog.askstring("Login", "Enter PIN:", show="*")

    if number in accounts and accounts[number]["pin"] == pin:
        current = number
        welcome.config(
            text=f"Welcome {accounts[current]['name']} "
                 f"({accounts[current]['type']})"
        )
        update_balance()
        show_history()
    else:
        messagebox.showerror("Error", "Invalid account number or PIN")


def update_balance():
    balance.config(text=f"₹ {accounts[current]['balance']:.2f}")


def amount_input():
    amount = simpledialog.askfloat(
        "Amount", "Enter amount:", minvalue=0.01
    )
    return amount


def deposit():
    amount = amount_input()
    if amount is not None:
        accounts[current]["balance"] += amount
        log("Deposit", amount)
        update_balance()
        messagebox.showinfo("Success", "Money deposited")


def withdraw():
    amount = amount_input()
    if amount is None:
        return

    if amount > accounts[current]["balance"]:
        messagebox.showerror("Error", "Insufficient balance")
        return

    accounts[current]["balance"] -= amount
    log("Withdrawal", amount)
    update_balance()
    messagebox.showinfo("Success", "Money withdrawn")


def transfer():
    receiver = simpledialog.askstring(
        "Transfer", "Enter receiver account number:"
    )

    if not receiver or receiver not in accounts:
        messagebox.showerror("Error", "Account not found")
        return

    if receiver == current:
        messagebox.showerror("Error", "Cannot transfer to yourself")
        return

    amount = amount_input()
    if amount is None:
        return

    if amount > accounts[current]["balance"]:
        messagebox.showerror("Error", "Insufficient balance")
        return

    accounts[current]["balance"] -= amount
    accounts[receiver]["balance"] += amount

    log("Transfer Sent", amount, "To " + receiver)

    accounts[receiver]["history"].append([
        datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "Transfer Received", amount, "From " + current
    ])

    save()
    update_balance()
    show_history()
    messagebox.showinfo("Success", "Transfer completed")


def interest():
    if accounts[current]["type"] != "Savings":
        messagebox.showinfo("Interest", "Savings accounts only")
        return

    rate = 4
    value = accounts[current]["balance"] * rate / 100

    messagebox.showinfo(
        "Interest",
        f"Annual rate: {rate}%\nEstimated interest: ₹{value:.2f}"
    )


def show_history():
    history.delete(0, tk.END)

    for item in accounts[current]["history"]:
        history.insert(
            tk.END,
            f"{item[0]} | {item[1]} | ₹{item[2]:.2f} | {item[3]}"
        )


def export_csv():
    filename = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )

    if not filename:
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Transaction", "Amount", "Details"])
        writer.writerows(accounts[current]["history"])

    messagebox.showinfo("Success", "History exported to CSV")


# GUI WINDOW
root = tk.Tk()
root.title("Bank Account Simulation")
root.geometry("700x600")
root.configure(bg="#edf2f7")

tk.Label(
    root, text="BANK ACCOUNT SIMULATION",
    font=("Arial", 20, "bold"),
    bg="#17365d", fg="white", pady=15
).pack(fill="x")

welcome = tk.Label(
    root, text="Create an account or login",
    font=("Arial", 13, "bold"), bg="#edf2f7"
)
welcome.pack(pady=10)

balance = tk.Label(
    root, text="₹ 0.00",
    font=("Arial", 22, "bold"),
    fg="green", bg="#edf2f7"
)
balance.pack()

buttons = [
    ("Create Account", create_account),
    ("Login", login),
    ("Deposit", deposit),
    ("Withdraw", withdraw),
    ("Transfer Funds", transfer),
    ("Calculate Interest", interest),
    ("Export History", export_csv)
]

frame = tk.Frame(root, bg="#edf2f7")
frame.pack(pady=10)

for i, (text, command) in enumerate(buttons):
    tk.Button(
        frame, text=text, command=command,
        width=17, bg="#2463a6", fg="white",
        font=("Arial", 10, "bold")
    ).grid(row=i // 3, column=i % 3, padx=5, pady=5)

tk.Label(
    root, text="Transaction History",
    font=("Arial", 13, "bold"), bg="#edf2f7"
).pack(pady=5)

history = tk.Listbox(root, width=85, height=12)
history.pack(padx=10, pady=5, fill="both", expand=True)

root.mainloop()