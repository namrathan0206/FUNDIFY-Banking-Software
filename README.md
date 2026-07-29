# 🏦 Fundify - Professional Banking Software

> A secure, full-stack, and fully responsive financial management dashboard built with Python, Flask, and Vanilla Web Technologies. Designed to simulate a modern, high-performance FinTech environment.

![Fundify App](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Testing-yellow)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
<img width="1792" height="938" alt="Screenshot 2026-07-29 215227" src="https://github.com/user-attachments/assets/f3153e63-0756-41e6-b60b-d25c4dcceaa8" />

---

## 📖 Project Overview
**Fundify** is a comprehensive banking portal developed as a major Software Development Life Cycle (SDLC) project. It bridges the gap between legacy banking systems and modern neo-banks by providing a seamless, Single Page Application (SPA) experience. 

The system features a robust backend architecture with an auto-initializing database, mathematically encrypted authentication, and a dynamic frontend that requires zero heavy JavaScript frameworks (like React or Angular) to achieve high-end interactivity.

---

## ✨ Core Features & Modules

### 🛡️ 1. Security & Backend Architecture
*   **Cryptographic Authentication:** Passwords are mathematically hashed using `Werkzeug` (PBKDF2/Bcrypt). Plain-text passwords are never stored or exposed.
*   **Auto-Initializing Database:** The backend dynamically checks for existing database schemas on launch. If missing, it safely generates the `fundify.db` SQLite file and injects default admin credentials.
*   **Bulletproof API Validation:** The REST API intercepts, sanitizes, and validates all incoming JSON payloads, actively rejecting anomalies like negative or ₹0 transactions with `400 Bad Request` codes.

### 💻 2. UI/UX & Frontend Experience
*   **Premium Glassmorphism:** Utilizes modern CSS `backdrop-filter` techniques to create depth, layering, and a premium "frosted glass" aesthetic.
*   **Deep Personalization:** Features a native **Dark Mode** toggle and a live **Background Engine** allowing users to switch between high-resolution themes seamlessly.
*   **Custom Micro-Interactions:** Includes a custom right-click context menu, a pulsing Floating Action Button (FAB) for quick transfers, and skeleton loading animations for data fetching.

### 💰 3. FinTech Capabilities
*   **Virtual Card Management:** An interactive debit card UI featuring iOS-style toggle switches for freezing the card and controlling International/Online transaction states.
*   **Dynamic Loan Calculator:** A built-in JavaScript engine that instantly calculates complex EMI schedules and total interest liabilities based on user input.
*   **Wealth & Analytics Dashboard:** Visual progress bars for "Active Savings Goals" and a dynamic monthly Income vs. Expense tracking module.
*   **AI Voice Simulation:** A simulated microphone input feature designed to capture voice commands for hands-free banking assistance.

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JS | Responsive, framework-less frontend for maximum speed. |
| **Backend** | Python 3, Flask | Lightweight WSGI web application framework. |
| **Database** | SQLite3 | Serverless, self-contained relational database. |
| **Security** | Werkzeug Security | Advanced password hashing and verification. |
| **Testing** | Pytest | Automated integration and unit testing suite. |

---

## 📡 API Reference Documentation

The Fundify backend exposes a fully functional RESTful API for application scalability.

| Endpoint | Method | Description | Payload |
| :--- | :---: | :--- | :--- |
| `/` | `POST` | Authenticates user & creates session | `{"username": "...", "password": "..."}` |
| `/api/transactions` | `GET` | Fetches full transaction history | *None* |
| `/api/transactions` | `POST` | Processes a new fund transfer | `{"name": "...", "upi": "...", "amount": 500}` |
| `/api/transactions/<id>` | `PUT` | Updates an existing transaction | `{"name": "...", "amount": 200}` |
| `/api/transactions/<id>`| `DELETE`| Reverses and deletes a transaction | *None* |

---

## 🚀 Installation & Local Setup

Running Fundify locally is incredibly simple and requires no external database servers.

### 1. Prerequisites
Ensure you have [Python 3.8+](https://www.python.org/downloads/) installed on your machine.

### 2. Clone and Setup Environment
Open your terminal and run the following commands:
```bash
# Clone the repository (if applicable)
git clone [https://github.com/yourusername/fundify-banking.git](https://github.com/yourusername/fundify-banking.git)
cd fundify-banking

# (Optional but recommended) Create a virtual environment
python -m venv .venv
source .venv/Scripts/activate  # On Windows
# source .venv/bin/activate    # On Mac/Linux

```

### 3. Install Dependencies

```bash
pip install flask werkzeug pytest

```

### 4. Run the Application

Start the Flask server. The database (`fundify.db`) will auto-generate upon launch.

```bash
python app.py

```

### 5. Access the Portal

Open your web browser and navigate to: 👉 **`http://127.0.0.1:5000`**

* **Default Username:** `admin`
* **Default Password:** `admin123`

---

## 🧪 Automated Testing Suite

This project adheres to strict Test-Driven Development (TDD) principles. A fully automated test suite is included to ensure API reliability, logic integrity, and regression prevention.

To run the integration tests, execute:

```bash
pytest test_app.py -v

```

**Test Coverage Summary:**

* [x] `test_valid_login`: Ensures successful authentication and session creation.
* [x] `test_invalid_login`: Ensures unauthorized access is blocked.
* [x] `test_get_transactions`: Validates JSON structure of transaction history.
* [x] `test_create_transaction`: Validates successful fund transfers and balance deduction.
* [x] `test_empty_transaction`: Validates security logic (rejects transfers of ₹0 or less).

---

## 🎓 SDLC Matrix (Major Project Compliance)

This software fulfills the 10 core phases of the Software Development Life Cycle (SDLC):

1. **Objective:** Full banking system successfully engineered.
2. **Requirement Analysis:** Core functional requirements (Authentication, Transfers, Portfolios) met.
3. **System Design:** Relational database schema implemented (`users`, `transactions`).
4. **Implementation:** Developed iteratively using Python, Flask, and Vanilla JS.
5. **Testing:** Unit and Integration testing executed successfully via `Pytest`.
6. **Deployment:** Hosted securely on a local WSGI server (`app.run`).
7. **Maintenance:** Built-in Python `logging` module tracks system events and errors natively.
8. **Documentation:** Comprehensive `README.md` and inline codebase documentation provided.
9. **Security:** Implemented secure session management, parameter binding (SQLi prevention), and PBKDF2 data encryption.
10. **Evaluation:** Application provides a seamless, dynamic workflow demonstrating full SDLC adherence.

---

## 🔮 Future Scope / Roadmap

If this project is expanded in the future, planned modules include:

* Integration with real-world payment gateways (Razorpay / Stripe APIs).
* Multi-user account creation via a public registration portal.
* Exporting transaction history to PDF and CSV formats.
* Real-time stock market API integration for the Wealth Dashboard.

---


```

```
