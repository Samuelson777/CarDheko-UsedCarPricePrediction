import streamlit as st
import pickle
import pandas as pd
import numpy as np
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="CarDheko",
    page_icon="🚗",
    layout="wide"
)

# Authentication function
def check_password():
    """Returns `True` if the user has the correct password."""
    def password_entered():
        if (
            st.session_state["username"] in st.secrets["credentials"]["usernames"]
            and st.session_state["password"] == st.secrets["credentials"]["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.sidebar.text_input("Username", on_change=password_entered, key="username")
        st.sidebar.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.sidebar.text_input("Username", on_change=password_entered, key="username")
        st.sidebar.text_input("Password", type="password", on_change=password_entered, key="password")
        st.sidebar.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

# Load data and model functions
@st.cache_data
def load_data():
    df = pd.read_csv("final_df.csv")
    return df

@st.cache_resource
def load_model():
    with open('pipeline.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

# Main application
def main():
    if not check_password():
        st.stop()  # Do not continue if check_password is False
        
    df = load_data()
    model = load_model()
    
    # Title of the application
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
                'Mileage ': [ML],
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

def create_usertable():
    st.secrets["credentials"] = {"usernames": [], "passwords": {}}

def add_userdata(new_user, new_password):
    st.secrets["credentials"]["usernames"].append(new_user)
    st.secrets["credentials"]["passwords"][new_user] = new_password

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if __name__ == '__main__':
    choice = st.sidebar.selectbox("Login or SignUp", ["Login", "SignUp"])
    
    if choice == "Login":
        main()
    elif choice == "SignUp":
        st.sidebar.subheader("Create New Account")
        new_user = st.sidebar.text_input("Username")
        new_password = st.sidebar.text_input("Password", type='password')

        if st.sidebar.button("Signup"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("Account created successfully! 🎉")
            st.info("Please login using your credentials")