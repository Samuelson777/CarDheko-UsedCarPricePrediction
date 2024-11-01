import streamlit as st
import pickle
import pandas as pd
import numpy as np
import hashlib
import sqlite3
import time
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="CarDheko",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- USER AUTHENTICATION FUNCTIONS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- DATABASE FUNCTIONS ---
conn = sqlite3.connect('cardheko.db', check_same_thread=False)
c = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data

# --- LOAD DATA AND MODEL ---
@st.cache_data
def load_data():
    df = pd.read_csv("final_df.csv")  # Update with your file path
    return df

@st.cache_resource
def load_model():
    with open('pipeline.pkl', 'rb') as file:  # Update with your model path
        model = pickle.load(file)
    return model

# --- MAIN APP ---
def main():
    df = load_data()
    model = load_model()

    # Sidebar for authentication
    st.sidebar.title("CarDheko 🚗")
    menu = ["Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.sidebar.subheader("Login Section")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type='password')
        
        if st.sidebar.checkbox("Login"):
            create_usertable()
            hashed_pswd = make_hashes(password)
            result = login_user(username, check_hashes(password, hashed_pswd))
            
            if result:
                st.success(f"Welcome {username}! 👋")
                
                # Main Application
                st.title("Car Price Prediction System")
                
                # Create three columns for input fields
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    with st.container():
                        st.markdown("### Basic Details")
                        Brand = st.selectbox("Brand", options=df['Brand'].unique())
                        filtered_models = df[df['Brand'] == Brand]['model'].unique()
                        Model = st.selectbox("Model", options=filtered_models)
                        Model_year = st.selectbox("Year", options=sorted(df['modelYear'].unique()))
                        Bt = st.selectbox("Body Type", ['Hatchback', 'SUV', 'Sedan', 'MUV', 'Coupe', 
                                                      'Minivans', 'Convertibles', 'Hybrids', 'Wagon', 'Pickup Trucks'])

                with col2:
                    with st.container():
                        st.markdown("### Technical Details")
                        Ft = st.selectbox("Fuel Type", ['Petrol', 'Diesel', 'Lpg', 'Cng', 'Electric'])
                        Tr = st.selectbox("Transmission", ['Manual', 'Automatic'])
                        ML = st.number_input("Mileage (km/l)", min_value=5, max_value=50, step=1)
                        seats = st.selectbox("Seats", options=sorted(df['Seats'].unique()))

                with col3:
                    with st.container():
                        st.markdown("### Additional Info")
                        Owner = st.selectbox("Previous Owners", [0, 1, 2, 3, 4, 5])
                        Km = st.slider("Kilometers Driven", min_value=100, max_value=100000, step=1000)
                        city = st.selectbox("City", options=df['City'].unique())
                        color = st.selectbox("Color", df['Color'].unique())
                        IV = st.selectbox("Insurance Validity", ['Third Party insurance', 'Comprehensive', 
                                                               'Third Party', 'Zero Dep', '2', '1', 'Not Available'])

                # Prediction button
                if st.button("Predict Price 🚀"):
                    with st.spinner("Calculating..."):
                        # Create input dataframe
                        input_data = pd.DataFrame({
                            'Fuel type': [Ft],
                            'body type': [Bt],
                            'transmission': [Tr],
                            'ownerNo': [Owner],
                            'Brand': [Brand],
                            'model': [Model],
                            'modelYear': [Model_year],
                            'Insurance Validity': [IV],
                            'Kms Driven': [Km],
                            'Mileage': [ML],
                            'Seats': [seats],
                            'Color': [color],
                            'City': [city]
                        })
                        
                        # Make prediction
                        prediction = model.predict(input_data)
                        
                        # Display result
                        st.success(f"Predicted Price: ₹ {prediction[0]:.2f} Lakhs")
                        
                        # Display car details
                        st.subheader("Selected Car Details:")
                        st.json({
                            "Brand": Brand,
                            "Model": Model,
                            "Year": Model_year,
                            "Fuel Type": Ft,
                            "Transmission": Tr,
                            "Kilometers Driven": f"{Km:,}",
                            "Mileage": f"{ML} km/l"
                        })

            else:
                st.error("Incorrect Username/Password")

    elif choice == "SignUp":
        st.sidebar.subheader("Create New Account")
        new_user = st.sidebar.text_input("Username")
        new_password = st.sidebar.text_input("Password", type='password')

        if st.sidebar.button("Signup"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("Account created successfully! 🎉")
            st.info("Please login using your credentials")

if __name__ == '__main__':
    main()
