import firebase_admin
from firebase_admin import credentials, auth as admin_auth, db
import pyrebase
import streamlit as st
import requests
import time
import os

from dotenv import load_dotenv

load_dotenv()
# Firebase Admin SDK setup
if not firebase_admin._apps:
    cred = credentials.Certificate("luna-virtual-assistant-f3308ce4f08a.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://luna-virtual-assistant-default-rtdb.firebaseio.com"
    })



# Pyrebase setup for user authentication
config = {
  "apiKey": os.getenv("firebase_api_key"),
  "authDomain": "luna-virtual-assistant.firebaseapp.com",
  "databaseURL": "https://luna-virtual-assistant-default-rtdb.firebaseio.com",
  "projectId": "luna-virtual-assistant",
  "storageBucket": "luna-virtual-assistant.firebasestorage.app",
  "messagingSenderId": "279763888428",
  "appId": "1:279763888428:web:4d9b632074fa9813716489",
  "measurementId": "G-DLX3HF7WRH"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()




def register_user(email, password, name, sex, phone_number):
    try:
        # Create a new user with email and password
        user = auth.create_user_with_email_and_password(email, password)

        # Send a verification email
        auth.send_email_verification(user['idToken'])
        st.success("Verification email sent. Please verify your email to complete registration.")

        # Save user data temporarily in the database
        user_data = {
            "name": name,
            "sex": sex,
            "phone_number": phone_number,
            "email": email,
            "verified": False  # Mark as not verified initially
        }
        db.reference(f"temp_users/{user['localId']}").set(user_data)
        print(f"User data saved for UID: {user['localId']} in temp_users.-53")

        # Start the email verification check
        check_email_verification_periodically(user)

        return user
    except requests.exceptions.HTTPError as e:
        error_message = str(e)
        if e.response:
            try:
                error_details = e.response.json()
                st.error(f"Registration failed: {error_details.get('error', {}).get('message', 'Unknown error')}")
            except ValueError:
                st.error(f"Error: {e.response.text}")
        else:
            st.error(f"Registration failed with unknown error: {error_message}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None


def check_email_verification_periodically(user):
    interval_seconds = 5  # Check every 5 seconds
    max_attempts = 12  # Max 1 minute
    attempts = 0

    while attempts < max_attempts:
        if is_email_verified(user):
            st.success("Email verified successfully!")
            return True
        else:
            time.sleep(interval_seconds)
            attempts += 1

    st.error("Email verification timed out. Please try again.")
    return False


def is_email_verified(user):
    try:
        # Debugging: Print the full user data
        print("User data received:", user)
        
        if 'refreshToken' not in user or 'idToken' not in user:
            st.error("Invalid user data. Missing required fields like 'refreshToken' or 'idToken'.")
            return False

        # Get the user's UID from the user data
        uid = user.get('localId')
        print(f"UID extracted: {uid}-95")  # Debugging print

        if not uid:
            st.error("User does not have a valid UID.")
            return False
        
        # Fetch the user from Firebase using their UID
        firebase_user = admin_auth.get_user(uid)
        print(f"Firebase user fetched: {firebase_user}-103")  # Debugging print

        # Check if the user's email is verified
        if firebase_user.email_verified:
            print("Email is verified!-107")
            return True
        else:
            print("Email is not verified.-110")
            return False

    except Exception as e:
        # Debugging: Print the exception error
        print(f"Error checking email verification: {e}")
        return False

def complete_registration():
    if "user" not in st.session_state or not st.session_state["user"]:
        st.error("No user data found. Please register first.")
        return

    user = st.session_state["user"]
    if 'localId' not in user:
        st.error("Invalid user data. Please try registering again.")
        return

    try:
        # Fetch temporary user data
        user_data = db.reference(f"temp_users/{user['localId']}").get()
        if not user_data:
            st.error("No temporary data found for this user.")
            return

        # Save to permanent users database
        db.reference(f"users/{user['localId']}").set(user_data)
        print("Data saved to permanent db")

        # Delete from temporary database
        db.reference(f"temp_users/{user['localId']}").delete()
        print("Data deleted from temp db")

        st.success("Registration completed successfully!")
    except Exception as e:
        st.error(f"An error occurred during registration: {str(e)}")


def resend_verification_email():
    if "user" in st.session_state:
        user = st.session_state["user"]
        try:
            auth.send_email_verification(user['idToken'])
            st.success("Verification email resent successfully!")
        except Exception as e:
            st.error(f"Failed to resend verification email: {str(e)}")
    else:
        st.error("No user data found. Please log in or register first.")

def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state["user"] = user  # Save user details in session state
        print(f"User logged in: {user}")
        return user
    except Exception as e:
        print(f"Login error: {e}")
        return None

def is_user_authenticated(token):
    try:
        decoded_token = admin_auth.verify_id_token(token)
        return True
    except Exception:
        return False

def get_user_data(user_id):
    try:
        user_ref = db.reference(f"users/{user_id}")
        user_data = user_ref.get()
        if user_data:
            user_data.setdefault("name", "Rishabh")
            user_data.setdefault("sex", "Not Specified")
            user_data.setdefault("phone_number", "N/A")
            user_data.setdefault("email", "N/A")
            return user_data
        else:
            raise Exception(f"No data found for user ID: {user_id}")
    except Exception as e:
        print(f"Error fetching user data for user ID {user_id}: {str(e)}")
        return {
            "name": "Rishabh",
            "sex": "Not Specified",
            "phone_number": "N/A",
            "email": "N/A"
        }
        
def get_user_name():
    try:
        # Ensure user data exists in session state
        if "user" in st.session_state and "localId" in st.session_state.user:
            # Fetch user data from the database
            user_data = get_user_data(st.session_state.user['localId'])
            
            # Check if the name field is present in the fetched data
            if "name" in user_data:
                return user_data['name']
            else:
                st.error("User name not found in database.")
                return "User"
        else:
            st.error("User not found in session state.")
            return "User"
    except Exception as e:
        st.error(f"Error fetching user name: {str(e)}")
        return "User"

        

def update_user_data(user_id, updated_data):
    try:
        user_ref = db.reference(f"users/{user_id}")
        user_ref.update(updated_data)
    except Exception as e:
        print(f"Error updating user data: {str(e)}")



def profile_page():
    user_data = get_user_data(st.session_state.user['localId'])  # Retrieve user data from Firebase

    # Add a classy and premium look to the display of user information
    st.markdown(f"""
    <style>
        .account-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #222233;  /* Dark theme background */
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
            width: 60%;
            margin: 0 auto;
            color: #fff; /* White text for contrast */
        }}
        .account-container h2 {{
            font-size: 32px;
            color: #00c8ff;
            font-weight: 700;
            margin-bottom: 20px;
            text-align: center;
        }}
        .account-container p {{
            font-size: 18px;
            color: #f0f0f0;
            margin: 8px 0;
            font-weight: 400;
        }}
        .account-container .edit-info {{
            margin-top: 30px;
            padding: 20px;
            background-color: #222;  /* Dark background for form */
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            width: 100%;
        }}
        .account-container input, .account-container select {{
            border-radius: 8px;
            border: 1px solid #444;
            padding: 12px;
            width: 100%;
            font-size: 16px;
            margin-bottom: 15px;
            background-color: #333; /* Dark input background */
            color: #fff;
        }}
        .account-container button {{
            background-color: #6a1b9a;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 16px;
            width: 100%;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }}
        .account-container button:hover {{
            background-color: #9c4dcc;
        }}
        .account-container .form-title {{
            color: #00c8ff;
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 20px;
        }}
    </style>

    <div class="account-container">
        <h2>Account Information</h2>
        <p><strong>Name</strong>: {user_data['name']}</p>
        <p><strong>Email</strong>: {user_data['email']}</p>
        <p><strong>Gender</strong>: {user_data['sex']}</p>
        <p><strong>Phone Number</strong>: {user_data['phone_number']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Allow user to update information
    st.markdown("<div class='edit-info'>", unsafe_allow_html=True)
    st.subheader("Edit Your Information")

    name = st.text_input("Name", value=user_data['name'])

    # Handle Gender Selection with fallback
    gender_options = ["Male", "Female", "Other", "Not Specified"]
    user_gender = user_data.get('sex', 'Not Specified')
    if user_gender not in gender_options:
        user_gender = "Not Specified"
    sex = st.selectbox("Gender", gender_options, index=gender_options.index(user_gender))

    phone_number = st.text_input("Phone Number", value=user_data['phone_number'])

    if st.button("Save Changes"):
        updated_data = {
            "name": name,
            "sex": sex,
            "phone_number": phone_number
        }
        update_user_data(st.session_state.user['localId'], updated_data)
        st.success("Account updated successfully!")

    st.markdown("</div>", unsafe_allow_html=True)
