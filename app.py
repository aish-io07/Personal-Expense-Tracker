import sqlite3
from datetime import datetime

# ---------------- DATABASE ----------------

connection = sqlite3.connect("expenses.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
""")

connection.commit()


# ---------------- ADD EXPENSE ----------------

def add_expense():
    print("\n--- Add Expense ---")

    try:
        amount = float(input("Enter amount: ₹"))

        if amount <= 0:
            print("❌ Amount must be greater than 0.")
            return

        category = input("Enter category: ").strip()
        description = input("Enter description: ").strip()

        date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
        INSERT INTO expenses (amount, category, description, date)
        VALUES (?, ?, ?, ?)
        """, (amount, category, description, date))

        connection.commit()

        print("✅ Expense added successfully!")

    except ValueError:
        print("❌ Please enter a valid amount.")


# ---------------- VIEW EXPENSES ----------------

def view_expenses():
    print("\n--- All Expenses ---")

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    if not expenses:
        print("No expenses recorded yet.")
        return

    print("\nID | Amount | Category | Description | Date")
    print("-" * 65)

    for expense in expenses:
        print(
            f"{expense[0]} | ₹{expense[1]:.2f} | "
            f"{expense[2]} | {expense[3]} | {expense[4]}"
        )


# ---------------- TOTAL SPENDING ----------------

def show_total():
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    print(f"\n💰 Total spending: ₹{total:.2f}")


# ---------------- CATEGORY SUMMARY ----------------

def category_summary():
    print("\n--- Category-wise Spending ---")

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    ORDER BY SUM(amount) DESC
    """)

    categories = cursor.fetchall()

    if not categories:
        print("No expenses recorded yet.")
        return

    for category, amount in categories:
        print(f"📌 {category}: ₹{amount:.2f}")


# ---------------- HIGHEST EXPENSE ----------------

def highest_expense():
    print("\n--- Highest Expense ---")

    cursor.execute("""
    SELECT amount, category, description, date
    FROM expenses
    ORDER BY amount DESC
    LIMIT 1
    """)

    expense = cursor.fetchone()

    if expense is None:
        print("No expenses recorded yet.")
        return

    amount, category, description, date = expense

    print(f"💸 Amount: ₹{amount:.2f}")
    print(f"🏷️ Category: {category}")
    print(f"📝 Description: {description}")
    print(f"📅 Date: {date}")


# ---------------- MONTHLY SPENDING ----------------

def monthly_spending():
    current_month = datetime.now().strftime("%Y-%m")

    cursor.execute("""
    SELECT SUM(amount)
    FROM expenses
    WHERE date LIKE ?
    """, (current_month + "%",))

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    print(f"\n📅 Spending this month: ₹{total:.2f}")


# ---------------- BUDGET ----------------

def check_budget():
    try:
        budget = float(input("\nEnter your monthly budget: ₹"))

        current_month = datetime.now().strftime("%Y-%m")

        cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE date LIKE ?
        """, (current_month + "%",))

        spending = cursor.fetchone()[0]

        if spending is None:
            spending = 0

        remaining = budget - spending

        print(f"\n💵 Monthly Budget: ₹{budget:.2f}")
        print(f"💸 Spent: ₹{spending:.2f}")

        if remaining > 0:
            print(f"✅ Remaining: ₹{remaining:.2f}")

        elif remaining == 0:
            print("⚠️ You have reached your budget!")

        else:
            print(f"🚨 You are over budget by ₹{abs(remaining):.2f}")

    except ValueError:
        print("❌ Please enter a valid budget.")


# ---------------- MAIN MENU ----------------

def main():

    while True:

        print("\n")
        print("=" * 45)
        print("       💰 PERSONAL EXPENSE TRACKER")
        print("=" * 45)

        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Show Total Spending")
        print("4. Category-wise Summary")
        print("5. Show Highest Expense")
        print("6. Show Monthly Spending")
        print("7. Check Monthly Budget")
        print("8. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_expense()

        elif choice == "2":
            view_expenses()

        elif choice == "3":
            show_total()

        elif choice == "4":
            category_summary()

        elif choice == "5":
            highest_expense()

        elif choice == "6":
            monthly_spending()

        elif choice == "7":
            check_budget()

        elif choice == "8":
            print("\nThank you for using Personal Expense Tracker! 👋")
            break

        else:
            print("❌ Invalid choice. Please try again.")


# ---------------- START PROGRAM ----------------

main()

connection.close()
