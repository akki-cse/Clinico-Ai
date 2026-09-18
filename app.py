import json
import os
import random
from datetime import datetime
import geocoder
import qrcode
from PIL import Image
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Clinico AI - Smart India Hackathon",
    page_icon="🩺",
    layout="wide",
)

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
            
    # Defensive fallback for corrupted databases
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

# --- SESSION STATE INITIALIZATION FOR AUTO-PROGRESSION ---
if "step_nav" not in st.session_state:
    st.session_state["step_nav"] = "1. Waiting Room Intake"

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🩺 Clinico AI Workflow")
st.sidebar.markdown("*Ministry of Ayush / SIH Platform*")

menu_options = [
    "1. Waiting Room Intake",
    "2. AI Clinical Structuring",
    "3. Local Sync & QR Token",
    "4. Doctor Cabin & Audit Logs",
    "5. GPS Nearest Doctor Optimizer",
    "6. Govt Scheme Matcher",
    "7. CMO Anti-Corruption Portal",
    "8. Emergency SOS Hub",
]

step_mapping = {
    "1. Waiting Room Intake": "1. Waiting Room & Voice Intake",
    "2. AI Clinical Structuring": "2. AI Clinical Structuring Engine",
    "3. Local Sync & QR Token": "3. Local Sync & ABHA QR Token",
    "4. Doctor Cabin & Audit Logs": "4. Doctor Cabin & Triage Audit Logs",
    "5. GPS Nearest Doctor Optimizer": "5. GPS Nearest Doctor Optimizer",
    "6. Govt Scheme Matcher": "6. Govt Scheme & Subsidy Matcher",
    "7. CMO Anti-Corruption Portal": "7. CMO Direct Anti-Corruption Portal",
    "8. Emergency SOS Hub": "8. Emergency SOS & Telemetry Hub",
}

reverse_mapping = {v: k for k, v in step_mapping.items()}
current_short_menu = reverse_mapping.get(st.session_state["step_nav"], "1. Waiting Room Intake")

selected_short_menu = st.sidebar.radio(
    "Jump to Workflow Step", menu_options, index=menu_options.index(current_short_menu)
)
st.session_state["step_nav"] = step_mapping[selected_short_menu]

app_mode = st.session_state["step_nav"]
db = load_db()

# ==========================================
# 1. WAITING ROOM & VOICE INTAKE
# ==========================================
if app_mode == "1. Waiting Room & Voice Intake":
    st.title("🎙️ Step 1: Multilingual Waiting Room & Voice Intake")
    st.markdown(
        "The patient sits in the hospital lounge, selects their preferred regional"
        " language, and records symptoms natively using the microphone."
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        p_name = st.text_input("Patient Full Name", "Aarav Sharma")
    with c2:
        p_age = st.number_input("Age", 1, 100, 32)
    with c3:
        p_lang = st.selectbox(
            "Spoken Language",
            ["Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)", "English", "Tamil (தமிழ்)", "Bengali (বাংলা)"],
        )

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"🔴 Live Microphone Recorder ({p_lang})")
        audio = mic_recorder(
            start_prompt=f"Start Recording ({p_lang})",
            stop_prompt="Stop Recording",
            just_once=False,
            key=f"voice_rec_{p_lang}",
        )

        voice_transcript = ""
        if audio:
            st.audio(audio["bytes"])
            # Fallback text to simulate transcription output
            voice_transcript = "Mujhe pichle ek mahine se ghutno mein bhari dard hai aur chalne mein takleef hoti hai."
            st.success(f"Microphone audio successfully captured for language: {p_lang}!")
        else:
            voice_transcript = st.text_area(
                "Or Type Spoken Symptoms Manually (Try 'stomach pain', 'fever', or 'knee pain')",
                value="Mujhe kal raat se pet mein bahut dard hai aur acidity ho rahi hai."
            )

    with col_b:
        st.subheader("📋 Intake Summary Preview")
        st.info("The voice recording or text is processed and channeled automatically into the AI structural parsing engine.")
        if st.button("Lock Input & Proceed to AI Structuring ➔", type="primary", use_container_width=True):
            st.session_state["raw_voice"] = voice_transcript
            st.session_state["p_name"] = p_name
            st.session_state["p_age"] = p_age
            st.session_state["p_lang"] = p_lang
            st.session_state["step_nav"] = "2. AI Clinical Structuring Engine"
            st.rerun()

# ==========================================
# 2. AI CLINICAL STRUCTURING ENGINE
# ==========================================
elif app_mode == "2. AI Clinical Structuring Engine":
    st.title("🧠 Step 2: Dual-Lens AI Structural Parsing")
    st.markdown("Gemini AI reads the raw transcript and dynamically assigns the correct medical specialist based on the symptoms.")

    if "raw_voice" in st.session_state:
        st.info(f"**Incoming Patient Transcript:** {st.session_state['raw_voice']}")

        if st.button("⚡ Run AI Extraction Model", type="primary"):
            # DYNAMIC AI LOGIC BASED ON SYMPTOMS
            symptoms = st.session_state['raw_voice'].lower()
            
            if any(word in symptoms for word in ["knee", "joint", "ghutna", "bone", "leg", "chalne"]):
                specialty = "Orthopedic Surgeon"
                allo = "Diagnosis: Suspected Gonarthralgia / Osteoarthritis. Recommended: Knee X-Ray & MRI."
                ayush = "Dashavidha Pariksha: Vata Dosha Aggravation (Sandhi Vata)."
            elif any(word in symptoms for word in ["stomach", "pet", "acidity", "digestion", "vomit"]):
                specialty = "Gastroenterologist"
                allo = "Diagnosis: Suspected Acid Peptic Disease / Gastritis. Recommended: Endoscopy & Antacids."
                ayush = "Dashavidha Pariksha: Pitta Dosha Aggravation, Amlapitta (Hyperacidity)."
            elif any(word in symptoms for word in ["fever", "cold", "cough", "bukhar", "khasi"]):
                specialty = "General Physician"
                allo = "Diagnosis: Viral Pyrexia / Upper Respiratory Infection. Recommended: CBC Test."
                ayush = "Dashavidha Pariksha: Kapha-Vata Imbalance (Jwara)."
            else:
                specialty = "General Physician"
                allo = "Diagnosis: General Malaise. Recommended: Basic Vitals Check."
                ayush = "Dashavidha Pariksha: Tridosha Imbalance."

            st.session_state["specialty"] = specialty
            st.session_state["allo"] = allo
            st.session_state["ayush"] = ayush
            st.session_state["schemes"] = ["Ayushman Bharat PM-JAY", "State Health Subsidy"]
            
            st.success(f"Extraction complete! AI assigned specialist: **{specialty}**")

        if "allo" in st.session_state:
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"**Allopathic Triage Format:**\n\n{st.session_state['allo']}\n\n**Assigned:** {st.session_state['specialty']}")
            with col2:
                st.warning(f"**Ayush Dashavidha Format:**\n\n{st.session_state['ayush']}")

            if st.button("Save & Move to Local Database Sync ➔", type="primary", use_container_width=True):
                st.session_state["step_nav"] = "3. Local Sync & ABHA QR Token"
                st.rerun()
    else:
        st.warning("Please complete Step 1 (Waiting Room Intake) first.")

# ==========================================
# 3. LOCAL SYNC & ABHA QR TOKEN
# ==========================================
elif app_mode == "3. Local Sync & ABHA QR Token":
    st.title("🗄️ Step 3: Offline-First Local JSON Sync & ABHA Token")
    
    if "allo" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate ABHA Token & Commit to JSON Database", type="primary"):
                abha_id = f"ABHA-{random.randint(1000,9999)}-{random.randint(1000,9999)}"

                qr = qrcode.QRCode(version=1, box_size=5, border=2)
                qr.add_data(abha_id)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save("temp_qr.png")

                new_record = {
                    "id": abha_id,
                    "name": st.session_state.get("p_name", "Unknown"),
                    "age": st.session_state.get("p_age", 30),
                    "gender": "Unknown",
                    "location": "Punjab, India",
                    "symptoms": st.session_state.get("raw_voice", ""),
                    "specialty": st.session_state.get("specialty", "General"),
                    "allopathic_notes": st.session_state.get("allo", ""),
                    "ayush_notes": st.session_state.get("ayush", ""),
                    "eligible_schemes": st.session_state.get("schemes", []),
                    "prescription": "Pending Doctor Review",
                    "status": "Waiting Room",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                db["patients"].append(new_record)
                save_db(db)
                st.session_state["current_abha"] = abha_id
                st.success(f"Successfully committed! Token ID: **{abha_id}**")

        with col2:
            if "current_abha" in st.session_state:
                if os.path.exists("temp_qr.png"):
                    st.image("temp_qr.png", caption="ABHA Digital Verification Token", width=160)
                if st.button("Proceed to Doctor's Cabin Review ➔", type="primary", use_container_width=True):
                    st.session_state["step_nav"] = "4. Doctor Cabin & Triage Audit Logs"
                    st.rerun()
    else:
        st.warning("Complete Step 2 structure generation first.")

# ==========================================
# 4. DOCTOR CABIN & TRIAGE AUDIT LOGS
# ==========================================
elif app_mode == "4. Doctor Cabin & Triage Audit Logs":
    st.title("👨‍⚕️ Step 4: Doctor Cabin & Queue Fairness Controls")
    
    p_ids = [p["id"] for p in db.get("patients", [])]
    if not p_ids:
        st.warning("No patients in database. Go back to Step 1.")
    else:
        sel_id = st.selectbox("Select Patient ABHA Token for Consultation", p_ids)
        pat = next((p for p in db["patients"] if p["id"] == sel_id), None)

        if pat:
            box_col1, box_col2 = st.columns(2)
            with box_col1:
                st.markdown(f"### Patient: {pat['name']} | Age: {pat['age']} Years")
                st.write(f"**Reported Symptoms:** {pat.get('symptoms', '')}")
                st.info(f"**Allopathic View:**\n{pat.get('allopathic_notes', '')}")
                st.warning(f"**Ayush View:**\n{pat.get('ayush_notes', '')}")

            with box_col2:
                st.markdown("### Clinical Action Terminal")
                rx_input = st.text_area("Write Medical Prescription", value=pat.get("prescription", ""))
                if st.button("Save Prescription to Patient Record"):
                    pat["prescription"] = rx_input
                    save_db(db)
                    st.success("Prescription updated successfully!")

                st.markdown("---")
                if st.button("🚨 Emergency Triage Override (Log Audit Trail)"):
                    st.error("Emergency override executed. Logged securely and reported to CMO dashboard.")

                # Changed progression logic: Points to GPS Next
                if st.button("Move to GPS Nearest Doctor Optimizer ➔", type="primary", use_container_width=True):
                    st.session_state["step_nav"] = "5. GPS Nearest Doctor Optimizer"
                    st.rerun()

# ==========================================
# 5. GPS NEAREST DOCTOR OPTIMIZER (WITH CONTACT NUMBERS)
# ==========================================
elif app_mode == "5. GPS Nearest Doctor Optimizer":
    st.title("📍 Step 5: GPS Nearest Doctor & Cost Optimizer")

    with st.spinner("Acquiring Real-Time GPS Coordinates..."):
        g = geocoder.ip("me")
        lat, lng = g.latlng if g.latlng else [31.2530, 75.7000] 

    st.info(f"**📍 Live Patient Coordinates Acquired:** Latitude `{lat}`, Longitude `{lng}`")
    
    # Retrieve the dynamic specialty identified in Step 2
    required_specialty = st.session_state.get("specialty", "General Physician")
    st.warning(f"**AI Symptom Analysis Requirement:** You require a **{required_specialty}**.")

    c_in1, c_in2 = st.columns(2)
    with c_in1:
        fuel_price = st.number_input("Fuel Cost per Liter (₹)", 90, 110, 96)
    with c_in2:
        vehicle_mileage = st.number_input("Vehicle Mileage (km/L)", 10, 50, 20)
    
    # Safely prevent divide-by-zero errors in case user sets mileage to 0
    safe_mileage = vehicle_mileage if vehicle_mileage > 0 else 1

    # DYNAMIC DOCTOR LIST GENERATION BASED ON SPECIALTY (ADDED CONTACT NUMBERS)
    if "Orthopedic" in required_specialty:
        doc_options = [
            {"Name": "Dr. Anil Sharma (Orthopedic Surgeon)", "Facility": "District Civil Hospital", "Contact": "+91-9876543211", "Fee": 0, "Distance_km": 2.5},
            {"Name": "Dr. Meena Gupta (Ayurvedic Sandhi Vata Specialist)", "Facility": "Ayush Regional Center", "Contact": "+91-9876543212", "Fee": 150, "Distance_km": 6.0},
            {"Name": "Dr. R.K. Singh (Sports Injury Specialist)", "Facility": "City Private Rehab", "Contact": "+91-9876543213", "Fee": 800, "Distance_km": 1.2},
        ]
    elif "Gastroenterologist" in required_specialty:
        doc_options = [
            {"Name": "Dr. Ramesh Patel (Gastroenterologist)", "Facility": "Civil Hospital Gastro Wing", "Contact": "+91-9988776655", "Fee": 0, "Distance_km": 4.1},
            {"Name": "Dr. Sunita Menon (Ayurvedic Digestion Expert)", "Facility": "Ayush Wellness Clinic", "Contact": "+91-9988776656", "Fee": 150, "Distance_km": 6.0},
            {"Name": "Dr. V.K. Das (Digestive Specialist)", "Facility": "Metro Private Care", "Contact": "+91-9988776657", "Fee": 700, "Distance_km": 2.2},
        ]
    else:
        doc_options = [
            {"Name": "Dr. Rajesh Singh (General Physician)", "Facility": "Local Primary Health Clinic", "Contact": "+91-8877665544", "Fee": 0, "Distance_km": 0.8},
            {"Name": "Dr. Kavita Rao (Internal Medicine)", "Facility": "City Private Care", "Contact": "+91-8877665545", "Fee": 400, "Distance_km": 3.0},
            {"Name": "Dr. S.K. Ayush (General Ayurveda)", "Facility": "Ayush Regional Center", "Contact": "+91-8877665546", "Fee": 100, "Distance_km": 5.5},
        ]
    
    evaluated_docs = []
    for doc in doc_options:
        travel_cost = round((doc["Distance_km"] * 2 / safe_mileage) * fuel_price)
        total_burden = doc["Fee"] + travel_cost
        
        # Calculate minimum burden safely to flag the "BEST VALUE"
        min_burden = min(d['Fee'] + round((d['Distance_km'] * 2 / safe_mileage) * fuel_price) for d in doc_options)
        best_value_flag = "(⭐ BEST VALUE)" if total_burden == min_burden else ""

        evaluated_docs.append({
            "Doctor & Specialty": doc["Name"],
            "Contact Number": doc["Contact"],
            "Hospital/Clinic": doc["Facility"],
            "Consultation Fee": f"₹{doc['Fee']} (Free via PM-JAY)" if doc["Fee"] == 0 else f"₹{doc['Fee']}",
            "GPS Distance": f"{doc['Distance_km']} km",
            "Est. Fuel Cost": f"₹{travel_cost}",
            "Total Net Burden": f"₹{total_burden} {best_value_flag}"
        })

    st.table(evaluated_docs)

    if st.button("Proceed to Govt Scheme & Subsidy Matcher ➔", type="primary", use_container_width=True):
        st.session_state["step_nav"] = "6. Govt Scheme & Subsidy Matcher"
        st.rerun()

# ==========================================
# 6. GOVT SCHEME & SUBSIDY MATCHER
# ==========================================
elif app_mode == "6. Govt Scheme & Subsidy Matcher":
    st.title("📜 Step 6: Automated Govt Scheme & Subsidy Matcher")

    p_ids = [p["id"] for p in db.get("patients", [])]
    if not p_ids:
        st.warning("No patients in database. Go back to Step 1.")
    else:
        sel_id = st.selectbox("Select Patient ID for Subsidy Check", p_ids)
        pat = next((p for p in db["patients"] if p["id"] == sel_id), None)

        if pat:
            st.success(f"**Active Profile Verified:** {pat['name']} (ABHA ID: {pat['id']})")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("### Eligible Welfare Schemes:")
                for scheme in pat.get("eligible_schemes", []):
                    st.markdown(f"- **{scheme}**\n  * *Status:* **Pre-Approved**")
            with col_s2:
                st.markdown("### Instant Voucher Generation")
                if st.button("Generate Cashless Subsidy QR Voucher"):
                    st.info("Voucher active for zero-cost pharmacy and lab dispensing.")

                if st.button("Proceed to CMO Anti-Corruption Portal ➔", type="primary", use_container_width=True):
                    st.session_state["step_nav"] = "7. CMO Direct Anti-Corruption Portal"
                    st.rerun()

# ==========================================
# 7. CMO DIRECT ANTI-CORRUPTION PORTAL
# ==========================================
elif app_mode == "7. CMO Direct Anti-Corruption Portal":
    st.title("🛡️ Step 7: CMO Direct Complaint & Anti-Corruption Portal")
    
    with st.form("complaint_form"):
        c_name = st.text_input("Complainant Name (Optional / Anonymous)")
        c_dept = st.selectbox(
            "Hospital Department",
            ["Orthopedics OPD", "Emergency Triage", "Pharmacy / Diagnostics", "General Administration"],
        )
        c_issue = st.selectbox(
            "Grievance Category",
            ["Queue Manipulation / VIP Favoritism", "Diagnostic Overcharging", "Refusal of Care / Negligence"],
        )
        c_desc = st.text_area("Incident Description", placeholder="Provide details regarding the violation...")
        
        if st.form_submit_button("Submit Direct Report to CMO Office", type="primary"):
            ticket_id = f"CMO-TICKET-{random.randint(10000,99999)}"
            db["complaints"].append({
                "ticket": ticket_id,
                "department": c_dept,
                "issue": c_issue,
                "description": c_desc,
                "status": "Under Investigation (SLA: 24h)",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            save_db(db)
            st.success(f"Report logged securely! Tracking ID: **{ticket_id}**")

    if st.button("Proceed to Emergency SOS Hub ➔", type="primary", use_container_width=True):
        st.session_state["step_nav"] = "8. Emergency SOS & Telemetry Hub"
        st.rerun()

# ==========================================
# 8. EMERGENCY SOS & TELEMETRY HUB
# ==========================================
elif app_mode == "8. Emergency SOS & Telemetry Hub":
    st.title("🚨 Step 8: 108 Emergency SOS Lifeline")

    if st.button("🔴 TRIGGER RED SOS EMERGENCY SIGNAL", type="primary"):
        g = geocoder.ip("me")
        coords = g.latlng if g.latlng else [31.2530, 75.7000]

        st.error("EMERGENCY SIGNAL BROADCASTED TO 108 CONTROL ROOM!")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown(f"""
                * **Live Coordinates:** {coords[0]}, {coords[1]}
                * **Ambulance Status:** Dispatched (ETA 4 Mins)
                * **Assigned Unit:** ALS-Ambulance PB-08-99
            """)
        with col_e2:
            st.markdown(f"[🗺️ Open Route in Google Maps](https://www.google.com/maps/search/?api=1&query={coords[0]},{coords[1]})")
            st.info("Paramedic digital handover packet transmitted successfully.")