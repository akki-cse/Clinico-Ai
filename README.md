# 🩺 Clinico AI - Smart Healthcare Triage & Optimization Platform
**Developed for Smart India Hackathon (SIH) 2026 | Ministry of Ayush**

Clinico AI is a comprehensive, offline-first digital healthcare platform designed to streamline the patient journey from the waiting room to the doctor's cabin and beyond. It leverages native Speech-to-Text, localized AI symptom structuring, ABHA ID verification, and geo-location to reduce hospital wait times, optimize diagnostic costs, and enforce systemic transparency.

## ✨ Key Features (The 9-Step Workflow)

1. **🎙️ Multilingual Waiting Room & Voice Intake:** Captures patient symptoms via live microphone in multiple regional languages (Hindi, Punjabi, English, Tamil, Bengali) using browser-native Speech-to-Text.
2. **🧠 Dual-Lens AI Structural Parsing:** Automatically routes patients to the correct department (Cardiology, Orthopedics, etc.) and generates both **Allopathic** and **Ayush (Dashavidha Pariksha)** clinical notes based on spoken symptoms.
3. **🗄️ Local Sync & OPD Token:** Integrates with India's ABHA ID system to generate a unique QR-based OPD Visit Token, syncing directly to the doctor's local server (offline-first JSON database).
4. **👨‍⚕️ Doctor Cabin & QR Scanner:** Allows doctors to use a webcam to scan the patient's OPD Token, instantly pulling up the AI-generated case file to prescribe medications or diagnostic tests.
5. **🧪 Prescribed Test Cost Optimizer:** Compares government, Jan Aushadhi, and private labs, calculating the total financial burden by factoring in test fees, vehicle mileage, and real-time fuel costs.
6. **📍 GPS Nearest Doctor Optimizer:** Uses IP-based geolocation to find the nearest appropriate specialists and calculates the most cost-effective travel and consultation routes.
7. **📜 Govt Scheme & Subsidy Matcher:** Automatically cross-references the patient's ABHA profile with state and central schemes (e.g., PM-JAY) and generates instant cashless QR vouchers.
8. **🛡️ CMO Anti-Corruption Portal:** A secure, direct-to-CMO pipeline for patients to anonymously report queue manipulation, VIP favoritism, or diagnostic overcharging.
9. **🚨 Emergency SOS Hub:** A 1-click 108 Emergency trigger that instantly captures live coordinates and dispatches them to the nearest ALS ambulance.

## 🛠️ Technology Stack
* **Frontend/UI:** Streamlit (Python)
* **Voice Processing:** `streamlit-mic-recorder` (Native Web Speech-to-Text API)
* **QR Generation & Scanning:** `qrcode`, `Pillow`, `opencv-python` (cv2), `numpy`
* **Geolocation:** `geocoder`
* **Database:** Offline-first Local JSON (`database.json`)

## ⚙️ Prerequisites & Installation

Make sure you have Python 3.8 or higher installed on your system. 

1. **Clone or Download the Repository**
2. **Install Required Python Packages:**
   Open your terminal/command prompt and run the following command:
   ```bash
   pip install streamlit streamlit-mic-recorder qrcode pillow numpy geocoder opencv-python

   🚀 How to Run the Application
Navigate to the folder containing your code in the terminal.

Run the Streamlit app:

Bash
streamlit run app.py
(Note: Replace app.py with whatever you named your Python file).

The application will automatically open in your default web browser at http://localhost:8501.

📁 Database Architecture
To ensure the system works seamlessly in rural areas with poor internet connectivity, the app utilizes an Offline-First JSON Database.

Upon running the app for the first time, a database.json file is automatically generated in the root directory.

Patient intakes, tokens, prescribed tests, and CMO grievances are securely appended to this local file.

⚠️ Important Notes for Testing
Microphone Permissions: When using Step 1, your browser will ask for microphone permissions. Please "Allow" to test the live multilingual speech-to-text functionality.

Webcam Permissions: Step 4 requires camera access to test the live QR code token scanning.

Language Support: The speech recognition accuracy relies on your browser's native engine (Google Chrome is highly recommended for the best Hindi/Punjabi/Regional dialect processing).
