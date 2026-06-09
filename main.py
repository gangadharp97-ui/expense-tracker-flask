import csv
import matplotlib.pyplot as plt
from datetime import datetime
import os

# -----------------------
# ADD EXPENSE
# -----------------------
def add_expense():
    expense = input("Enter Expense Name: ").strip()
    try:
        amount = float(input("Enter Amount: "))
    except ValueError:
        print("Invalid amount! Please enter a valid number.")
        return

    category = input("Enter Category: ").strip()
    date = datetime.now().strftime("%Y-%m-%d")

    with open("expenses.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([expense, amount, category, date])

    print("Expense Added Successfully!")


# -----------------------
# VIEW EXPENSES
# -----------------------
def view_expenses():
    try:
        with open("expenses.csv", "r") as file:
            reader = csv.reader(file)

            print("\n--- Expense List ---")
            print(f"{'Name':<18} | {'Amount':<10} | {'Category':<15} | {'Date':<10}")
            print("-" * 65)

            for row in reader:
                if len(row) == 4:
                    print(f"{row[0]:<18} | ₹{float(row[1]):<9.2f} | {row[2]:<15} | {row[3]:<10}")

    except FileNotFoundError:
        print("No expenses found. Write an expense entry first.")


# -----------------------
# TOTAL SPENDING OVERVIEW
# -----------------------
def show_total():
    total = 0
    try:
        with open("expenses.csv", "r") as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row) == 4:
                    try:
                        total += float(row[1])
                    except ValueError:
                        continue

        print(f"\nTotal Spending: ₹{total:.2f}")

    except FileNotFoundError:
        print("No expenses file found.")


# -----------------------
# CATEGORY SUMMARY
# -----------------------
def category_summary():
    summary = {}
    try:
        with open("expenses.csv", "r") as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row) == 4:
                    try:
                        category = row[2].strip()
                        amount = float(row[1].strip())
                        summary[category] = summary.get(category, 0) + amount
                    except ValueError:
                        continue

        print("\n--- Category-wise Spending ---")
        if not summary:
            print("No data parameters processed.")
        for k, v in summary.items():
            print(f"{k} → ₹{v:.2f}")

    except FileNotFoundError:
        print("No expense file found.")


# -----------------------
# DELETE EXPENSE row
# -----------------------
def delete_expense():
    try:
        if not os.path.exists("expenses.csv"):
            print("No expenses to delete.")
            return

        with open("expenses.csv", "r") as file:
            reader = list(csv.reader(file))

        # Filter out invalid structural lines
        valid_rows = [row for row in reader if len(row) == 4]

        if not valid_rows:
            print("No valid expense targets found to delete.")
            return

        print("\n--- Current Ledger Records ---")
        for i, row in enumerate(valid_rows):
            print(f"{i}. {row[0]} | ₹{float(row[1]):.2f} | {row[2]} ({row[3]})")

        try:
            index = int(input("\nEnter index to delete: "))
        except ValueError:
            print("Please enter a valid structural row index number.")
            return

        if index < 0 or index >= len(valid_rows):
            print("Invalid index selection range.")
            return

        removed = valid_rows.pop(index)

        with open("expenses.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(valid_rows)

        print(f"Successfully Deleted Account Action: {removed[0]}")

    except FileNotFoundError:
        print("No expenses file found.")


# -----------------------
# MONTHLY FILTRATION RECORD
# -----------------------
def monthly_summary():
    month = input("Enter month (YYYY-MM): ").strip()
    total = 0

    try:
        with open("expenses.csv", "r") as file:
            reader = csv.reader(file)

            print(f"\n--- Expenses for {month} ---")
            print(f"{'Name':<18} | {'Amount':<10} | {'Category':<15}")
            print("-" * 50)

            found_any = False
            for row in reader:
                if len(row) == 4:
                    if row[3].startswith(month):
                        print(f"{row[0]:<18} | ₹{float(row[1]):<9.2f} | {row[2]:<15}")
                        total += float(row[1])
                        found_any = True

            if not found_any:
                print("No records matched this target month parameter.")

        print(f"\nTotal Outflow for {month}: ₹{total:.2f}")

    except FileNotFoundError:
        print("No metrics data found.")


# -----------------------
# LOCAL MATPLOTLIB ENGINE
# -----------------------
def show_graph():
    summary = {}
    try:
        with open("expenses.csv", "r") as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row) == 4:
                    try:
                        category = row[2].strip()
                        amount = float(row[1])
                        summary[category] = summary.get(category, 0) + amount
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("Cannot assemble metrics map: expenses.csv file does not exist yet.")
        return

    if not summary:
        print("No structural database markers to present visually.")
        return

    categories = list(summary.keys())
    values = list(summary.values())

    # Styling updates for native desktop chart popup window
    plt.figure(figsize=(8, 5))
    plt.bar(categories, values, color='#8b5cf6', edgecolor='#7c3aed', alpha=0.85)
    plt.title("Expense Category Breakdown (Terminal Engine)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Classified Category Type", fontsize=11, labelpad=10)
    plt.ylabel("Accumulated Outflow Amount (₹)", fontsize=11, labelpad=10)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()


# -----------------------
# RUN ENTRY POINT CONTROLLER
# -----------------------
if __name__ == "__main__":
    while True:
        print("\n=== EXPENSE TRACKER TERMINAL ENGINE ===")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Show Total Spending")
        print("4. Category Summary")
        print("5. Delete Expense")
        print("6. Monthly Summary")
        print("7. Show Graph")
        print("8. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_total()
        elif choice == "4":
            category_summary()
        elif choice == "5":
            delete_expense()
        elif choice == "6":
            monthly_summary()
        elif choice == "7":
            show_graph()
        elif choice == "8":
            print("System down. Goodbye!")
            break
        else:
            print("Invalid selection boundary parameter. Try again.")