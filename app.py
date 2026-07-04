import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Page configuration
st.set_page_config(layout="wide")
st.title("📊 Instalment & Recovery Management System")

# --- GOOGLE SHEETS CONNECTION ---
# (Is part mein aapki google sheet ki credentials file connect hogi)
def connect_to_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    # Apni credentials json file ka data yahan dalna hoga (Main aapko guide karoon ga)
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    # Aapki sheet ka naam 'Recovery_Database' hona chahiye
    sheet = client.open("Recovery_Database").sheet1
    return sheet

# --- INTERACTIVE FORM ---
st.subheader("📝 Naya Khata / Recovery Entry")

with st.form("recovery_form", clear_on_submit=True):
    # Screen ko 3 columns mein divide kiya hai taake table wale saare fields fit aa sakein
    col1, col2, col3 = st.columns(3)
    
    with col1:
        invoice_no = st.text_input("Invoice No")
        invoice_date = st.date_input("Invoice Date", datetime.now())
        customer_name = st.text_input("Customer Name")
        cell_no = st.text_input("Cell No (WhatsApp)")
        products = st.text_input("Products Details")
        
    with col2:
        price = st.number_input("Total Price", min_value=0.0, step=500.0)
        m_inst = st.number_input("M.Inst (Monthly Instalment)", min_value=0.0, step=100.0)
        nom = st.number_input("NOM (Number of Months)", min_value=1, step=1)
        last_inst_date = st.date_input("Last Inst Date", datetime.now())

    with col3:
        due_am = st.number_input("Due Am (Is Mahine ki Kist)", min_value=0.0, step=100.0)
        dis_am = st.number_input("Dis Am (Discount)", min_value=0.0, step=500.0)
        act_recv = st.number_input("Act Recv (Jo Paise Abhi Diye)", min_value=0.0, step=100.0)

    # Form Submit Button
    submitted = st.form_submit_button("Data Save Karain")
    
    if submitted:
        try:
            # Automate Calculations (Jo calculations software khud karega)
            # 1. Rem Due = Due Am - Dis Am - Act Recv
            rem_due = due_am - dis_am - act_recv
            
            # 2. Yeh calculations hum pehli entry ke hisab se kar rahe hain, baad mein update hoti rahengi
            recv_am = act_recv 
            rem_balance = price - recv_am - dis_am
            
            # Row data structure exact aapki image ke mutabiq
            row_data = [
                "", # Sr No (Google sheet khud handle kar sakti hai ya automatic lag jaye)
                invoice_no,
                str(invoice_date),
                customer_name,
                cell_no,
                products,
                str(last_inst_date),
                price,
                m_inst,
                due_am,
                dis_am,
                act_recv,
                recv_am,
                rem_due,
                rem_balance,
                nom
            ]
            
            # Data ko sheet mein bhejrahe hain
            sheet = connect_to_sheet()
            sheet.append_row(row_data)
            
            st.success(f"✔️ Invoice {invoice_no} ({customer_name}) ka record kamyabi se save ho gaya!")
            st.info(f"Calculated: Rem Due = {rem_due} | Total Rem Balance = {rem_balance}")
            
        except Exception as e:
            st.error(f"Error: Google Sheet connect nahi ho saki. (Technical Details: {e})")
