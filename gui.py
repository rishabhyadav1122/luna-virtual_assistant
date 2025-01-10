import streamlit as st
from client import *
import time
from streamlit_option_menu import option_menu
from firebase_config import login_user, register_user ,profile_page , get_user_data , is_email_verified , complete_registration
from dotenv import load_dotenv
import os
import smtplib

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Custom CSS for styling
st.markdown(
    """
    <style>
        /* General page style */
        body {
            font-family: "Arial", sans-serif;
            background-color: #1e1e2f;
            color: #fff;
        }
        /* Title styling */
        .title {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: #ebecee;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            font-style: italic;
            color: #aaaaaa;
            margin-bottom: 40px;
        }
        /* Button styling */
        .button {
            display: block;
            width: 250px;
            height: 50px;
            margin: 10px auto;
            font-size: 18px;
            font-weight: bold;
            color: #fff;
            background: linear-gradient(90deg, #00c8ff, #007bff);
            border: none;
            border-radius: 25px;
            cursor: pointer;
            transition: 0.4s;
            text-align: center;
            line-height: 50px;
        }
        .button:hover {
            background: linear-gradient(90deg, #007bff, #00c8ff);
        }
        /* Listening animation */
            @keyframes bounce {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-10px);
            }
        }
        .dots {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        .dot {
            width: 15px;
            height: 15px;
            margin: 0 5px;
            background-color: #1e90ff;
            border-radius: 50%;
            animation: bounce 1.5s infinite;
        }
        .dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        .dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        /* Sidebar styling */
        .css-18e3th9 {
            background-color: #222233 !important;
            border-right: 1px solid #444;
        }
        .sidebar-button {
            width: 100%;
            font-size: 18px;
            font-weight: bold;
            color: #00c8ff;
            background: #222233;
            border: 1px solid #00c8ff;
            border-radius: 8px;
            margin-bottom: 15px;
            transition: 0.3s;
        }
        .sidebar-button:hover {
            background: #00c8ff;
            color: #fff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)



def instructions_page():
    st.markdown(
        """
    <style>
        .instructions-container {
            padding: 30px;
            background-color: #1a1a2e; /* Elegant dark theme background */
            color: #eaeaea; /* Soft light text for readability */
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            max-width: 70%;
            margin: 30px auto;
            font-family: 'Arial', sans-serif;
        }
        .instructions-container .note {
            margin-bottom: 25px;
            padding: 15px;
            background-color: #24243e; /* Slightly darker background */
            color: #b8c1ec; /* Softer text color for note */
            border-left: 5px solid #ff9800;
            font-size: 16px;
            line-height: 1.5;
            border-radius: 8px;
        }
        .instructions-container .note strong {
            color: #00c8ff;
        }
        .instructions-container h2 {
            text-align: center;
            font-size: 24px;
            color: #00c8ff;
            margin-bottom: 15px;
        }
        .instructions-container ul {
            list-style-type: none;
            padding: 0;
        }
        .instructions-container li {
            margin-bottom: 15px;
            padding: 10px;
            background-color: #2f2f45;
            border-radius: 8px;
            box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.3);
            font-size: 16px;
            display: flex;
            align-items: center;
        }
        .instructions-container li span.command {
            font-weight: bold;
            color: #ff9800; /* Updated accent color */
            margin-right: 10px;
        }
        .instructions-container li span.description {
            color: #d1d1d1;
        }
    </style>

    <div class="instructions-container">
        <div class="note">
            <strong>Note:</strong> Speak 2 seconds after the assistant says <em>"Speak Now"</em> or <em>"Say Luna".</em> <br>
            Please be kind and patient, as I'm just a new developer improving this assistant every day! <br>
            <strong>Important for Music:</strong> Ensure that Spotify is open in the background for music playback to work correctly.
        </div>
        <h2>Instructions and Commands</h2>
        <ul>
            <li><span class="command">Weather:</span> <span class="description">Say "weather in [city]" to get the weather information for the specified city.</span></li>
            <li><span class="command">Play on YouTube:</span> <span class="description">Say "play [video name] on YouTube" to play a video.</span></li>
            <li><span class="command">Play Music:</span> <span class="description">Say "play [song name]" to play a song. <strong>Note:</strong> Spotify must be open in the background.</span></li>
            <li><span class="command">Reminders:</span> <span class="description">Say "remind me to [task] at [time]" or "in [X minutes/hours]" to set a reminder.</span></li>
            <li><span class="command">Find Nearby:</span> <span class="description">Say "find [place type] nearby" (e.g., restaurant, ATM) to search for locations.</span></li>
            <li><span class="command">Currency Conversion:</span> <span class="description">Say "convert [amount] [currency] to [currency]" to convert currencies.</span></li>
            <li><span class="command">AI Response:</span> <span class="description">Ask any general question or give a command, and the assistant will process it using AI.</span></li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

def initialize_database():
    connection = sqlite3.connect("user_data.db")
    cursor = connection.cursor()

    # Create the history table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        command TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    connection.commit()
    connection.close()
    print("Database initialized and history table ensured.")

# Call this function at the start of your application

    
def add_history(user_id, action):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO history (user_id, action, timestamp)
        VALUES (?, ?, ?)
    """, (user_id, action, timestamp))
    
    conn.commit()
    conn.close()
    print(f"Added to database: {action}")   

def get_user_history(user_id):
    connection = sqlite3.connect("user_data.db")
    cursor = connection.cursor()
    cursor.execute("""
    SELECT command, timestamp FROM history WHERE user_id = ? ORDER BY timestamp DESC
    """, (user_id,))
    history = cursor.fetchall()
    connection.close()
    return history



# Define pages for navigation
def assistant_page():
    st.markdown("<div class='title'>Luna: Your Virtual Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Personalized Assistance Just for You!</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
            .note-container {
                margin: 20px auto;
                padding: 15px 20px;
                background: linear-gradient(135deg, #1a1a2e, #3a3a5e);
                color: #f0f0f0;
                border-left: 5px solid #00c8ff;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
                max-width: 70%;
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
            }
            .note-container strong {
                color: #ff9800;
            }
            .note-container a {
                color: #00c8ff;
                text-decoration: none;
                font-weight: bold;
            }
            .note-container a:hover {
                text-decoration: underline;
            }
        </style>
        <div class="note-container">
            <strong>Note 1:</strong> Start speaking 2 seconds after the assistant says 
            <em>"Speak Now"</em> or <em>"Say Luna"</em>. This ensures Luna captures your commands accurately.
            <br><br>
            <strong>Note 2:</strong> For more information about commands, open the <b> Instruction Page </b> 
            
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Buttons with functionality
    if st.button("Initialize Luna", key="initialize", help="Prepare Luna for interaction"):
        initialize_luna()
        st.success("Luna Initialized!")

    if st.button("Start Luna", key="start", help="Start Luna and listen for commands"):
        start_luna()
        is_running=True
        # Show listening dots animation
        if is_running:
            st.markdown(
                """
                <div class="dots">
                    <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if st.button("Stop Luna", key="stop", help="Stop Luna and end the session"):
        stop_luna()
        st.info("Luna Stopped!")

def about_us_page():
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; background-color: #222233; border-radius: 10px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);">
            <h1 style="color: #00c8ff; font-size: 48px; margin-bottom: 10px;">About Us</h1>
            <p style="font-size: 20px; color: #e0e0e0; margin-bottom: 30px;">
                I am a passionate web developer dedicated to crafting innovative and user-friendly digital solutions
            </p>
            <div style="background-color: #1e1e2f; padding: 20px; border-radius: 8px; margin: 0 auto; width: 60%; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);">
                <p style="font-size: 18px; color: #ffffff;"><b>Developer Name :</b> Rishabh Yadav</p>
                <p style="font-size: 18px; color: #ffffff;"><b>Contact:</b> <a href="mailto:yrishabh325@gmail.com" style="color: #00c8ff; text-decoration: none;">yrishabh325@gmail.com</a></p>
            </div>
            <h2 style="color: #00c8ff; font-size: 28px; font-weight: bold; margin-bottom: 20px;">Connect with me on : </h2>
            <div style="margin-top: 20px;">
                <a href="https://www.instagram.com/rishabh_yadav_1302/" target="_blank" style="margin-right: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" alt="Instagram" width="40" height="40">
                </a>
                <a href="https://www.linkedin.com/in/rishabh-yadav-40a288289/" target="_blank" style="margin-right: 10px; margin-left: 10px">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="40" height="40">
                </a>
                <a href="https://www.facebook.com/profile.php?id=100012021993965" target="_blank" style="margin-right: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174848.png" alt="Facebook" width="40" height="40">
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def send_email(name, email, message):
    """Send an email with the feedback details."""
    try:
        # Establish connection to the email server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            # Create email content
            subject = "New Feedback Received"
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            email_message = f"Subject: {subject}\n\n{body}"

            # Send email
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, email_message)  # To: Yourself
    except Exception as e:
        st.error(f"Error sending email: {e}")

def contact_us_page():
    """Contact Us page where users can send feedback."""
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; background-color: #222233; border-radius: 10px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);">
            <h1 style="color: #00c8ff; font-size: 48px; margin-bottom: 10px;">Contact Us</h1>
            <p style="font-size: 20px; color: #e0e0e0; margin-bottom: 30px;">
                We value your feedback and suggestions. Feel free to reach out to us!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Input fields
    name = st.text_input("Name", placeholder="Enter your name")
    email = st.text_input("Email", placeholder="Enter your email")
    message = st.text_area("Message", placeholder="Write your message here")

    # Submit button
    if st.button("Send Feedback"):
        if not name or not email or not message:
            st.warning("Please fill in all the fields.")
        else:
            send_email(name, email, message)
            st.success("Thank you for your feedback!")


def fetch_command_history():
    conn = sqlite3.connect("commands_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    return data

# Streamlit UI for the history page
def history_page():
    # Add CSS styling
    st.markdown(
        """
        <style>
        .record-container {
            background-color: #2c2c2c;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            font-family: 'Arial', sans-serif;
            color: #f5f5f5;
        }
        .record-header {
            font-size: 20px;
            font-weight: bold;
            color: #e0e0e0;
            margin-bottom: 10px;
        }
        .record-body {
            font-size: 16px;
            color: #cfcfcf;
        }
        .record-body strong {
            color: #00c8ff;
        }
        .delete-button {
            display: inline-block;
            margin-top: 20px;
            background-color: #e74c3c;
            color: white;
            font-size: 16px;
            padding: 10px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            box-shadow: 0 4px 10px rgba(231, 76, 60, 0.4);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .delete-button:hover {
            background-color: #c0392b;
            box-shadow: 0 6px 15px rgba(192, 57, 43, 0.5);
            transform: scale(1.05);
        }
        .no-history {
            text-align: center;
            font-size: 18px;
            color: #cfcfcf;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1 style='text-align:center; color:#00c8ff;'>Command History</h1>", unsafe_allow_html=True)
    # Fetch history from the database
    

    if "user" in st.session_state:
        user_id = st.session_state["user"]["localId"]
        commands = get_user_history(user_id)
        if commands:
            for command in commands:
                id_, cmd, timestamp = command
                st.markdown(
                    f"""
                    <div class="record-container">
                        <div class="record-header">Command ID: {id_}</div>
                        <div class="record-body">
                            <strong>Command:</strong> {cmd} <br>
                            <strong>Timestamp:</strong> {timestamp}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<p class='no-history'>No commands in history. Start giving some commands!</p>",
                unsafe_allow_html=True,
            )

        # Delete history button
        delete_history_clicked = st.button("Delete History")
        if delete_history_clicked:
            st.warning("This will delete all command history.")
            delete_all_history()


    

# Sidebar navigation
if "user" not in st.session_state:
    st.session_state.user = None

# If user is logged in, show a success message and the assistant page
if st.session_state.user:

    user_data = get_user_data(st.session_state.user['localId'])
    st.sidebar.markdown(f"<div class='title'>Welcome  {user_data['name']}</div>", unsafe_allow_html=True)

    
    st.markdown("""
    <style>
        .nav-link {
            font-size: 18px !important;
            font-weight: bold !important;
            color: #00c8ff !important;
            background-color: #1a1a1a !important;
            border-radius: 8px !important;
            padding: 10px 15px !important;
            margin: 10px 0 !important;
            transition: all 0.3s ease-in-out !important;
        }
        .nav-link:hover {
            background-color: #00c8ff !important;
            color: white !important;
            transform: scale(1.05) !important;
        }
        .nav-link-active {
            background-color: #005580 !important;
            color: white !important;
        }
        .nav-container {
            padding: 20px !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation using streamlit_option_menu
    with st.sidebar:
        page = option_menu(
            menu_title="Navigate",  # Title for the sidebar
            options=["Open Assistant", "About Us", "Contact Us", "Your Account","Instructions" ,"History"],  # Menu options
            icons=["robot", "info-circle", "envelope", "person-circle","book", "clock"],  # Icons for the menu
            menu_icon="menu-up",  # Icon for the menu title
            default_index=0,  # Default selected menu
            styles={
                "container": {
                    "background-color": "#1a1a1a", 
                    "padding": "10px",
                    "border-radius": "10px",
                    "box-shadow": "0 4px 10px rgba(0, 0, 0, 0.5)"
                },
                "nav-link": {
                    "font-size": "18px",
                    "color": "#00c8ff",
                    "background-color": "#333",
                    "margin": "5px",
                    "border-radius": "8px",
                    "transition": "all 0.3s ease-in-out",
                },
                "nav-link:hover": {
                    "background-color": "#00c8ff",
                    "color": "white",
                    "transform": "scale(1.05)",
                },
                "nav-link-selected": {
                    "background-color": "#005580",
                    "color": "white",
                },
            },
        )



    if page == "Open Assistant":
        assistant_page()
    elif page == "About Us":
        about_us_page()
    elif page == "Contact Us":
        contact_us_page()
    elif page == "Your Account":
        profile_page()
    elif page == "Instructions":
        instructions_page()
        
    elif page == "History":
        history_page()
        
    
    

else:
# Custom CSS for the premium look
    st.markdown("""
        <style>
        body {
            background-color: #f7f7f7;
            font-family: 'Helvetica', sans-serif;
        }
        .title {
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
            text-align: center;
            
        }
        .card {
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 40px;
            width: 100%;
            max-width: 400px;
            margin: 50px auto;
        }
        .stButton > button {
            background-color: #3498db;
            color: white;
            border-radius: 30px;
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: none;
            cursor: pointer;
        }
        .stButton > button:hover {
            background-color: #2980b9;
        }
        .input-field {
            margin-bottom: 15px;
        }
        .input-field input, .input-field select {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #bdc3c7;
            font-size: 16px;
        }
        .error {
            color: #e74c3c;
            font-size: 14px;
            font-weight: 600;
        }
        .success {
            color: #2ecc71;
            font-size: 14px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title of the page
    st.markdown('<h1 class="title">Virtual Assistant Authentication</h1>', unsafe_allow_html=True)


# Use this unique key in your radio button element
    auth_mode = st.radio("", ["Login", "Register"], index=0)


    if auth_mode == "Login":
        with st.form(key="login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                user = login_user(email, password)
                if user:
                    st.session_state["user"] = user  # Save user details in session state
                    st.success("Login successful!", icon="✅")
                    st.rerun()
                else:
                    st.error("Login failed! Check your credentials.", icon="❌")

    elif auth_mode == "Register":
        with st.form(key="register_form"):
            # Inputs
            name = st.text_input("Name", placeholder="Enter your full name")
            sex = st.selectbox("Gender", ["Male", "Female", "Other"])
            phone_number = st.text_input("Phone Number", placeholder="Enter your phone number")
            email = st.text_input("Email", placeholder="Enter your email address")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

            register_button = st.form_submit_button("Register")
            
            if register_button:
                if password == confirm_password:
                    # Register user
                    user = register_user(email, password, name, sex, phone_number)
                    
                    if user:
                        # Check if the user object has the correct structure
                        print(f"Registered user: done-644")

                        # Inform the user to verify their email
                        st.warning("Please verify your email to complete the registration process.")
                        
                        # Wait for verification
                        verified = is_email_verified(user)
                        print(verified)
                        
                        if verified:
                            st.session_state["user"] = user
                            complete_registration()
                            print("Registration completed-604")
                            print(st.session_state)  
                            st.session_state["user"] = user
                            st.success("Registration completed successfully!")
                            st.rerun()  # Refresh with logged-in user
                        else:
                            st.error("Email not verified. Please check your email and verify it.", icon="❌")
                    else:
                        st.error("Registration failed. Please try again.", icon="❌")
                else:
                    st.error("Passwords do not match!", icon="❌")

# Logout functionality
if st.session_state.user:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()  # Rerun the app to refresh the page



