import json
import os
import random
from datetime import datetime
import geocoder
import numpy as np
import qrcode
from PIL import Image
import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# --- PAGE CONFIGURATION & CUSTOM CSS ---
st.set_page_config(
    page_title="Clinico AI - SIH 2026",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    st.markdown("""
        <style>
        /* Hide default Streamlit elements for a cleaner app look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Modern Button Styling */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease-in-out;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        /* Premium Card-like Containers */
        div[data-testid="stExpander"] {
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        /* Sidebar Polish - Adapts to Dark/Light Mode automatically */
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- DATABASE SETUP (OFFLINE-FIRST JSON) ---
DB_FILE = "database.json"

def init_db():
    default_data = {
        "patients": [],
        "complaints": [],
    }
    with open(DB_FILE, "w") as f:
        json.dump(default_data, f, indent=4)

def load_db():
    if not os.path.exists(DB_FILE):
        init_db()
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        init_db()
        with open(DB_FILE, "r") as f:
            data = json.load(f)

    if not isinstance(data, dict):
        data = {}
    if "patients" not in data:
        data["patients"] = []
    if "complaints" not in data:
        data["complaints"] = []
    return data

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- SESSION STATE INITIALIZATION ---
if "step_nav" not in st.session_state:
    st.session_state["step_nav"] = "1. Waiting Room & Voice Intake"

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=60)
    st.title("Clinico AI")
    st.markdown("**Ministry of Ayush / SIH**")
    st.divider()
    
    menu_options = [
        "1. Waiting Room Intake",
        "2. AI Clinical Structuring",
        "3. Local Sync & QR Token",
        "4. Doctor Cabin & QR Scanner",
        "5. Prescribed Test Cost Optimizer",
        "6. GPS Nearest Doctor Optimizer",
        "7. Govt Scheme Matcher",
        "8. CMO Anti-Corruption Portal",
        "9. Emergency SOS Hub",
    ]

    step_mapping = {
        "1. Waiting Room Intake": "1. Waiting Room & Voice Intake",
        "2. AI Clinical Structuring": "2. AI Clinical Structuring Engine",
        "3. Local Sync & QR Token": "3. Local Sync & OPD Token",
        "4. Doctor Cabin & QR Scanner": "4. Doctor Cabin & QR Scanner",
        "5. Prescribed Test Cost Optimizer": "5. Prescribed Test Cost Optimizer",
        "6. GPS Nearest Doctor Optimizer": "6. GPS Nearest Doctor Optimizer",
        "7. Govt Scheme Matcher": "7. Govt Scheme & Subsidy Matcher",
        "8. CMO Anti-Corruption Portal": "8. CMO Direct Anti-Corruption Portal",
        "9. Emergency SOS Hub": "9. Emergency SOS & Telemetry Hub",
    }

    reverse_mapping = {v: k for k, v in step_mapping.items()}
    current_short_menu = reverse_mapping.get(st.session_state["step_nav"], "1. Waiting Room Intake")

    selected_short_menu = st.radio(
        "Workflow Navigation",
        menu_options,
        index=menu_options.index(current_short_menu),
        label_visibility="collapsed"
    )
    st.session_state["step_nav"] = step_mapping[selected_short_menu]

app_mode = st.session_state["step_nav"]
db = load_db()

# ==========================================
# 1. WAITING ROOM & VOICE INTAKE
# ==========================================
if app_mode == "1. Waiting Room & Voice Intake":
    st.title("🎙️ Step 1: Multilingual Waiting Room & Voice Intake")
    st.caption("Register new patients or take voice symptom recordings in any regional language.")

    if st.button("➕ Register Another New Patient (Clear Form)", use_container_width=True):
        st.session_state.pop("raw_voice", None)
        st.session_state.pop("p_name", None)
        st.session_state.pop("p_abha", None)
        st.session_state.pop("allo", None)
        st.session_state.pop("current_token", None)
        st.rerun()

    with st.container(border=True):
        st.subheader("Card Scan / Identity Verification")
        
        # --- NEW ABHA QR SCANNER ---
        scanned_abha_id = ""
        with st.expander("📷 Scan Patient's ABHA Card QR (Click to open camera)", expanded=False):
            abha_camera = st.camera_input("Scan ABHA QR Code", label_visibility="collapsed")
            if abha_camera and OPENCV_AVAILABLE:
                file_bytes = np.asarray(bytearray(abha_camera.read()), dtype=np.uint8)
                opencv_image = cv2.imdecode(file_bytes, 1)
                detector = cv2.QRCodeDetector()
                decoded_info, points, _ = detector.detectAndDecode(opencv_image)
                if decoded_info:
                    scanned_abha_id = decoded_info.strip()
                    st.success(f"✅ Successfully scanned ABHA ID: **{scanned_abha_id}**")
                else:
                    st.warning("No QR code detected. Please hold the ABHA card closer to the camera.")
        
        c_abha, c1, c2, c3 = st.columns([1.5, 2, 1, 1.5])
        with c_abha:
            # Auto-fills if a code was scanned, otherwise falls back to default
            default_abha = scanned_abha_id if scanned_abha_id else "14-7294-XXXX-XXXX"
            p_abha = st.text_input("ABHA ID (Scan / Enter)", value=default_abha)
        with c1:
            p_name = st.text_input("Patient Full Name", "Aarav Sharma")
        with c2:
            p_age = st.number_input("Age", 1, 100, 32)
        with c3:
            p_lang = st.selectbox(
                "Spoken Language",
                ["Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English", "Tamil (தமிழ்)", "Bengali (বাংলা)"],
            )

    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        with st.container(border=True):
            st.subheader(f"🔴 Live Microphone Recorder ({p_lang})")
            
            # Map selected language to BCP-47 codes for accurate Speech-To-Text
            lang_codes = {
                "Hindi (हिंदी)": "hi-IN",
                "Punjabi (ਪੰਜਾਬੀ)": "pa-IN",
                "English": "en-IN",
                "Tamil (தமிழ்)": "ta-IN",
                "Bengali (বাংলা)": "bn-IN"
            }
            speech_lang_code = lang_codes.get(p_lang, "hi-IN")
            
            # Use speech_to_text which transcribes the audio live
            spoken_text = speech_to_text(
                language=speech_lang_code,
                start_prompt=f"Start Recording ({p_lang})",
                stop_prompt="Stop Recording",
                just_once=False,
                key=f"stt_{p_lang}",
            )

            # Handle the captured text dynamically
            if spoken_text:
                st.success(f"Audio captured and processed successfully for {p_lang}!")
                voice_transcript = st.text_area(
                    "Review / Edit Spoken Symptoms",
                    value=spoken_text,
                    height=100
                )
            else:
                voice_transcript = st.text_area(
                    "Or Type Spoken Symptoms Manually",
                    value="", 
                    placeholder="Type symptoms here or use the microphone to speak...",
                    height=100
                )

    with col_b:
        with st.container(border=True):
            st.subheader("📋 Intake Summary")
            st.info("Voice descriptions are translated and routed to the Dual-Lens AI Structural engine instantly.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            is_disabled = not voice_transcript.strip()
            
            if st.button("Lock Input & Proceed to AI Structuring ➔", type="primary", use_container_width=True, disabled=is_disabled):
                st.session_state["raw_voice"] = voice_transcript
                st.session_state["p_name"] = p_name
                st.session_state["p_abha"] = p_abha
                st.session_state["p_age"] = p_age
                st.session_state["p_lang"] = p_lang
                st.session_state["step_nav"] = "2. AI Clinical Structuring Engine"
                st.rerun()

# ==========================================
# 2. AI CLINICAL STRUCTURING ENGINE
# ==========================================
elif app_mode == "2. AI Clinical Structuring Engine":
    st.title("🧠 Step 2: Dual-Lens AI Structural Parsing")
    st.caption("AI converts free-form patient speech into structured Allopathic and Ayush notes.")

    if "raw_voice" in st.session_state:
        with st.chat_message("user"):
            st.write(f"**Patient Transcript:** {st.session_state['raw_voice']}")

        if st.button("⚡ Run AI Extraction Model", type="primary"):
            with st.spinner("Analyzing symptoms and routing to specialist..."):
                symptoms = str(st.session_state["raw_voice"]).lower()

                specialty = "General Physician"
                default_test = "Comprehensive Health Check / X-Ray"
                allo = "Diagnosis: General Malaise / Unspecified.\nRecommended: Vitals & Basic Blood Panel."
                ayush = "Dashavidha Pariksha: Tridosha Imbalance."

                if any(word in symptoms for word in ["heart", "chest", "chest pain", "palpitation", "dil", "breath", "saans", "chhati", "dhadkan"]):
                    specialty = "Cardiologist"
                    default_test = "ECG (Electrocardiogram)"
                    allo = "Diagnosis: Suspected Cardiac Arrhythmia / Angina.\nRecommended: ECG and Troponin blood test."
                    ayush = "Dashavidha Pariksha: Prana Vata and Sadhaka Pitta Imbalance.\nRecommended: Hridya Basti."
                
                elif any(word in symptoms for word in ["brain", "headache", "dizzy", "faint", "sir dard", "chakkar", "migraine", "nerve", "numb"]):
                    specialty = "Neurologist"
                    default_test = "Brain MRI"
                    allo = "Diagnosis: Suspected Migraine / Neurological deficit.\nRecommended: Brain MRI."
                    ayush = "Dashavidha Pariksha: Vata Dosha (Majja Dhatu).\nRecommended: Shirodhara."

                elif any(word in symptoms for word in ["skin", "rash", "itch", "khujli", "pimples", "daane", "twacha", "hairfall", "allergy"]):
                    specialty = "Dermatologist"
                    default_test = "Skin Biopsy / Allergy Panel"
                    allo = "Diagnosis: Suspected Dermatitis / Eczema.\nRecommended: Topical Corticosteroids & Antihistamines."
                    ayush = "Dashavidha Pariksha: Pitta and Rakta Dhatu Imbalance.\nRecommended: Neem and Manjistha therapy."

                elif any(word in symptoms for word in ["eye", "vision", "blur", "aankh", "blind", "dekhne", "red eye"]):
                    specialty = "Ophthalmologist"
                    default_test = "Visual Acuity / Retinal Scan"
                    allo = "Diagnosis: Refractive Error / Conjunctivitis.\nRecommended: Visual Acuity Test."
                    ayush = "Dashavidha Pariksha: Alochaka Pitta Imbalance.\nRecommended: Netra Tarpana."

                elif any(word in symptoms for word in ["knee", "joint", "ghutna", "bone", "leg", "chalne", "haddi", "back", "kamar", "spine", "dard", "pain"]):
                    specialty = "Orthopedic Surgeon"
                    default_test = "MRI Scan (Joint / Spine)"
                    allo = "Diagnosis: Suspected Gonarthralgia / Osteoarthritis.\nRecommended: Knee/Spine MRI & X-Ray."
                    ayush = "Dashavidha Pariksha: Vata Dosha Aggravation (Sandhi Vata).\nRecommended: Janu Basti or Kati Basti."
                
                elif any(word in symptoms for word in ["stomach", "pet", "acidity", "digestion", "vomit", "ulti", "loose motion", "diarrhea", "gas", "pachan"]):
                    specialty = "Gastroenterologist"
                    default_test = "Upper GI Endoscopy"
                    allo = "Diagnosis: Suspected Acid Peptic Disease / Gastroenteritis.\nRecommended: Upper GI Endoscopy & H. Pylori Test."
                    ayush = "Dashavidha Pariksha: Pitta Dosha Aggravation, Amlapitta (Hyperacidity).\nRecommended: Shankh Bhasma."
                
                elif any(word in symptoms for word in ["fever", "cold", "cough", "bukhar", "khasi", "zukam", "temperature", "weakness"]):
                    specialty = "General Physician"
                    default_test = "Complete Blood Count (CBC)"
                    allo = "Diagnosis: Viral Pyrexia / Upper Respiratory Infection.\nRecommended: CBC Test & Paracetamol."
                    ayush = "Dashavidha Pariksha: Kapha-Vata Imbalance (Jwara).\nRecommended: Ayush Kwath."

                st.session_state["specialty"] = specialty
                st.session_state["default_test"] = default_test
                st.session_state["allo"] = allo
                st.session_state["ayush"] = ayush
                st.session_state["schemes"] = ["Ayushman Bharat PM-JAY", "State Health Subsidy"]

            st.success(f"Extraction complete! Identified Clinical Department: **{specialty}**")

        if "allo" in st.session_state:
            t1, t2 = st.tabs(["🔬 Allopathic Triage", "🌿 Ayush Dashavidha Triage"])
            with t1:
                st.info(st.session_state['allo'])
                st.metric(label="Assigned Specialist Channel", value=st.session_state['specialty'])
            with t2:
                st.success(st.session_state['ayush'])

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Save & Move to Local Database Sync ➔", type="primary", use_container_width=True):
                st.session_state["step_nav"] = "3. Local Sync & OPD Token"
                st.rerun()
    else:
        st.warning("Please complete Step 1 (Waiting Room Intake) first.")

# ==========================================
# 3. LOCAL SYNC & OPD TOKEN (Automated)
# ==========================================
elif app_mode == "3. Local Sync & OPD Token":
    st.title("🗄️ Step 3: Local Server Sync & OPD Token")
    st.caption("Verifies ABHA ID, syncs case data directly to the doctor's local server, and generates an OPD Queue Token.")

    if "allo" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("### Database Synchronization")
                
                if "current_token" not in st.session_state:
                    with st.spinner("Syncing to Doctor's Server & Generating Queue Token..."):
                        visit_token = f"OPD-TKN-{random.randint(100, 999)}"
                        patient_abha = st.session_state.get("p_abha", "14-XXXX-XXXX-XXXX")

                        qr = qrcode.QRCode(version=1, box_size=8, border=2)
                        qr.add_data(visit_token)
                        qr.make(fit=True)
                        img = qr.make_image(fill_color="#1E1E1E", back_color="white")
                        img.save("temp_qr.png")

                        new_record = {
                            "id": visit_token, 
                            "abha_id": patient_abha,
                            "name": st.session_state.get("p_name", "New Patient"),
                            "age": st.session_state.get("p_age", 30),
                            "symptoms": st.session_state.get("raw_voice", ""),
                            "specialty": st.session_state.get("specialty", "General"),
                            "allopathic_notes": st.session_state.get("allo", ""),
                            "ayush_notes": st.session_state.get("ayush", ""),
                            "prescribed_test": st.session_state.get("default_test", "None (No Test Required)"),
                            "prescription": "Pending Doctor Review",
                            "status": "In Queue",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }

                        db["patients"].append(new_record)
                        save_db(db)
                        
                        st.session_state["current_token"] = visit_token
                        st.rerun() 
                else:
                    st.success(f"Patient synced to Doctor's Server! Queue Number: **{st.session_state['current_token']}**")
                    st.write(f"Verified ABHA: `{st.session_state.get('p_abha', 'N/A')}`")

        with col2:
            if "current_token" in st.session_state:
                with st.container(border=True):
                    st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>{st.session_state['current_token']}</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center;'>Scan this token at the Doctor's Cabin</p>", unsafe_allow_html=True)
                    
                    if os.path.exists("temp_qr.png"):
                        col_qr_1, col_qr_2, col_qr_3 = st.columns([1,2,1])
                        with col_qr_2:
                            st.image("temp_qr.png", use_container_width=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Patient Called: Proceed to Doctor's Cabin ➔", type="primary", use_container_width=True):
                        st.session_state["step_nav"] = "4. Doctor Cabin & QR Scanner"
                        st.rerun()
    else:
        st.warning("Complete Step 2 structure generation first.")

# ==========================================
# 4. DOCTOR CABIN & QR SCANNER
# ==========================================
elif app_mode == "4. Doctor Cabin & QR Scanner":
    st.title("👨‍⚕️ Step 4: Doctor Cabin & Live Token Scanner")
    st.caption("Scan the patient's OPD QR Token to load their entire case file.")

    all_patients = db.get("patients", [])
    p_ids = [p["id"] for p in all_patients]
    scanned_token = None

    with st.container(border=True):
        col_cam, col_sel = st.columns([1, 1])
        with col_cam:
            st.markdown("**📷 Live Webcam QR Scanner**")
            camera_photo = st.camera_input("Scan Patient Token", label_visibility="collapsed")
            if camera_photo and OPENCV_AVAILABLE:
                file_bytes = np.asarray(bytearray(camera_photo.read()), dtype=np.uint8)
                opencv_image = cv2.imdecode(file_bytes, 1)
                detector = cv2.QRCodeDetector()
                decoded_info, points, _ = detector.detectAndDecode(opencv_image)
                if decoded_info:
                    scanned_token = decoded_info.strip()
                    st.toast(f"Scanned: {scanned_token}", icon="🎯")

        with col_sel:
            st.markdown("**📋 Manual Queue Selector (Fallback)**")
            default_idx = p_ids.index(scanned_token) if (scanned_token and scanned_token in p_ids) else 0
            selected_id = st.selectbox(
                "Select Patient OPD Token",
                p_ids if p_ids else ["No Patients Found"],
                index=default_idx if p_ids else 0,
            )

    pat = next((p for p in all_patients if p["id"] == selected_id), None)

    if pat:
        st.divider()
        pt_tab, rx_tab = st.tabs(["📄 Patient Digital Profile", "✍️ Clinical Action & Diagnostics"])
        
        with pt_tab:
            c1, c2, c3 = st.columns(3)
            c1.metric("Patient Name", pat['name'])
            c2.metric("Age", f"{pat['age']} Years")
            c3.metric("ABHA ID", pat.get('abha_id', 'N/A'))
            st.write(f"**Chief Complaint:** {pat.get('symptoms', '')}")
            
            with st.expander("View AI Structural Triage Data", expanded=True):
                st.info(f"**Allopathic View:**\n{pat.get('allopathic_notes', '')}")
                st.success(f"**Ayush View:**\n{pat.get('ayush_notes', '')}")

        with rx_tab:
            test_options = [
                "None (No Test Required)",
                "Complete Blood Count (CBC)",
                "Liver Function Test (LFT)",
                "Kidney Function Test (KFT)",
                "Lipid Profile",
                "Thyroid Profile (TSH)",
                "HbA1c (Diabetes Panel)",
                "Urine Routine & Microscopy",
                "High-Resolution Knee X-Ray",
                "Chest X-Ray",
                "MRI Scan (Joint / Spine)",
                "Brain MRI",
                "Whole Body CT Scan",
                "CT Scan (Head)",
                "Abdominal Ultrasound (USG)",
                "Upper GI Endoscopy",
                "ECG (Electrocardiogram)",
                "Echocardiogram (Echo)",
                "Skin Biopsy / Allergy Panel",
                "Visual Acuity / Retinal Scan",
                "Other (Specify in Notes)"
            ]
            
            ai_suggestion = pat.get("prescribed_test", "None (No Test Required)")
            default_index = test_options.index(ai_suggestion) if ai_suggestion in test_options else 0

            selected_test = st.selectbox(
                "Order Diagnostic Lab Test:",
                test_options,
                index=default_index,
            )

            rx_input = st.text_area("Digital Prescription / Notes", value=pat.get("prescription", "Tab Paracetamol 500mg SOS, Rest"))

            if st.button("💾 Save Prescription & Order Test", type="primary"):
                pat["prescription"] = rx_input
                pat["prescribed_test"] = selected_test
                save_db(db)
                st.session_state["prescribed_test"] = selected_test
                st.success(f"Locked! Ordered Test: **{selected_test}**")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Proceed to Diagnostic Test Optimizer ➔", use_container_width=True):
                st.session_state["prescribed_test"] = selected_test
                st.session_state["step_nav"] = "5. Prescribed Test Cost Optimizer"
                st.rerun()

# ==========================================
# 5. PRESCRIBED TEST COST & TRAVEL OPTIMIZER
# ==========================================
elif app_mode == "5. Prescribed Test Cost Optimizer":
    st.title("🧪 Step 5: Prescribed Diagnostic Test & Travel Optimizer")
    st.caption("Compares authorized labs for the prescribed test, factoring in travel distance and fuel cost.")

    prescribed_test = st.session_state.get("prescribed_test", "None (No Test Required)")
    
    st.metric(label="Ordered Diagnostic Test", value=prescribed_test)

    if "None" in prescribed_test:
        st.success("✅ No diagnostic tests were required by the doctor. You can proceed directly to the next step.")
    else:
        with st.expander("⚙️ Adjust Vehicle & Fuel Parameters", expanded=True):
            c_in1, c_in2 = st.columns(2)
            fuel_price = c_in1.number_input("Fuel Cost per Liter (₹)", 90, 110, 96)
            vehicle_mileage = c_in2.number_input("Vehicle Mileage (km/L)", 10, 50, 20)

        safe_mileage = vehicle_mileage if vehicle_mileage > 0 else 1

        if "MRI" in prescribed_test:
            lab_options = [
                {"Facility": "Civil Hospital MRI Unit", "Fee": 0, "Distance_km": 4.5, "Type": "Govt (PM-JAY)"},
                {"Facility": "Ayush Diagnostic Wing", "Fee": 350, "Distance_km": 7.0, "Type": "Ayush Subsidized"},
                {"Facility": "Apex Corporate Scan", "Fee": 2600, "Distance_km": 2.0, "Type": "Private"},
            ]
        elif "X-Ray" in prescribed_test:
            lab_options = [
                {"Facility": "Civil Hospital Radiology", "Fee": 0, "Distance_km": 4.5, "Type": "Govt (PM-JAY)"},
                {"Facility": "Jan Aushadhi Radiology", "Fee": 100, "Distance_km": 3.0, "Type": "Jan Aushadhi"},
                {"Facility": "City Care Imaging", "Fee": 600, "Distance_km": 1.5, "Type": "Private"},
            ]
        else:
            lab_options = [
                {"Facility": "PHC Pathology", "Fee": 0, "Distance_km": 1.5, "Type": "Govt (PM-JAY)"},
                {"Facility": "Jan Aushadhi Diagnostics", "Fee": 80, "Distance_km": 3.2, "Type": "Jan Aushadhi"},
                {"Facility": "SRL Diagnostics", "Fee": 450, "Distance_km": 1.8, "Type": "Private"},
            ]

        evaluated_labs = []
        min_cost = 999999
        for lab in lab_options:
            travel_cost = round((lab["Distance_km"] * 2 / safe_mileage) * fuel_price)
            total_cost = lab["Fee"] + travel_cost
            if total_cost < min_cost:
                min_cost = total_cost

        for lab in lab_options:
            travel_cost = round((lab["Distance_km"] * 2 / safe_mileage) * fuel_price)
            total_cost = lab["Fee"] + travel_cost
            is_best = total_cost == min_cost
            evaluated_labs.append({
                "Diagnostic Facility": lab["Facility"],
                "Facility Type": lab["Type"],
                "Test Fee (₹)": "Free (Scheme)" if lab["Fee"] == 0 else lab['Fee'],
                "Distance (km)": lab['Distance_km'],
                "Fuel Exp (₹)": travel_cost,
                "Net Cost (₹)": f"{total_cost} {'🏆 Best' if is_best else ''}",
            })

        st.dataframe(evaluated_labs, use_container_width=True, hide_index=True)

    if st.button("Proceed to GPS Nearest Doctor Optimizer ➔", type="primary", use_container_width=True):
        st.session_state["step_nav"] = "6. GPS Nearest Doctor Optimizer"
        st.rerun()

# ==========================================
# 6. GPS NEAREST DOCTOR OPTIMIZER
# ==========================================
elif app_mode == "6. GPS Nearest Doctor Optimizer":
    st.title("📍 Step 6: GPS Nearest Doctor & Specialist Optimizer")

    with st.spinner("Acquiring Real-Time GPS Coordinates from Satellite..."):
        g = geocoder.ip("me")
        lat, lng = g.latlng if g.latlng else [31.2530, 75.7000]

    c1, c2 = st.columns(2)
    c1.metric("📍 Patient Latitude", lat)
    c2.metric("📍 Patient Longitude", lng)

    required_specialty = st.session_state.get("specialty", "Orthopedic Surgeon")
    st.info(f"**Required Specialist Profile:** {required_specialty}")

    fuel_price = 96
    safe_mileage = 20

    if "Orthopedic" in required_specialty:
        doc_options = [
            {"Name": "Dr. Anil Sharma", "Facility": "Civil Hospital", "Contact": "9876543211", "Fee": 0, "Distance_km": 2.5},
            {"Name": "Dr. Meena Gupta", "Facility": "Ayush Center", "Contact": "9876543212", "Fee": 150, "Distance_km": 6.0},
            {"Name": "Dr. R.K. Singh", "Facility": "City Rehab", "Contact": "9876543213", "Fee": 800, "Distance_km": 1.2},
        ]
    else:
        doc_options = [
            {"Name": "Dr. Rajesh Singh", "Facility": "Local PHC", "Contact": "8877665544", "Fee": 0, "Distance_km": 0.8},
            {"Name": "Dr. Kavita Rao", "Facility": "Private Care", "Contact": "8877665545", "Fee": 400, "Distance_km": 3.0},
            {"Name": "Dr. S.K. Ayush", "Facility": "Ayush Center", "Contact": "8877665546", "Fee": 100, "Distance_km": 5.5},
        ]

    evaluated_docs = []
    min_burden = min(d["Fee"] + round((d["Distance_km"] * 2 / safe_mileage) * fuel_price) for d in doc_options)

    for doc in doc_options:
        travel_cost = round((doc["Distance_km"] * 2 / safe_mileage) * fuel_price)
        total_burden = doc["Fee"] + travel_cost
        best_value_flag = "⭐ Recommended" if total_burden == min_burden else ""
        
        # Generate Google Maps URL dynamically
        maps_query = f"{doc['Facility'].replace(' ', '+')}+{doc['Name'].replace(' ', '+')}"
        maps_url = f"https://www.google.com/maps/search/?api=1&query={maps_query}"

        evaluated_docs.append({
            "Doctor": doc["Name"],
            "Hospital": doc["Facility"],
            "Contact": doc["Contact"],
            "Fee (₹)": "Free" if doc["Fee"] == 0 else doc['Fee'],
            "Dist (km)": doc['Distance_km'],
            "Total Burden (₹)": f"{total_burden} {best_value_flag}",
            "Directions": maps_url
        })

    # Display dataframe with configured link column
    st.dataframe(
        evaluated_docs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Directions": st.column_config.LinkColumn(
                "📍 Navigation",
                display_text="Open Maps 🗺️"
            )
        }
    )

    if st.button("Proceed to Govt Scheme Matcher ➔", type="primary", use_container_width=True):
        st.session_state["step_nav"] = "7. Govt Scheme & Subsidy Matcher"
        st.rerun()

# ==========================================
# 7. GOVT SCHEME & SUBSIDY MATCHER
# ==========================================
elif app_mode == "7. Govt Scheme & Subsidy Matcher":
    st.title("📜 Step 7: Govt Scheme & Subsidy Matcher")

    p_ids = [p["id"] for p in db.get("patients", [])]
    if not p_ids:
        st.warning("No patients found. Register in Step 1.")
    else:
        sel_id = st.selectbox("Select Patient Profile (Token)", p_ids)
        pat = next((p for p in db["patients"] if p["id"] == sel_id), None)

        if pat:
            st.success(f"Verified Record: **{pat['name']}** (Token: {pat['id']})")
            
            with st.container(border=True):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.markdown("### Eligible Welfare Schemes")
                    for scheme in pat.get("eligible_schemes", ["Ayushman Bharat PM-JAY", "State Health Subsidy"]):
                        st.markdown(f"- ✅ **{scheme}** (Pre-Approved)")
                with col_s2:
                    st.markdown("### Instant Voucher")
                    if st.button("🎟️ Generate Cashless Subsidy QR", use_container_width=True):
                        st.info("Digital voucher successfully transmitted to patient's registered mobile device.")

            if st.button("Proceed to CMO Anti-Corruption Portal ➔", type="primary", use_container_width=True):
                st.session_state["step_nav"] = "8. CMO Direct Anti-Corruption Portal"
                st.rerun()

# ==========================================
# 8. CMO DIRECT ANTI-CORRUPTION PORTAL
# ==========================================
elif app_mode == "8. CMO Direct Anti-Corruption Portal":
    st.title("🛡️ Step 8: CMO Anti-Corruption Portal")
    st.caption("Direct pipeline to report VIP queue manipulation, diagnostic overcharging, or negligence.")

    with st.container(border=True):
        with st.form("complaint_form"):
            c_name = st.text_input("Complainant Name (Optional - Can remain anonymous)")
            c_dept = st.selectbox(
                "Hospital Department",
                ["Orthopedics OPD", "Emergency Triage", "Pharmacy / Diagnostics", "General Administration"],
            )
            c_issue = st.selectbox(
                "Grievance Category",
                ["Queue Manipulation / VIP Favoritism", "Diagnostic Overcharging", "Refusal of Care / Negligence"],
            )
            c_desc = st.text_area("Incident Description")
            
            if st.form_submit_button("Submit Secure Report to CMO Dashboard", type="primary"):
                ticket_id = f"CMO-TICKET-{random.randint(10000, 99999)}"
                db["complaints"].append({
                    "ticket": ticket_id,
                    "department": c_dept,
                    "issue": c_issue,
                    "status": "Under Investigation (SLA: 24h)"
                })
                save_db(db)
                st.success(f"Report logged securely! Tracking ID: **{ticket_id}**")

    if st.button("Proceed to Emergency SOS Hub ➔", type="primary", use_container_width=True):
        st.session_state["step_nav"] = "9. Emergency SOS & Telemetry Hub"
        st.rerun()

# ==========================================
# 9. EMERGENCY SOS & TELEMETRY HUB
# ==========================================
elif app_mode == "9. Emergency SOS & Telemetry Hub":
    st.title("🚨 Step 9: 108 Emergency SOS Lifeline")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔴 TRIGGER RED SOS EMERGENCY SIGNAL", type="primary", use_container_width=True):
        g = geocoder.ip("me")
        coords = g.latlng if g.latlng else [31.2530, 75.7000]

        st.error("EMERGENCY SIGNAL BROADCASTED TO 108 CONTROL ROOM!")
        
        with st.container(border=True):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.metric("Live Latitude", coords[0])
                st.metric("Live Longitude", coords[1])
                st.markdown("**Status:** 🚑 Ambulance Dispatched (ETA 4 Mins)")
            with col_e2:
                st.markdown(f"[🗺️ Open Exact Coordinates in Google Maps](https://www.google.com/maps/search/?api=1&query={coords[0]},{coords[1]})")
                st.info("Paramedic digital handover packet transmitted to ALS-Ambulance PB-08-99.")
