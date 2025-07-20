import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyttsx3
import datetime

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://static.vecteezy.com/system/resources/previews/025/414/767/large_2x/elegant-flying-gold-coin-with-golden-sparkle-in-black-background-crypto-currency-modern-illustration-backdrop-free-photo.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .block-container, 
    .sidebar .sidebar-content {
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border-radius: 12px;
        padding: 20px;
    }
    .block-container * {
        color: white !important;
    }
    .sidebar .sidebar-content * {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

st.title("💰 SmartPay Planner")

st.sidebar.header("📋 Loan Inputs")
loan_amount = st.sidebar.number_input("Enter the Loan Amount (Rs.)", min_value=1000, step=1000)
interest_rate = st.sidebar.number_input("Enter the Annual Interest Rate (%)", min_value=0.0, step=0.1)
loan_term_years = st.sidebar.number_input("Enter the Loan Term (Years)", min_value=1)
start_date = st.sidebar.date_input("Select Loan Start Date", value=datetime.date.today())
speak_summary = st.sidebar.checkbox("🔊 Voice Summary")
submit = st.sidebar.button("Submit")

if submit:
    if speak_summary:
        speak(f"Loan amount is {loan_amount} rupees")
        speak(f"Interest rate is {interest_rate} percent")
        speak(f"Loan term is {loan_term_years} years")

    monthly_rate = interest_rate / 100 / 12
    months = loan_term_years * 12

    monthly_payment = loan_amount / months if monthly_rate == 0 else \
        loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** -months)

    st.subheader("📆 Monthly Payment")
    st.success(f"Rs.{monthly_payment:,.2f}")

  
    schedule = []
    balance = loan_amount
    total_interest = 0

    for month in range(1, months + 1):
        interest = balance * monthly_rate
        principal = monthly_payment - interest
        balance -= principal
        total_interest += interest
        schedule.append([
            month,
            monthly_payment,
            interest,
            principal,
            max(balance, 0)
        ])

    df = pd.DataFrame(schedule, columns=["Month", "Payment", "Interest", "Principal", "Balance"])
    df = df.round(2)

  
    dated_schedule = []
    for i in range(len(df)):
        payment_date = start_date + pd.DateOffset(months=i)
        dated_schedule.append([
            df.at[i, "Month"],
            payment_date.date(),
            df.at[i, "Payment"],
            df.at[i, "Interest"],
            df.at[i, "Principal"],
            df.at[i, "Balance"]
        ])

    df_with_dates = pd.DataFrame(dated_schedule, columns=["Month", "Payment Date", "Payment", "Interest", "Principal", "Balance"])

    st.subheader("📑 Repayment Schedule with Dates")
    st.dataframe(df_with_dates.style.format({
        "Payment": "Rs.{:,.2f}",
        "Interest": "Rs.{:,.2f}",
        "Principal": "Rs.{:,.2f}",
        "Balance": "Rs.{:,.2f}"
    }), height=350)

    st.subheader("💸 Total Interest Paid")
    st.info(f"Rs.{total_interest:,.2f}")
    if interest_rate == 0:
        st.warning("Since the interest rate is 0%, this is an interest-free loan.")

    csv = df_with_dates.to_csv(index=False).encode('utf-8')
    st.download_button("⬇ Download Repayment Schedule", data=csv, file_name="repayment_schedule.csv", mime="text/csv")

    st.subheader("📉 Loan Balance Over Time")
    fig, ax = plt.subplots()
    ax.plot(df["Month"], df["Balance"], label="Remaining Balance", color="#00c0ff")
    ax.set_xlabel("Month")
    ax.set_ylabel("Balance (Rs.)")
    ax.set_title("Loan Balance Over Time")
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("📊 Loan Breakdown")
    labels = ["Principal", "Total Interest"]
    sizes = [loan_amount, total_interest]
    fig2, ax2 = plt.subplots()
    ax2.pie(sizes, labels=labels, autopct='%1.1f%%', colors=["#4CAF50", "#FF5722"])
    ax2.axis("equal")
    st.pyplot(fig2)

    st.subheader("📌 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly EMI", f"Rs.{monthly_payment:,.2f}")
    col2.metric("Total Interest", f"Rs.{total_interest:,.2f}")
    col3.metric("Total Duration", f"{months} months")

    if st.checkbox("🔁 Replay Summary"):
        speak(f"Your monthly EMI is {monthly_payment:.2f} rupees")
        speak(f"Total interest payable is {total_interest:.2f} rupees")

    st.markdown("""
    <hr style="border: 0.5px solid #666;" />
    <p style="text-align:center; color: #888;">🛡 SmartPay Planner by Shubhi and Shweta | Built with Streamlit</p>
    """, unsafe_allow_html=True)