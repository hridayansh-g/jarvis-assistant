import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import cohere
import speech_recognition as sr
import eel
from gtts import gTTS
import playsound
import uuid
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
cohere_api_key = os.getenv("COHERE_API_KEY")

# Initialize Cohere
co = cohere.Client(cohere_api_key)

# 🎙️ Initialize pyttsx3 & speech recognition
engine = pyttsx3.init('nsss')  # For macOS
engine.setProperty('rate', 200)  # 🐢 Slow down speech rate (default ~200)
listener = sr.Recognizer()

# Set voice properties
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

chat_history = []

def talk(text):
    print(f"Jarvis says: {text}")
    eel.showChat("Jarvis", text)
    try:
        tts = gTTS(text=text, lang='en', tld='co.in')  # 🇮🇳 Indian accent
        filename = f"temp_{uuid.uuid4()}.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print("⚠️ TTS error:", e)

def welcome_message():
    talk("Hello Hridayansh! Jarvis is online. Ready to assist you anytime.")

def take_command():
    print("🎤 Starting take_command()...")
    try:
        with sr.Microphone() as source:
            print("🎙️ Adjusting for background noise...")
            listener.adjust_for_ambient_noise(source, duration=1)
            print("🟢 Listening for up to 7 seconds...")
            voice = listener.listen(source, timeout=5, phrase_time_limit=7)
            print("🎧 Got audio, recognizing...")
            try:
                command = listener.recognize_google(voice, language='en-IN').lower().strip()
            except:
                command = listener.recognize_google(voice, language='hi-IN').lower().strip()
            print(f"🗣️ You said: {command}")
            return command
    except sr.WaitTimeoutError:
        print("⏳ Timeout: No one spoke.")
        talk("You didn't say anything. Please try again.")
    except sr.UnknownValueError:
        print("🤷 Couldn't understand the speech.")
        talk("Sorry, I did not understand.")
    except sr.RequestError:
        print("🌐 Network error with Google API.")
        talk("Network error. Please check your internet connection.")
    except Exception as e:
        print("❌ Unknown error in take_command():", e)
        talk("An unexpected error occurred.")
    return ""

def get_ai_reply(query):
    prompt = f"""
You are Jarvis, a smart AI assistant. Reply to the following user message briefly and clearly in 1-3 sentences. Do not explain too much. Avoid long paragraphs.

User: {query}
Jarvis:
"""
    try:
        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=200,
            temperature=0.5
        )
        reply = response.generations[0].text.strip()
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print("🛑 Cohere Chat Error:", e)
        return "Sorry, I couldn't get a response."

def parse_command(command):
    prompt = f"""
You are an intelligent voice assistant. Your job is to classify the user's spoken input into one of the following intent keywords:

- play_song
- tell_time
- search_wikipedia
- tell_joke
- relationship_status
- ai_chat
- unknown

Here are examples for reference:

- "play kesariya song" → play_song  
- "kya time hua hai" → tell_time  
- "who is virat kohli" → search_wikipedia  
- "मुझे जोक सुनाओ" → tell_joke  
- "are you single" → relationship_status  
- "jarvis tum kya kar sakte ho?" → ai_chat  
- "tell me any latest news" → ai_chat  
- "prime minister of india" → ai_chat  
- "बिना मतलब की बात" → unknown

👉 If you're unsure or no clear intent is matched, default to **ai_chat**.

Return only one of the 7 keywords exactly. No explanation.

User input: "{command}"
"""
    try:
        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=6,
            temperature=0.2
        )
        intent = response.generations[0].text.strip().lower()
        return intent
    except Exception as e:
        print("Intent parsing error:", e)
        return "unknown"
# --------- Handlers ---------

def handle_play_command(command):
    song = command.replace('play', '').strip()
    talk(f'Playing {song}')
    try:
        pywhatkit.playonyt(song)
    except Exception as e:
        print("YouTube error:", e)
        talk("Sorry, I couldn't play the song.")

def handle_time_command():
    time_now = datetime.datetime.now().strftime('%I:%M %p')
    talk('Current time is ' + time_now)

def handle_whois_command(command):
    person = command.replace('who is', '').replace('what is', '').strip()
    if not person:
        talk("Please specify whom or what you want to know about.")
        return
    try:
        info = wikipedia.summary(person, sentences=2)
        talk(info)
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            info = wikipedia.summary(e.options[0], sentences=2)
            talk(info)
        except Exception:
            talk("Sorry, I couldn't find clear information.")
    except wikipedia.exceptions.PageError:
        talk(f"Sorry, no information found about {person}.")
    except Exception:
        talk("Sorry, something went wrong while searching.")

def handle_joke_command():
    try:
        response = co.generate(
            model='command-r-plus',
            prompt="Tell me a short, funny joke in one line.",
            max_tokens=30
        )
        joke = response.generations[0].text.strip()
        talk(joke)
    except Exception as e:
        print("Joke error:", e)
        talk("Sorry, I couldn't find a joke right now.")

def handle_relationship_command(command):
    if 'date' in command:
        talk('Sorry, I have a headache.')
    elif 'single' in command or 'relationship' in command:
        talk('I am in a relationship with WiFi.')
    else:
        talk('Love is complicated, my friend.')

def handle_ai_chat(command):
    response = get_ai_reply(command)
    talk(response)

# --------- Main Controller ---------

def start_jarvis():
    command = take_command()
    if not command:
        return

    eel.showChat("You", command)

    greetings = ["jarvis", "hello", "hi", "hey", "you"]

    if command.strip() in greetings:
        if command == "jarvis":
            talk("Hello Hridayansh! Jarvis is online. Ready to assist you anytime.")
        elif command == "you":
            talk("Yes Hridayansh, I am listening.")
        else:
            talk("Hello! How can I assist you today?")
        return

    intent = parse_command(command)
    print(f"🧠 Detected Intent: {intent}")

    if intent == 'play_song':
        handle_play_command(command)
    elif intent == 'tell_time':
        handle_time_command()
    elif intent == 'search_wikipedia':
        handle_whois_command(command)
    elif intent == 'tell_joke':
        handle_joke_command()
    elif intent == 'relationship_status':
        handle_relationship_command(command)
    elif intent == 'ai_chat':
        handle_ai_chat(command)
    else:
        talk("I'm not sure what you meant. Please repeat.")