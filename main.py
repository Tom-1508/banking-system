import streamlit as st
import sqlite3
import random
import string
import pandas as pd


# ================== Bank Class (Handles Database Operations) ==================
class Bank:
    def __init__(self, db_name="bank.db"):
        """Initialize connection to SQLite database"""
        self.conn = sqlite3.connect(db_name, check_same_thread=False)  # allow Streamlit multi-threading
        self.cursor = self.conn.cursor()

    # ---------- Account Number Generator ----------
    @classmethod
    def __account_number_generator(cls):
        """Generate a random account number (letters + digits + symbols)"""
        alpha = random.choices(string.ascii_letters, k=4)
        number = random.choices(string.digits, k=3)
        symb = random.choices('!@#$%^&*', k=2)
        acc_id = alpha + number + symb
        random.shuffle(acc_id)
        return "".join(acc_id)

    # ---------- Create New Account ----------
    def create_account(self, name, email, age, pin):
        """Create a new bank account if conditions are valid"""
        account_no = self.__account_number_generator()
        balance = 0

        if age < 18 or len(str(pin)) != 4:
            return None, "❌ Account can't be created (must be 18+ and 4-digit pin)."

        self.cursor.execute(
            "INSERT INTO accounts (name, email, age, pin, account_no, balance) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, age, pin, account_no, balance),
        )
        self.conn.commit()
        return account_no, "✅ Account created successfully!"

    # ---------- Deposit Money ----------
    def deposit_money(self, acc, pin, amount):
        """Deposit money into an account"""
        self.cursor.execute("SELECT balance FROM accounts WHERE account_no=? AND pin=?", (acc, pin))
        row = self.cursor.fetchone()
        if not row:
            return "❌ Invalid account or pin!"
        if amount > 10000 or amount <= 0:
            return "❌ Deposit must be between 1 and 10,000."

        new_balance = row[0] + amount
        self.cursor.execute("UPDATE accounts SET balance=? WHERE account_no=?", (new_balance, acc))
        self.conn.commit()
        return f"✅ Deposit successful! New balance: {new_balance}"

    # ---------- Withdraw Money ----------
    def withdraw_money(self, acc, pin, amount):
        """Withdraw money from an account"""
        self.cursor.execute("SELECT balance FROM accounts WHERE account_no=? AND pin=?", (acc, pin))
        row = self.cursor.fetchone()
        if not row:
            return "❌ Invalid account or pin!"
        if amount <= 0 or amount > row[0]:
            return "❌ Invalid withdrawal amount."

        new_balance = row[0] - amount
        self.cursor.execute("UPDATE accounts SET balance=? WHERE account_no=?", (new_balance, acc))
        self.conn.commit()
        return f"✅ Withdrawal successful! New balance: {new_balance}"

    # ---------- Get Account Details ----------
    def get_details(self, acc, pin):
        """Fetch account details for a given account and pin"""
        self.cursor.execute(
            "SELECT name, email, age, pin, account_no, balance FROM accounts WHERE account_no=? AND pin=?",
            (acc, pin),
        )
        return self.cursor.fetchone()

    # ---------- Update Account Details ----------
    def update_details(self, acc, pin, new_name, new_email, new_pin):
        """Update name, email or pin of an account"""
        self.cursor.execute("SELECT id, name, email, pin FROM accounts WHERE account_no=? AND pin=?", (acc, pin))
        row = self.cursor.fetchone()
        if not row:
            return "❌ Invalid account or pin!"

        # Keep old values if new values are not provided
        new_name = new_name or row[1]
        new_email = new_email or row[2]
        new_pin = int(new_pin or row[3])

        self.cursor.execute(
            "UPDATE accounts SET name=?, email=?, pin=? WHERE account_no=?",
            (new_name, new_email, new_pin, acc),
        )
        self.conn.commit()
        return "✅ Details updated successfully!"

    # ---------- Delete Account ----------
    def delete_account(self, acc, pin):
        """Delete an account permanently"""
        self.cursor.execute("SELECT id FROM accounts WHERE account_no=? AND pin=?", (acc, pin))
        row = self.cursor.fetchone()
        if not row:
            return "❌ Invalid account or pin!"

        self.cursor.execute("DELETE FROM accounts WHERE account_no=?", (acc,))
        self.conn.commit()
        return "✅ Account deleted successfully!"
    
    # ---------- View All Accounts (Admin Only) ----------
    def view_all_accounts(self):
        """Fetch all accounts (for admin view only)"""
        self.cursor.execute("SELECT * FROM accounts")
        return self.cursor.fetchall()


# ================== Streamlit UI (Frontend) ==================
st.set_page_config(page_title="Bank Management System", page_icon="🏦", layout="centered")
st.title("🏦 Bank Management System")

# Create Bank object
user = Bank()

# Sidebar menu
menu = [
    "Create Account", 
    "Deposit Money", 
    "Withdraw Money", 
    "Get Account Details", 
    "Update Details", 
    "Delete Account", 
    "👨‍💼 Admin – View Database"
]
choice = st.sidebar.selectbox("Select Action", menu)


# ---------- User Options ----------
if choice == "Create Account":
    st.subheader("➕ Create a New Account")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
    pin = st.text_input("4-digit PIN", type="password", max_chars=4)

    if st.button("Create Account"):
        if not (name and email and pin):
            st.warning("⚠️ Please fill all fields.")
        else:
            acc_no, msg = user.create_account(name, email, age, int(pin))
            st.info(msg)
            if acc_no:
                st.success(f"🎉 Your Account Number: `{acc_no}`")

elif choice == "Deposit Money":
    st.subheader("💰 Deposit Money")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1, step=1)

    if st.button("Deposit"):
        st.info(user.deposit_money(acc, int(pin), amount))

elif choice == "Withdraw Money":
    st.subheader("💵 Withdraw Money")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1, step=1)

    if st.button("Withdraw"):
        st.info(user.withdraw_money(acc, int(pin), amount))

elif choice == "Get Account Details":
    st.subheader("📄 Account Details")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")

    if st.button("Get Details"):
        row = user.get_details(acc, int(pin))
        if row:
            st.success("✅ Account Found")
            st.write(f"**Name**: {row[0]}")
            st.write(f"**Email**: {row[1]}")
            st.write(f"**Age**: {row[2]}")
            st.write(f"**PIN**: {row[3]}") 
            st.write(f"**Account No**: {row[4]}")
            st.write(f"**Balance**: ₹{row[5]}")
        else:
            st.error("❌ Invalid account or pin!")

elif choice == "Update Details":
    st.subheader("✏️ Update Account Details")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")

    new_name = st.text_input("New Name (leave blank to keep same)")
    new_email = st.text_input("New Email (leave blank to keep same)")
    new_pin = st.text_input("New PIN (leave blank to keep same)")

    if st.button("Update"):
        st.info(user.update_details(acc, int(pin), new_name, new_email, new_pin))

elif choice == "Delete Account":
    st.subheader("🗑️ Delete Account")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")

    if st.button("Delete"):
        st.warning(user.delete_account(acc, int(pin)))


# ---------- Secure Admin Section ----------
elif choice == "👨‍💼 Admin – View Database":
    st.subheader("🔐 Admin Login Required")

    # Store login state in session
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    # If not logged in, show login form
    if not st.session_state.admin_logged_in:
        admin_user = st.text_input("Admin Username")
        admin_pass = st.text_input("Admin Password", type="password")

        if st.button("Login"):
            if admin_user == "admin" and admin_pass == "1234":  # ⚠️ Replace with secure credentials
                st.session_state.admin_logged_in = True
                st.success("✅ Login successful!")
                st.rerun()   # Immediately reruns app so DB loads
            else:
                st.error("❌ Invalid credentials")

    # If logged in, show database
    else:
        st.success("✅ Welcome, Admin!")
        rows = user.view_all_accounts()
        
        if rows:
            df = pd.DataFrame(
                rows, 
                columns=["ID", "Name", "Email", "Age", "PIN", "Account No", "Balance"]
            )
            st.dataframe(df, use_container_width=True)

            # Download CSV option
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download as CSV",
                data=csv,
                file_name="bank_accounts.csv",
                mime="text/csv",
            )
        else:
            st.info("ℹ️ No accounts found in the database.")

        # Admin logout button
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.warning("👋 Logged out!")