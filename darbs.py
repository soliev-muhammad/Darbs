import sqlite3
import hashlib
from tkinter import *
from tkinter import messagebox

# Create or connect to the SQLite database
conn = sqlite3.connect('contacts.db')
cursor = conn.cursor()

# Create User and Contact tables (if not exists)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Contact (
        contact_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT NOT NULL,
        phone_number TEXT,
        email TEXT,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
''')

# Commit the changes
conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registration function
def register(username, password):
    password_hash = hash_password(password)
    cursor.execute("INSERT INTO User (username, password_hash) VALUES (?, ?)", (username, password_hash))
    conn.commit()
    messagebox.showinfo("Success", "User registered successfully.")

# Login function
def login(username, password):
    password_hash = hash_password(password)
    cursor.execute("SELECT * FROM User WHERE username = ? AND password_hash = ?", (username, password_hash))
    user = cursor.fetchone()
    if user:
        messagebox.showinfo("Success", "Login successful.")
        return user[0]  # Return user_id
    else:
        messagebox.showerror("Error", "Invalid username or password.")
        return None

# Add contact function
def add_contact(user_id, name, phone_number, email):
    cursor.execute("INSERT INTO Contact (user_id, name, phone_number, email) VALUES (?, ?, ?, ?)",
                   (user_id, name, phone_number, email))
    conn.commit()
    messagebox.showinfo("Success", "Contact added successfully.")

# Get contacts function
def get_contacts(user_id):
    cursor.execute("SELECT * FROM Contact WHERE user_id = ?", (user_id,))
    contacts = cursor.fetchall()
    return contacts

# Sort contacts by name
def sort_contacts_by_name(user_id):
    cursor.execute("SELECT * FROM Contact WHERE user_id = ? ORDER BY name", (user_id,))
    contacts = cursor.fetchall()
    return contacts

# Remove contact by ID
def remove_contact(contact_id):
    cursor.execute("DELETE FROM Contact WHERE contact_id = ?", (contact_id,))
    conn.commit()
    messagebox.showinfo("Success", "Contact removed successfully.")

# GUI Functions
def register_user():
    register_window = Toplevel(root)
    register_window.title("Register")
    register_window.geometry("300x150")

    username_label = Label(register_window, text="Username:")
    username_label.pack()
    username_entry = Entry(register_window)
    username_entry.pack()

    password_label = Label(register_window, text="Password:")
    password_label.pack()
    password_entry = Entry(register_window, show="*")
    password_entry.pack()

    def register_user_db():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            register(username, password)
            register_window.destroy()
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    register_button = Button(register_window, text="Register", command=register_user_db)
    register_button.pack()

def login_user():
    login_window = Toplevel(root)
    login_window.title("Login")
    login_window.geometry("300x150")

    username_label = Label(login_window, text="Username:")
    username_label.pack()
    username_entry = Entry(login_window)
    username_entry.pack()

    password_label = Label(login_window, text="Password:")
    password_label.pack()
    password_entry = Entry(login_window, show="*")
    password_entry.pack()

    def login_user_db():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            user_id = login(username, password)
            if user_id:
                login_window.destroy()
                show_contacts(user_id)
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    login_button = Button(login_window, text="Login", command=login_user_db)
    login_button.pack()

def show_contacts(user_id):
    contacts_window = Toplevel(root)
    contacts_window.title("Contacts")
    contacts_window.geometry("400x300")

    def refresh_contacts():
        contacts_list.delete(0, END)
        contacts = get_contacts(user_id)
        for contact in contacts:
            contacts_list.insert(END, f"{contact[0]}: {contact[2]} - {contact[3]} - {contact[4]}")

    def add_contact_window():
        add_contact_window = Toplevel(contacts_window)
        add_contact_window.title("Add Contact")
        add_contact_window.geometry("300x200")

        name_label = Label(add_contact_window, text="Name:")
        name_label.pack()
        name_entry = Entry(add_contact_window)
        name_entry.pack()

        phone_label = Label(add_contact_window, text="Phone Number:")
        phone_label.pack()
        phone_entry = Entry(add_contact_window)
        phone_entry.pack()

        email_label = Label(add_contact_window, text="Email:")
        email_label.pack()
        email_entry = Entry(add_contact_window)
        email_entry.pack()

        def add_contact_db():
            name = name_entry.get()
            phone = phone_entry.get()
            email = email_entry.get()
            if name:
                add_contact(user_id, name, phone, email)
                add_contact_window.destroy()
                refresh_contacts()
            else:
                messagebox.showerror("Error", "Please enter a name for the contact.")

        add_button = Button(add_contact_window, text="Add Contact", command=add_contact_db)
        add_button.pack()

    def remove_contact_window():
        selected_contact = contacts_list.curselection()
        if selected_contact:
            contact_info = contacts_list.get(selected_contact)
            contact_id = int(contact_info.split(":")[0])
            remove_contact(contact_id)
            refresh_contacts()
        else:
            messagebox.showerror("Error", "Please select a contact to remove.")

    def sort_by_name():
        contacts_list.delete(0, END)
        contacts = sort_contacts_by_name(user_id)
        for contact in contacts:
            contacts_list.insert(END, f"{contact[0]}: {contact[2]} - {contact[3]} - {contact[4]}")

    contacts_frame = Frame(contacts_window)
    contacts_frame.pack(pady=20)

    contacts_list = Listbox(contacts_frame, width=50)
    contacts_list.pack(side=LEFT, fill=Y)

    scroll_bar = Scrollbar(contacts_frame, orient=VERTICAL)
    scroll_bar.pack(side=RIGHT, fill=Y)

    scroll_bar.config(command=contacts_list.yview)
    contacts_list.config(yscrollcommand=scroll_bar.set)

    refresh_contacts_button = Button(contacts_window, text="Refresh Contacts", command=refresh_contacts)
    refresh_contacts_button.pack()

    add_contact_button = Button(contacts_window, text="Add Contact", command=add_contact_window)
    add_contact_button.pack()

    remove_contact_button = Button(contacts_window, text="Remove Contact", command=remove_contact_window)
    remove_contact_button.pack()

    sort_button = Button(contacts_window, text="Sort by Name", command=sort_by_name)
    sort_button.pack()

# Main GUI
root = Tk()
root.title("Contact List Organizer")
root.geometry("300x150")

register_button = Button(root, text="Register", command=register_user)
register_button.pack(pady=20)

login_button = Button(root, text="Login", command=login_user)
login_button.pack(pady=20)

root.mainloop()

# Close the connection
conn.close()
