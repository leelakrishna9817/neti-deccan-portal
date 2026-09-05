import streamlit as st
import json
import os
from datetime import datetime

# 1. Initialize page configuration to wide layout format
st.set_page_config(page_title="Neti Deccan - Admin Control", layout="wide")

SAVE_FOLDER = "NetiDeccan_Articles"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# ====================================================================
# 🔒 UPDATED ADMINISTRATIVE LOGIN CREDENTIALS
# ====================================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Updated password to admin123

# Initialize required persistent session parameters to prevent state loss
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if 'active_image_stream' not in st.session_state:
    st.session_state['active_image_stream'] = None

def convert_file_to_cache_data(uploaded_file):
    try:
        import base64
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode("utf-8")
        return f"data:image/png;base64,{base64_str}"
    except Exception:
        return ""

# Scan folder directory to track existing entries
saved_files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith('.json')]
saved_files.sort(reverse=True)

all_articles = {}
for file in saved_files:
    try:
        with open(os.path.join(SAVE_FOLDER, file), "r", encoding="utf-8") as f:
            data = json.load(f)
            headline = data.get("headline", f"Untitled Article ({file})")
            all_articles[headline] = file
    except Exception:
        continue

# Inject shared styling headers to block developer diagnostic tools
st.markdown(
    """
    <style>
        .block-container { padding-top: 0.5rem !important; }
        iframe[src*="host-service"], iframe[title="Manage app"], [data-testid="stDeploymentButton"], footer, [data-testid="stHeader"], [data-testid="stSidebarNav"] {
            display: none !important; visibility: hidden !important; height: 0px !important; opacity: 0 !important;
        }
        .logo-english-sub { font-size: 28px !important; font-weight: 800 !important; color: #111111 !important; letter-spacing: 6px !important; margin: 6px 0 2px 0 !important; font-family: 'Arial Black', sans-serif; }
        .breaking-marquee-box { background-color: #fff8f8; border-top: 1px solid #ffcdd2; border-bottom: 1px solid #ffcdd2; padding: 6px 0; margin-top: 10px; margin-bottom: 25px; }
        .marquee-text-style { font-size: 18px; font-weight: 700; color: #c62828; font-family: sans-serif; }
    </style>
    """,
    unsafe_allow_html=True
)

# Render identical brand logo header matching the public face layout
if os.path.exists("official_logo.png"): 
    st.image("official_logo.png", width=320)
st.markdown("<div class='logo-english-sub'>NETIDECCAN</div>", unsafe_allow_html=True)
st.markdown("<div class='breaking-marquee-box'><marquee behavior='scroll' direction='left' scrollamount='6'><span class='marquee-text-style'>🔥 నేటి డెక్కన్ వార్తలకు స్వాగతం తాజా రాజకీయ, ఆర్థిక, క్రీడా వార్తలు మీ కోసం ప్రతి క్షణం నిజమైన సమాచారం నేటి డెక్కన్ – మీ నమ్మకమైన వార్తా వేదిక.</span></marquee></div>", unsafe_allow_html=True)

st.markdown("<div style='background-color:#f1f5f9; padding:10px; border-radius:4px; text-align:center;'><h4>✍️ నేటి డెక్కన్ - EDIT CONTROL PANEL</h4></div><br>", unsafe_allow_html=True)

# ====================================================================
# SECURE LOGIN FORM LAYER
# ====================================================================
st.sidebar.title("🔐 Secure Login Gateway")
if not st.session_state["authenticated"]:
    user_input = st.text_input("Username:", placeholder="Type user id...", key="adm_user_in")
    pass_input = st.text_input("Password:", type="password", placeholder="Type secure key...", key="adm_pass_in")
    if st.button("🔒 Login", use_container_width=True):
        if user_input == ADMIN_USERNAME and pass_input == ADMIN_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else: 
            st.error("❌ Incorrect username or password combination.")
            
# Unlocks advanced layout and creation dashboard tools if verified
else:
    st.sidebar.success("🟢 Authenticated Admin")
    if st.sidebar.button("🚪 Log Out"):
        st.session_state["authenticated"] = False
        st.session_state['active_image_stream'] = None
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Edit/View Past Articles")
    
    # Allows viewing and quick updating of past archived files natively
    editor_map = {"--- ➕ Create New Article ---": None}
    editor_map.update(all_articles)
    selected_headline = st.sidebar.radio("Select Article to Edit:", list(editor_map.keys()))
    active_file = editor_map[selected_headline]
    is_edit_mode = active_file is not None

    if is_edit_mode:
        with open(os.path.join(SAVE_FOLDER, active_file), "r", encoding="utf-8") as f: 
            loaded_data = json.load(f)
        default_headline = loaded_data.get("headline", "")
        default_sub_header = loaded_data.get("sub_header", "")
        default_body = loaded_data.get("content", "")
        default_date = loaded_data.get("date", "")
        default_category = loaded_data.get("category", "Casual News")
        default_image_log = loaded_data.get("associated_image", "")
        page_header = f"📝 Editing Past Article: {selected_headline}"
        button_label = "💾 Update and Save Changes to This Article"
        if default_image_log: 
            st.session_state['active_image_stream'] = default_image_log
    else:
        default_headline = ""
        default_sub_header = ""
        default_body = ""
        default_date = datetime.now().strftime("%B %d, %Y")
        default_category = "Casual News"
        default_image_log = ""
        page_header = "➕ Create and Format a New Article"
        button_label = "🚀 Publish and Save New Article to Archives"

    st.markdown(f"### {page_header}")
    headline_input = st.text_input(label="Main Headline:", value=default_headline, key="main_head_form")
    sub_header_input = st.text_input(label="Sub-Header Option (Optional):", value=default_sub_header, key="sub_head_form")
    
    # Updated category classifications dropdown selection array
    category_input = st.selectbox(
        label="News Section Category (వార్త విభాగం):",
        options=["Casual News", "Politics", "Sports", "Cinema", "International", "National", "Business"],
        index=["Casual News", "Politics", "Sports", "Cinema", "International", "National", "Business"].index(default_category)
    )
    
    body_input = st.text_area(label="News Content:", value=default_body, height=200, key="body_txt_form")
    date_input = st.text_input(label="Publish Date:", value=default_date, key="pub_date_form")

    st.write("### 🖼️ Layout Photo Settings")
    image_option = st.radio("Choose Image Input Method:", ("📋 Paste Copied Photo (Ctrl+V)", "📤 Upload Local File from Device", "Use Web Image URL"))
    pasted_stream_result = None

    if image_option == "📋 Paste Copied Photo (Ctrl+V)":
        pasted_stream_result = st.components.v1.html('<div id="c-paste" style="border:2px dashed #999; padding:20px; text-align:center;">[ CLICK HERE & CTRL+V ]</div><script>document.addEventListener("paste",function(e){var items=e.clipboardData.items;for(var i=0;i<items.length;i++){if(items[i].type.indexOf("image")!==-1){var blob=items[i].getAsFile();var reader=new FileReader();reader.onload=function(ev){window.parent.postMessage({type:"streamlit:setComponentValue",value:ev.target.result},"*");};reader.readAsDataURL(blob);}}});</script>', height=95)
        if pasted_stream_result:
            try:
                val = pasted_stream_result.value if hasattr(pasted_stream_result, 'value') else pasted_stream_result
                if isinstance(val, str) and val.startswith("data:image"): 
                    st.session_state['active_image_stream'] = val
            except Exception: 
                pass
    elif image_option == "📤 Upload Local File from Device":
        file_device_upload = st.file_uploader("Select image file:", type=["jpg", "jpeg", "png"])
        if file_device_upload: 
            st.session_state['active_image_stream'] = convert_file_to_cache_data(file_device_upload)
    else:
        initial_url = default_image_log if default_image_log and default_image_log.startswith("http") else "https://unsplash.com"
        image_url = st.text_input("Paste Image URL:", value=initial_url, key="img_url_form")
        if image_url: 
            st.session_state['active_image_stream'] = image_url

    st.write("### 💾 Database Control Actions")
    col_save, col_delete = st.columns([0.7, 0.3])
    with col_save:
        if st.button(button_label, use_container_width=True, key="save_art_btn"):
            if not headline_input.strip(): 
                st.error("❌ Heading cannot be blank!")
            else:
                timestamp_str = active_file.replace("article_", "").replace(".json", "") if is_edit_mode else datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"{SAVE_FOLDER}/article_{timestamp_str}.json"
                article_data = {"headline": headline_input, "sub_header": sub_header_input, "category": category_input, "content": body_input, "date": date_input, "associated_image": st.session_state['active_image_stream'] if st.session_state['active_image_stream'] else "", "exported_at": timestamp_str}
                with open(file_path, "w", encoding="utf-8") as f: 
                    json.dump(article_data, f, ensure_ascii=False, indent=4)
                st.success("🎉 Article Saved and Synced Successfully!")
                st.session_state['active_image_stream'] = None
                st.rerun()
                
    with col_delete:
        if is_edit_mode:
            if st.button("🗑️ Delete This Article Permanently", type="secondary", use_container_width=True, key="del_art_btn"):
                file_to_remove = os.path.join(SAVE_FOLDER, active_file)
                if os.path.exists(file_to_remove): 
                    os.remove(file_to_remove)
                st.success("💥 Article Deleted!")
                st.rerun()

    st.markdown("---")
    st.write("### 👀 Live Layout Preview:")
    with st.container(border=True):
        if headline_input: st.markdown(f"## {headline_input}")
        if sub_header_input: st.markdown(f"#### *{sub_header_input}*")
        st.caption(f"📅 తేదీ: {date_input} | 🏷️ వర్గం: {category_input}")
        st.markdown("---")
        col_p_text, col_p_photo = st.columns([0.65, 0.35], gap="large")
        with col_p_text: st.write(body_input)
        with col_p_photo:
            if st.session_state['active_image_stream']: 
                st.image(st.session_state['active_image_stream'], use_container_width=True)
