import speech_recognition as sr
import webbrowser
import pyttsx3
import pyaudio
import music_library
import requests
import google.generativeai as genai
import re
from datetime import datetime,timedelta
from flask import Flask, request, send_from_directory
import threading
import time
import sqlite3
import schedule
import dateparser
from gtts import gTTS
import pygame
import io
from gui import initialize_database , add_history
import streamlit as st
from firebase_config import get_user_name
import os
from dotenv import load_dotenv
import tempfile
from streamlit_webrtc import webrtc_streamer
import base64

load_dotenv()




# gemini_api_key = os.getenv("gemini_api_key")
# newsapi = os.getenv("newsapi")
# weather_api_key = os.getenv("weather_api_key") 
# fourSquare_api_key = os.getenv("fourSquare_api_key") 
# currency_api_key = os.getenv("currency_api_key")

gemini_api_key = st.secrets["gemini_api_key"]
newsapi = st.secrets["newsapi"]
weather_api_key = st.secrets["weather_api_key"]
fourSquare_api_key = st.secrets["fourSquare_api_key"]
currency_api_key = st.secrets["currency_api_key"]



# Username........




# Initialize session state variables if not already initialized
if 'is_initialized' not in st.session_state:
    st.session_state.is_initialized = False

if 'is_running' not in st.session_state:
    st.session_state.is_running = False




app = Flask(__name__)

# Global variable to store user location
user_location = {"latitude": None, "longitude": None}


def init_flask_app():
    @app.route("/")
    def index():
        return send_from_directory('.', 'location.html')

    @app.route("/set-location")
    def set_location():
        user_location['latitude'] = request.args.get('lat')
        user_location['longitude'] = request.args.get('lon')
        print(f"Location set to: {user_location}")
        return "Location received!", 200

    threading.Thread(target=lambda: app.run(port=5000), daemon=True).start()
    print("Flask app is running...")

# Basic need Functions
def view_reminders():
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders")
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        print(row)
        

def delete_all_reminders():
    # Connect to the SQLite database
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()

    # Delete all rows from the reminders table
    cursor.execute("DELETE FROM reminders")

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    print("All reminders have been deleted.")       
    
def view_history():
    conn = sqlite3.connect("commands_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history")
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        print(row)
        
def delete_all_history():
    # Connect to the SQLite database
    conn = sqlite3.connect("commands_history.db")
    cursor = conn.cursor()

    # Delete all rows from the reminders table
    cursor.execute("DELETE FROM history")

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    print("All reminders have been deleted.")  
          



# Initialize the database
def init_db_reminder():
    conn = sqlite3.connect("reminders.db")  # Creates or opens the database file
    cursor = conn.cursor()
    # Create the reminders table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        time TEXT NOT NULL,
        notified INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()
    print("rem-db initialised")
    
def init_db_history():
    conn = sqlite3.connect("commands_history.db")
    cursor = conn.cursor()
    # Create the history table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("history-db initialised")

def add_reminder_to_db_reminder(task, reminder_time):
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (task, time) VALUES (?, ?)", (task, reminder_time))
    conn.commit()
    conn.close()
    speak(f"Reminder set for {task} at {reminder_time}.")
    print(f"Added to database: {task} at {reminder_time}")
    
# def add_to_database_history(command):
#     conn = sqlite3.connect("commands_history.db")
#     cursor = conn.cursor()
#     # Insert command into the table
#     cursor.execute("INSERT INTO history (command, timestamp) VALUES (?, ?)", 
#                    (command, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
#     conn.commit()
#     conn.close()
#     print(f"Added to database: {command}")  

def check_reminders_from_db():
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"Current time: {current_time}")

    # Fetch reminders that match the current time and haven't been notified
    cursor.execute("SELECT id, task, time FROM reminders WHERE time <= ? AND notified = 0", (current_time,))
    reminders_to_notify = cursor.fetchall()

    for reminder in reminders_to_notify:
        reminder_id, task, reminder_time = reminder
        speak(f"Reminder: {task} at {reminder_time}")
        print(f"Reminder triggered: {task} at {reminder_time}")

        # Mark the reminder as notified
        cursor.execute("UPDATE reminders SET notified = 1 WHERE id = ?", (reminder_id,))

    conn.commit()
    conn.close()



def get_user_location():
    url = "http://localhost:5000/"
    speak("Waiting for you to  provide location...")
    webbrowser.open(url)

    # Wait until the location is set by checking the user_location variable
    while not user_location['latitude'] or not user_location['longitude']:
        time.sleep(1)  # Check every second until location is received

    speak("Thank you! I have received your location.")
    
    return user_location['latitude'], user_location['longitude']
    
    # # Call find_nearby_places function as a test (you can customize this for a specific place type)
    # place_type = "restaurant"  # Example place type
    # find_nearby_places(place_type)


def find_nearby_places(place_type):
    if not user_location['latitude'] or not user_location['longitude']:
        speak("Location not set. Please provide your location first.")
        return

    latitude = user_location['latitude']
    longitude = user_location['longitude']

    # Define Foursquare API settings
    api_key = fourSquare_api_key  # Replace with your actual Foursquare API key
    url = "https://api.foursquare.com/v3/places/search"

    headers = {
        "Accept": "application/json",
        "Authorization": api_key
    }

    # Define search parameters using user location
    params = {
        "ll": f"{latitude},{longitude}",
        "query": place_type,
        "limit": 5
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        places = response.json().get('results', [])
        if places:
            for place in places:
                name = place.get('name')
                location = place.get('location', {})
                formatted_address = location.get('formatted_address', '')
                speak(f"{name}, located at {formatted_address}")
        else:
            speak(f"Sorry, I couldn't find any {place_type} nearby.")
    else:
        speak("There was an error retrieving the information. Please try again later.")


def get_custom_greeting():
    """Generates a custom greeting based on the time of day."""
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    return f"{greeting}! hope you're having a great day!"

def greet_user():
    """Speaks a personalized greeting to the user."""
    greeting_message = get_custom_greeting()
    speak(greeting_message) 
    print(greeting_message)

# def speak(text, lang="en"):
#     try:
#         # Generate speech audio in memory
#         tts = gTTS(text=text, lang=lang)
#         audio_data = io.BytesIO()
#         tts.write_to_fp(audio_data)
#         audio_data.seek(0)

#         # Initialize pygame and play audio
#         pygame.mixer.init()
#         pygame.mixer.music.load(audio_data, "mp3")
#         pygame.mixer.music.play()

#         # Wait for playback to finish
#         while pygame.mixer.music.get_busy():
#             continue

#         pygame.mixer.music.stop()
#         pygame.mixer.quit()

#     except Exception as e:
#         print(f"Error in speech synthesis: {e}")

def speak(text, lang="en"):
    """
    Convert text to speech, play automatically, and hide the audio UI in Streamlit.
    """
    try:
        # Generate speech audio
        tts = gTTS(text=text, lang=lang)
        audio_file_path = "output.mp3"
        tts.save(audio_file_path)

        # Encode the audio file for embedding
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()

        # Create an autoplay audio player
        audio_html = f"""
        <audio autoplay hidden>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error in speech synthesis: {e}")




def aiProcess(command):
    try:
        print("Initializing Gemini AI...")
        genai.configure(api_key=gemini_api_key)  # Ensure API key is correct
        print("Gemini AI configured successfully.")
        
        model = genai.GenerativeModel("gemini-1.5-flash")  # Check model name/version
        

        chat = model.start_chat(
            history=[
                {"role": "user", "parts": "Hello, Give Short responses"},
                {"role": "model", "parts": "Great to meet you. What would you like to know?"},
            ]
        )
        
        response = chat.send_message(command)
        print(f"Gemini AI response: {response.text}")
        return response.text
    except Exception as e:
        print(f"Error in aiProcess: {e}")
        return "Sorry, there was an error processing your command with Gemini AI."


def get_weather(city):
    """Fetch weather information from OpenWeatherMap API."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        weather = data['weather'][0]
        temperature = main['temp']
        humidity = main['humidity']
        weather_description = weather['description']
        return f"The temperature in {city} is {temperature}°C with {weather_description} and humidity of {humidity}%."
    else:
        return "Sorry, I couldn't fetch the weather information for that city."

def convert_currency(amount, from_currency, to_currency, api_key=currency_api_key):
    # Prepare the API request URL
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"

    # Make the request to get conversion rates
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if the 'to_currency' is available in the conversion data
        if to_currency in data['conversion_rates']:
            conversion_rate = data['conversion_rates'][to_currency]
            converted_amount = amount * conversion_rate
            return round(converted_amount, 2)
        else:
            return f"Sorry, I couldn't find conversion rates for {to_currency}."
    else:
        return "Sorry, I couldn't fetch the conversion rates. Please try again later."


def processCommand(c):
    print(f"Processing command: {c}")  # Debugging line to confirm command is processed
    if "open google" in c.lower():
        print("Opening Google...")  # Debugging line
        webbrowser.open("https://google.com")
        speak("Opening Google.")
    elif "open facebook" in c.lower():
        print("Opening Facebook...")  # Debugging line
        webbrowser.open("https://facebook.com")
        speak("Opening Facebook.")
    elif "open youtube" in c.lower():
        print("Opening YouTube...")  # Debugging line
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube.")
    elif "open linkedin" in c.lower():
        print("Opening LinkedIn...")  # Debugging line
        webbrowser.open("https://linkedin.com")
        speak("Opening LinkedIn.")
    elif c.lower().startswith("play"):
        print("Playing song...")  # Debugging line
        song = c.lower().split(" ")[1]
        link = music_library.music.get(song, None)
        if link:
            webbrowser.open(link)
            speak(f"Playing {song}.")
        else:
            speak(f"Sorry, I couldn't find {song} in my music library.")
    elif "weather" in c.lower():
        print("Checking weather...")  # Debugging line
        match = re.search(r'weather(?: in)? (\w+)', c, re.IGNORECASE)
        if match:
            city = match.group(1)
            weather_info = get_weather(city)
            speak(weather_info)
        else:
            speak("Please specify a city to get the weather information.")
    elif "remind me" in c.lower():
        try:
            # Extract task and time description from the command
            if "to" in c.lower():
                parts = c.lower().split(" to ", 1)
                task_part = parts[1]
                if " at " in task_part or " in " in task_part:
                    if " at " in task_part:
                        task, time_part = task_part.split(" at ", 1)
                    else:
                        task, time_part = task_part.split(" in ", 1)
                else:
                    task = task_part
                    time_part = "today"

                # Handle "in X minutes/hours" explicitly
                relative_match = re.match(r"(\d+)\s*(minute|hour)s?", time_part.lower())
                if relative_match:
                    value, unit = int(relative_match.group(1)), relative_match.group(2)
                    if unit == "minute":
                        reminder_time = datetime.now() + timedelta(minutes=value)
                    elif unit == "hour":
                        reminder_time = datetime.now() + timedelta(hours=value)
                else:
                    # Parse other time descriptions using dateparser
                    reminder_time = dateparser.parse(time_part)

                if not reminder_time:
                    raise ValueError("Invalid time format")

                # Convert to database-friendly format
                reminder_time_str = reminder_time.strftime("%Y-%m-%d %H:%M")
                add_reminder_to_db_reminder(task.strip(), reminder_time_str)
            else:
                raise ValueError("Invalid command format")
        except Exception as e:
            speak("Sorry, I couldn't set the reminder. Please provide a clear task and time.")
            print(f"Error: {e}")   
    elif "find" in c.lower() and "nearby" in c.lower():
        place_types = {
            "restaurant": "restaurant",
            "atm": "atm",
            "gas station": "gas station",
            "hospital": "hospital",
            "pharmacy": "pharmacy"
        }
        
        found = False
        for key in place_types:
            if key in c.lower():
                found = True
                latitude, longitude = get_user_location()
                if latitude and longitude:
                    find_nearby_places(place_types[key])
                else:
                    speak("I'm unable to determine your location.")
                break
        if not found:
            speak("Please specify the type of place you want to find nearby, such as restaurant, atm, or hospital.")
    elif "convert" in c.lower() and "currency" in c.lower():
        try:
            # Example format: "Convert 100 USD to INR"
            match = re.match(r'convert (\d+) (\w+) to (\w+)', c, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                from_currency = match.group(2).upper()
                to_currency = match.group(3).upper()
                
                # Call the currency converter function
                conversion_result = convert_currency(amount, from_currency, to_currency)
                
                # Speak the result to the user
                speak(f"{amount} {from_currency} is equal to {conversion_result} {to_currency}.")
            else:
                speak("Please use the format: Convert [amount] [from_currency] to [to_currency].")
        except Exception as e:
            speak("Sorry, I couldn't process the currency conversion. Please make sure the format is correct.")
            print(f"Error: {e}") 
    else:
        print("Command  recognized by AI process.")  # Debugging line
        output = aiProcess(c)
        speak(output)
        print(f"AI response: {output}")  # Debugging the AI response


def listen_for_commands():
    recognizer = sr.Recognizer()
    while st.session_state.is_running:
        try:
            with sr.Microphone() as source:
                print("Listening for commands...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            command = recognizer.recognize_google(audio).lower()
            print(f"Heard command: {command}")
            add_command_to_history(command)

            if "stop" in command:
                st.session_state.is_running = False
                speak("Goodbye! Have a great day.")
                stop_luna()
                break
            else:
                processCommand(command)

        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            # You can add this message to a list or use session state to show messages in the UI
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
        except Exception as e:
            print(f"Error in command listening: {e}")



# def start_listening():
#     global is_running
#     while is_running:
#         try:
#             with sr.Microphone() as source:
#                 print("Listening for wake word 'Luna'...")
#                 speak("Say Luna")

#                 # Adjust ambient noise quickly
                
#                 r.adjust_for_ambient_noise(source, duration=0.5)

#                 # Start listening
                
#                 audio = r.listen(source, timeout=5, phrase_time_limit=10)
               

#                 # Recognize the wake word
#                 word = r.recognize_google(audio).lower() 
#                 print(f"Heard: {word}")

#                 if "luna" in word:
#                     greet_user()  # Function to respond to user
#                     listen_for_commands()  # Transition to command mode

#         except sr.UnknownValueError:
#             print("Could not understand audio. Trying again...")
#             speak("I didn't catch that. Please try again.")
#         except sr.RequestError as e:
#             print(f"Request error from Google Speech API: {e}")
#         except sr.WaitTimeoutError:
#             print("Timeout: No speech detected.")
#         except Exception as e:
#             print(f"Error in start_listening: {e}")
#         finally:
#             time.sleep(1)  # Small pause to prevent CPU overload

def start_listening():
    if not st.session_state.get("is_initialized"):
        st.warning("Please initialize Luna first.")
        return
    
    st.session_state["is_running"] = True

    def listen():
        recognizer = sr.Recognizer()
        while st.session_state["is_running"]:
            try:
                with sr.Microphone() as source:
                    speak("Say 'Luna' to wake me up.")
                    print("Listening for 'Luna'...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                command = recognizer.recognize_google(audio).lower()
                print(f"Heard: {command}")

                if "luna" in command:
                    greet_user()
                    threading.Thread(target=listen_for_commands, daemon=True).start()

            except sr.UnknownValueError:
                print("Could not understand audio.")
                speak("I didn't catch that. Please try again.")
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                speak("There was an issue with speech recognition. Try again.")
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected.")
            except Exception as e:
                print(f"Error in listening: {e}")
    
    # Run the listener in a thread
    threading.Thread(target=listen, daemon=True).start()


def initialize_luna():
    st.session_state["is_initialized"] = True
    st.session_state["is_running"] = False
    speak("Initializing Luna...")
    print("Luna is ready!")
    
    

def start_luna():
    if not st.session_state.is_initialized:
        print("Luna is not initialized. Call initialize_luna first.")
        speak("Luna is not initialized. Press initialize Luna first.")
        return

    if st.session_state.is_running:
        print("Luna is already running.")
        return

    st.session_state.is_running = True
    # Start the listening in a background thread, but only update session state here
    threading.Thread(target=start_listening, daemon=True).start()
    print("Luna is now listening for commands.")




# def stop_luna():
#     global is_running
#     if not is_running:
#         print("Luna is not running.")
#         return
#     is_running = False
#     speak("Luna is shutting down!")
#     print("Luna has stopped.")
def stop_luna():
    """
    Stops the assistant and performs necessary cleanup.
    """
    st.session_state.is_running = False
    if st.session_state.listening_thread and st.session_state.listening_thread.is_alive():
        st.session_state.listening_thread.join()
    speak("Luna has been stopped. Goodbye!")



# Schedule the reminder checker
schedule.every(1).minute.do(check_reminders_from_db)

# Initialize the recognizer once
r = sr.Recognizer()

def add_command_to_history(command, user_id=None):
    print(st.session_state)  
    if user_id is None:
        if "user" in st.session_state:
            user_id = st.session_state["user"]["localId"]
        else:
            print("User not found in session state.")
            return

    add_history(user_id, command)
    print("Database updated!")

# def listen_for_commands():
#     while is_running:
#         try:
            
#             schedule.run_pending()
#             time.sleep(1)
#             with sr.Microphone() as source:
#                 print("Listening for commands...")
#                 speak("Speak Now")
#                 r.adjust_for_ambient_noise(source)
#                 audio = r.listen(source, timeout=5, phrase_time_limit=10)
#             command = r.recognize_google(audio).lower()
#             print(f"Heard command: {command}")# Debugging line to confirm command is heard
#             add_command_to_history(command)
#             if "stop" in command:
#                 speak("Goodbye , Have a good time")
#                 stop_luna()
#                 break
#             else:
#                 processCommand(command)
#         except sr.UnknownValueError:
#             print("Sorry, I couldn't understand that.")
#             speak("Sorry, I couldn't understand that. Please speak again.")
#         except sr.RequestError as e:
#             print(f"Speech recognition service error: {e}")
#             speak("Sorry , Speak again")
#         except Exception as e:
#             print(f"Error: {e}")
#             speak("Sorry, Speak again")





# if __name__ == "__main__":
#     try:
#         initialize_luna()
#         start_luna()
#         while is_running:
#             time.sleep(1)  # Keeps the main thread alive
#     except KeyboardInterrupt:
#         print("KeyboardInterrupt received. Shutting down Luna.")
#         stop_luna()
#     except Exception as e:
#         print(f"Unhandled exception: {e}")
#         stop_luna()