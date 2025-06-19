import eel
from jarvis_functions import start_jarvis, welcome_message

# Initialize Eel app folder
eel.init('web')

@eel.expose
def run_jarvis():
    print("Jarvis activated from UI")
    start_jarvis()

def start_app():
    try:
        welcome_message()
        eel.start('index.html', size=(600, 400), port=8000, mode='chrome')
    except Exception as e:
        print("Error starting the app:", e)

if __name__ == "__main__":
    start_app()