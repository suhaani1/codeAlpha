import tkinter as tk
from tkinter import messagebox
import sqlite3
import yfinance as yf

def create_db():
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER,
            price REAL,
            value REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


def insert_stock_db(name, quantity, price):
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO stocks (name, quantity, price)
        VALUES (?, ?, ?)
    ''', (name, quantity, price))
    conn.commit()
    conn.close()


def read_all_stocks_db():
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute('SELECT id, name, quantity, price, value FROM stocks')
    stocks = c.fetchall()
    conn.close()
    return stocks


def update_stock_value_db(stock_id, value):
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute('''
        UPDATE stocks SET value = ?
        WHERE id = ?
    ''', (value, stock_id))
    conn.commit()
    conn.close()


def delete_stock_db():
    try:
        selected = stock_listbox.curselection()
        if selected:
            stock_id = stock_listbox.get(selected[0])[0]  # Get the stock ID from the selected item
            conn = sqlite3.connect('stock.db')
            c = conn.cursor()
            c.execute('DELETE FROM stocks WHERE id = ?', (stock_id,))
            conn.commit()
            conn.close()
            update_stock_listbox()
        else:
            messagebox.showwarning("No Selection", "Please select a stock to delete.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while deleting the stock: {e}")


def get_current_price(stock_name):
    try:
        stock = yf.Ticker(stock_name)
        data = stock.history(period='1d')
        return data['Close'].iloc[-1]
    except Exception as e:
        print(f"Error fetching price for {stock_name}: {e}")
        return None


def update_stock_listbox():
    stock_listbox.delete(0, tk.END)  # delete existing content
    stocks = read_all_stocks_db()
    for stock in stocks:
        stock_id, name, quantity, price, value = stock
        current_price = get_current_price(name)
        if current_price is not None:
            value = (current_price - price) * quantity
            stock_info = f"{name} | Quantity: {quantity} | Price: {current_price:.2f} | Gain/Loss: {value:.2f}"
            stock_listbox.insert(tk.END, (stock_id, stock_info))  # insert new content
            update_stock_value_db(stock_id, value)


def add_stock():
    try:
        name = input_stock_name.get()
        quantity = int(input_stock_quantity.get())
        price = float(input_stock_price.get())
        if yf.Ticker(name).history(period='1d').empty:
            messagebox.showerror("Invalid Stock Symbol", f"The stock symbol '{name}' is not valid.")
            return
        insert_stock_db(name, quantity, price)
        update_stock_listbox()
    except Exception as e:
        messagebox.showerror("Invalid Input", f"Please enter valid quantity and price values. {e}")
    finally:
        input_stock_name.delete(0, tk.END)
        input_stock_quantity.delete(0, tk.END)
        input_stock_price.delete(0, tk.END)



root = tk.Tk()
root.title("Stock Portfolio Tracker")

input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=10)
tk.Label(input_frame, text="Stock Name:").grid(row=0, column=0)
input_stock_name = tk.Entry(input_frame)
input_stock_name.grid(row=0, column=1)
tk.Label(input_frame, text="Quantity:").grid(row=1, column=0)
input_stock_quantity = tk.Entry(input_frame)
input_stock_quantity.grid(row=1, column=1)
tk.Label(input_frame, text="Buy Price:").grid(row=2, column=0)
input_stock_price = tk.Entry(input_frame)
input_stock_price.grid(row=2, column=1)
add_button = tk.Button(input_frame, text="Add Stock", command=add_stock)
add_button.grid(row=3, columnspan=2, pady=10)

stock_frame = tk.Frame(root)
stock_frame.pack(padx=10, pady=10)
stock_listbox = tk.Listbox(stock_frame, width=60, height=10)
stock_listbox.pack()

delete_button = tk.Button(root, text="Delete Stock", command=delete_stock_db)
delete_button.pack(side=tk.LEFT, padx=10, pady=10)
refresh_button = tk.Button(root, text="Refresh Stock", command=update_stock_listbox)
refresh_button.pack(side=tk.LEFT, padx=10, pady=10)

create_db()
update_stock_listbox()
root.after(60000, update_stock_listbox)

root.mainloop()
