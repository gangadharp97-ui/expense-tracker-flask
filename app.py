from flask import Flask, render_template, request, redirect, url_for, Response, session
import sqlite3
from datetime import datetime
import os
from collections import defaultdict
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'  # Required to run secure user login sessions

DB_FILE = "tracker.db"

# --------------------------------------------------------------------------
# DATABASE INITIALIZATION ENGINE
# --------------------------------------------------------------------------
def init_db():
    """Initializes the SQLite database and creates structural tracking tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # 2. Create Expenses Table linked to Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# Run database setup automatically on initialization
init_db()


# --------------------------------------------------------------------------
# SECURE ROUTE PROTECTION SHIELD
# --------------------------------------------------------------------------
def get_current_user():
    """Helper to fetch logged-in user ID from browser session context."""
    return session.get('user_id')


# --------------------------------------------------------------------------
# USER AUTHENTICATION CONTROLLERS
# --------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]
        
        if not username or not password:
            return "Username and Password cannot be empty!", 400
            
        hashed_password = generate_password_hash(password)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "That username is already taken! Please try another one.", 400
        finally:
            conn.close()
            
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user_record = cursor.fetchone()
        conn.close()
        
        if user_record and check_password_hash(user_record[1], password):
            session['user_id'] = user_record[0]
            session['username'] = username
            return redirect(url_for("index"))
        else:
            return "Invalid Username or Password!", 401
            
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --------------------------------------------------------------------------
# HOME PAGE (DASHBOARD)
# --------------------------------------------------------------------------
@app.route("/")
def index():
    user_id = get_current_user()
    if not user_id:
        return redirect(url_for("login"))

    total_expense = 0
    count = 0
    highest_expense = 0
    expenses_list = []
    category_totals = defaultdict(float)
    
    current_month_str = datetime.now().strftime("%Y-%m")
    daily_raw_map = defaultdict(float)

    # Fetch expenses belonging only to this logged-in account
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, amount, category, date FROM expenses WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        name, amt, cat, dt = row[0], float(row[1]), row[2].strip(), row[3].strip()
        
        total_expense += amt
        count += 1
        if amt > highest_expense:
            highest_expense = amt
        
        expenses_list.append({"name": name, "amount": amt, "category": cat, "date": dt})
        category_totals[cat] += amt
        
        if dt.startswith(current_month_str):
            daily_raw_map[dt] += amt

    sorted_days = sorted(daily_raw_map.keys())
    daily_amounts = [daily_raw_map[day] for day in sorted_days]
    
    daily_labels = []
    for day in sorted_days:
        try:
            daily_labels.append(datetime.strptime(day, "%Y-%m-%d").strftime("%d %b"))
        except ValueError:
            daily_labels.append(day)

    categories = list(category_totals.keys())
    values = list(category_totals.values())

    insight_msg = "Track your parameters live. Ready for analytical profiling."
    if total_expense > 10000:
        insight_msg = "Outflow alert: Volume parameters expanding. Review categories."

    return render_template(
        "index.html",
        total_expense=total_expense,
        count=count,
        highest_expense=highest_expense,
        categories=categories,
        values=values,
        expenses=expenses_list,
        insight=insight_msg,
        daily_labels=daily_labels,
        daily_amounts=daily_amounts,
        current_month=datetime.now().strftime("%B %Y")
    )


# --------------------------------------------------------------------------
# 🧠 SMART INSIGHTS
# --------------------------------------------------------------------------
@app.route("/insights")
def insights():
    user_id = get_current_user()
    if not user_id:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, amount, category, date FROM expenses WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    expenses = [{"name": r[0], "amount": float(r[1]), "category": r[2], "date": r[3]} for r in rows]

    total = sum(e["amount"] for e in expenses)
    count = len(expenses)
    avg = round(total / count, 2) if count else 0
    highest = max((e["amount"] for e in expenses), default=0)

    category_data = defaultdict(float)
    for e in expenses:
        category_data[e["category"]] += e["amount"]

    top_category = None
    top_amount = 0
    for cat, amt in category_data.items():
        if amt > top_amount:
            top_amount = amt
            top_category = cat

    insights_list = []
    if count == 0:
        insights_list.append("No expenses recorded yet.")
    else:
        insights_list.append(f"You have recorded {count} expenses totaling ₹{total:.2f}.")
        insights_list.append(f"Your average expense is ₹{avg:.2f}.")
        insights_list.append(f"Your highest single expense was ₹{highest:.2f}.")
        if top_category:
            insights_list.append(f"You spend the most on {top_category}, with total spending of ₹{top_amount:.2f}.")
    
    score = 100
    if avg > 3000: score -= 25
    elif avg > 1500: score -= 15
    if highest > avg * 3 and avg > 0: score -= 10
    score = max(score, 0)

    potential_saving = round(top_amount * 0.10, 2) if top_amount else 0

    monthly_data = defaultdict(float)
    for e in expenses:
        try:
            month = datetime.strptime(e["date"], "%Y-%m-%d").strftime("%b %Y")
            monthly_data[month] += e["amount"]
        except:
            continue

    months = list(monthly_data.keys())
    monthly_totals = list(monthly_data.values())
    recent_transactions = sorted(expenses, key=lambda x: x["date"], reverse=True)[:5]

    # Quick Local Fallbacks for User Settings Parameters
    monthly_budget = 20000
    if os.path.exists(f"budget_{user_id}.txt"):
        try:
            with open(f"budget_{user_id}.txt", "r") as f: monthly_budget = float(f.read())
        except: pass

    budget_used = round((total / monthly_budget) * 100, 1) if monthly_budget > 0 else 0
    remaining_budget = max(monthly_budget - total, 0)
    
    goal_amount = 50000
    if os.path.exists(f"goal_{user_id}.txt"):
        try:
            with open(f"goal_{user_id}.txt", "r") as f: goal_amount = float(f.read())
        except: pass

    saved_amount = max(monthly_budget - total, 0)
    goal_progress = min(round((saved_amount / goal_amount) * 100, 1) if goal_amount > 0 else 0, 100)
    remaining_goal = max(goal_amount - saved_amount, 0)

    forecast = round(avg * count, 2)
    risk = "Unknown"
    if monthly_budget > 0:
        if forecast > monthly_budget: risk = "High"
        elif forecast > monthly_budget * 0.8: risk = "Medium"
        else: risk = "Low"

    return render_template(
        "insights.html",
        insights=insights_list, total=total, count=count, avg=avg, highest=highest,
        top_category=top_category, top_amount=top_amount, score=score,
        potential_saving=potential_saving, months=months, monthly_totals=monthly_totals,
        recent_transactions=recent_transactions, monthly_budget=monthly_budget,
        budget_used=budget_used, remaining_budget=remaining_budget, forecast=forecast,
        risk=risk, goal_amount=goal_amount, saved_amount=saved_amount,
        goal_progress=goal_progress, remaining_goal=remaining_goal
    )


# --------------------------------------------------------------------------
# ADD EXPENSE
# --------------------------------------------------------------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    user_id = get_current_user()
    if not user_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, name, amount, category, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, amount, category, date)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add.html")


# --------------------------------------------------------------------------
# DELETE EXPENSE
# --------------------------------------------------------------------------
@app.route("/delete", methods=["GET", "POST"])
def delete():
    user_id = get_current_user()
    if not user_id:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if request.method == "POST":
        try:
            target_id = int(request.form["index"])
            # Ensure the row belongs to the current user before running deletion
            cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (target_id, user_id))
            conn.commit()
        except:
            pass
        return redirect(url_for("index"))

    cursor.execute("SELECT id, name, amount, category, date FROM expenses WHERE user_id = ?", (user_id,))
    user_rows = cursor.fetchall()
    conn.close()

    # Pass rows to the view layout
    display_rows = [[row[0], [row[1], row[2], row[3], row[4]]] for row in user_rows]

    return render_template("delete.html", rows=display_rows)


# --------------------------------------------------------------------------
# EXPENSES PAGE (INTERACTIVE LEDGER)
# --------------------------------------------------------------------------
@app.route("/expenses")
def expenses_page():
    user_id = get_current_user()
    if not user_id:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, amount, category, date FROM expenses WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    # Formatted explicitly to feed your JavaScript ledger filter script engine safely
    expenses_list = [[row[0], [row[1], row[2], row[3], row[4]]] for row in rows]
    categories = sorted(list(set(row[2].strip() for row in rows if len(row) >= 3)))

    return render_template("expenses.html", expenses=expenses_list, categories=categories)


# --------------------------------------------------------------------------
# EDIT EXPENSE
# --------------------------------------------------------------------------
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    user_id = get_current_user()
    if not user_id:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute(
            "UPDATE expenses SET name = ?, amount = ?, category = ? WHERE id = ? AND user_id = ?",
            (request.form["name"], float(request.form["amount"]), request.form["category"], index, user_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("expenses_page"))

    cursor.execute("SELECT name, amount, category, date FROM expenses WHERE id = ? AND user_id = ?", (index, user_id))
    expense = cursor.fetchone()
    conn.close()

    if not expense:
        return redirect(url_for("expenses_page"))

    return render_template("edit.html", expense=expense, index=index)


# --------------------------------------------------------------------------
# LEDGER DATA BACKUP UTILITY ENGINE (CSV EXPORTS)
# --------------------------------------------------------------------------
@app.route("/export-csv")
def export_csv():
    user_id = get_current_user()
    if not user_id: return redirect(url_for("login"))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, amount, category, date FROM expenses WHERE user_id = ?", (user_id,))
    expenses = cursor.fetchall()
    conn.close()

    def generate_download_stream():
        yield "Expense Name,Amount (₹),Category,Date Logged\n"
        for row in expenses:
            name = f'"{row[0]}"' if ',' in row[0] else row[0]
            yield f"{name},{row[1]},{row[2]},{row[3]}\n"

    current_date = datetime.now().strftime("%Y-%m-%d")
    return Response(
        generate_download_stream(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=Ledger_Export_{current_date}.csv"}
    )


@app.route("/export-monthly-csv")
def export_monthly_csv():
    user_id = get_current_user()
    if not user_id: return redirect(url_for("login"))

    current_month_str = datetime.now().strftime("%Y-%m")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, amount, category, date FROM expenses WHERE user_id = ? AND date LIKE ?", 
        (user_id, f"{current_month_str}%")
    )
    expenses = cursor.fetchall()
    conn.close()

    def generate_monthly_stream():
        yield "Expense Name,Amount (₹),Category,Date Logged\n"
        for row in expenses:
            name = f'"{row[0]}"' if ',' in row[0] else row[0]
            yield f"{name},{row[1]},{row[2]},{row[3]}\n"

    return Response(
        generate_monthly_stream(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=Statement_{current_month_str}.csv"}
    )


# --------------------------------------------------------------------------
# LEGACY FALLBACK STATIC ENDPOINTS (PRESERVED)
# --------------------------------------------------------------------------
@app.route("/upcoming")
def upcoming(): return render_template("upcoming.html", reminders=[])
@app.route("/add-reminder", methods=["GET", "POST"])
def add_reminder(): return redirect(url_for("upcoming"))
@app.route("/set-budget", methods=["POST"])
def set_budget(): return redirect(url_for("insights"))
@app.route("/set-goal", methods=["POST"])
def set_goal(): return redirect(url_for("insights"))


if __name__ == "__main__":
    app.run(debug=True)