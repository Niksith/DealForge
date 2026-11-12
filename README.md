# DealForge
### Coupon Validation and Best-Offer Optimisation Engine

## 1. Project Overview

DealForge is a Python-based coupon validation and best-offer optimisation application. It allows users to manage customers, products, coupons, shopping carts and orders through a graphical user interface.

The system validates coupon eligibility, compares available discounts and automatically selects the best valid offer for a customer.

## 2. Features

- **Customer Management:** Add and manage customer records.
- **Shopping Cart:** Add, update and remove products and calculate cart totals.
- **Coupon Management:** Create flat and percentage-based coupons.
- **Coupon Validation:** Check coupon eligibility, expiry dates, minimum cart values and category restrictions.
- **Weekday Restrictions:** Configure coupons to be valid only on selected weekdays.
- **Time Restrictions:** Configure coupon validity periods using Indian Standard Time (IST).
- **Best-Offer Optimisation:** Compare valid coupons and select the highest discount.
- **Coupon Stacking:** Apply multiple eligible coupons while respecting discount limits and minimum cart requirements.
- **One-Time Coupon Usage:** Prevent customers from using the same coupon more than once.
- **Checkout:** Process orders with or without coupons and record individual coupon discounts and usage.
- **Reports:** View order history, coupon usage and discount statistics.

## 3. Technologies Used

- Programming Language: Python
- GUI: Tkinter
- Database: SQLite
- Database Interface: Python sqlite3
- Testing: Python unittest
- Timezone Support: Python zoneinfo and tzdata
- Development Environment: Visual Studio Code

## 4. Project Structure

DealForge/
│
├── .venv/
├── archive/
├── data/
├── tests/
│   ├── __init__.py
│   ├── test_optimizer.py
│   └── test_time_restrictions.py
│
├── main.py
├── gui.py
├── database.py
├── coupons.py
├── validation.py
├── optimizer.py
├── cart.py
├── usage_tracker.py
├── checkout.py
├── reports.py
│
├── .gitignore
├── requirements.txt
└── README.md

## 5. Installation

### Prerequisites

- Python 3.10 or later recommended.
- Visual Studio Code or another Python-compatible editor.
- Tkinter must be available in the Python installation.

### Clone or Download the Project

Download the DealForge project and open its folder in Visual Studio Code.

### Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

DealForge primarily uses Python standard-library modules. The `tzdata` package is included to provide timezone database support on Windows.

## 6. Running the Application

Run the following command from the project directory:

```bash
python main.py
```

The DealForge graphical application will open.

## 7. Running Automated Tests

Run the automated test suite using:

```bash
python -m unittest discover -s tests -v
```

The current automated test suite contains **23 tests**, covering:

- Coupon validation and eligibility.
- Percentage-based and flat discount calculations.
- Maximum discount limits.
- Category-based discounts.
- Best-coupon selection.
- Coupon stacking and minimum cart revalidation.
- Prevention of discounts exceeding the cart total.
- One-time coupon usage.
- Checkout with multiple coupons.
- Recording individual coupon discounts.
- Checkout without applying a coupon.
- Weekday and time restrictions.

**Latest verified test result: 23 tests passed successfully.**

## 8. Database

DealForge uses SQLite to store:

- Customer information.
- Coupon information.
- Order records.
- Coupon usage records.

The database tables are created through the database initialization functionality.

Database schema migrations add new coupon restriction fields while preserving existing records.

## 9. Currency Handling

Monetary values are stored internally as integer paise to avoid floating-point rounding errors.

For example:

- ₹100 = 10000 paise
- ₹500 = 50000 paise

Discount calculations use integer-based monetary values.

## 10. Coupon Restrictions

DealForge supports additional coupon eligibility conditions:

- **Weekday Restrictions:** Coupons can be restricted to selected days of the week.
- **Time Restrictions:** Coupons can be restricted to a specified start and end time.
- **Timezone:** Time-based validation uses Indian Standard Time (IST).
- **Time Window:** The start time is included, while the end time is excluded.
- **Category Restrictions:** Coupons apply only to eligible product categories.
- **Minimum Cart Value:** The minimum purchase requirement is checked against the eligible category subtotal.
- **Coupon Stacking:** Minimum cart requirements are rechecked after previously applied discounts.

## 11. Checkout and Order Processing

The checkout module processes customer orders and records the associated financial information.

It supports:

- Checkout using a single coupon or multiple eligible coupons.
- Checkout without applying a coupon.
- Calculation of the final payable amount.
- Recording individual coupon discounts.
- Recording coupon usage against the customer and order.
- Prevention of repeated usage of the same coupon by a customer.

Order and coupon usage records are stored in SQLite.

## 12. Project Objective

The main objective of DealForge is to provide an efficient and reliable coupon management and discount optimisation system that automatically identifies the most beneficial valid coupon combination for a customer's shopping cart.

---

**Project:** DealForge  
**Type:** Python Application  
**Database:** SQLite  
**Interface:** Tkinter  
**Testing:** Python unittest  
**Verified Automated Tests:** 23 Passed