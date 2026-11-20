"""A simple command-line inventory and reorder tracker."""

import csv
import math
import os
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
INVENTORY_FILE = os.path.join(PROJECT_DIRECTORY, "inventory.csv")
TRANSACTIONS_FILE = os.path.join(PROJECT_DIRECTORY, "transactions.csv")
INVENTORY_FIELDS = [
    "item_id",
    "name",
    "category",
    "quantity",
    "price",
    "reorder_level",
]
TRANSACTION_FIELDS = [
    "item_id",
    "item_name",
    "transaction_type",
    "quantity",
    "date",
    "time",
]
INVENTORY_REPORT_COLUMNS = [
    "Item ID",
    "Name",
    "Category",
    "Quantity",
    "Price",
    "Reorder Level",
    "Stock Value",
]
TRANSACTION_REPORT_COLUMNS = [
    "Item ID",
    "Item name",
    "Transaction type",
    "Quantity",
    "Date",
    "Time",
]
MONTHLY_REPORT_COLUMNS = [
    "Year",
    "Month",
    "Stock-in Quantity",
    "Stock-out Quantity",
]


class Item:
    """Represent one item and provide its basic stock operations."""

    def __init__(self, item_id, name, category, quantity, price, reorder_level):
        self.item_id = item_id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.price = price
        self.reorder_level = reorder_level

    def stock_in(self, quantity):
        """Add a positive whole-number quantity and report whether it succeeded."""
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            return False
        self.quantity += quantity
        return True

    def stock_out(self, quantity):
        """Remove stock only when quantity is valid and available."""
        if (
            not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity <= 0
            or quantity > self.quantity
        ):
            return False
        self.quantity -= quantity
        return True

    def needs_reorder(self):
        """Return whether the item has reached or fallen below its reorder level."""
        return self.quantity <= self.reorder_level

    def display_info(self):
        """Display this item's details in a readable format."""
        print(f"Item ID: {self.item_id}")
        print(f"Name: {self.name}")
        print(f"Category: {self.category}")
        print(f"Quantity: {self.quantity}")
        print(f"Unit price: {self.price:.2f}")
        print(f"Reorder level: {self.reorder_level}")


def get_non_empty_input(prompt):
    """Keep asking until the user enters non-empty text."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def get_item_id(prompt):
    """Ask for an integer item ID."""
    while True:
        value = input(prompt).strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid whole-number item ID.")


def get_non_negative_integer(prompt):
    """Ask for a whole number that is zero or greater."""
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
            if number >= 0:
                return number
            print("Please enter a number that is zero or greater.")
        except ValueError:
            print("Please enter a valid whole number.")


def get_positive_integer(prompt):
    """Ask for a whole number greater than zero."""
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
            if number > 0:
                return number
            print("Please enter a whole number greater than zero.")
        except ValueError:
            print("Please enter a valid whole number.")


def get_non_negative_price(prompt):
    """Ask for a finite price that is zero or greater."""
    while True:
        value = input(prompt).strip()
        try:
            price = float(value)
            if math.isfinite(price) and price >= 0:
                return price
            print("Please enter a finite price that is zero or greater.")
        except ValueError:
            print("Please enter a valid number for the price.")


def initialize_csv_files():
    """Create the CSV files with headers when they are missing or empty."""
    csv_files = [
        (INVENTORY_FILE, INVENTORY_FIELDS),
        (TRANSACTIONS_FILE, TRANSACTION_FIELDS),
    ]
    for file_path, fieldnames in csv_files:
        try:
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                with open(file_path, "w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
        except OSError as error:
            print(f"Could not initialize {os.path.basename(file_path)}: {error}")


def load_inventory():
    """Load valid inventory records and recreate their Item objects."""
    inventory = {}
    try:
        with open(INVENTORY_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                return inventory
            if not set(INVENTORY_FIELDS).issubset(reader.fieldnames):
                print("Inventory CSV has missing columns. It was not loaded.")
                return None

            for row in reader:
                try:
                    item_id = int(row["item_id"])
                    name = row["name"].strip()
                    category = row["category"].strip()
                    quantity = int(row["quantity"])
                    price = float(row["price"])
                    reorder_level = int(row["reorder_level"])
                    if (
                        not name
                        or not category
                        or quantity < 0
                        or not math.isfinite(price)
                        or price < 0
                        or reorder_level < 0
                    ):
                        raise ValueError("record contains invalid item values")
                    if item_id in inventory:
                        print(f"Skipping duplicate item ID {item_id} in inventory CSV.")
                        continue
                    inventory[item_id] = Item(
                        item_id, name, category, quantity, price, reorder_level
                    )
                except (AttributeError, TypeError, ValueError) as error:
                    print(f"Skipping malformed inventory record: {error}")
    except FileNotFoundError:
        return inventory
    except (OSError, UnicodeError, csv.Error) as error:
        print(f"Could not load inventory CSV: {error}")
        return None
    return inventory


def save_inventory(inventory):
    """Write the current inventory snapshot to the CSV file."""
    try:
        with open(INVENTORY_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=INVENTORY_FIELDS)
            writer.writeheader()
            for item in inventory.values():
                writer.writerow(
                    {
                        "item_id": item.item_id,
                        "name": item.name,
                        "category": item.category,
                        "quantity": item.quantity,
                        "price": item.price,
                        "reorder_level": item.reorder_level,
                    }
                )
    except (OSError, csv.Error) as error:
        print(f"Could not save inventory CSV: {error}")
        return False
    return True


def load_transactions():
    """Load valid transaction records from the CSV file."""
    transactions = []
    try:
        with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                return transactions
            if not set(TRANSACTION_FIELDS).issubset(reader.fieldnames):
                print("Transaction CSV has missing columns. It was not loaded.")
                return None

            for row in reader:
                try:
                    item_id = int(row["item_id"])
                    item_name = row["item_name"].strip()
                    transaction_type = row["transaction_type"].strip()
                    quantity = int(row["quantity"])
                    date = row["date"].strip()
                    time = row["time"].strip()
                    if (
                        not item_name
                        or transaction_type not in ("STOCK-IN", "STOCK-OUT")
                        or quantity <= 0
                        or not date
                        or not time
                    ):
                        raise ValueError("record contains invalid transaction values")
                    transactions.append(
                        {
                            "Item ID": item_id,
                            "Item name": item_name,
                            "Transaction type": transaction_type,
                            "Quantity": quantity,
                            "Date": date,
                            "Time": time,
                        }
                    )
                except (AttributeError, TypeError, ValueError) as error:
                    print(f"Skipping malformed transaction record: {error}")
    except FileNotFoundError:
        return transactions
    except (OSError, UnicodeError, csv.Error) as error:
        print(f"Could not load transaction CSV: {error}")
        return None
    return transactions


def save_transaction(transaction):
    """Append one transaction, writing its header only for an empty file."""
    try:
        file_is_empty = (
            not os.path.exists(TRANSACTIONS_FILE)
            or os.path.getsize(TRANSACTIONS_FILE) == 0
        )
        if not file_is_empty:
            with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                existing_header = next(reader, [])
                if existing_header != TRANSACTION_FIELDS:
                    print("Transaction CSV has an invalid header. Transaction was not saved.")
                    return False

        with open(TRANSACTIONS_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=TRANSACTION_FIELDS)
            if file_is_empty:
                writer.writeheader()
            writer.writerow(
                {
                    "item_id": transaction["Item ID"],
                    "item_name": transaction["Item name"],
                    "transaction_type": transaction["Transaction type"],
                    "quantity": transaction["Quantity"],
                    "date": transaction["Date"],
                    "time": transaction["Time"],
                }
            )
    except (OSError, UnicodeError, csv.Error) as error:
        print(f"Could not save transaction CSV: {error}")
        return False
    return True


def save_inventory_if_loaded(inventory, inventory_loaded):
    """Save only when startup loaded the existing inventory safely."""
    if inventory_loaded:
        save_inventory(inventory)
    else:
        print("Inventory CSV could not be loaded; this session was not saved.")


def create_transaction(item, transaction_type, quantity):
    """Create a transaction record with separate date and time fields."""
    now = datetime.now()
    return {
        "Item ID": item.item_id,
        "Item name": item.name,
        "Transaction type": transaction_type,
        "Quantity": quantity,
        "Date": now.strftime("%Y-%m-%d"),
        "Time": now.strftime("%H:%M:%S"),
    }


def create_inventory_dataframe(inventory):
    """Copy Item attributes into a Pandas DataFrame for reporting."""
    rows = [
        {
            "Item ID": item.item_id,
            "Name": item.name,
            "Category": item.category,
            "Quantity": item.quantity,
            "Price": item.price,
            "Reorder Level": item.reorder_level,
            "Stock Value": item.quantity * item.price,
        }
        for item in inventory.values()
    ]
    return pd.DataFrame(rows, columns=INVENTORY_REPORT_COLUMNS)


def create_transaction_dataframe(transactions):
    """Copy transaction records into a Pandas DataFrame."""
    rows = [
        {
            "Item ID": transaction.get("Item ID"),
            "Item name": transaction.get("Item name"),
            "Transaction type": transaction.get("Transaction type"),
            "Quantity": transaction.get("Quantity"),
            "Date": transaction.get("Date"),
            "Time": transaction.get("Time"),
        }
        for transaction in transactions
    ]
    return pd.DataFrame(rows, columns=TRANSACTION_REPORT_COLUMNS)


def get_transaction_quantity_array(transactions, transaction_type):
    """Create a NumPy array of valid quantities for one transaction type."""
    quantities = []
    for transaction in transactions:
        if transaction.get("Transaction type") != transaction_type:
            continue
        raw_quantity = transaction.get("Quantity")
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            continue
        if isinstance(raw_quantity, float) and not raw_quantity.is_integer():
            continue
        if quantity >= 0:
            quantities.append(quantity)
    return np.array(quantities, dtype=np.int64)


def display_inventory_statistics(inventory, transactions):
    """Use NumPy to calculate inventory and transaction statistics."""
    quantities = np.array(
        [item.quantity for item in inventory.values()],
        dtype=np.int64,
    )
    stock_values = np.array(
        [item.quantity * item.price for item in inventory.values()],
        dtype=float,
    )

    print("\nInventory statistics (NumPy)")
    print(f"Total inventory quantity: {int(np.sum(quantities))}")
    print(f"Total inventory value: {float(np.sum(stock_values)):.2f}")
    if quantities.size:
        print(f"Average quantity per item: {float(np.mean(quantities)):.2f}")
        print(f"Maximum stock quantity: {int(np.max(quantities))}")
        print(f"Minimum stock quantity: {int(np.min(quantities))}")
        print(f"Stock quantity standard deviation: {float(np.std(quantities)):.2f}")
    else:
        print("No inventory items are available for quantity statistics.")

    stock_in_quantities = get_transaction_quantity_array(
        transactions, "STOCK-IN"
    )
    stock_out_quantities = get_transaction_quantity_array(
        transactions, "STOCK-OUT"
    )
    print(f"Total stock-in quantity: {int(np.sum(stock_in_quantities))}")
    print(f"Total stock-out quantity: {int(np.sum(stock_out_quantities))}")
    if stock_out_quantities.size:
        print(
            "Average consumption per stock-out transaction: "
            f"{float(np.mean(stock_out_quantities)):.2f}"
        )
    else:
        print("Average consumption per stock-out transaction: no stock-out records.")


def display_stock_consumption_analysis(transactions):
    """Summarize only STOCK-OUT transactions with Pandas."""
    transaction_df = create_transaction_dataframe(transactions)
    stock_out_df = transaction_df.loc[
        transaction_df["Transaction type"] == "STOCK-OUT"
    ].copy()
    if stock_out_df.empty:
        print("No stock-out records are available for consumption analysis.")
        return pd.DataFrame(
            columns=["Item ID", "Item name", "Total Consumption"]
        )

    stock_out_df["Quantity"] = pd.to_numeric(
        stock_out_df["Quantity"], errors="coerce"
    )
    stock_out_df = stock_out_df.dropna(
        subset=["Item ID", "Item name", "Quantity"]
    )
    if stock_out_df.empty:
        print("Stock-out records do not contain valid item details and quantities.")
        return pd.DataFrame(
            columns=["Item ID", "Item name", "Total Consumption"]
        )

    item_consumption = (
        stock_out_df.groupby(["Item ID", "Item name"], as_index=False)["Quantity"]
        .sum()
        .rename(columns={"Quantity": "Total Consumption"})
    )
    total_consumed = int(stock_out_df["Quantity"].sum())
    average_per_transaction = float(stock_out_df["Quantity"].mean())

    print("\nStock consumption report (STOCK-OUT only)")
    print(f"Total quantity consumed: {total_consumed}")
    print(f"Average quantity per stock-out transaction: {average_per_transaction:.2f}")
    print("Item-wise total consumption:")
    print(item_consumption.to_string(index=False))

    most_consumed = item_consumption.loc[
        item_consumption["Total Consumption"].idxmax()
    ]
    least_consumed = item_consumption.loc[
        item_consumption["Total Consumption"].idxmin()
    ]
    print(
        "Most consumed item: "
        f'{most_consumed["Item name"]} '
        f'({int(most_consumed["Total Consumption"])} units)'
    )
    print(
        "Least consumed item with recorded consumption: "
        f'{least_consumed["Item name"]} '
        f'({int(least_consumed["Total Consumption"])} units)'
    )
    print("Items with no stock-out records are not included in item-wise consumption.")
    return item_consumption


def display_inventory_dataframe(inventory):
    """Display inventory as a sortable and filterable Pandas DataFrame."""
    inventory_df = create_inventory_dataframe(inventory)
    if inventory_df.empty:
        print("No inventory items are available for the DataFrame report.")
        return inventory_df

    category_filter = input("Filter by category (press Enter for all): ").strip()
    displayed_df = inventory_df
    if category_filter:
        displayed_df = inventory_df.loc[
            inventory_df["Category"].str.casefold() == category_filter.casefold()
        ]
        if displayed_df.empty:
            print(f"No items found in category '{category_filter}'.")
            return displayed_df

    print("\nSort by: 1. None  2. Quantity (high to low)  3. Price (high to low)  4. Name (A-Z)")
    sort_choice = input("Choose a sort option: ").strip()
    sort_columns = {
        "2": ("Quantity", False),
        "3": ("Price", False),
        "4": ("Name", True),
    }
    if sort_choice in sort_columns:
        column, ascending = sort_columns[sort_choice]
        displayed_df = displayed_df.sort_values(column, ascending=ascending)
    elif sort_choice not in ("1", ""):
        print("Invalid sort option. Displaying without sorting.")

    print("\nInventory DataFrame")
    print(displayed_df.to_string(index=False))

    low_stock_df = inventory_df.loc[
        inventory_df["Quantity"] <= inventory_df["Reorder Level"]
    ]
    print("\nItems at or below their reorder level:")
    if low_stock_df.empty:
        print("No items need reordering.")
    else:
        print(low_stock_df.to_string(index=False))

    maximum_quantity = inventory_df["Quantity"].max()
    minimum_quantity = inventory_df["Quantity"].min()
    print("\nHighest-stock item(s):")
    print(
        inventory_df.loc[inventory_df["Quantity"] == maximum_quantity].to_string(
            index=False
        )
    )
    print("Lowest-stock item(s):")
    print(
        inventory_df.loc[inventory_df["Quantity"] == minimum_quantity].to_string(
            index=False
        )
    )
    return displayed_df


def display_category_report(inventory):
    """Group inventory by category and rank categories by inventory value."""
    inventory_df = create_inventory_dataframe(inventory)
    if inventory_df.empty:
        print("No inventory items are available for the category report.")
        return pd.DataFrame()

    category_report = (
        inventory_df.groupby("Category")
        .agg(
            item_count=("Item ID", "count"),
            total_stock_quantity=("Quantity", "sum"),
            average_stock_per_item=("Quantity", "mean"),
            total_inventory_value=("Stock Value", "sum"),
        )
        .reset_index()
        .rename(
            columns={
                "item_count": "Item Count",
                "total_stock_quantity": "Total Stock Quantity",
                "average_stock_per_item": "Average Stock per Item",
                "total_inventory_value": "Total Inventory Value",
            }
        )
        .sort_values("Total Inventory Value", ascending=False)
    )
    print("\nCategory-wise report (ranked by inventory value)")
    print(category_report.to_string(index=False, formatters={
        "Average Stock per Item": "{:.2f}".format,
        "Total Inventory Value": "{:.2f}".format,
    }))
    return category_report


def display_inventory_valuation_report(inventory):
    """Display each item's stock value and the total inventory valuation."""
    inventory_df = create_inventory_dataframe(inventory)
    if inventory_df.empty:
        print("No inventory items are available for the valuation report.")
        return inventory_df

    valuation_df = inventory_df.sort_values("Stock Value", ascending=False)
    print("\nInventory valuation report (highest value first)")
    print(valuation_df.to_string(index=False))
    print(f"Total inventory valuation: {inventory_df['Stock Value'].sum():.2f}")
    return valuation_df


def create_monthly_transaction_summary(transactions):
    """Return monthly totals and the number of records that could not be used."""
    transaction_df = create_transaction_dataframe(transactions)
    if transaction_df.empty:
        return pd.DataFrame(columns=MONTHLY_REPORT_COLUMNS), 0

    transaction_df["Date"] = pd.to_datetime(
        transaction_df["Date"], errors="coerce"
    )
    transaction_df["Quantity"] = pd.to_numeric(
        transaction_df["Quantity"], errors="coerce"
    )
    valid_transactions = transaction_df.dropna(subset=["Date", "Quantity"]).copy()
    valid_transactions = valid_transactions.loc[
        valid_transactions["Transaction type"].isin(("STOCK-IN", "STOCK-OUT"))
    ]
    skipped_count = len(transaction_df) - len(valid_transactions)
    if valid_transactions.empty:
        return pd.DataFrame(columns=MONTHLY_REPORT_COLUMNS), skipped_count

    valid_transactions["Year"] = valid_transactions["Date"].dt.year
    valid_transactions["Month"] = valid_transactions["Date"].dt.month
    monthly_totals = (
        valid_transactions.groupby(["Year", "Month", "Transaction type"])["Quantity"]
        .sum()
        .unstack(fill_value=0)
        .reindex(columns=["STOCK-IN", "STOCK-OUT"], fill_value=0)
        .reset_index()
        .rename(
            columns={
                "STOCK-IN": "Stock-in Quantity",
                "STOCK-OUT": "Stock-out Quantity",
            }
        )
        .sort_values(["Year", "Month"])
    )
    return monthly_totals, skipped_count


def display_monthly_transaction_report(transactions):
    """Display grouped stock-in and stock-out totals by month."""
    monthly_totals, skipped_count = create_monthly_transaction_summary(transactions)
    if not transactions:
        print("No transactions are available for the monthly report.")
        return monthly_totals
    if skipped_count:
        print(
            f"Skipped {skipped_count} transaction(s) with invalid dates, "
            "quantities, or transaction types."
        )
    if monthly_totals.empty:
        print("No transactions have valid dates, quantities, and transaction types.")
        return monthly_totals

    print("\nMonthly transaction summary")
    print(monthly_totals.to_string(index=False))
    return monthly_totals


def display_figure(figure):
    """Show and close a Matplotlib figure."""
    figure.tight_layout()
    try:
        plt.show()
    finally:
        plt.close(figure)
    return figure


def show_stock_quantity_chart(inventory):
    """Plot stock quantities for all inventory items."""
    inventory_df = create_inventory_dataframe(inventory)
    if inventory_df.empty:
        print("No inventory items are available for the stock chart.")
        return None

    labels = (
        inventory_df["Item ID"].astype(str) + " - " + inventory_df["Name"]
    )
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(labels, inventory_df["Quantity"], color="steelblue")
    axis.set_title("Stock Quantity by Item")
    axis.set_xlabel("Item")
    axis.set_ylabel("Quantity in stock")
    axis.tick_params(axis="x", labelrotation=45)
    for label in axis.get_xticklabels():
        label.set_ha("right")
    return display_figure(figure)


def show_category_distribution_chart(inventory):
    """Plot total stock quantity in each category."""
    inventory_df = create_inventory_dataframe(inventory)
    if inventory_df.empty:
        print("No inventory items are available for the category chart.")
        return None

    category_totals = inventory_df.groupby("Category")["Quantity"].sum()
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.bar(category_totals.index, category_totals.values, color="seagreen")
    axis.set_title("Inventory Quantity by Category")
    axis.set_xlabel("Category")
    axis.set_ylabel("Total stock quantity")
    axis.tick_params(axis="x", labelrotation=30)
    for label in axis.get_xticklabels():
        label.set_ha("right")
    return display_figure(figure)


def show_inventory_valuation_chart(inventory):
    """Plot the total stock value of each inventory item."""
    inventory_df = create_inventory_dataframe(inventory)
    if inventory_df.empty:
        print("No inventory items are available for the valuation chart.")
        return None

    labels = (
        inventory_df["Item ID"].astype(str) + " - " + inventory_df["Name"]
    )
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(labels, inventory_df["Stock Value"], color="darkorange")
    axis.set_title("Inventory Valuation by Item")
    axis.set_xlabel("Item")
    axis.set_ylabel("Stock value")
    axis.tick_params(axis="x", labelrotation=45)
    for label in axis.get_xticklabels():
        label.set_ha("right")
    return display_figure(figure)


def show_monthly_transaction_chart(transactions):
    """Compare monthly stock-in and stock-out quantities."""
    monthly_totals, skipped_count = create_monthly_transaction_summary(transactions)
    if skipped_count:
        print(f"Skipped {skipped_count} transaction(s) with invalid report data.")
    if monthly_totals.empty:
        print("No valid monthly transaction data is available for the chart.")
        return None

    positions = np.arange(len(monthly_totals))
    bar_width = 0.35
    month_labels = [
        f"{int(year)}-{int(month):02d}"
        for year, month in zip(monthly_totals["Year"], monthly_totals["Month"])
    ]
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.bar(
        positions - bar_width / 2,
        monthly_totals["Stock-in Quantity"],
        bar_width,
        label="Stock-in",
        color="seagreen",
    )
    axis.bar(
        positions + bar_width / 2,
        monthly_totals["Stock-out Quantity"],
        bar_width,
        label="Stock-out",
        color="indianred",
    )
    axis.set_title("Monthly Stock-in vs. Stock-out")
    axis.set_xlabel("Month")
    axis.set_ylabel("Quantity")
    axis.set_xticks(positions, month_labels)
    axis.legend()
    return display_figure(figure)


def show_low_stock_chart(inventory):
    """Compare current and reorder quantities for items needing restock."""
    inventory_df = create_inventory_dataframe(inventory)
    low_stock_df = inventory_df.loc[
        inventory_df["Quantity"] <= inventory_df["Reorder Level"]
    ]
    if low_stock_df.empty:
        print("No low-stock items are available to chart.")
        return None

    labels = low_stock_df["Item ID"].astype(str) + " - " + low_stock_df["Name"]
    positions = np.arange(len(low_stock_df))
    bar_width = 0.35
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.bar(
        positions - bar_width / 2,
        low_stock_df["Quantity"],
        bar_width,
        label="Current quantity",
        color="steelblue",
    )
    axis.bar(
        positions + bar_width / 2,
        low_stock_df["Reorder Level"],
        bar_width,
        label="Reorder level",
        color="goldenrod",
    )
    axis.set_title("Low-stock Items and Reorder Levels")
    axis.set_xlabel("Item")
    axis.set_ylabel("Quantity")
    axis.set_xticks(positions, labels)
    axis.tick_params(axis="x", labelrotation=45)
    for label in axis.get_xticklabels():
        label.set_ha("right")
    axis.legend()
    return display_figure(figure)


def display_visualization_menu():
    """Show the available Matplotlib charts."""
    print("\nMatplotlib Visualizations")
    print("1. Stock quantity by item")
    print("2. Inventory quantity by category")
    print("3. Inventory valuation by item")
    print("4. Monthly stock-in vs. stock-out")
    print("5. Low-stock items and reorder levels")
    print("6. Return to analytics menu")


def run_visualization_menu(inventory, transactions):
    """Run Matplotlib charts until the user returns to analytics."""
    while True:
        display_visualization_menu()
        choice = input("Choose a visualization option (1-6): ").strip()

        if choice == "1":
            show_stock_quantity_chart(inventory)
        elif choice == "2":
            show_category_distribution_chart(inventory)
        elif choice == "3":
            show_inventory_valuation_chart(inventory)
        elif choice == "4":
            show_monthly_transaction_chart(transactions)
        elif choice == "5":
            show_low_stock_chart(inventory)
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please select an option from 1 to 6.")


def display_analytics_menu():
    """Show the available analytics and reporting operations."""
    print("\nInventory Analytics and Reporting System")
    print("1. Inventory statistics (NumPy)")
    print("2. Stock consumption analysis")
    print("3. Inventory DataFrame (Pandas)")
    print("4. Category-wise report")
    print("5. Inventory valuation report")
    print("6. Monthly transaction report")
    print("7. Matplotlib visualizations")
    print("8. Return to main menu")


def run_analytics_menu(inventory, transactions):
    """Run analytics reports until the user returns to the main menu."""
    while True:
        display_analytics_menu()
        choice = input("Choose an analytics option (1-8): ").strip()

        if choice == "1":
            display_inventory_statistics(inventory, transactions)
        elif choice == "2":
            display_stock_consumption_analysis(transactions)
        elif choice == "3":
            display_inventory_dataframe(inventory)
        elif choice == "4":
            display_category_report(inventory)
        elif choice == "5":
            display_inventory_valuation_report(inventory)
        elif choice == "6":
            display_monthly_transaction_report(transactions)
        elif choice == "7":
            run_visualization_menu(inventory, transactions)
        elif choice == "8":
            break
        else:
            print("Invalid choice. Please select an option from 1 to 8.")


def add_item(inventory, inventory_loaded=True):
    """Collect item details and add a new item to the inventory."""
    item_id = get_item_id("Enter item ID: ")
    if item_id in inventory:
        print("That item ID already exists. Item IDs must be unique.")
        return

    name = get_non_empty_input("Enter item name: ")
    category = get_non_empty_input("Enter category: ")
    quantity = get_non_negative_integer("Enter quantity: ")
    price = get_non_negative_price("Enter unit price: ")
    reorder_level = get_non_negative_integer("Enter reorder level: ")
    inventory[item_id] = Item(item_id, name, category, quantity, price, reorder_level)
    save_inventory_if_loaded(inventory, inventory_loaded)
    print("Item added successfully.")


def display_items(inventory):
    """Display every inventory item in a formatted table."""
    if not inventory:
        print("The inventory is empty.")
        return

    headers = ["Item ID", "Name", "Category", "Quantity", "Unit price", "Reorder level"]
    rows = []
    for item_id, item in inventory.items():
        rows.append(
            [
                str(item_id),
                item.name,
                item.category,
                str(item.quantity),
                f"{item.price:.2f}",
                str(item.reorder_level),
            ]
        )

    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    print(" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def search_item(inventory):
    """Find and display an item using its unique ID."""
    item_id = get_item_id("Enter the item ID to search for: ")
    item = inventory.get(item_id)
    if item is None:
        print("No item was found with that ID.")
        return

    item.display_info()


def stock_in(inventory, transactions, inventory_loaded=True):
    """Add received stock to an existing item and record the transaction."""
    item_id = get_item_id("Enter the item ID receiving stock: ")
    item = inventory.get(item_id)
    if item is None:
        print("No item was found with that ID. Stock-in was not completed.")
        return

    quantity_added = get_positive_integer("Enter the quantity received: ")
    previous_quantity = item.quantity
    if not item.stock_in(quantity_added):
        print("Stock-in quantity was invalid. No stock was changed.")
        return
    print(f"Previous quantity: {previous_quantity}")
    print(f"Added quantity: {quantity_added}")
    print(f"Updated quantity: {item.quantity}")

    save_inventory_if_loaded(inventory, inventory_loaded)
    transaction = create_transaction(item, "STOCK-IN", quantity_added)
    transactions.append(transaction)
    save_transaction(transaction)


def stock_out(inventory, transactions, inventory_loaded=True):
    """Remove sold or consumed stock when enough quantity is available."""
    item_id = get_item_id("Enter the item ID losing stock: ")
    item = inventory.get(item_id)
    if item is None:
        print("No item was found with that ID. Stock-out was not completed.")
        return

    quantity_deducted = get_positive_integer("Enter the quantity sold or consumed: ")
    previous_quantity = item.quantity
    if not item.stock_out(quantity_deducted):
        print(
            f"Insufficient stock: only {previous_quantity} available. "
            "Stock-out was cancelled."
        )
        return

    print(f"Previous quantity: {previous_quantity}")
    print(f"Deducted quantity: {quantity_deducted}")
    print(f"Remaining quantity: {item.quantity}")

    save_inventory_if_loaded(inventory, inventory_loaded)
    transaction = create_transaction(item, "STOCK-OUT", quantity_deducted)
    transactions.append(transaction)
    save_transaction(transaction)


def display_transaction_history(transactions):
    """Display all successful stock transactions in a formatted table."""
    if not transactions:
        print("There are no stock transactions yet.")
        return

    headers = [
        "Item ID",
        "Item name",
        "Transaction type",
        "Quantity",
        "Date",
        "Time",
    ]
    rows = [
        [str(transaction[header]) for header in headers]
        for transaction in transactions
    ]
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    print(" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def display_low_stock_items(inventory):
    """Display items at or below their reorder levels."""
    low_stock_items = {
        item_id: item for item_id, item in inventory.items() if item.needs_reorder()
    }
    if not low_stock_items:
        print("No items need reordering.")
        return

    print("Items at or below their reorder level:")
    display_items(low_stock_items)


def display_menu():
    """Show the available menu actions."""
    print("\nInventory and Reorder Tracker")
    print("1. Add a new item")
    print("2. Display all items")
    print("3. Search item by ID")
    print("4. Stock-in")
    print("5. Stock-out")
    print("6. View transaction history")
    print("7. Check low-stock items")
    print("8. Analytics & Reports")
    print("9. Exit")


def main():
    """Run the menu until the user chooses to exit."""
    initialize_csv_files()
    loaded_inventory = load_inventory()
    inventory_loaded = loaded_inventory is not None
    inventory = loaded_inventory if inventory_loaded else {}

    loaded_transactions = load_transactions()
    transactions = loaded_transactions if loaded_transactions is not None else []

    while True:
        display_menu()
        choice = input("Choose an option (1-9): ").strip()

        if choice == "1":
            add_item(inventory, inventory_loaded)
        elif choice == "2":
            display_items(inventory)
        elif choice == "3":
            search_item(inventory)
        elif choice == "4":
            stock_in(inventory, transactions, inventory_loaded)
        elif choice == "5":
            stock_out(inventory, transactions, inventory_loaded)
        elif choice == "6":
            display_transaction_history(transactions)
        elif choice == "7":
            display_low_stock_items(inventory)
        elif choice == "8":
            run_analytics_menu(inventory, transactions)
        elif choice == "9":
            save_inventory_if_loaded(inventory, inventory_loaded)
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select an option from 1 to 9.")


if __name__ == "__main__":
    main()
