import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------- CUSTOM STYLING ----------------

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #666;
    margin-top: 0;
    margin-bottom: 30px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.08);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    transition: transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
}

/* Section spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    border-right: 1px solid #e5e7eb;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}

/* Form */
[data-testid="stForm"] {
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #e5e7eb;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------

connection = sqlite3.connect("expenses.db")

# Create settings table
connection.execute("""
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    monthly_budget REAL
)
""")

connection.commit()


# ---------------- READ EXPENSES ----------------

df = pd.read_sql_query(
    "SELECT * FROM expenses ORDER BY date DESC",
    connection
)

# Convert date column
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])


# ---------------- SIDEBAR ----------------

st.sidebar.title("🔎 Filters")

if not df.empty:

    # Category filter
    categories = ["All"] + sorted(
        df["category"].dropna().unique().tolist()
    )

    selected_category = st.sidebar.selectbox(
        "🏷️ Category",
        categories
    )

    if selected_category != "All":
        df = df[df["category"] == selected_category]


    # Date filter
    if not df.empty:

        min_date = df["date"].min().date()
        max_date = df["date"].max().date()

        start_date = st.sidebar.date_input(
            "📅 From",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

        end_date = st.sidebar.date_input(
            "📅 To",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

        if start_date > end_date:

            st.sidebar.error(
                "⚠️ Start date must be before end date."
            )

        else:

            df = df[
                (pd.to_datetime(df["date"]).dt.date >= start_date)
                &
                (pd.to_datetime(df["date"]).dt.date <= end_date)
            ]

else:

    st.sidebar.info("No expenses available.")


# ---------------- TITLE ----------------

st.markdown(
    '<div class="main-title">💰 Personal Expense Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Track, analyze and manage your spending.</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================

if df.empty:

    st.info(
        "No expenses recorded for the selected filters."
    )

else:

    # ---------------- SUMMARY ----------------

    total_spending = df["amount"].sum()

    current_month = pd.Timestamp.now().month
    current_year = pd.Timestamp.now().year

    monthly_df = df[
        (df["date"].dt.month == current_month)
        &
        (df["date"].dt.year == current_year)
    ]

    monthly_spending = monthly_df["amount"].sum()

    highest_expense = df["amount"].max()


    # ---------------- SUMMARY CARDS ----------------

    st.subheader("📌 Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Total Spending",
            f"₹{total_spending:,.2f}"
        )

    with col2:

        st.metric(
            "📅 This Month",
            f"₹{monthly_spending:,.2f}"
        )

    with col3:

        st.metric(
            "💸 Highest Expense",
            f"₹{highest_expense:,.2f}"
        )

    with col4:

        st.metric(
            "🧾 Transactions",
            len(df)
        )


    # ---------------- CATEGORY DATA ----------------

    category_data = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )


    # ---------------- CHARTS ----------------

    st.subheader("📊 Spending Analytics")

    chart_col1, chart_col2 = st.columns(2)


    # Bar chart
    with chart_col1:

        st.write("### 📊 Spending by Category")

        st.bar_chart(category_data)


    # Donut chart
    with chart_col2:

        st.write("### 🥧 Category Distribution")

        fig = px.pie(
            category_data,
            values=category_data.values,
            names=category_data.index,
            hole=0.45
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ---------------- MONTHLY TREND ----------------

    st.subheader("📈 Monthly Spending Trend")

    monthly_data = (
        df.groupby(
            df["date"].dt.to_period("M")
        )["amount"]
        .sum()
    )

    monthly_data.index = monthly_data.index.astype(str)

    st.line_chart(monthly_data)


    # ---------------- EXPENSE TABLE ----------------

    st.subheader("🧾 Recent Expenses")

    display_df = df.copy()

    display_df["amount"] = display_df["amount"].apply(
        lambda x: f"₹{x:,.2f}"
    )

    st.dataframe(
        display_df,
        use_container_width=True
    )

# ---------------- EXPORT EXPENSES ----------------

csv_data = df.to_csv(index=False)

st.download_button(
    label="📥 Download Expenses as CSV",
    data=csv_data,
    file_name="my_expenses.csv",
    mime="text/csv"
)

# =========================================================
# MONTHLY BUDGET
# =========================================================

st.subheader("🎯 Monthly Budget")

st.caption("Monitor your monthly spending against your saved budget.")

# Get saved budget
budget_result = connection.execute(
    "SELECT monthly_budget FROM settings WHERE id = 1"
).fetchone()

saved_budget = (
    budget_result[0]
    if budget_result
    else 5000.0
)


# Budget input
budget = st.number_input(
    "Set your monthly budget (₹)",
    min_value=0.0,
    value=float(saved_budget),
    step=500.0
)


# Save budget
connection.execute("""
INSERT INTO settings (id, monthly_budget)
VALUES (1, ?)
ON CONFLICT(id)
DO UPDATE SET monthly_budget = excluded.monthly_budget
""", (budget,))

connection.commit()


# ---------------- BUDGET CALCULATION ----------------

if not df.empty:

    current_month = pd.Timestamp.now().month
    current_year = pd.Timestamp.now().year

    monthly_spending = df[
        (df["date"].dt.month == current_month)
        &
        (df["date"].dt.year == current_year)
    ]["amount"].sum()

else:

    monthly_spending = 0


remaining = budget - monthly_spending


if budget > 0:

    progress = min(
        monthly_spending / budget,
        1.0
    )

else:

    progress = 0.0


st.progress(progress)


budget_col1, budget_col2 = st.columns(2)


with budget_col1:

    st.metric(
        "💸 Spent",
        f"₹{monthly_spending:,.2f}"
    )


with budget_col2:

    if remaining >= 0:

        st.metric(
            "💚 Remaining",
            f"₹{remaining:,.2f}"
        )

    else:

        st.metric(
            "🚨 Over Budget",
            f"₹{abs(remaining):,.2f}"
        )


if remaining < 0:

    st.error(
        "🚨 You have exceeded your monthly budget!"
    )

elif progress >= 0.8:

    st.warning(
        "⚠️ You have used more than 80% of your budget."
    )

else:

    st.success(
        "✅ You are within your budget!"
    )


# =========================================================
# ADD EXPENSE
# =========================================================

st.subheader("➕ Add New Expense")


with st.form("expense_form"):

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.01,
        step=10.0
    )

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Education",
            "Entertainment",
            "Bills",
            "Other"
        ]
    )

    description = st.text_input(
        "Description"
    )

    expense_date = st.date_input(
        "📅 Expense Date"
    )

    submitted = st.form_submit_button(
        "➕ Add Expense"
    )


    if submitted:

        connection = sqlite3.connect(
            "expenses.db"
        )

        cursor = connection.cursor()

        date = expense_date.strftime(
            "%Y-%m-%d"
        )

        cursor.execute("""
        INSERT INTO expenses
        (amount, category, description, date)
        VALUES (?, ?, ?, ?)
        """, (
            amount,
            category,
            description,
            date
        ))

        connection.commit()

        connection.close()

        st.success(
            "✅ Expense added successfully!"
        )

        st.rerun()


# =========================================================
# DELETE EXPENSE
# =========================================================

st.subheader("🗑️ Delete an Expense")


if not df.empty:

    expense_options = {

        f"₹{row.amount:,.2f} | "
        f"{row.category} | "
        f"{row.description} | "
        f"{row.date.strftime('%Y-%m-%d')}":
        row.id

        for row in df.itertuples()
    }


    if expense_options:

        selected_expense = st.selectbox(
            "Select an expense to delete",
            list(expense_options.keys())
        )


        if st.button(
            "🗑️ Delete Selected Expense"
        ):

            expense_id = expense_options[
                selected_expense
            ]

            delete_connection = sqlite3.connect(
                "expenses.db"
            )

            delete_cursor = delete_connection.cursor()

            delete_cursor.execute(
                "DELETE FROM expenses WHERE id = ?",
                (expense_id,)
            )

            delete_connection.commit()

            delete_connection.close()

            st.success(
                "✅ Expense deleted successfully!"
            )

            st.rerun()

else:

    st.info(
        "No expenses available to delete."
    )


# ---------------- CLOSE DATABASE ----------------

connection.close()