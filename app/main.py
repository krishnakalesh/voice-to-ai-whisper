import os
import whisper
import requests
import pyaudio
import wave
import tempfile
import warnings
import pyttsx3

from dotenv import load_dotenv
from openai import OpenAI

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

load_dotenv()
OPEN_API_KEY =os.getenv("OPENAI_API_KEY")

# Constants
CHUNK = 1024# Buffer size
FORMAT = pyaudio.paInt16# Audio format
CHANNELS = 1# Mono audio
RATE = 16000# Sample rate

def capture_audio(duration):
    """Capture live audio from the microphone."""
    print("Capturing audio.")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording complete.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        with wave.open(temp_audio.name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        return temp_audio.name

def transcribe_audio(audio_file_path):
    try:
        print(f"File exists:{audio_file_path}:  {os.path.exists(audio_file_path)}")
        model = whisper.load_model("tiny")# Load Whisper model
        print("Transcribing audio...")
        result = model.transcribe(audio_file_path)
        print(result.get("text", ""))
        return result.get("text", "")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

# Function to play text on the speaker
def speak_text(text):
    print(f"Speaking text: {text}")
    engine = pyttsx3.init() # Initialize the TTS engine
    # Optional: Set properties (voice, rate, volume)
    engine.setProperty('rate', 150) # Speed of speech (default is ~200)
    engine.setProperty('volume', 1.0)# Volume (0.0 to 1.0)
    # Speak the text
    engine.say(text)
    engine.runAndWait()

def get_openai_response(prompt):
  try:
    print("Calling  open ai...")
    client = OpenAI(api_key=OPEN_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.01,
    )
    return response.choices[0].message.content
  except Exception as e:
    print(f"Error: {e}")
    return None

def call_business_api(question):
    """Call LLM API with the transcribed question."""
    url = "http://localhost:8080/business/"
    payload = {"question": question}
    headers = {"Content-Type": "application/json"}
    try:
        print(f"Calling API with question: {question}")
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            print("API Response:", response_json)
            business_res = response_json.get("business_response", "")
            if business_res:
                speak_text(business_res)
            else:
                print("No business response to play.")
        else:
            print("Failed to get response. Status Code:", response.status_code)
            print("Response:", response.text)
    except Exception as e:
        print(f"Error while calling API: {e}")

# Transcribe audio
if __name__ == "__main__":
    try:
        duration = int(input("Enter recording duration (seconds): "))
        audio_file = capture_audio(duration)
        transcribed_text = transcribe_audio(audio_file)
        if transcribed_text:
            print("Transcribed Text:", transcribed_text)
            business_response = get_openai_response(transcribed_text)
            if business_response:
                speak_text(business_response)
            else:
                print("No business response to play.") 

        else:
            print("Transcription failed.")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")