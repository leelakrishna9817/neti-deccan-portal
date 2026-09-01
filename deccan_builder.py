import streamlit as st
import json
import os
from datetime import datetime

# ====================================================================
# 1. APPLICATION ENVIRONMENT CONFIGURATION
# ====================================================================
st.set_page_config(page_title="Neti Deccan Portal Engine", layout="wide")

# Directory name where your structured article database records remain stored
SAVE_FOLDER = "NetiDeccan_Articles"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# ====================================================================
# 2. BRANDED MASTHEAD: Bilingual Newspaper Title Header
# ====================================================================
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 25px;'>
        <h1 style='margin: 0; padding: 0; font-size: 52px; font-weight: 800; color: #000000;'>నేటి డెక్కన్</h1>
        <h3 style='margin: 5px 0 0 0; padding: 0; font-size: 26px; font-weight: 600; color: #555555; letter-spacing: 2px;'>NETI DECCAN</h3>
    </div>
    <hr style='border-top: 3px double #333; margin-bottom: 30px;'>
    """, 
    unsafe_allow_html=True
)

# ====================================================================
# 3. SIDEBAR NAVIGATION: Keyword Search Filter & Document Archives Feed
# ====================================================================
st.sidebar.title("📁 Neti Deccan Archives")
search_query = st.sidebar.text_input("🔍 Search articles by keyword:", placeholder="Type to filter...").strip()

# Scan folder directory to track existing entries
saved_files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith('.json')]
saved_files.sort(reverse=True)

# Map actual editorial Headline text strings -> to their corresponding file tokens
all_articles = {}
for file in saved_files:
    try:
        with open(os.path.join(SAVE_FOLDER, file), "r", encoding="utf-8") as f:
            data = json.load(f)
            headline = data.get("headline", f"Untitled Article ({file})")
            all_articles[headline] = file
    except Exception:
        continue

# Dynamically filter headlines inside the left workspace menu if query is input
filtered_articles = {"--- ➕ Create New Article ---": None}
for headline, file in all_articles.items():
    if search_query:
        if search_query.lower() in headline.lower() or search_query.lower() in file.lower():
            filtered_articles[headline] = file
    else:
        filtered_articles[headline] = file

selected_headline = st.sidebar.radio("Navigate Workspace Actions:", list(filtered_articles.keys()))
active_file = filtered_articles[selected_headline]

# ====================================================================
# 4. WORKSPACE MODE CONTROLLER & DEFAULT DATA INITIALIZATION
# ====================================================================
is_edit_mode = active_file is not None

if is_edit_mode:
    with open(os.path.join(SAVE_FOLDER, active_file), "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    default_headline = loaded_data.get("headline", "")
    default_sub_header = loaded_data.get("sub_header", "")
    default_source_location = loaded_data.get("source_location", "ఆనందపురం డెక్కన్ న్యూస్")
    default_body = loaded_data.get("content", "")
    default_date = loaded_data.get("date", "")
    default_image_log = loaded_data.get("associated_image", "No Image Uploaded")
    page_header = f"📝 Editing Article: {selected_headline}"
    button_label = "💾 Update and Save Changes to This Article"
else:
    default_headline = ""
    default_sub_header = ""
    default_source_location = "ఆనందపురం డెక్కన్ న్యూస్"
    default_body = ""
    default_date = datetime.now().strftime("%B %d, %Y")
    default_image_log = "No Image Uploaded"
    page_header = "➕ Create and Format a New Article"
    button_label = "🚀 Publish and Save New Article to Archives"

# ====================================================================
# 5. MAIN EDITING PANEL EDIT FORM
# ====================================================================
st.subheader(page_header)

headline_input = st.text_input(label="Main Headline (ప్రధాన శీర్షిక):", value=default_headline)
sub_header_input = st.text_input(label="Sub-Header Option (ఉప శీర్షిక - Optional):", value=default_sub_header, placeholder="Type secondary subtitle details here...")

source_location_input = st.text_input(
    label="News Source / Incident Location (వార్త మూలం / స్థలం):", 
    value=default_source_location,
    placeholder="e.g., ఆనందపురం డెక్కన్ న్యూస్"
)

body_input = st.text_area(label="News Content (వార్త వివరాలు):", value=default_body, height=200)
date_input = st.text_input(label="Publish Date (తేదీ):", value=default_date)

# ====================================================================
# 6. MEDIA CONFIGURATOR PANEL: Integrated Paste, Upload & URL Core
# ====================================================================
st.write("### 🖼️ Layout Photo Settings")
if is_edit_mode and default_image_log and not default_image_log.startswith("data:image"):
    st.info(f"📁 Current Saved Media Reference: `{default_image_log}`")

# RESTORED: Uploader option is back alongside paste layer options
image_option = st.radio(
    "Choose Image Input Method:", 
    ("📋 Paste Copied Photo (Ctrl+V)", "📤 Upload Local File from Device", "Use Web Image URL")
)

uploaded_image = None
image_name_log = default_image_log

# Handle clean initialization of internal clipboard cache variables
if 'final_pasted_image_string' not in st.session_state:
    st.session_state['final_pasted_image_string'] = None

if is_edit_mode and default_image_log and default_image_log.startswith("data:image"):
    st.session_state['final_pasted_image_string'] = default_image_log

# Execution routes based on active radio layout choice
if image_option == "📋 Paste Copied Photo (Ctrl+V)":
    st.write("👇 **Click once inside the box below**, then press **Ctrl + V** to paste your clipboard picture:")
    
    paste_html_bridge = """
    <div id="canvas-paste" style="border: 2px dashed #999; background: #fdfdfd; padding: 22px; text-align: center; color: #444; font-family: sans-serif; cursor: pointer; font-weight: bold; border-radius: 4px;">
        [ CLICK HERE & PRESS CTRL+V TO PASTE IMAGE ]
    </div>
    <script>
    document.addEventListener('paste', function (e) {
        var items = e.clipboardData.items;
        for (var i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                var blob = items[i].getAsFile();
                var reader = new FileReader();
                reader.onload = function (event) {
                    document.getElementById('canvas-paste').style.background = '#eafaea';
                    document.getElementById('canvas-paste').style.borderColor = '#4caf50';
                    document.getElementById('canvas-paste').innerText = '✅ Image Captured into App Memory!';
                    
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: event.target.result
                    }, '*');
                };
                reader.readAsDataURL(blob);
            }
        }
    });
    </script>
    """
    pasted_stream_result = st.components.v1.html(paste_html_bridge, height=95)
    
    if pasted_stream_result and isinstance(pasted_stream_result, str) and pasted_stream_result.startswith("data:image"):
        st.session_state['final_pasted_image_string'] = pasted_stream_result

    if st.session_state['final_pasted_image_string']:
        uploaded_image = st.session_state['final_pasted_image_string']
        image_name_log = uploaded_image

elif image_option == "📤 Upload Local File from Device":
    # Clear out conflicting clip memory states upon switching method tabs
    st.session_state['final_pasted_image_string'] = None
    file_device_upload = st.file_uploader("Select or drop a layout image file from your device folder:", type=["jpg", "jpeg", "png"])
    if file_device_upload:
        uploaded_image = file_device_upload
        image_name_log = file_device_upload.name

else:
    st.session_state['final_pasted_image_string'] = None
    initial_url = default_image_log if default_image_log and default_image_log.startswith("http") else "https://unsplash.com"
    image_url = st.text_input("Paste Image URL:", value=initial_url)
    if image_url:
        uploaded_image = image_url
        image_name_log = image_url

# ====================================================================
# 7. EXPORT DATA DATABASE LOG ENGINE
# ====================================================================
st.write("### 💾 Database Control Actions")
col_save, col_delete = st.columns([0.7, 0.3])

with col_save:
    if st.button(button_label, use_container_width=True):
        if not headline_input.strip():
            st.error("❌ Heading cannot be blank! Please provide a main headline string.")
        else:
            if is_edit_mode:
                file_path = os.path.join(SAVE_FOLDER, active_file)
                timestamp_str = active_file.replace("article_", "").replace(".json", "")
            else:
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"{SAVE_FOLDER}/article_{timestamp_str}.json"
                
            article_data = {
                "headline": headline_input,
                "sub_header": sub_header_input,
                "source_location": source_location_input,
                "content": body_input,
                "date": date_input,
                "associated_image": image_name_log if image_name_log else "No Image Uploaded",
                "exported_at": timestamp_str
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(article_data, f, ensure_ascii=False, indent=4)
            st.success("🎉 Success! Article configuration updated successfully!")
            st.rerun()

with col_delete:
    if is_edit_mode:
        if st.button("🗑️ Delete This Article Permanently", type="secondary", use_container_width=True):
            file_to_remove = os.path.join(SAVE_FOLDER, active_file)
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)
                st.session_state['final_pasted_image_string'] = None
                st.success("💥 Article successfully deleted from local files!")
                st.rerun()
    else:
        st.button("🗑️ Delete Option Unavailable", disabled=True, use_container_width=True)

# ====================================================================
# 8. LIVE SCREEN PREVIEW CARD LAYOUT GENERATOR
# ====================================================================
st.markdown("---")
st.write("### Live Layout Preview:")
with st.container(border=True):
    if headline_input:
        st.markdown(f"## {headline_input}")
    else:
        st.markdown("## *[Headline Block Blank]*")
        
    if sub_header_input:
        st.markdown(f"#### *{sub_header_input}*")
        
    st.caption(f"📅 తేదీ: {date_input}")
    st.markdown("---")
    
    col_text, col_photo = st.columns([0.65, 0.35], gap="medium")
    with col_text:
        display_text = ""
        if source_location_input:
            display_text += f"**{source_location_input} :** "
        if body_input:
            display_text += body_input
            st.write(display_text)
        else:
            st.info("Write news content inside the text box to preview paragraphs here.")
            
    with col_photo:
        # Robust verification block checks for local file buffers or image source links safely
        if uploaded_image:
            st.image(uploaded_image, caption="నేటి డెక్కన్ వార్తా చిత్రం (News Photo)", use_container_width=True)
        elif is_edit_mode and default_image_log and (isinstance(default_image_log, str) and (default_image_log.startswith("http") or default_image_log.startswith("data:image"))):
            st.image(default_image_log, caption="నేటి డెక్కన్ వార్తా చిత్రం (News Photo)", use_container_width=True)
        else:
            st.info("No photo added to this layout canvas block.")

# ====================================================================
# 9. FOOTER STATUS BAR MONITOR
# ====================================================================
st.markdown("---")
with st.container():
    col_status_l, col_status_r = st.columns([0.5, 0.5])
    with col_status_l:
        st.caption("📰 **నేటి డెక్కన్ (Neti Deccan) Layout Panel v2.5**")
    with col_status_r:
        if is_edit_mode:
            st.caption(f"🟢 Active Workspace: *Editing Mode ({selected_headline[:20]}...)*")
        else:
            st.caption("🔵 Active Workspace: *Fresh Article Sandbox*")
