# Inventory and Reorder Tracker

## Project Description

Inventory and Reorder Tracker is a beginner-friendly command-line application
for maintaining inventory, recording stock movements, and reviewing reports.
Inventory items are represented as Python objects and saved between runs using
CSV files.

## Objectives

- Keep item details and stock quantities organized by a unique item ID.
- Record stock received and stock sold or consumed.
- Identify items at or below their reorder levels.
- Preserve inventory and transaction history between program runs.
- Summarize inventory and consumption data and visualize it with charts.

## Features

- Add, display, and search inventory items.
- Reject duplicate item IDs and validate quantities and prices.
- Record stock-in and stock-out transactions without allowing negative stock.
- View transaction history and low-stock alerts.
- Save inventory and transactions to CSV files.
- Calculate inventory and transaction statistics with NumPy.
- Filter, sort, group, and report on inventory using Pandas.
- Display stock, category, valuation, monthly movement, and low-stock charts
  with Matplotlib.
- Handle missing or empty CSV files and skip malformed records where possible.

## Technologies Used

- Python
- CSV files for local data persistence
- NumPy for numerical statistics
- Pandas for table-based analytics and reports
- Matplotlib for charts

## Python Libraries

| Library | Purpose |
| --- | --- |
| `csv` (built in) | Reads and writes inventory and transaction CSV files. |
| `datetime` (built in) | Records the date and time of stock transactions. |
| `math` (built in) | Checks that prices are finite numbers. |
| `os` (built in) | Locates the CSV files beside the application. |
| NumPy (`numpy`) | Calculates totals, averages, minimums, maximums, and standard deviation. |
| Pandas (`pandas`) | Creates DataFrames and performs filtering, sorting, grouping, and reporting. |
| Matplotlib (`matplotlib`) | Displays inventory and transaction charts. |

## Installation Requirements

- Python 3.10 or later is recommended.
- `numpy`, `pandas`, and `matplotlib` must be installed.
- A graphical display is needed to view Matplotlib charts.

Install the required third-party libraries from a terminal:

```powershell
python -m pip install numpy pandas matplotlib
```

## How to Run

Open a terminal in the existing project folder and run:

```powershell
python main.py
```

On Windows, `py main.py` can be used if the `python` command is unavailable.
The application creates `inventory.csv` and `transactions.csv` beside
`main.py` when they are missing or empty.

## Main Menu

1. **Add a new item** — enter a unique whole-number ID, name, category,
   quantity, price, and reorder level.
2. **Display all items** — view inventory in a formatted table.
3. **Search item by ID** — view one item's details.
4. **Stock-in** — add a positive quantity to an existing item.
5. **Stock-out** — deduct a positive quantity when enough stock is available.
6. **View transaction history** — review saved stock-in and stock-out records.
7. **Check low-stock items** — list items at or below their reorder levels.
8. **Analytics & Reports** — open the analytics, reporting, and visualization
   submenu.
9. **Exit** — save the current inventory and close the application.

The analytics submenu includes NumPy inventory statistics, stock consumption
analysis, a sortable and filterable inventory DataFrame, category and valuation
reports, a monthly transaction report, and a Matplotlib visualization submenu.

## Item Class and OOP

The `Item` class represents one inventory item. Its attributes are `item_id`,
`name`, `category`, `quantity`, `price`, and `reorder_level`. The inventory is
a dictionary that maps each integer item ID to an `Item` object.

Each object also has methods for stock-in, stock-out, reorder checks, and
displaying its details. The `self` parameter refers to the current object;
for example, `self.quantity` accesses that item's quantity.

## CSV Persistence

`inventory.csv` stores one row per item with the fields `item_id`, `name`,
`category`, `quantity`, `price`, and `reorder_level`. When the application
starts, `csv.DictReader` reads the rows and the program converts numeric fields
back to integers or floats before creating `Item` objects.

`csv.DictWriter` saves the current inventory as a fresh snapshot after changes
and on exit. This prevents a save from duplicating inventory rows.
`transactions.csv` stores item ID, item name, transaction type, quantity, date,
and time. New successful transactions are appended so earlier history remains.

Both CSV files are local plain-text files. Keep backups if their contents are
important.

## NumPy and Pandas Analytics

NumPy arrays hold stock quantities, stock values, and transaction quantities
for numerical calculations such as sums, averages, minimums, maximums, and
standard deviation. Stock-out quantities alone are used as consumption.

Pandas DataFrames are constructed from copies of item attributes and
transaction records. They support sorting and category filtering, category
grouping, item-wise consumption totals, valuation summaries, and monthly
stock-in/stock-out totals. Invalid or missing transaction dates are excluded
from the monthly report; the saved transaction records are not changed.

## Matplotlib Visualizations

The visualization submenu generates charts from the current inventory and
transaction history:

- Stock quantity by item
- Total stock quantity by category
- Inventory value by item
- Monthly stock-in versus stock-out
- Current quantity compared with reorder level for low-stock items

Charts are displayed interactively and are not saved as image files.

## Project Limitations

- Data is stored locally in CSV files; there is no database, user account, or
  multi-user support.
- CSV files can be edited manually, so malformed values may be skipped when
  loading.
- The application has no automated test suite included.
- Charts require a graphical display backend.
- JSON export/import is not implemented in the current project.

## Future Scope

- Add automated unit tests and stronger validation for manually edited files.
- Add optional JSON import/export or scheduled backups.
- Add a graphical user interface or a database for larger inventories.
- Add user access controls and more advanced audit or reorder reports.
