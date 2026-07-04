import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# Page Configuration (View changes start here)
st.set_page_config(page_title="Instalment & Recovery System", layout="wide")

# Custom CSS for Professional Branding
st.markdown("""
    <style>
    .main-title { font-size: 30px; font-weight: bold; color: #1E3A8A; text-align: center; padding-bottom: 15px; }
    .stButton>button { background-color: #1E3A8A; color: white; border-radius: 6px; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #1D4ED8; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS CONNECTION ---
def connect_to_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    try:
        # Re-authorizing with strict settings to avoid JWT Signature errors
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open("Recovery_Database").sheet1
        return sheet
    except Exception as e:
        st.error(f"Google Sheet Connection Error: {e}")
        return None

sheet = connect_to_sheet()

# --- SIDEBAR NAVIGATION (NEW VIEW) ---
st.sidebar.title("📁 Navigation Menu")
page = st.sidebar.radio("Kahan jana hai?", ["📝 Naya Khata / Entry Form", "📊 Poora Record Dekhein"])

# --- PAGE 1: NAYA KHATA FORM ---
if page == "📝 Naya Khata / Entry Form":
    st.markdown('<div class="main-title">💼 Naya Khata / Recovery Entry Form</div>', unsafe_allow_html=True)
    
    with st.form("recovery_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            invoice_no = st.text_input("Invoice No")
            invoice_date = st.date_input("Invoice Date", datetime.now())
            customer_name = st.text_input("Customer Name")
            cell_no = st.text_input("Cell No (WhatsApp)")
            products = st.text_input("Products Details")
            
        with col2:
            price = st.number_input("Total Price (Keemat)", min_value=0.0, step=500.0)
            m_inst = st.number_input("M.Inst (Mahana Kist)", min_value=0.0, step=100.0)
            nom = st.number_input("NOM (Number of Months)", min_value=1, step=1)
            last_inst_date = st.date_input("Last Inst Date", datetime.now())

        with col3:
            due_am = st.number_input("Due Am (Is Mahine ki Kist)", min_value=0.0, step=100.0)
            dis_am = st.number_input("Dis Am (Discount)", min_value=0.0, step=100.0)
            act_recv = st.number_input("Act Recv (Jo Paise Abhi Diye)", min_value=0.0, step=100.0)

        submitted = st.form_submit_button("Data Save Karain")
        
        if submitted:
            if sheet:
                # Calculations
                rem_due = due_am - dis_am - act_recv
                recv_am = act_recv 
                rem_balance = price - recv_am - dis_am
                
                row_data = [
                    "", # Sr No
                    invoice_no, str(invoice_date), customer_name, cell_no, products,
                    str(last_inst_date), price, m_inst, due_am, dis_am, act_recv,
                    recv_am, rem_due, rem_balance, nom
                ]
                
                sheet.append_row(row_data)
                st.success(f"✔️ {customer_name} ka record save ho gaya!")
            else:
                st.error("Data save nahi ho saka kyunke Google Sheet connect nahi hai. Upar ka error check karain.")

# --- PAGE 2: POORA RECORD DEKHEIN ---
elif page == "📊 Poora Record Dekhein":
    st.markdown('<div class="main-title">📊 Customer Accounts Ledger</div>', unsafe_allow_html=True)
    
    if sheet:
        with st.spinner("Google Sheet se live data load ho raha hai..."):
            all_data = sheet.get_all_records()
            
            if all_data:
                df = pd.DataFrame(all_data)
                
                # Live Search Bar
                search_query = st.text_input("🔍 Customer ka Naam ya Invoice Number likh kar search karain:")
                if search_query:
                    df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
                
                # Displaying interactive table
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Abhi database khali hai. Pehle koi entry karain!")
    else:
        st.error("Database view nahi ho sakta kyunke Google Sheet connect nahi hai.")
