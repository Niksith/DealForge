
import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation

from database import get_connection
from coupons import create_coupon
from checkout import checkout

from optimizer import find_best_coupon_combination

from cart import (
    add_item,
    remove_item,
    update_quantity,
    calculate_cart_total,
    get_cart_items_for_validation
)

from reports import (
    get_total_orders,
    get_total_coupons_used,
    get_total_discounts,
    get_coupon_usage_report,
    get_customer_usage_report,
    get_order_history
)



class DealForgeApp:

    def __init__(self, root):
        self.root = root

        self.root.title("DealForge - Coupon Optimisation System")
        self.root.geometry("1200x750")
        self.root.minsize(950, 600)
        self.root.configure(bg="#F5F6FA")

        # Application colours
        self.ORANGE = "#F47721"
        self.DARK = "#252A34"
        self.WHITE = "#FFFFFF"
        self.BACKGROUND = "#F5F6FA"
        self.TEXT = "#333333"
        self.GRAY = "#777777"

        self.cart = []

        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    def setup_styles(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=self.WHITE,
            foreground=self.TEXT,
            rowheight=30,
            fieldbackground=self.WHITE,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=self.ORANGE,
            foreground=self.WHITE,
            font=("Arial", 10, "bold")
        )

    def create_layout(self):

        self.main_frame = tk.Frame(
            self.root,
            bg=self.BACKGROUND
        )
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(
            self.main_frame,
            bg=self.DARK,
            width=230
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Application title
        tk.Label(
            self.sidebar,
            text="DEALFORGE",
            font=("Arial", 22, "bold"),
            bg=self.DARK,
            fg=self.ORANGE
        ).pack(pady=(35, 5))

        tk.Label(
            self.sidebar,
            text="Coupon Optimisation System",
            font=("Arial", 9),
            bg=self.DARK,
            fg="#BBBBBB"
        ).pack(pady=(0, 35))

        # Navigation
        navigation = [
            ("Dashboard", self.show_dashboard),
            ("Customers", self.show_customers),
            ("Shopping Cart", self.show_cart),
            ("Coupons", self.show_coupons),
            ("Checkout", self.show_checkout),
            ("Reports", self.show_reports)
        ]

        for name, command in navigation:

            button = tk.Button(
                self.sidebar,
                text="   " + name,
                command=command,
                font=("Arial", 11),
                bg=self.DARK,
                fg=self.WHITE,
                activebackground=self.ORANGE,
                activeforeground=self.WHITE,
                relief="flat",
                anchor="w",
                padx=15,
                pady=13,
                cursor="hand2",
                bd=0
            )

            button.pack(fill="x", padx=10, pady=3)

        tk.Label(
            self.sidebar,
            text="DealForge v1.0",
            font=("Arial", 9),
            bg=self.DARK,
            fg="#AAAAAA"
        ).pack(side="bottom", pady=20)

        # Main content
        self.content = tk.Frame(
            self.main_frame,
            bg=self.BACKGROUND
        )
        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def create_page_header(self, title, description, parent=None):

            if parent is None:
                parent = self.content

            header = tk.Frame(
                parent,
                bg=self.BACKGROUND
            )
            header.pack(fill="x", padx=35, pady=(30, 20))

            tk.Label(
                header,
                text=title,
                font=("Arial", 24, "bold"),
                bg=self.BACKGROUND,
                fg=self.DARK
            ).pack(anchor="w")

            tk.Label(
                header,
                text=description,
                font=("Arial", 10),
                bg=self.BACKGROUND,
                fg=self.GRAY
            ).pack(anchor="w", pady=(5, 0))
    
    def create_placeholder_page(self, title, description):

        self.clear_content()
        self.create_page_header(title, description)

        panel = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )
        panel.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 35)
        )

        tk.Label(
            panel,
            text=title,
            font=("Arial", 20, "bold"),
            bg=self.WHITE,
            fg=self.ORANGE
        ).pack(pady=(100, 15))

        tk.Label(
            panel,
            text="This section will be implemented next.",
            font=("Arial", 12),
            bg=self.WHITE,
            fg=self.GRAY
        ).pack()


   

    def show_dashboard(self):

        self.clear_content()

        self.create_page_header(
            "Dashboard",
            "Welcome to DealForge Coupon Optimisation System"
        )

        welcome = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )
        welcome.pack(fill="x", padx=35, pady=10)

        tk.Label(
            welcome,
            text="Welcome to DealForge!",
            font=("Arial", 22, "bold"),
            bg=self.WHITE,
            fg=self.DARK
        ).pack(anchor="w", padx=30, pady=(25, 10))

        tk.Label(
            welcome,
            text=(
                "Manage coupons, compare discounts, "
                "optimise offers and complete customer checkouts."
            ),
            font=("Arial", 11),
            bg=self.WHITE,
            fg=self.GRAY,
            wraplength=700
        ).pack(anchor="w", padx=30, pady=(0, 25))

        cards_frame = tk.Frame(
            self.content,
            bg=self.BACKGROUND
        )
        cards_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        features = [
            (
                "Customers",
                "Manage customer information",
                self.show_customers
            ),
            (
                "Shopping Cart",
                "Add and manage products",
                self.show_cart
            ),
            (
                "Coupons",
                "Create and validate coupons",
                self.show_coupons
            ),
            (
                "Best Offer",
                "Compare coupons and find the highest discount",
                self.show_checkout
            ),
            (
                "Checkout",
                "Save orders and coupon usage",
                self.show_checkout
            ),
            (
                "Reports",
                "View usage and order reports",
                self.show_reports
            )
        ]

        for index, (title, description, command) in enumerate(features):

            row = index // 2
            column = index % 2

            card = tk.Frame(
                cards_frame,
                bg=self.WHITE,
                highlightbackground="#E5E5E5",
                highlightthickness=1,
                cursor="hand2"
            )

            card.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=10,
                pady=10
            )

            title_label = tk.Label(
                card,
                text=title,
                font=("Arial", 14, "bold"),
                bg=self.WHITE,
                fg=self.ORANGE,
                cursor="hand2"
            )
            title_label.pack(
                anchor="w",
                padx=20,
                pady=(20, 8)
            )

            description_label = tk.Label(
                card,
                text=description,
                font=("Arial", 10),
                bg=self.WHITE,
                fg=self.GRAY,
                cursor="hand2"
            )
            description_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 20)
            )

            # Make the entire card clickable
            for widget in (card, title_label, description_label):
                widget.bind(
                    "<Button-1>",
                    lambda event, page=command: page()
                )

            # Hover effect
            def on_enter(event, current_card=card):
                current_card.config(
                    highlightbackground=self.ORANGE
                )

            def on_leave(event, current_card=card):
                current_card.config(
                    highlightbackground="#E5E5E5"
                )

            for widget in (card, title_label, description_label):
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)

        for row in range(3):
            cards_frame.grid_rowconfigure(row, weight=1)



    def show_customers(self):

        self.clear_content()

        self.create_page_header(
            "Customer Management",
            "Add new customers and manage existing customer records"
        )

        form = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )
        form.pack(fill="x", padx=35, pady=10)

        tk.Label(
            form,
            text="Add New Customer",
            font=("Arial", 15, "bold"),
            bg=self.WHITE,
            fg=self.ORANGE
        ).pack(anchor="w", padx=20, pady=(20, 15))

        input_frame = tk.Frame(form, bg=self.WHITE)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(
            input_frame,
            text="Customer ID",
            bg=self.WHITE
        ).grid(row=0, column=0, sticky="w", padx=5)

        customer_id_entry = ttk.Entry(
            input_frame,
            width=25
        )
        customer_id_entry.grid(
            row=1, column=0, padx=5, pady=8
        )

        tk.Label(
            input_frame,
            text="Customer Name",
            bg=self.WHITE
        ).grid(row=0, column=1, sticky="w", padx=5)

        customer_name_entry = ttk.Entry(
            input_frame,
            width=30
        )
        customer_name_entry.grid(
            row=1, column=1, padx=5, pady=8
        )

        table_frame = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
        )

        tk.Label(
            table_frame,
            text="Registered Customers",
            font=("Arial", 15, "bold"),
            bg=self.WHITE,
            fg=self.DARK
        ).pack(anchor="w", padx=20, pady=15)

        tree = ttk.Treeview(
            table_frame,
            columns=("customer_id", "customer_name"),
            show="headings"
        )

        tree.heading("customer_id", text="Customer ID")
        tree.heading("customer_name", text="Customer Name")

        tree.column(
            "customer_id",
            width=200,
            anchor="center"
        )
        tree.column(
            "customer_name",
            width=350,
            anchor="w"
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        def load_customers():

            for item in tree.get_children():
                tree.delete(item)

            connection = get_connection()

            try:
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT customer_id, customer_name
                    FROM customers
                    ORDER BY customer_id
                """)

                customers = cursor.fetchall()

                for customer in customers:
                    tree.insert("", "end", values=customer)

            except sqlite3.Error as error:
                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

            finally:
                connection.close()

        def add_customer():

            customer_id = customer_id_entry.get().strip()
            customer_name = customer_name_entry.get().strip()

            if not customer_id:
                messagebox.showwarning(
                    "Invalid Input",
                    "Customer ID cannot be empty."
                )
                return

            if not customer_name:
                messagebox.showwarning(
                    "Invalid Input",
                    "Customer name cannot be empty."
                )
                return

            connection = get_connection()

            try:
                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO customers
                    (customer_id, customer_name)
                    VALUES (?, ?)
                """, (customer_id, customer_name))

                connection.commit()

                messagebox.showinfo(
                    "Success",
                    "Customer added successfully!"
                )

                customer_id_entry.delete(0, tk.END)
                customer_name_entry.delete(0, tk.END)

                load_customers()

            except sqlite3.IntegrityError:
                connection.rollback()

                messagebox.showerror(
                    "Duplicate Customer",
                    "This customer ID already exists."
                )

            except sqlite3.Error as error:
                connection.rollback()

                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

            finally:
                connection.close()

        add_button = tk.Button(
            input_frame,
            text="Add Customer",
            command=add_customer,
            bg=self.ORANGE,
            fg=self.WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )

        add_button.grid(row=1, column=2, padx=15)

        load_customers()

        
    
    def show_cart(self):

        self.clear_content()

        self.create_page_header(
            "Shopping Cart",
            "Add products and manage your shopping cart"
        )

        # Product entry form
        form = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )
        form.pack(fill="x", padx=35, pady=10)

        tk.Label(
            form,
            text="Add Product",
            font=("Arial", 15, "bold"),
            bg=self.WHITE,
            fg=self.ORANGE
        ).pack(anchor="w", padx=20, pady=15)

        input_frame = tk.Frame(form, bg=self.WHITE)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        fields = [
            ("Product Name", 0, 25),
            ("Category", 1, 20),
            ("Price (₹)", 2, 15),
            ("Quantity", 3, 10)
        ]

        entries = {}

        for label, column, width in fields:

            tk.Label(
                input_frame,
                text=label,
                bg=self.WHITE,
                font=("Arial", 10)
            ).grid(row=0, column=column, sticky="w", padx=5)

            entry = ttk.Entry(
                input_frame,
                width=width
            )

            entry.grid(
                row=1,
                column=column,
                padx=5,
                pady=8
            )

            entries[label] = entry

        # Cart table container
        table_frame = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
        )

        tk.Label(
            table_frame,
            text="Cart Items",
            font=("Arial", 15, "bold"),
            bg=self.WHITE,
            fg=self.DARK
        ).pack(anchor="w", padx=20, pady=15)

        # Cart table
        tree = ttk.Treeview(
            table_frame,
            columns=(
                "name",
                "category",
                "price",
                "quantity",
                "subtotal"
            ),
            show="headings"
        )

        headings = {
            "name": "Product Name",
            "category": "Category",
            "price": "Unit Price",
            "quantity": "Quantity",
            "subtotal": "Subtotal"
        }

        for column, heading in headings.items():
            tree.heading(column, text=heading)

        tree.column("name", width=180)
        tree.column("category", width=130)
        tree.column("price", width=120, anchor="center")
        tree.column("quantity", width=90, anchor="center")
        tree.column("subtotal", width=130, anchor="center")

        # Quantity update controls
        quantity_frame = tk.Frame(
            table_frame,
            bg=self.WHITE
        )
        quantity_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        tk.Label(
            quantity_frame,
            text="New Quantity:",
            bg=self.WHITE,
            font=("Arial", 10)
        ).pack(side="left", padx=(0, 5))

        quantity_entry = ttk.Entry(
            quantity_frame,
            width=10
        )
        quantity_entry.pack(side="left")

        # Total display
        total_label = tk.Label(
            table_frame,
            text="Cart Total: ₹0.00",
            font=("Arial", 16, "bold"),
            bg=self.WHITE,
            fg=self.ORANGE
        )

        total_label.pack(anchor="e", padx=25, pady=10)

        # Refresh cart
        def refresh_cart():

            for item in tree.get_children():
                tree.delete(item)

            for index, item in enumerate(self.cart):

                subtotal = item["price"] * item["quantity"]

                tree.insert(
                    "",
                    "end",
                    iid=str(index),
                    values=(
                        item["name"],
                        item["category"],
                        f"₹{item['price'] / 100:.2f}",
                        item["quantity"],
                        f"₹{subtotal / 100:.2f}"
                    )
                )

            success, message, total = calculate_cart_total(self.cart)

            if success:
                total_label.config(
                    text=f"Cart Total: ₹{total / 100:.2f}"
                )

        # Add product
        def add_product():

            name = entries["Product Name"].get().strip()
            category = entries["Category"].get().strip()
            price_text = entries["Price (₹)"].get().strip()
            quantity_text = entries["Quantity"].get().strip()

            if not price_text or not quantity_text:
                messagebox.showwarning(
                    "Invalid Input",
                    "Price and quantity are required."
                )
                return

            try:
                price_rupees = Decimal(price_text)
                quantity = int(quantity_text)

                if not price_rupees.is_finite() or price_rupees <= 0:
                    raise ValueError

                price_in_paise = price_rupees * 100

                if price_in_paise != price_in_paise.to_integral_value():
                    raise ValueError

                price_paise = int(price_in_paise)

            except (ValueError, InvalidOperation):
                messagebox.showerror(
                    "Invalid Input",
                    "Enter a valid price with up to 2 decimal places "
                    "and a whole-number quantity."
                )
                return

            success, message = add_item(
                self.cart,
                name,
                category,
                price_paise,
                quantity
            )

            if success:
                messagebox.showinfo("Success", message)

                for entry in entries.values():
                    entry.delete(0, tk.END)


                refresh_cart()

            else:
                messagebox.showerror("Error", message)

        # Remove selected product
        def remove_selected():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Selection Required",
                    "Please select a product to remove."
                )
                return

            index = int(selected[0])

            success, message = remove_item(
                self.cart,
                index
            )

            if success:
                refresh_cart()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

        # Update product quantity
        def change_quantity():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Selection Required",
                    "Please select a product first."
                )
                return

            new_quantity = quantity_entry.get().strip()

            try:
                quantity = int(new_quantity)
            except ValueError:
                messagebox.showerror(
                    "Invalid Quantity",
                    "Enter a valid whole number."
                )
                return

            index = int(selected[0])

            success, message = update_quantity(
                self.cart,
                index,
                quantity
            )

            if success:
                quantity_entry.delete(0, tk.END)
                refresh_cart()

                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

        # Add and remove buttons
        button_frame = tk.Frame(
            form,
            bg=self.WHITE
        )
        button_frame.pack(pady=(0, 15))

        tk.Button(
            button_frame,
            text="Add Product",
            command=add_product,
            bg=self.ORANGE,
            fg=self.WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(side="left", padx=8)

        tk.Button(
            button_frame,
            text="Remove Selected",
            command=remove_selected,
            bg="#D9534F",
            fg=self.WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(side="left", padx=8)

        # Update quantity button
        tk.Button(
            quantity_frame,
            text="Update Quantity",
            command=change_quantity,
            bg=self.DARK,
            fg=self.WHITE,
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2"
        ).pack(side="left", padx=10)

        # Display table after creating its controls
        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        refresh_cart()


    

    def show_coupons(self):

        
        from datetime import date,datetime
        from zoneinfo import ZoneInfo

        self.clear_content()

        self.create_page_header(
            "Coupons",
            "Create, view and manage discount coupons"
        )

        # Coupon creation form
        form = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )
        form.pack(fill="x", padx=35, pady=10)

        tk.Label(
            form,
            text="Create New Coupon",
            font=("Arial", 15, "bold"),
            bg=self.WHITE,
            fg=self.ORANGE
        ).pack(anchor="w", padx=20, pady=15)

        input_frame = tk.Frame(form, bg=self.WHITE)
        input_frame.pack(fill="x", padx=20, pady=5)

        fields = [
            ("Coupon Code", 0, 20),
            ("Discount Value", 1, 15),
            ("Minimum Cart (₹)", 2, 15),
            ("Maximum Discount (₹)", 3, 18),
            ("Expiry Date (YYYY-MM-DD)", 4, 25),
            ("Category", 5, 18)
        ]

        entries = {}

        for label, column, width in fields:

            tk.Label(
                input_frame,
                text=label,
                bg=self.WHITE,
                font=("Arial", 9)
            ).grid(row=0, column=column, sticky="w", padx=5)

            entry = ttk.Entry(
                input_frame,
                width=width
            )

            entry.grid(
                row=1,
                column=column,
                padx=5,
                pady=8
            )

            entries[label] = entry

        # Discount type selection
        type_frame = tk.Frame(form, bg=self.WHITE)
        type_frame.pack(anchor="w", padx=25, pady=10)

        tk.Label(
            type_frame,
            text="Discount Type:",
            bg=self.WHITE,
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=5)

        discount_type = tk.StringVar(value="percentage")

        ttk.Combobox(
            type_frame,
            textvariable=discount_type,
            values=("percentage", "flat"),
            state="readonly",
            width=15
        ).pack(side="left", padx=10)

        # Weekday restrictions
        weekday_frame = tk.Frame(form, bg=self.WHITE)
        weekday_frame.pack(anchor="w", padx=25, pady=10)

        tk.Label(
            weekday_frame,
            text="Allowed Weekdays:",
            bg=self.WHITE,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=5)

        weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        weekday_vars = {}

        checkbox_frame = tk.Frame(weekday_frame, bg=self.WHITE)
        checkbox_frame.pack(anchor="w")

        for weekday in weekdays:
            weekday_vars[weekday] = tk.BooleanVar(value=False)

            ttk.Checkbutton(
                checkbox_frame,
                text=weekday,
                variable=weekday_vars[weekday]
            ).pack(side="left", padx=5)

        # Time restrictions (IST)
        time_frame = tk.Frame(form, bg=self.WHITE)
        time_frame.pack(anchor="w", padx=25, pady=10)

        tk.Label(
            time_frame,
            text="Time Restrictions (IST):",
            bg=self.WHITE,
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=5)

        tk.Label(
            time_frame,
            text="Start Time (HH:MM):",
            bg=self.WHITE
        ).grid(row=1, column=0, padx=5, sticky="w")

        start_time_var = tk.StringVar()

        ttk.Entry(
            time_frame,
            textvariable=start_time_var,
            width=12
        ).grid(row=1, column=1, padx=5)

        tk.Label(
            time_frame,
            text="End Time (HH:MM):",
            bg=self.WHITE
        ).grid(row=1, column=2, padx=5, sticky="w")

        end_time_var = tk.StringVar()

        ttk.Entry(
            time_frame,
            textvariable=end_time_var,
            width=12
        ).grid(row=1, column=3, padx=5)

        tk.Label(
            time_frame,
            text="Leave both fields blank for an all-day coupon.",
            bg=self.WHITE,
            fg="gray",
            font=("Arial", 9)
        ).grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=5)

        # Existing coupons section
        table_frame = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
        )

        tk.Label(
            table_frame,
            text="Existing Coupons",
            font=("Arial", 15, "bold"),
            bg=self.WHITE,
            fg=self.DARK
        ).pack(anchor="w", padx=20, pady=15)

        columns = (
            "code",
            "type",
            "value",
            "minimum",
            "maximum",
            "expiry",
            "category",
            "weekdays",
            "time",
            "status"
        )

        
        # Container for the coupon table and scrollbars
        tree_container = tk.Frame(
            table_frame,
            bg=self.WHITE
        )

        tree_container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        # Configure container layout
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Existing coupons table
        tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings"
        )

        # Vertical scrollbar
        scrollbar = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=tree.yview
        )

        # Horizontal scrollbar
        horizontal_scrollbar = ttk.Scrollbar(
            tree_container,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )

        # Display table and scrollbars using grid
        tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        headings = {
            "code": "Coupon Code",
            "type": "Discount Type",
            "value": "Value",
            "minimum": "Min Cart",
            "maximum": "Max Discount",
            "expiry": "Expiry Date",
            "category": "Category",
            "weekdays": "Allowed Days",
            "time": "Valid Time (IST)",
            "status": "Status"
        }

        for column, heading in headings.items():
            tree.heading(column, text=heading)

        tree.column("code", width=110, anchor="center")
        tree.column("type", width=110, anchor="center")
        tree.column("value", width=80, anchor="center")
        tree.column("minimum", width=110, anchor="center")
        tree.column("maximum", width=120, anchor="center")
        tree.column("expiry", width=110, anchor="center")
        tree.column("category", width=110, anchor="center")
        tree.column("weekdays", width=190, anchor="center")
        tree.column("time", width=140, anchor="center")
        tree.column("status", width=90, anchor="center")

        # Refresh coupon list
        def refresh_coupons():

            for item in tree.get_children():
                tree.delete(item)

            connection = get_connection()

            try:
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT code, discount_type, discount_value,
                        min_cart_value, max_discount,
                        expiry_date, category, allowed_weekdays,
                        start_time, end_time, is_active
                    FROM coupons
                    ORDER BY coupon_id DESC
                """)

                coupons = cursor.fetchall()

                for coupon in coupons:

                    (
                        code, dtype, value, minimum, maximum, expiry,
                        category, allowed_weekdays, start_time, end_time, active
                    ) = coupon

                    if dtype == "percentage":
                        display_value = f"{value}%"
                    else:
                        display_value = f"₹{value / 100:.2f}"

                    minimum_display = f"₹{minimum / 100:.2f}"

                    maximum_display = (
                        f"₹{maximum / 100:.2f}"
                        if maximum is not None
                        else "No limit"
                    )

                    # Calculate actual coupon status
                    if active != 1:
                        status = "Inactive"

                    else:
                        try:
                            expiry_day = date.fromisoformat(expiry)

                            if datetime.now(ZoneInfo("Asia/Kolkata")).date() > expiry_day:
                                status = "Expired"
                            else:
                                status = "Active"

                        except (ValueError, TypeError):
                            status = "Invalid Date"

                    # Format weekday and time restrictions for display
                    if allowed_weekdays is None:
                        weekdays_display = "All days"
                    else:
                        weekdays_display = allowed_weekdays.replace(",", ", ")

                    if start_time is None and end_time is None:
                        time_display = "All day"
                    elif start_time is not None and end_time is not None:
                        time_display = f"{start_time} - {end_time}"
                    else:
                        time_display = "Invalid restriction"

                    tree.insert(
                        "",
                        "end",
                        values=(
                            code,
                            dtype.title(),
                            display_value,
                            minimum_display,
                            maximum_display,
                            expiry,
                            category.title(),
                            weekdays_display,
                            time_display,
                            status
                        )
                    )

            except sqlite3.Error as error:
                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

            finally:
                connection.close()

        # Create coupon
        def save_coupon():

            code = entries["Coupon Code"].get().strip()
            value_text = entries["Discount Value"].get().strip()
            minimum_text = entries["Minimum Cart (₹)"].get().strip()
            maximum_text = entries["Maximum Discount (₹)"].get().strip()
            expiry = entries["Expiry Date (YYYY-MM-DD)"].get().strip()
            category = entries["Category"].get().strip()

            start_time = start_time_var.get().strip()
            end_time = end_time_var.get().strip()

            if not start_time and not end_time:
                start_time = None
                end_time = None

            if not code or not value_text or not expiry or not category:
                messagebox.showwarning(
                    "Missing Information",
                    "Please fill in all required fields."
                )
                return

            try:
                value = int(value_text)
                minimum = int(minimum_text) if minimum_text else 0

                maximum = (
                    int(maximum_text)
                    if maximum_text
                    else None
                )

                if minimum < 0:
                    raise ValueError

                if maximum is not None and maximum <= 0:
                    raise ValueError

                if value <= 0:
                    raise ValueError

                if discount_type.get() == "percentage":
                    discount_value = value
                else:
                    discount_value = value * 100

                minimum_paise = minimum * 100

                maximum_paise = (
                    maximum * 100
                    if maximum is not None
                    else None
                )

            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Enter valid positive whole numbers for discount and rupee amounts. Minimum cart can be zero."
                )
                return

            # Collect selected weekdays
            selected_weekdays = [
                weekday
                for weekday, variable in weekday_vars.items()
                if variable.get()
            ]

            # No selection means the coupon is valid every day
            if not selected_weekdays:
                selected_weekdays = None

            # Create coupon with weekday and time restrictions
            success, message = create_coupon(
                code,
                discount_type.get(),
                discount_value,
                minimum_paise,
                maximum_paise,
                expiry,
                category,
                allowed_weekdays=selected_weekdays,
                start_time=start_time,
                end_time=end_time
            )

            if success:

                messagebox.showinfo("Success", message)

                for entry in entries.values():
                    entry.delete(0, tk.END)

                # Reset weekday checkboxes
                for variable in weekday_vars.values():
                    variable.set(False)

                # Reset time fields
                start_time_var.set("")
                end_time_var.set("")

                refresh_coupons()

            else:
                messagebox.showerror("Coupon Error", message)

        # Create button
        tk.Button(
            form,
            text="Create Coupon",
            command=save_coupon,
            bg=self.ORANGE,
            fg=self.WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=25,
            pady=9,
            cursor="hand2"
        ).pack(pady=15)

        refresh_coupons()



    def show_checkout(self):

        self.clear_content()

        # Main scrollable container
        checkout_container = tk.Frame(
            self.content,
            bg=self.BACKGROUND
        )
        checkout_container.pack(fill="both", expand=True)

        checkout_canvas = tk.Canvas(
            checkout_container,
            bg=self.BACKGROUND,
            highlightthickness=0
        )
        checkout_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        checkout_scrollbar = ttk.Scrollbar(
            checkout_container,
            orient="vertical",
            command=checkout_canvas.yview
        )
        checkout_scrollbar.pack(side="right", fill="y")

        checkout_canvas.configure(
            yscrollcommand=checkout_scrollbar.set
        )

        checkout_content = tk.Frame(
            checkout_canvas,
            bg=self.BACKGROUND
        )

        checkout_window = checkout_canvas.create_window(
            (0, 0),
            window=checkout_content,
            anchor="nw"
        )

        def update_scroll_region(event=None):
            checkout_canvas.configure(
                scrollregion=checkout_canvas.bbox("all")
            )

        def update_content_width(event):
            checkout_canvas.itemconfigure(
                checkout_window,
                width=event.width
            )

        checkout_content.bind(
            "<Configure>",
            update_scroll_region
        )

        checkout_canvas.bind(
            "<Configure>",
            update_content_width
        )

        # Mouse wheel and touchpad scrolling
        # A custom bindtag limits scrolling to widgets inside this checkout page.
        checkout_scroll_tag = f"DealForgeCheckoutScroll{id(checkout_canvas)}"

        def scroll_checkout(event):

            if event.num == 4:
                checkout_canvas.yview_scroll(-3, "units")

            elif event.num == 5:
                checkout_canvas.yview_scroll(3, "units")

            elif event.delta:
                if abs(event.delta) >= 120:
                    movement = int(-event.delta / 120)
                else:
                    movement = -1 if event.delta > 0 else 1

                checkout_canvas.yview_scroll(
                    movement * 3,
                    "units"
                )

            return "break"

        def install_checkout_scroll_bindings(widget):

            current_tags = widget.bindtags()

            if checkout_scroll_tag not in current_tags:
                widget.bindtags(
                    (current_tags[0], checkout_scroll_tag) + current_tags[1:]
                )

            for child in widget.winfo_children():
                install_checkout_scroll_bindings(child)

        def remove_checkout_scroll_bindings(event=None):

            for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                self.root.unbind_class(checkout_scroll_tag, sequence)

        self.root.bind_class(
            checkout_scroll_tag,
            "<MouseWheel>",
            scroll_checkout
        )
        self.root.bind_class(
            checkout_scroll_tag,
            "<Button-4>",
            scroll_checkout
        )
        self.root.bind_class(
            checkout_scroll_tag,
            "<Button-5>",
            scroll_checkout
        )

        checkout_container.bind(
            "<Destroy>",
            remove_checkout_scroll_bindings,
            add="+"
        )

        # Checkout heading
        header = tk.Frame(
            checkout_content,
            bg=self.BACKGROUND
        )
        header.pack(fill="x", padx=35, pady=(30, 20))

        tk.Label(
            header,
            text="Checkout",
            font=("Arial", 24, "bold"),
            bg=self.BACKGROUND,
            fg=self.DARK
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Apply the best coupon and complete your order",
            font=("Arial", 10),
            bg=self.BACKGROUND,
            fg=self.GRAY
        ).pack(anchor="w", pady=(5, 0))

        # Customer details
        form = tk.Frame(
            checkout_content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )
        form.pack(fill="x", padx=35, pady=10)

        tk.Label(
            form,
            text="Customer Details",
            font=("Arial", 15, "bold"),
            bg=self.WHITE,
            fg=self.ORANGE
        ).pack(anchor="w", padx=20, pady=(20, 15))

        input_frame = tk.Frame(
            form,
            bg=self.WHITE
        )
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(
            input_frame,
            text="Customer ID",
            bg=self.WHITE,
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="w", padx=5)

        customer_id_entry = ttk.Entry(
            input_frame,
            width=25
        )
        customer_id_entry.grid(
            row=1,
            column=0,
            padx=5,
            pady=8
        )

        tk.Label(
            input_frame,
            text="Coupon Codes",
            bg=self.WHITE,
            font=("Arial", 10)
        ).grid(row=0, column=1, sticky="w", padx=5)

        coupon_entry = ttk.Entry(
            input_frame,
            width=35
        )
        coupon_entry.grid(
            row=1,
            column=1,
            padx=5,
            pady=8
        )

        tk.Label(
            input_frame,
            text="Separate multiple codes with commas",
            bg=self.WHITE,
            fg=self.GRAY,
            font=("Arial", 9)
        ).grid(row=2, column=1, sticky="w", padx=5)

        # Order summary
        summary_frame = tk.Frame(
            checkout_content,
            bg=self.WHITE,
            highlightbackground="#E5E5E5",
            highlightthickness=1
        )
        summary_frame.pack(fill="x", padx=35, pady=15)

        tk.Label(
            summary_frame,
            text="Order Summary",
            font=("Arial", 15, "bold"),
            bg=self.WHITE,
            fg=self.DARK
        ).pack(anchor="w", padx=20, pady=15)

        cart_success, cart_message, cart_total = calculate_cart_total(
            self.cart
        )

        if not cart_success:
            cart_total = 0

        tk.Label(
            summary_frame,
            text=f"Cart Total: ₹{cart_total / 100:.2f}",
            font=("Arial", 13, "bold"),
            bg=self.WHITE,
            fg=self.DARK
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # Preview result container
        result_frame = tk.Frame(
            checkout_content,
            bg=self.BACKGROUND
        )
        result_frame.pack(
            fill="x",
            padx=35,
            pady=10
        )

        def clear_preview():

            for widget in result_frame.winfo_children():
                widget.destroy()

        def add_preview_section(title, color=None):

            section = tk.Frame(
                result_frame,
                bg=self.WHITE,
                highlightbackground="#E5E5E5",
                highlightthickness=1
            )
            section.pack(fill="x", pady=6)

            tk.Label(
                section,
                text=title,
                font=("Arial", 13, "bold"),
                bg=self.WHITE,
                fg=color or self.DARK
            ).pack(anchor="w", padx=20, pady=(15, 8))

            return section

        # Preview coupon
        def preview_coupon():

            customer_id = customer_id_entry.get().strip()
            coupon_text = coupon_entry.get().strip()

            clear_preview()

            if not customer_id:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a Customer ID."
                )
                return

            connection = get_connection()

            try:
                cursor = connection.cursor()

                cursor.execute(
                    "SELECT customer_id FROM customers WHERE customer_id = ?",
                    (customer_id,)
                )

                customer = cursor.fetchone()

            finally:
                connection.close()

            if customer is None:
                messagebox.showerror(
                    "Invalid Customer",
                    "Customer does not exist."
                )
                return

            if not self.cart:
                messagebox.showwarning(
                    "Empty Cart",
                    "Please add products to your cart before checkout."
                )
                return

            cart_success, cart_message, cart_total = calculate_cart_total(
                self.cart
            )

            if not cart_success:
                messagebox.showerror(
                    "Cart Error",
                    cart_message
                )
                return

            items_success, items_message, cart_items = (
                get_cart_items_for_validation(self.cart)
            )

            if not items_success:
                messagebox.showerror(
                    "Cart Error",
                    items_message
                )
                return

            coupon_codes = [
                code.strip().upper()
                for code in coupon_text.split(",")
                if code.strip()
            ]

            (
                best_coupons,
                discount,
                coupon_message,
                coupon_breakdown
            ) = find_best_coupon_combination(
                coupon_codes,
                customer_id,
                cart_items
            )

            final_amount = cart_total - discount

            # Preview heading
            tk.Label(
                result_frame,
                text="COUPON PREVIEW",
                font=("Arial", 18, "bold"),
                bg=self.BACKGROUND,
                fg=self.DARK
            ).pack(anchor="w", pady=(5, 12))

            # Applied coupons
            applied_section = add_preview_section(
                "Applied Coupons",
                "#218838"
            )

            if coupon_breakdown:

                for item in coupon_breakdown:

                    tk.Label(
                        applied_section,
                        text=(
                            f"{item['code']}     "
                            f"- ₹{item['discount'] / 100:.2f}"
                        ),
                        font=("Arial", 11),
                        bg=self.WHITE,
                        fg="#218838"
                    ).pack(anchor="w", padx=20, pady=3)

            else:

                tk.Label(
                    applied_section,
                    text="No coupons applied.",
                    font=("Arial", 10),
                    bg=self.WHITE,
                    fg=self.GRAY
                ).pack(anchor="w", padx=20, pady=3)

            # Parse coupon validation details
            valid_codes = set()
            rejected_codes = []

            for line in coupon_message.splitlines():

                line = line.strip()

                if ":" not in line:
                    continue

                code, reason = line.split(":", 1)

                code = code.strip().upper()
                reason = reason.strip()

                if code in coupon_codes:

                    if reason.lower() == "valid for stacking.":
                        valid_codes.add(code)

                    elif code not in best_coupons:
                        rejected_codes.append((code, reason))

            # Other valid coupons not selected
            other_valid = [
                code for code in valid_codes
                if code not in best_coupons
            ]

            if other_valid:

                valid_section = add_preview_section(
                    "Other Valid Coupons",
                    self.ORANGE
                )

                for code in other_valid:

                    tk.Label(
                        valid_section,
                        text=f"{code} was valid but was not selected.",
                        font=("Arial", 10),
                        bg=self.WHITE,
                        fg=self.TEXT
                    ).pack(anchor="w", padx=20, pady=3)

            # Rejected coupons
            if rejected_codes:

                rejected_section = add_preview_section(
                    "Rejected Coupons",
                    "#D9534F"
                )

                for code, reason in rejected_codes:

                    tk.Label(
                        rejected_section,
                        text=f"{code}  -  {reason}",
                        font=("Arial", 10),
                        bg=self.WHITE,
                        fg="#D9534F",
                        wraplength=750,
                        justify="left"
                    ).pack(anchor="w", padx=20, pady=4)

            # Discount summary
            discount_section = add_preview_section(
                "Discount Summary"
            )

            tk.Label(
                discount_section,
                text=f"Cart Total: ₹{cart_total / 100:.2f}",
                font=("Arial", 11),
                bg=self.WHITE,
                fg=self.DARK
            ).pack(anchor="w", padx=20, pady=4)

            tk.Label(
                discount_section,
                text=f"Total Discount: -₹{discount / 100:.2f}",
                font=("Arial", 13, "bold"),
                bg=self.WHITE,
                fg="#218838"
            ).pack(anchor="w", padx=20, pady=5)

            # Final payable amount
            final_section = tk.Frame(
                result_frame,
                bg=self.WHITE,
                highlightbackground=self.ORANGE,
                highlightthickness=2
            )
            final_section.pack(fill="x", pady=10)

            tk.Label(
                final_section,
                text="FINAL AMOUNT TO PAY",
                font=("Arial", 13, "bold"),
                bg=self.WHITE,
                fg=self.GRAY
            ).pack(anchor="w", padx=20, pady=(15, 5))

            tk.Label(
                final_section,
                text=f"₹{final_amount / 100:.2f}",
                font=("Arial", 24, "bold"),
                bg=self.WHITE,
                fg=self.ORANGE
            ).pack(anchor="w", padx=20, pady=(0, 15))

            tk.Label(
                result_frame,
                text="This is only a preview. No order has been placed.",
                font=("Arial", 10, "italic"),
                bg=self.BACKGROUND,
                fg=self.GRAY
            ).pack(anchor="w", pady=10)

            install_checkout_scroll_bindings(result_frame)
            update_scroll_region()

        # Complete checkout
        def complete_checkout():

            customer_id = customer_id_entry.get().strip()

            coupon_text = coupon_entry.get().strip()

            if not customer_id:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a Customer ID."
                )
                return

            success, message, result = checkout(
                customer_id,
                self.cart,
                [
                    code.strip().upper()
                    for code in coupon_text.split(",")
                    if code.strip()
                ]
            )

            if not success:
                messagebox.showerror(
                    "Checkout Failed",
                    message
                )
                return

            order_total = result["cart_total"] / 100
            discount = result["discount"] / 100
            final_amount = result["final_amount"] / 100

            individual_discounts = "\n".join(
                f"{item['code']}: ₹{item['discount'] / 100:.2f}"
                for item in result["coupon_discounts"]
            )

            order_details = (
                f"Order ID: {result['order_id']}\n"
                f"Customer ID: {result['customer_id']}\n"
                f"Cart Total: ₹{order_total:.2f}\n"
                f"Coupons Applied: {result['coupon_code'] or 'None'}\n"
                f"Discount: ₹{discount:.2f}\n"
                f"Final Amount: ₹{final_amount:.2f}\n\n"
                f"Individual Discounts:\n"
                f"{individual_discounts or 'No discounts applied.'}"
            )

            messagebox.showinfo(
                "Checkout Successful",
                "Your order has been completed successfully!\n\n"
                + order_details
            )

            self.cart.clear()

            self.show_checkout()

        # Buttons
        button_frame = tk.Frame(
            checkout_content,
            bg=self.BACKGROUND
        )
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Preview Coupon",
            command=preview_coupon,
            bg=self.DARK,
            fg=self.WHITE,
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=8)

        tk.Button(
            button_frame,
            text="Complete Checkout",
            command=complete_checkout,
            bg=self.ORANGE,
            fg=self.WHITE,
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=8)

        install_checkout_scroll_bindings(checkout_content)
        update_scroll_region()



    def show_reports(self):

        self.clear_content()

        self.create_page_header(
            "Reports Dashboard",
            "Monitor orders, coupon performance and customer activity"
        )

        # Summary cards
        summary_frame = tk.Frame(
            self.content,
            bg=self.BACKGROUND
        )
        summary_frame.pack(fill="x", padx=25, pady=15)

        def create_summary_card(parent, title, value, column):

            card = tk.Frame(
                parent,
                bg=self.WHITE,
                highlightbackground="#E5E5E5",
                highlightthickness=1
            )

            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=8,
                pady=5
            )

            tk.Label(
                card,
                text=title,
                font=("Arial", 11),
                bg=self.WHITE,
                fg=self.GRAY
            ).pack(pady=(18, 8))

            value_label = tk.Label(
                card,
                text=value,
                font=("Arial", 20, "bold"),
                bg=self.WHITE,
                fg=self.ORANGE
            )

            value_label.pack(pady=(0, 18))

            return value_label

        for column in range(3):
            summary_frame.grid_columnconfigure(
                column,
                weight=1
            )

        orders_label = create_summary_card(
            summary_frame, "Total Orders", "0", 0
        )

        coupons_label = create_summary_card(
            summary_frame, "Coupons Used", "0", 1
        )

        discounts_label = create_summary_card(
            summary_frame, "Total Discounts", "₹0.00", 2
        )

        # Reports notebook
        notebook_frame = tk.Frame(
            self.content,
            bg=self.WHITE
        )

        notebook_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
        )

        notebook = ttk.Notebook(notebook_frame)
        notebook.pack(fill="both", expand=True)

        # Helper function to create a treeview with scrollbar
        def create_scrollable_tree(parent, columns):

            table_frame = tk.Frame(
                parent,
                bg=self.WHITE
            )

            table_frame.pack(
                fill="both",
                expand=True,
                padx=15,
                pady=15
            )

            tree = ttk.Treeview(
                table_frame,
                columns=columns,
                show="headings"
            )

            scrollbar = ttk.Scrollbar(
                table_frame,
                orient="vertical",
                command=tree.yview
            )

            tree.configure(
                yscrollcommand=scrollbar.set
            )

            tree.pack(
                side="left",
                fill="both",
                expand=True
            )

            scrollbar.pack(
                side="right",
                fill="y"
            )

            return tree

        # Coupon usage tab
        coupon_tab = tk.Frame(
            notebook,
            bg=self.WHITE
        )

        notebook.add(coupon_tab, text="Coupon Usage")

        coupon_tree = create_scrollable_tree(
            coupon_tab,
            ("code", "count", "discount")
        )

        coupon_tree.heading("code", text="Coupon Code")
        coupon_tree.heading("count", text="Times Used")
        coupon_tree.heading("discount", text="Total Discount")

        coupon_tree.column("code", width=200, anchor="center")
        coupon_tree.column("count", width=150, anchor="center")
        coupon_tree.column("discount", width=200, anchor="center")

        # Customer usage tab
        customer_tab = tk.Frame(
            notebook,
            bg=self.WHITE
        )

        notebook.add(customer_tab, text="Customer Usage")

        customer_tree = create_scrollable_tree(
            customer_tab,
            ("id", "name", "count", "discount")
        )

        customer_tree.heading("id", text="Customer ID")
        customer_tree.heading("name", text="Customer Name")
        customer_tree.heading("count", text="Coupons Used")
        customer_tree.heading("discount", text="Total Discount")

        customer_tree.column("id", width=130, anchor="center")
        customer_tree.column("name", width=200, anchor="w")
        customer_tree.column("count", width=130, anchor="center")
        customer_tree.column("discount", width=180, anchor="center")

        # Order history tab
        order_tab = tk.Frame(
            notebook,
            bg=self.WHITE
        )

        notebook.add(order_tab, text="Order History")

        order_tree = create_scrollable_tree(
            order_tab,
            ("order", "customer", "total", "final", "date")
        )

        order_tree.heading("order", text="Order ID")
        order_tree.heading("customer", text="Customer ID")
        order_tree.heading("total", text="Cart Total")
        order_tree.heading("final", text="Final Amount")
        order_tree.heading("date", text="Order Date")

        order_tree.column("order", width=80, anchor="center")
        order_tree.column("customer", width=120, anchor="center")
        order_tree.column("total", width=130, anchor="center")
        order_tree.column("final", width=130, anchor="center")
        order_tree.column("date", width=180, anchor="center")

        # Refresh report data
        def refresh_reports():

            try:
                total_orders = get_total_orders()
                total_coupons = get_total_coupons_used()
                total_discounts = get_total_discounts()

                orders_label.config(
                    text=str(total_orders)
                )

                coupons_label.config(
                    text=str(total_coupons)
                )

                discounts_label.config(
                    text=f"₹{total_discounts / 100:.2f}"
                )

                # Refresh coupon report
                for item in coupon_tree.get_children():
                    coupon_tree.delete(item)

                for row in get_coupon_usage_report():

                    coupon_tree.insert(
                        "",
                        "end",
                        values=(
                            row[0],
                            row[1],
                            f"₹{row[2] / 100:.2f}"
                        )
                    )

                # Refresh customer report
                for item in customer_tree.get_children():
                    customer_tree.delete(item)

                for row in get_customer_usage_report():

                    customer_tree.insert(
                        "",
                        "end",
                        values=(
                            row[0],
                            row[1],
                            row[2],
                            f"₹{row[3] / 100:.2f}"
                        )
                    )

                # Refresh order history
                for item in order_tree.get_children():
                    order_tree.delete(item)

                for row in get_order_history():

                    order_tree.insert(
                        "",
                        "end",
                        values=(
                            row[0],
                            row[1],
                            f"₹{row[2] / 100:.2f}",
                            f"₹{row[3] / 100:.2f}",
                            row[4]
                        )
                    )

            except Exception as error:

                messagebox.showerror(
                    "Reports Error",
                    f"Unable to load reports:\n{error}"
                )

        # Refresh button
        refresh_button = tk.Button(
            self.content,
            text="Refresh Reports",
            command=refresh_reports,
            bg=self.ORANGE,
            fg=self.WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )

        refresh_button.pack(pady=10)

        refresh_reports()


if __name__ == "__main__":

    root = tk.Tk()

    app = DealForgeApp(root)

    root.mainloop()
