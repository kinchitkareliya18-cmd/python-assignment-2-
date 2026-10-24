
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Enter your MySQL password below when prompted.
    "database": "python_assignment2",
}


class ContactManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("850x520")
        self.selected_id = None

        self.connect_database()
        if self.connection is None:
            self.root.after(100, self.root.destroy)
            return

        self.create_table()
        self.build_gui()
        self.load_contacts()

    def connect_database(self):
        try:
            password = __import__("getpass").getpass(
                "Enter MySQL root password: "
            )
            self.connection = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=password,
                database=DB_CONFIG["database"],
            )
        except Error as error:
            self.connection = None
            messagebox.showerror(
                "Database error",
                f"Could not connect to MySQL:\n{error}"
            )

    def create_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS Contacts (
                contact_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(25) NOT NULL UNIQUE,
                email VARCHAR(254)
            )
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        finally:
            cursor.close()

    def build_gui(self):
        form = ttk.LabelFrame(self.root, text="Contact details", padding=12)
        form.pack(fill="x", padx=12, pady=10)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Phone").grid(row=1, column=0, sticky="w")
        ttk.Label(form, text="Email").grid(row=2, column=0, sticky="w")

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()

        ttk.Entry(form, textvariable=self.name_var, width=38).grid(
            row=0, column=1, padx=8, pady=4
        )
        ttk.Entry(form, textvariable=self.phone_var, width=38).grid(
            row=1, column=1, padx=8, pady=4
        )
        ttk.Entry(form, textvariable=self.email_var, width=38).grid(
            row=2, column=1, padx=8, pady=4
        )

        buttons = ttk.Frame(form)
        buttons.grid(row=0, column=2, rowspan=3, padx=12)

        ttk.Button(buttons, text="Add", command=self.add_contact).pack(
            fill="x", pady=3
        )
        ttk.Button(buttons, text="Update", command=self.update_contact).pack(
            fill="x", pady=3
        )
        ttk.Button(buttons, text="Delete", command=self.delete_contact).pack(
            fill="x", pady=3
        )
        ttk.Button(buttons, text="Clear", command=self.clear_form).pack(
            fill="x", pady=3
        )

        search_frame = ttk.Frame(self.root, padding=(12, 0))
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=35
        )
        search_entry.pack(side="left", padx=8)
        search_entry.bind("<KeyRelease>", lambda event: self.load_contacts())
        ttk.Button(
            search_frame, text="Refresh", command=self.load_contacts
        ).pack(side="left")

        columns = ("id", "name", "phone", "email")
        self.tree = ttk.Treeview(
            self.root, columns=columns, show="headings", height=12
        )
        for column, heading, width in [
            ("id", "ID", 55),
            ("name", "Name", 190),
            ("phone", "Phone", 150),
            ("email", "Email", 300),
        ]:
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width)

        self.tree.pack(fill="both", expand=True, padx=12, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.select_contact)

    def load_contacts(self):
        if self.connection is None or not self.connection.is_connected():
            return

        search = f"%{self.search_var.get().strip()}%"
        query = """
            SELECT contact_id, name, phone, COALESCE(email, '')
            FROM Contacts
            WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s
            ORDER BY name
        """

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (search, search, search))
            rows = cursor.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Error as error:
            messagebox.showerror("Database error", str(error))
        finally:
            cursor.close()

    def get_form_values(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()

        if not name or not phone:
            raise ValueError("Name and phone are required.")

        if email and ("@" not in email or "." not in email.rsplit("@", 1)[-1]):
            raise ValueError("Enter a valid email address.")

        return name, phone, email or None

    def add_contact(self):
        try:
            values = self.get_form_values()
            cursor = self.connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Contacts (name, phone, email) "
                    "VALUES (%s, %s, %s)", values
                )
                self.connection.commit()
            finally:
                cursor.close()

            self.load_contacts()
            self.clear_form()
            messagebox.showinfo("Success", "Contact added.")
        except ValueError as error:
            messagebox.showwarning("Invalid input", str(error))
        except Error as error:
            self.connection.rollback()
            messagebox.showerror("Database error", str(error))

    def select_contact(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return

        row = self.tree.item(selection[0], "values")
        self.selected_id = int(row[0])
        self.name_var.set(row[1])
        self.phone_var.set(row[2])
        self.email_var.set(row[3])

    def update_contact(self):
        if self.selected_id is None:
            messagebox.showwarning("Select contact", "Select a contact first.")
            return

        try:
            values = self.get_form_values()
            cursor = self.connection.cursor()
            try:
                cursor.execute(
                    "UPDATE Contacts SET name=%s, phone=%s, email=%s "
                    "WHERE contact_id=%s",
                    (*values, self.selected_id)
                )
                self.connection.commit()
            finally:
                cursor.close()

            self.load_contacts()
            self.clear_form()
            messagebox.showinfo("Success", "Contact updated.")
        except ValueError as error:
            messagebox.showwarning("Invalid input", str(error))
        except Error as error:
            self.connection.rollback()
            messagebox.showerror("Database error", str(error))

    def delete_contact(self):
        if self.selected_id is None:
            messagebox.showwarning("Select contact", "Select a contact first.")
            return

        if not messagebox.askyesno(
            "Confirm delete", "Delete the selected contact?"
        ):
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM Contacts WHERE contact_id=%s",
                (self.selected_id,)
            )
            self.connection.commit()
            self.load_contacts()
            self.clear_form()
        except Error as error:
            self.connection.rollback()
            messagebox.showerror("Database error", str(error))
        finally:
            cursor.close()

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = ContactManager(window)
    if app.connection is not None:
        window.protocol("WM_DELETE_WINDOW", app.close)
        window.mainloop()
