import streamlit as st
import os
import json
import smtplib
import zipfile
import io
import urllib.parse
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ----------------------------------------------------
# 1. Configurare Pagină Streamlit
# ----------------------------------------------------
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
    "enable_whatsapp": True,
    "whatsapp_phone": "",
    "whatsapp_apikey": "",
    "enable_notifications": False,
    "smtp_server": "[suspicious link removed]",
    "smtp_port": 587,
    "sender_email": "",
    "sender_password": "",
    "notification_email": ""
}

# ----------------------------------------------------
# 2. Funcții Utilitare (JSON, Foldere, Arhive)
# ----------------------------------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_USERS, f, indent=4)
        return DEFAULT_USERS
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_USERS

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def create_zip_archive(dir_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", [link suspect eliminat]_DEFLATED) as zip_file:
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dir_path)
                zip_file.write(file_path, arcname)
    [link suspect eliminat](0)
    return buffer

# ----------------------------------------------------
# 3. Trimitere Notificări (WhatsApp / E-mail)
# ----------------------------------------------------
def send_whatsapp_notification(company_name, year, month, uploaded_files_info):
    settings = load_settings()
    if not settings.get("enable_whatsapp", False):
        return False, "Notificările WhatsApp sunt dezactivate."
    
    phone = settings.get("whatsapp_phone", "").strip()
    apikey = settings.get("whatsapp_apikey", "").strip()

    if not phone or not apikey:
        return False, "Numărul de telefon sau ApiKey-ul WhatsApp nu sunt configurate."

    try:
        file_list_str = ", ".join([f"{name} ({size:.1f}KB)" for name, size in uploaded_files_info])
        data_ora = [link suspect eliminat]().strftime("%d-%m-%Y %H:%M")

        message = (
            f"🔔 *Documente noi in Portal!*\n\n"
            f"🏢 *Societate:* {company_name}\n"
            f"📅 *Perioada:* {month}/{year}\n"
            f"🕒 *Data:* {data_ora}\n"
            f"📄 *Fișiere:* {file_list_str}"
        )

        encoded_msg = urllib.parse.quote(message)
        url = f"[suspicious link removed]{phone}&text={encoded_msg}&apikey={apikey}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            res_text = [link suspect eliminat]().decode('utf-8')
            if "200" in str(response.status) or "Message sent" in res_text:
                return True, "Notificare WhatsApp trimisă!"
            return True, "Notificarea a fost procesată."
    except Exception as e:
        return False, f"Eroare WhatsApp: {str(e)}"

def send_email_notification(company_name, year, month, uploaded_files_info):
    settings = load_settings()
    if not settings.get("enable_notifications", False):
        return True, "Notificările e-mail sunt dezactivate."
    
    try:
        smtp_server = settings.get("smtp_server")
        smtp_port = int(settings.get("smtp_port", 587))
        sender_email = settings.get("sender_email")
        sender_password = settings.get("sender_password")
        receiver_email = settings.get("notification_email")

        if not sender_password or not sender_email:
            return False, "Datele e-mail nu sunt configurate."

        subject = f"🔔 Documente noi incarcate: {company_name} ({month}/{year})"
        file_list_str = "\n".join([f"- {name} ({size:.1f} KB)" for name, size in uploaded_files_info])
        data_ora = [link suspect eliminat]().strftime("%d-%m-%Y la %H:%M")

        body = (
            f"Salut,\n\n"
            f"Clientul '{company_name}' a incarcat documente noi in portalul de contabilitate!\n\n"
            f"📌 Detalii incarcare:\n"
            f"- Societate: {company_name}\n"
            f"- Perioada: {month} / {year}\n"
            f"- Data & Ora: {data_ora}\n\n"
            f"📄 Fisiere incarcate:\n"
            f"{file_list_str}\n\n"
            f"Te poti conecta in portal pentru a le descarca.\n"
        )

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

        return True, "E-mail trimis cu succes!"
    except Exception as e:
        return False, f"Eroare e-mail: {str(e)}"

# ----------------------------------------------------
# 4. Inițializare Sesiune
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "company" not in st.session_state:
    [link suspect eliminat] = None

users = load_users()

# ----------------------------------------------------
# 5. Ecran Autentificare
# ----------------------------------------------------
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
                    [link suspect eliminat] = users[username]["company"]
                    st.success("Autentificare reuşită!")
                    st.rerun()
                else:
                    st.error("Nume de utilizator sau parolă incorectă.")

        [link suspect eliminat](
            "**Conturi de test configurate:**\n"
            "- **Admin:** `admin` | Parola: `admin123`\n"
            "- **Client 1:** `client_alfa` | Parola: `pass123` (Firma: Alfa_SRL)\n"
            "- **Client 2:** `client_beta` | Parola: `pass123` (Firma: Beta_Construct_SRL)\n"
        )

# ----------------------------------------------------
# 6. Aplicația Principală
# ----------------------------------------------------
else:
    st.sidebar.title(f"👤 {st.session_state.username}")
    st.sidebar.write(f"**Rol:** {'Administrator' if st.session_state.role == 'admin' else 'Client'}")
    st.sidebar.write(f"**Societate:** {[link suspect eliminat]}")
    
    if st.sidebar.button("Deconectare"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        [link suspect eliminat] = None
        st.rerun()

    st.sidebar.markdown("---")

    # ====================================================
    # INTERFAȚĂ CLIENT
    # ====================================================
    if st.session_state.role == "client":
        company_folder = [link suspect eliminat]
        st.markdown(f"<h2>📁 Portal Client - {company_folder}</h2>", unsafe_allow_html=True)
        st.write("Încarcă documentele contabile lunare sau fă o poză direct cu camera telefonului.")

        col_an, col_luna = st.columns(2)
        with col_an:
            an_curent = [link suspect eliminat]().year
            an_selectat = st.selectbox("Selectează Anul", [str(an_curent), str(an_curent - 1), str(an_curent + 1)], index=0)
        
        with col_luna:
            luni = ["01_Ianuarie", "02_Februarie", "03_Martie", "04_Aprilie", "05_Mai", "06_Iunie", 
                    "07_Iulie", "08_August", "09_Septembrie", "10_Octombrie", "11_Noiembrie", "12_Decembrie"]
            luna_curenta_idx = [link suspect eliminat]().month - 1
            luna_selectata = st.selectbox("Selectează Luna", luni, index=luna_curenta_idx)

        target_dir = os.path.join(BASE_DIR, company_folder, an_selectat, luna_selectata)
        ensure_directory(target_dir)

        st.markdown(f"**Folder de salvare:** `{company_folder} / {an_selectat} / {luna_selectata}`")

        tab_files, tab_camera = st.tabs(["📁 Încarcă Fișiere / Poze Salvate în Telefon sau PC", "📷 Fă o Poză cu Camera Foto"])

        # TAB 1: Incarcare Fișiere existente (PDF, XML, XLSX, JPG etc.)
        with tab_files:
            uploaded_files = st.file_uploader(
                "Selectează fișierele din telefon sau PC (PDF, XML, PNG, JPG, JPEG, HEIC, XLSX, XLS, DOC, DOCX, TXT, CSV):",
                type=["pdf", "xml", "png", "jpg", "jpeg", "heic", "xlsx", "xls", "doc", "docx", "txt", "csv"],
                accept_multiple_files=True,
                key="client_file_uploader"
            )

            if uploaded_files:
                if st.button("💾 Salvează Fișierele & Notifică Contabilul", key="btn_save_client_files"):
                    uploaded_files_info = []
                    for idx, file in enumerate(uploaded_files):
                        orig_name = [link suspect eliminat]
                        base_name, ext = os.path.splitext(orig_name)
                        clean_ext = ext.lower() if ext else ".jpg"
                        
                        # Curățare nume și prevenire suprascriere pentru nume generice de pe telefon
                        if base_name.lower() in ["image", "photo", "camera", "captured_image", "file", "img", "document"]:
                            time_str = [link suspect eliminat]().strftime("%Y%m%d_%H%M%S")
                            safe_filename = f"document_{time_str}_{idx+1}{clean_ext}"
                        else:
                            safe_filename = "".join([c if c.isalnum() or c in "._-" else "_" for c in orig_name])

                        file_path = os.path.join(target_dir, safe_filename)
                        file_bytes = file.getvalue()
                        file_size_kb = len(file_bytes) / 1024

                        with open(file_path, "wb") as f:
                            f.write(file_bytes)
                        uploaded_files_info.append((safe_filename, file_size_kb))
                    
                    st.success(f"✅ {len(uploaded_files)} fișiere au fost salvate cu succes!")
                    
                    send_whatsapp_notification(company_folder, an_selectat, luna_selectata, uploaded_files_info)
                    send_email_notification(company_folder, an_selectat, luna_selectata, uploaded_files_info)
                    st.rerun()

        # TAB 2: Captură Poză Directă cu Camera
        with tab_camera:
            st.write("Apasă pe butonul de mai jos pentru a activa camera telefonului sau a laptopului:")
            camera_photo = [link suspect eliminat]_input("📷 Fă o poză documentului", key="client_camera_input")

            if camera_photo:
                custom_photo_name = st.text_input("Denumire opțională pentru poză (ex: Factura_Utilitati):", value="", key="cam_custom_title")
                
                if st.button("💾 Salvează Poza Capturată & Notifică Contabilul", key="btn_save_camera_photo"):
                    time_str = [link suspect eliminat]().strftime("%Y%m%d_%H%M%S")
                    if custom_photo_name.strip():
                        safe_title = "".join([c if c.isalnum() or c in "._-" else "_" for c in custom_photo_name.strip()])
                        filename = f"Poza_{safe_title}_{time_str}.jpg"
                    else:
                        filename = f"Poza_Camera_{time_str}.jpg"

                    file_path = os.path.join(target_dir, filename)
                    photo_bytes = camera_photo.getvalue()
                    file_size_kb = len(photo_bytes) / 1024

                    with open(file_path, "wb") as f:
                        f.write(photo_bytes)

                    st.success(f"✅ Poza '{filename}' a fost salvată cu succes!")

                    send_whatsapp_notification(company_folder, an_selectat, luna_selectata, [(filename, file_size_kb)])
                    send_email_notification(company_folder, an_selectat, luna_selectata, [(filename, file_size_kb)])
                    st.rerun()

        st.markdown("---")
        
        # Vizualizare Descarcare și Ștergere Documente de către Client
        existing_files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))] if os.path.exists(target_dir) else []
        
        st.subheader("📄 Documente încărcate în această lună:")
        if existing_files:
            col_h, col_z = st.columns([3, 1])
            with col_z:
                zip_data = create_zip_archive(target_dir)
                [link suspect eliminat]_button(
                    label="📦 Descarcă toate (.ZIP)",
                    data=zip_data,
                    file_name=f"{company_folder}_{an_selectat}_{luna_selectata}.zip",
                    mime="application/zip",
                    use_container_width=True
                )

            for fname in sorted(existing_files):
                fpath = os.path.join(target_dir, fname)
                fsize = os.path.getsize(fpath) / 1024
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"📄 **{fname}**")
                c2.write(f"{fsize:.1f} KB")
                
                with open(fpath, "rb") as fp:
                    [link suspect eliminat]_button("📥 Descarcă", fp, file_name=fname, key=f"dl_client_{fname}")
                
                if c4.button("🗑️ Șterge", key=f"del_client_{fname}"):
                    try:
                        os.remove(fpath)
                        st.success(f"Fișierul '{fname}' a fost șters!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Eroare la ștergere: {err}")
        else:
            [link suspect eliminat]("Nu există niciun document încărcat pentru această lună.")

    # ====================================================
    # INTERFAȚĂ ADMINISTRATOR
    # ====================================================
    elif st.session_state.role == "admin":
        st.markdown("<h2>🛠️ Panou Administrare - Birou Contabilitate</h2>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📂 Vizualizare & Gestionare Documente Clienți", 
            "➕ Adăugare Societate / Client", 
            "💬 Notificări WhatsApp / E-mail",
            "👤 Conturi Active"
        ])

        # TAB 1: Vizualizare & Ștergere Documente de către Admin
        with tab1:
            ensure_directory(BASE_DIR)
            companies = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
            
            if not companies:
                st.warning("Nu există nicio societate creată încă.")
            else:
                selected_company = st.selectbox("Selectează Societatea:", sorted(companies))
                comp_path = os.path.join(BASE_DIR, selected_company)
                ani = [d for d in os.listdir(comp_path) if os.path.isdir(os.path.join(comp_path, d))]
                
                if ani:
                    selected_an = st.selectbox("Selectează Anul:", sorted(ani, reverse=True))
                    an_path = os.path.join(comp_path, selected_an)
                    luni = [d for d in os.listdir(an_path) if os.path.isdir(os.path.join(an_path, d))]
                    
                    if luni:
                        selected_luna = st.selectbox("Selectează Luna:", sorted(luni))
                        luna_path = os.path.join(an_path, selected_luna)
                        
                        col_title, col_zip_admin = st.columns([3, 1])
                        with col_title:
                            st.markdown(f"### 📄 Documente în: `{selected_company} / {selected_an} / {selected_luna}`")
                        
                        files = [f for f in os.listdir(luna_path) if os.path.isfile(os.path.join(luna_path, f))]
                        if files:
                            with col_zip_admin:
                                zip_admin_data = create_zip_archive(luna_path)
                                [link suspect eliminat]_button(
                                    label="📦 Descarcă Arhiva ZIP Lună",
                                    data=zip_admin_data,
                                    file_name=f"{selected_company}_{selected_an}_{selected_luna}.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )

                            st.write("---")
                            for fname in sorted(files):
                                fpath = os.path.join(luna_path, fname)
                                fsize = os.path.getsize(fpath) / 1024
                                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                                c1.write(f"📄 **{fname}**")
                                c2.write(f"{fsize:.1f} KB")
                                
                                with open(fpath, "rb") as fp:
                                    [link suspect eliminat]_button("📥 Descarcă", fp, file_name=fname, key=f"admin_dl_{selected_company}_{fname}")
                                
                                if c4.button("🗑️ Șterge Document", key=f"admin_del_{selected_company}_{fname}"):
                                    try:
                                        os.remove(fpath)
                                        st.success(f"Fișierul '{fname}' a fost șters cu succes!")
                                        st.rerun()
                                    except Exception as err:
                                        st.error(f"Eroare la ștergerea fișierului: {err}")
                        else:
                            [link suspect eliminat]("Folderul este gol pentru această lună.")
                    else:
                        [link suspect eliminat]("Nu există luni create pentru acest an.")
                else:
                    [link suspect eliminat]("Societatea nu are încă documente sau foldere create.")

        # TAB 2: Adăugare Client
        with tab2:
            st.subheader("Creează o nouă societate și cont pentru client")
            with st.form("add_client_form"):
                new_company = st.text_input("Nume Societate (ex: SR_Design_SRL)")
                new_username = st.text_input("Nume Utilizator Client")
                new_password = st.text_input("Parola Client", type="password")
                create_btn = st.form_submit_button("Creează Cont Client & Folder")

                if create_btn:
                    if new_company and new_username and new_password:
                        clean_comp_name = "".join([c if c.isalnum() or c in "._-" else "_" for c in new_company.strip()])
                        users[new_username] = {
                            "password": new_password,
                            "role": "client",
                            "company": clean_comp_name
                        }
                        save_users(users)
                        ensure_directory(os.path.join(BASE_DIR, clean_comp_name))
                        st.success(f"✅ Societatea '{clean_comp_name}' și contul '{new_username}' au fost create!")
                        st.rerun()
                    else:
                        st.error("Te rugăm să completezi toate câmpurile.")

        # TAB 3: Setări Notificări
        with tab3:
            st.subheader("💬 Configurare Notificări WhatsApp & E-mail")
            current_settings = load_settings()

            st.markdown("""
            **Ghid Notificări WhatsApp (CallMeBot):**
            1. Deschide **WhatsApp** pe telefon.
            2. Trimite mesajul `I allow callmebot to send me messages` la numărul **`+34 644 51 91 69`**.
            3. Primești înapoi un **ApiKey** (cod din 6 cifre).
            4. Completează numărul tău cu `+40` și ApiKey-ul primit.
            """)

            with st.form("notifications_settings_form"):
                st.markdown("#### 📱 Setări WhatsApp")
                enable_wa = st.checkbox("Activează notificările pe WhatsApp", value=current_settings.get("enable_whatsapp", True))
                wa_phone = st.text_input("Numărul tău de telefon (cu +40, ex: +40722123456):", value=current_settings.get("whatsapp_phone", ""))
                wa_key = st.text_input("ApiKey primit pe WhatsApp:", value=current_settings.get("whatsapp_apikey", ""))

                st.markdown("---")
                st.markdown("#### 📧 Setări E-mail (Opțional)")
                enable_em = st.checkbox("Activează notificările pe E-mail", value=current_settings.get("enable_notifications", False))
                dest_e = st.text_input("E-mail Contabil (destinatar):", value=current_settings.get("notification_email", ""))
                smtp_s = st.text_input("Server SMTP:", value=current_settings.get("smtp_server", "[suspicious link removed]"))
                smtp_p = st.number_input("Port SMTP:", value=int(current_settings.get("smtp_port", 587)))
                sender_e = st.text_input("E-mail Expeditor:", value=current_settings.get("sender_email", ""))
                sender_p = st.text_input("Parolă Expeditor / App Password:", value=current_settings.get("sender_password", ""), type="password")

                save_st_btn = st.form_submit_button("💾 Salvează Toate Setările")

                if save_st_btn:
                    updated_st = {
                        "enable_whatsapp": enable_wa,
                        "whatsapp_phone": wa_phone.strip(),
                        "whatsapp_apikey": wa_key.strip(),
                        "enable_notifications": enable_em,
                        "notification_email": dest_e.strip(),
                        "smtp_server": smtp_s.strip(),
                        "smtp_port": int(smtp_p),
                        "sender_email": sender_e.strip(),
                        "sender_password": sender_p.strip()
                    }
                    save_settings(updated_st)
                    st.success("✅ Setările au fost salvate cu succes!")

        # TAB 4: Administrare Conturi
        with tab4:
            st.subheader("Utilizatori înregistrați în sistem")
            st.json(users)
            
            st.markdown("---")
            st.write("#### 🗑️ Ștergere Cont Client")
            non_admin_users = [u for u in users.keys() if users[u]["role"] != "admin"]
            if non_admin_users:
                user_to_delete = st.selectbox("Selectează un cont pentru ștergere:", non_admin_users)
                if st.button("Șterge Cont Client"):
                    if user_to_delete in users:
                        del users[user_to_delete]
                        save_users(users)
                        st.success(f"Contul '{user_to_delete}' a fost șters!")
                        st.rerun()
            else:
                [link suspect eliminat]("Nu există conturi de clienți create.")
