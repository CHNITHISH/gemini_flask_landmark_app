from flask import Flask, render_template, request
import os
import google.generativeai as genai
import folium
from gtts import gTTS
import base64
import plotly.graph_objects as go

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up Gemini API key
genai.configure(api_key="AIzaSyD4m718IwSa97TqWR6VgRkdQm_W7DNeamI")

# Function to fetch landmark description using Gemini
def fetch_landmark_description(place_name):
    prompt = f"Provide a detailed history and description of {place_name}."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip() if response.text else "No description available."

# Function to generate video script
def generate_landmark_video(description):
    prompt = f"Create a detailed video script explaining: {description}."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip() if response.text else "No video script available."

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts_path = os.path.join(app.config['UPLOAD_FOLDER'], "description.mp3")
    tts.save(tts_path)
    return tts_path

# Function to generate a 3D model visualization
def generate_3d_model():
    fig = go.Figure(
        data=[go.Mesh3d(x=[0, 1, 2, 0], y=[0, 1, 0, 2], z=[0, 1, 2, 3],
                        i=[0, 0, 0, 1], j=[1, 2, 3, 2], k=[2, 3, 1, 3],
                        color='lightblue', opacity=0.50)]
    )
    model_path = os.path.join(app.config['UPLOAD_FOLDER'], "3d_model.html")
    fig.write_html(model_path)
    return model_path

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    description = video_script = tts_path = img_path = model_path = None

    if request.method == "POST":
        landmark = request.form.get("landmark")
        uploaded_file = request.files.get("image")

        if uploaded_file:
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(img_path)

        if landmark:
            description = fetch_landmark_description(landmark)
            video_script = generate_landmark_video(description)
            tts_path = text_to_speech(description)
            model_path = generate_3d_model()

    return render_template("index.html", description=description, video_script=video_script,
                           tts_path=tts_path, img_path=img_path, model_path=model_path)

if __name__ == "__main__":
    app.run(debug=True)
