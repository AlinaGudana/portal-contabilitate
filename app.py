import streamlit as st
import os
import json
import smtplib
import zipfile
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configurarea paginii
st.set_page_config(
    page_title="Portal Contabilitate - Incarcare Documente",
    page_icon="📁",
    layout="wide"
)

BASE_DIR = "documente_clienti"
USERS_FILE = "users_db.json"
SETTINGS_FILE = "email_settings.json"

DEFAULT_USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "company": "Birou Contabilitate (ADMIN)"
    },
    "client_alfa": {
        "password": "pass123",
        "role": "client",
        "company": "Alfa_SRL"
    },
    "client_beta": {
        "password": "pass123",
        "role": "client",
        "company": "Beta_Construct_SRL"
    }
}

DEFAULT_SETTINGS = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "regnskabsrl@gmail.com",
    "sender_password": "",
    "notification_email": "regnskabsrl@gmail.com",
    "enable_notifications": True
}

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_USERS, f, indent=4)
        return DEFAULT_USERS
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def create_zip_archive(dir_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dir_path)
                zip_file.write(file_path, arcname)
    buffer.seek(0)
    return buffer

def send_email_notification(company_name, year, month, uploaded_files_info):
    settings = load_settings()
    if not settings.get("enable_notifications", True):
        return True, "Notificarile sunt dezactivate din setari."
    
    try:
        smtp_server = settings.get("smtp_server")
        smtp_port = int(settings.get("smtp_port", 587))
        sender_email = settings.get("sender_email")
        sender_password = settings.get("sender_password")
        receiver_email = settings.get("notification_email")

        if not sender_password or len(sender_password.strip()) == 0:
            return False, "Parola de e-mail nu este configurata in panoul Admin."

        subject = f"🔔 Documente noi incarcate de: {company_name} ({month}/{year})"
        file_list_str = "\n".join([f"- {name} ({size:.1f} KB)" for name, size in uploaded_files_info])
        data_ora = datetime.now().strftime("%d-%m-%Y la %H:%M")

        body = f"""Salut,

Clientul '{company_name}' a incarcat documente noi in portalul de contabilitate!

📌 Detalii incarcare:
- Societate: {company_name}
- Perioada: {month} / {year}
- Data & Ora: {data_ora}

📄 Fisiere / Poze incarcate:
{file_list_str}

Te poti conecta in portal pentru a vizualiza si descarca documentele sau arhiva ZIP completa.
---
Notificare automata - Portal Contabilitate
"""

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return True, "E-mail de notificare trimis cu succes!"
    except Exception as e:
        return False, f"Eroare la trimiterea e-mailului: {str(e)}"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "company" not in st.session_state:
    st.session_state.company = None

users = load_users()

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔐 Portal Contabilitate - Autentificare</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Nume Utilizator / Email")
            password = st.text_input("Parola", type="password")
            submit = st.form_submit_button("Conectare")
            
            if submit:
                if username in users and users[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = users[username]["role"]
                    st.session_state.company = users[username]["company"]
                    st.success("Autentificare reusita!")
                    st.rerun()
                else:
                    st.error("Nume de utilizator sau parola incorecta.")

        st.info("""
        **Conturi Demo:**
        - **Admin:** `admin` | Parola: `admin123`
        - **Client 1:** `client_alfa` | Parola: `pass123` (Firma: Alfa_SRL)
        - **Client 2:** `client_beta` | Parola: `pass123` (Firma: Beta_Construct_SRL)
        """)

else:
    st.sidebar.title(f"👤 {st.session_state.username}")
    st.sidebar.write(f"**Rol:** {'Administrator' if st.session_state.role == 'admin' else 'Client'}")
    st.sidebar.write(f"**Societate:** {st.session_state.company}")
    
    if st.sidebar.button("Deconectare"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.company = None
        st.rerun()

    st.sidebar.markdown("---")

    if st.session_state.role == "client":
        company_folder = st.session_state.company
        st.markdown(f"<h2>📁 Portal Client - {company_folder}</h2>", unsafe_allow_html=True)
        st.write("Incarca documentele contabile lunare (fisiere sau poze).")

        col_an, col_luna = st.columns(2)
        with col_an:
            an_curent = datetime.now().year
            an_selectat = st.selectbox("Selecteaza Anul", [str(an_curent), str(an_curent - 1)], index=0)
        
        with col_luna:
            luni = ["01_Ianuarie", "02_Februarie", "03_Martie", "04_Aprilie", "05_Mai", "06_Iunie", 
                    "07_Iulie", "08_August", "09_Septembrie", "10_Octombrie", "11_Noiembrie", "12_Decembrie"]
            luna_curenta_idx = datetime.now().month - 1
            luna_selectata = st.selectbox("Selecteaza Luna", luni, index=luna_curenta_idx)

        target_dir = os.path.join(BASE_DIR, company_folder, an_selectat, luna_selectata)
        ensure_directory(target_dir)

        st.markdown(f"**Folder de salvare:** `{company_folder} / {an_selectat} / {luna_selectata}`")

        tab_file, tab_cam = st.tabs(["📁 Incarca Fisiere / Poze din Telefon", "📷 Fa o Poza cu Camera Foto"])

        uploaded_files_info = []

        with tab_file:
            uploaded_files = st.file_uploader(
                "Selecteaza fisiere (PDF, XML, PNG, JPG, XLSX, HEIC):",
                accept_multiple_files=True,
                type=["pdf", "xml", "png", "jpg", "jpeg", "xlsx", "heic"]
            )

            if uploaded_files:
                if st.button("💾 Salveaza Fisierele & Notifica Contabilul", key="btn_files"):
                    for file in uploaded_files:
                        file_path = os.path.join(target_dir, file.name)
                        file_size_kb = len(file.getbuffer()) / 1024
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        uploaded_files_info.append((file.name, file_size_kb))
                    
                    st.success(f"✅ {len(uploaded_files)} fisiere au fost salvate cu succes!")
                    success, msg = send_email_notification(company_folder, an_selectat, luna_selectata, uploaded_files_info)
                    if success:
                        st.info("📧 Notificarea pe e-mail a fost trimisa catre biroul de contabilitate!")
                    else:
                        st.warning(f"Fisierele au fost salvate, dar e-mailul nu a putut fi trimis. Detalii: {msg}")

        with tab_cam:
            camera_photo = st.camera_input("Captureaza bonul / factura cu camera telefonului:")
            if camera_photo:
                st.image(camera_photo, caption="Previzualizare poza capturata", use_container_width=True)
                if st.button("💾 Salveaza Poza Capturata", key="btn_cam"):
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    photo_name = f"Poza_Camera_{timestamp_str}.jpg"
                    photo_path = os.path.join(target_dir, photo_name)
                    photo_size_kb = len(camera_photo.getbuffer()) / 1024
                    
                    with open(photo_path, "wb") as f:
                        f.write(camera_photo.getbuffer())
                    
                    uploaded_files_info.append((photo_name, photo_size_kb))
                    st.success(f"✅ Poza '{photo_name}' a fost salvata cu succes!")
                    
                    success, msg = send_email_notification(company_folder, an_selectat, luna_selectata, uploaded_files_info)
                    if success:
                        st.info("📧 Notificarea pe e-mail a fost trimisa catre biroul de contabilitate!")

        st.markdown("---")
        
        existing_files = os.listdir(target_dir)
        if existing_files:
            c_header, c_zip = st.columns([3, 1])
            with c_header:
                st.subheader("📄 Documente incarcate in aceasta luna:")
            with c_zip:
                zip_data = create_zip_archive(target_dir)
                st.download_button(
                    label="📦 Descarca toate (.ZIP)",
                    data=zip_data,
                    file_name=f"{company_folder}_{an_selectat}_{luna_selectata}.zip",
                    mime="application/zip",
                    use_container_width=True
                )

            for fname in existing_files:
                fpath = os.path.join(target_dir, fname)
                fsize = os.path.getsize(fpath) / 1024
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"📄 {fname}")
                c2.write(f"{fsize:.1f} KB")
                with open(fpath, "rb") as fp:
                    c3.download_button("Descarca", fp, file_name=fname, key=f"dl_{fname}")
        else:
            st.subheader("📄 Documente incarcate in aceasta luna:")
            st.info("Nu exista documente incarcate pentru aceasta luna.")

    elif st.session_state.role == "admin":
        st.markdown("<h2>🛠️ Panou Administrare - Birou Contabilitate</h2>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📂 Vizualizare Documente Clienti", 
            "➕ Adaugare Societate / Client", 
            "⚙️ Configurare Notificari E-mail", 
            "👤 Conturi Active"
        ])

        with tab1:
            ensure_directory(BASE_DIR)
            companies = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
            
            if not companies:
                st.warning("Nu exista nicio societate creata inca.")
            else:
                selected_company = st.selectbox("Selecteaza Societatea:", companies)
                comp_path = os.path.join(BASE_DIR, selected_company)
                ani = [d for d in os.listdir(comp_path) if os.path.isdir(os.path.join(comp_path, d))]
                
                if ani:
                    selected_an = st.selectbox("Selecteaza Anul:", sorted(ani, reverse=True))
                    an_path = os.path.join(comp_path, selected_an)
                    luni = [d for d in os.listdir(an_path) if os.path.isdir(os.path.join(an_path, d))]
                    
                    if luni:
                        selected_luna = st.selectbox("Selecteaza Luna:", sorted(luni))
                        luna_path = os.path.join(an_path, selected_luna)
                        
                        col_title, col_zip_admin = st.columns([3, 1])
                        with col_title:
                            st.markdown(f"### 📄 Documente in: `{selected_company} / {selected_an} / {selected_luna}`")
                        
                        files = os.listdir(luna_path)
                        if files:
                            with col_zip_admin:
                                zip_admin_data = create_zip_archive(luna_path)
                                st.download_button(
                                    label="📦 Descarca Arhiva ZIP Luna",
                                    data=zip_admin_data,
                                    file_name=f"{selected_company}_{selected_an}_{selected_luna}.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )

                            for fname in files:
                                fpath = os.path.join(luna_path, fname)
                                fsize = os.path.getsize(fpath) / 1024
                                c1, c2, c3 = st.columns([3, 1, 1])
                                c1.write(f"📄 {fname}")
                                c2.write(f"{fsize:.1f} KB")
                                with open(fpath, "rb") as fp:
                                    c3.download_button("Descarca", fp, file_name=fname, key=f"admin_dl_{selected_company}_{fname}")
                        else:
                            st.info("Folderul este gol pentru aceasta luna.")
                    else:
                        st.info("Nu exista luni create pentru acest an.")
                else:
                    st.info("Societatea nu are inca documente incarcate.")

        with tab2:
            st.subheader("Creeaza o noua societate si cont pentru client")
            with st.form("add_client_form"):
                new_company = st.text_input("Nume Societate (ex: SR_Design_SRL)")
                new_username = st.text_input("Nume Utilizator Client")
                new_password = st.text_input("Parola Client", type="password")
                create_btn = st.form_submit_button("Creeaza Cont Client & Folder")

                if create_btn:
                    if new_company and new_username and new_password:
                        clean_comp_name = new_company.strip().replace(" ", "_")
                        users[new_username] = {
                            "password": new_password,
                            "role": "client",
                            "company": clean_comp_name
                        }
                        save_users(users)
                        ensure_directory(os.path.join(BASE_DIR, clean_comp_name))
                        st.success(f"✅ Societatea '{clean_comp_name}' si contul '{new_username}' au fost create!")
                    else:
                        st.error("Te rugam sa completezi toate campurile.")

        with tab3:
            st.subheader("📧 Setari Notificari pe E-mail")
            current_settings = load_settings()

            with st.form("email_settings_form"):
                enable = st.checkbox("Activeaza notificarile pe e-mail", value=current_settings.get("enable_notifications", True))
                dest_email = st.text_input("E-mail Contabil (unde primesti alertele):", value=current_settings.get("notification_email", "regnskabsrl@gmail.com"))
                smtp_srv = st.text_input("Server SMTP (ex: smtp.gmail.com):", value=current_settings.get("smtp_server", "smtp.gmail.com"))
                smtp_p = st.number_input("Port SMTP:", value=int(current_settings.get("smtp_port", 587)))
                sender_e = st.text_input("E-mail Expeditor (contul folosit pentru trimitere):", value=current_settings.get("sender_email", "regnskabsrl@gmail.com"))
                sender_p = st.text_input("Parola / App Password Expeditor (16 caractere Google):", value=current_settings.get("sender_password", ""), type="password")

                save_st_btn = st.form_submit_button("Salveaza Setarile E-mail")

                if save_st_btn:
                    updated_st = {
                        "enable_notifications": enable,
                        "notification_email": dest_email,
                        "smtp_server": smtp_srv,
                        "smtp_port": smtp_p,
                        "sender_email": sender_e,
                        "sender_password": sender_p
                    }
                    save_settings(updated_st)
                    st.success("✅ Setarile pentru e-mail au fost salvate cu succes!")

        with tab4:
            st.subheader("Utilizatori inregistrati in sistem")
            st.json(users)
