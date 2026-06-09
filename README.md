# 💰 Multi-User Personal Finance Tracker & Analytics Hub

A premium, full-stack web application designed to track personal financial outflows, analyze daily spending velocities, and provide interactive data visualization. Built using a Python Flask backend and an optimized relational SQLite database, the system features a sleek, modern glassmorphism UI with real-time asynchronous data control mechanics.

## 🌟 Key Product Features

- **Encrypted Multi-User Authentication:** Secure registration and login gateway utilizing cryptographically hashed user credentials (`Werkzeug`). 
- **Isolated User Ledger Spaces:** Full data isolation across separate user accounts via SQL relational mapping strategies.
- **Dual-Engine Interactive Graphing:** Real-time spending distribution chart with a live front-end toggle switching between a modern Doughnut ring and a traditional Pie chart layout (`Chart.js`).
- **Color-Locked Data Filtering:** Dynamic category filters that isolate specific spending while retaining cohesive palette tracking for instant visual assessment.
- **Daily Spending Velocity Timeline:** Chronological historical bar chart tracking daily spending parameters across the active running month.
- **Premium Spreadsheet Data Stream:** Custom inline CSV data streaming component enabling one-click historical backups and current-month statement downloads optimized for Microsoft Excel.

## 🛠️ Tech Stack & Architecture

- **Backend Architecture:** Python 3, Flask Web Framework, SQLite Database, SQL Parameterization
- **Frontend Engine:** Semantic HTML5, Vanilla JavaScript (ES6+ Custom Data Filters), Modern CSS3 (Glassmorphism Core Theme)
- **Data Visualization Library:** Chart.js Engine (Doughnut, Pie, and Bar Configurations)
- **Security Utilities:** Werkzeug Password Security Hashing Modules (`scrypt`)

## 📦 System Directory Map

```text
├── app.py                # Main Flask Server Engine, SQL Controllers & Session Handlers
├── tracker.db            # Active SQLite Database (Auto-generated on launch)
├── requirements.txt      # Deployment Core Dependency Manifest
├── static/
│   └── style.css         # Signature Lavender/Midnight Glassmorphism Layout Framework
└── templates/
    ├── index.html        # Primary Analytics Dashboard & Core Graph Interfaces
    ├── expenses.html     # Interactive Transaction Ledger & Search Controls
    ├── login.html        # Authentication Gateway View
    ├── register.html     # Account Provisioning View
    ├── add.html          # Expense Recording Form
    └── edit.html         # Data Mutation/Correction Panel