import streamlit as st
import json
import os
from datetime import datetime

# 1. Initialize page configuration to wide layout format
st.set_page_config(page_title="Neti Deccan - నేటి డెక్కన్", layout="wide")

# Safe validation framework for local article storage folder
SAVE_FOLDER = "NetiDeccan_Articles"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# ====================================================================
# 🔒 ADMIN CREDENTIALS & MULTI-PAGE WORKSPACE STATE INITIALIZATION
# ====================================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# Initialize required session variables to prevent state loss
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if 'active_image_stream' not in st.session_state:
    st.session_state['active_image_stream'] = None
if 'current_viewing_article_file' not in st.session_state:
    st.session_state['current_viewing_article_file'] = None

# Helper function to convert uploaded device files into cloud-safe data strings safely
def convert_file_to_cache_data(uploaded_file):
    try:
        import base64
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode("utf-8")
        return f"data:image/png;base64,{base64_str}"
    except Exception:
        return ""

# ====================================================================
# 🏛️ BRANDED MASTHEAD: Bilingual Newspaper Title Header (Always Visible)
# ====================================================================
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 25px;'>
        <h1 style='margin: 0; padding: 0; font-size: 56px; font-weight: 800; color: #000000; font-family: sans-serif;'>నేటి డెక్కన్</h1>
        <h3 style='margin: 5px 0 0 0; padding: 0; font-size: 24px; font-weight: 600; color: #555555; letter-spacing: 3px;'>NETI DECCAN</h3>
    </div>
    <hr style='border-top: 3px double #333; margin-bottom: 30px;'>
    """, 
    unsafe_allow_html=True
)

# ====================================================================
# 🔒 URL QUERY PARAMETER ROUTER ENGINE (THE TWO FACES)
# ====================================================================
url_parameters = st.query_params
is_admin_url = url_parameters.get("mode") == "admin"

# Scan the local folder directory to track existing entries
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

# ====================================================================
# FACE 1: PRIVATE EDITING WORKSPACE GATEWAY (Activated via ?mode=admin)
# ====================================================================
if is_admin_url:
    st.sidebar.title("🔐 Secure Login Gateway")
    
    if not st.session_state["authenticated"]:
        st.subheader("Admin Verification Access Form")
        st.write("Please provide your authorization credentials to unlock your news workspace:")
        
        user_input = st.text_input("Username (యూజర్ నేమ్):", placeholder="Type user id...", key="adm_user_in")
        pass_input = st.text_input("Password (పాస్‌వర్డ్):", type="password", placeholder="Type secure key...", key="adm_pass_in")
        
        if st.button("🔒 Login and Open Workspace", use_container_width=True):
            if user_input == ADMIN_USERNAME and pass_input == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.success("🎉 Access Granted! Unlocking your layout workspace panel...")
                st.rerun()
            else:
                st.error("❌ Incorrect credentials pattern. Access Denied.")
                
    else:
        st.sidebar.success("🟢 Authenticated Admin")
        if st.sidebar.button("🚪 Log Out of Workspace"):
            st.session_state["authenticated"] = False
            st.session_state['active_image_stream'] = None
            st.rerun()
            
        st.sidebar.markdown("---")
        st.sidebar.subheader("📁 Article File Manager")
        
        editor_map = {"--- ➕ Create New Article ---": None}
        editor_map.update(all_articles)
        
        selected_headline = st.sidebar.radio("Select an Article to Edit:", list(editor_map.keys()))
        active_file = editor_map[selected_headline]
        
        is_edit_mode = active_file is not None

        if is_edit_mode:
            with open(os.path.join(SAVE_FOLDER, active_file), "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            default_headline = loaded_data.get("headline", "")
            default_sub_header = loaded_data.get("sub_header", "")
            default_body = loaded_data.get("content", "")
            default_date = loaded_data.get("date", "")
            default_image_log = loaded_data.get("associated_image", "")
            page_header = f"📝 Editing Article: {selected_headline}"
            button_label = "💾 Update and Save Changes to This Article"
            if default_image_log:
                st.session_state['active_image_stream'] = default_image_log
        else:
            default_headline = ""
            default_sub_header = ""
            default_body = ""
            default_date = datetime.now().strftime("%B %d, %Y")
            default_image_log = ""
            page_header = "➕ Create and Format a New Article"
            button_label = "🚀 Publish and Save New Article to Archives"

        st.markdown(f"### {page_header}")

        headline_input = st.text_input(label="Main Headline (ప్రధాన శీర్షిక):", value=default_headline, key="main_head_form")
        sub_header_input = st.text_input(label="Sub-Header Option (ఉప శీర్షిక - Optional):", value=default_sub_header, key="sub_head_form")
        body_input = st.text_area(label="News Content (వార్త వివరాలు):", value=default_body, height=200, key="body_txt_form")
        date_input = st.text_input(label="Publish Date (తేదీ):", value=default_date, key="pub_date_form")

        st.write("### 🖼️ Layout Photo Settings")
        image_option = st.radio("Choose Image Input Method:", ("📋 Paste Copied Photo (Ctrl+V)", "📤 Upload Local File from Device", "Use Web Image URL"))

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
                            window.parent.postMessage({type: 'streamlit:setComponentValue', value: event.target.result}, '*');
                        };
                        reader.readAsDataURL(blob);
                    }
                }
            });
            </script>
            """
            pasted_stream_result = st.components.v1.html(paste_html_bridge, height=95)
            if pasted_stream_result and isinstance(pasted_stream_result, str) and pasted_stream_result.startswith("data:image"):
                st.session_state['active_image_stream'] = pasted_stream_result
                
        elif image_option == "📤 Upload Local File from Device":
            file_device_upload = st.file_uploader("Select an image file:", type=["jpg", "jpeg", "png"])
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
                    if is_edit_mode:
                        file_path = os.path.join(SAVE_FOLDER, active_file)
                        timestamp_str = active_file.replace("article_", "").replace(".json", "")
                    else:
                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_path = f"{SAVE_FOLDER}/article_{timestamp_str}.json"
                        
                    article_data = {
                        "headline": headline_input,
                        "sub_header": sub_header_input,
                        "content": body_input,
                        "date": date_input,
                        "associated_image": st.session_state['active_image_stream'] if st.session_state['active_image_stream'] else "",
                        "exported_at": timestamp_str
                    }
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(article_data, f, ensure_ascii=False, indent=4)
                    st.success("🎉 Success! Article compiled and fully saved into archives.")
                    st.session_state['active_image_stream'] = None
                    st.rerun()

        with col_delete:
            if is_edit_mode:
                if st.button("🗑️ Delete This Article Permanently", type="secondary", use_container_width=True, key="del_art_btn"):
                    file_to_remove = os.path.join(SAVE_FOLDER, active_file)
                    if os.path.exists(file_to_remove):
                        os.remove(file_to_remove)
                        st.session_state['active_image_stream'] = None
                        st.success("💥 Article successfully deleted!")
                        st.rerun()
            else:
                st.button("🗑️ Delete Option Unavailable", disabled=True, use_container_width=True, key="disabled_del_btn")

        # Admin View Live Layout Preview Box
        st.markdown("---")
        st.write("### 👀 Live Layout Preview (నిజ సమయ ప్రివ్యూ):")
        with st.container(border=True):
            if headline_input:
                st.markdown(f"## {headline_input}")
            else:
                st.markdown("## *[Headline Block Blank]*")
            if sub_header_input:
                st.markdown(f"#### *{sub_header_input}*")
            st.caption(f"📅 తేదీ: {date_input}")
            st.markdown("---")
            col_p_text, col_p_photo = st.columns([0.65, 0.35], gap="large")
            with col_p_text:
                if body_input:
                    st.write(body_input)
            with col_p_photo:
                if st.session_state['active_image_stream']:
                    st.image(st.session_state['active_image_stream'], caption="ప్రివ్యూ చిత్రం (Preview)", use_container_width=True)

        st.markdown("---")
        st.caption("📰 **నేటి డెక్కన్ (Neti Deccan) Editor Panel Workspace active**")

# ====================================================================
# FACE 2: PREMIUM PUBLIC PORTAL NEWS READER (The Viewers Face)
# ====================================================================
else:
    # FORCEFUL CSS INJECTION: Erases the default Streamlit hosting "Manage App" layout drawer button entirely from the viewer page
    st.markdown(
        """
        <style>
            /* Completely hides the developer app manage widget panel and standard header fields */
            iframe[src*="host-service"], iframe[title="Manage app"], [data-testid="stDeploymentButton"], footer, [data-testid="stHeader"] {
                display: none !important;
                visibility: hidden !important;
                height: 0px !important;
                width: 0px !important;
                opacity: 0 !important;
            }
            
            /* Custom Style Elements to simulate fully clickable layout rows */
            .news-clickable-box {
                border: 1px solid #e2e8f0;
                padding: 20px;
                border-radius: 6px;
                margin-bottom: 18px;
                transition: transform 0.2s, box-shadow 0.2s;
                background-color: #ffffff;
            }
            .news-clickable-box:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                border-color: #cbd5e1;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------------
    # SUBPAGE CONTROLLER: ARTICLE FULL VIEW (With Pinned Media Sidebar!)
    # ----------------------------------------------------------------
    if st.session_state['current_viewing_article_file'] is not None:
        target_file = st.session_state['current_viewing_article_file']
        
        # Check if the file still exists safely
        if not os.path.exists(os.path.join(SAVE_FOLDER, target_file)):
            st.session_state['current_viewing_article_file'] = None
            st.rerun()
            
        with open(os.path.join(SAVE_FOLDER, target_file), "r", encoding="utf-8") as f:
            full_art = json.load(f)
            
        # Return to homepage link anchor execution element
        if st.button("⬅️ తిరిగి హోమ్‌పేజీకి (Back to Homepage)", type="primary", key="global_back_to_home"):
            st.session_state['current_viewing_article_file'] = None
            st.rerun()
            
        st.write("") # Spacer
        
        # Split article subpage view side-by-side (72% Main Read Content, 28% Pinned Trending Module)
        col_sub_article, col_sub_sidebar = st.columns([0.72, 0.28], gap="large")
        
        with col_sub_article:
            st.markdown(f"<h1 style='font-size:36px; font-weight:800; color:#000000; line-height:1.3;'>{full_art.get('headline')}</h1>", unsafe_allow_html=True)
            if full_art.get('sub_header'):
                st.markdown(f"<h3 style='color:#555555; font-style:italic; font-size:19px; font-weight:500; margin-top:5px;'>{full_art.get('sub_header')}</h3>", unsafe_allow_html=True)
            st.caption(f"📅 ప్రచురణ తేదీ: {full_art.get('date')}")
            st.markdown("<hr style='border-top:2px solid #222; margin-top:10px; margin-bottom:20px;'>", unsafe_allow_html=True)
            
            # Subpage media core block placement
            f_img = full_art.get('associated_image')
            if f_img and (f_img.startswith("http") or f_img.startswith("data:image")):
                st.image(f_img, use_container_width=True)
                st.write("") # Spacer
                
            st.markdown(f"<p style='font-size:18px; line-height:1.75; color:#1a1a1a; font-family:sans-serif;'>{full_art.get('content')}</p>", unsafe_allow_html=True)

        with col_sub_sidebar:
            # Pinned Trending Headlines list compiled strictly inside the news article subpage section!
            st.markdown("<h3 style='margin-top:0; color:#c00000; border-bottom:2px solid #c00000; padding-bottom:5px; font-size:22px;'>🔥 ముఖ్యాంశాలు (Trending Headlines)</h3>", unsafe_allow_html=True)
            st.write("")
            
            # Filter down selection excluding the active read article from recommendation loops
            side_items = [(h, f) for h, f in all_articles.items() if f != target_file]
            
            if side_items:
                for s_idx, (side_headline, side_file) in enumerate(side_items[:6]):
                    with open(os.path.join(SAVE_FOLDER, side_file), "r", encoding="utf-8") as f:
                        s_art = json.load(f)
                        
                    s_head = s_art.get("headline", "")
                    s_sub = s_art.get("sub_header", "")
                    s_img = s_art.get("associated_image", "")
                    
                    # Clean Clickable Cards for sidebar trending modules (No read buttons!)
                    with st.container(border=True):
                        col_side_txt, col_side_img = st.columns([0.72, 0.28], gap="small")
                        
                        with col_side_txt:
                            # Big Size title alignment
                            st.markdown(f"<p style='font-size:16px; font-weight:700; line-height:1.3; color:#111; margin:0;'>{s_head}</p>", unsafe_allow_html=True)
                            if s_sub:
                                st.markdown(f"<p style='font-size:11px; color:#555; margin-top:3px; margin-bottom:0; line-height:1.2;'>{s_sub[:40]}...</p>", unsafe_allow_html=True)
                                
                            # Mini subtle action text row allowing direct subpage hops right from the trending panel!
                            if st.button("చదవండి (Read)", key=f"side_hop_sub_{s_idx}", use_container_width=True):
                                st.session_state['current_viewing_article_file'] = side_file
                                st.rerun()
                                
                        with col_side_img:
                            if s_img and isinstance(s_img, str) and (s_img.startswith("http") or s_img.startswith("data:image")):
                                st.image(s_img, use_container_width=True)
                    st.write("")
            else:
                st.caption("No additional headlines recorded inside the secondary stream data log folder.")

    # ----------------------------------------------------------------
    # MAIN PORTAL HOMEPAGE ARCHITECTURE (Reader Landing View Face)
    # ----------------------------------------------------------------
    else:
        search_query = st.sidebar.text_input("🔍 వెతకండి (Search articles by keyword):", placeholder="Type keywords here...", key="reader_search_in").strip()
        
        st.markdown("<h3 style='margin-top:0; font-weight:700; font-size:26px;'>📰 తాజా వార్తలు (Latest News Updates)</h3>", unsafe_allow_html=True)
        st.write("") # Spacer

        # HOMEPAGE LAYOUT: Full wide single column grid feed. The trending sidebar column is entirely gone from here!
        if all_articles:
            for idx, (headline, file) in enumerate(all_articles.items()):
                if search_query and search_query.lower() not in headline.lower():
                    continue
                    
                with open(os.path.join(SAVE_FOLDER, file), "r", encoding="utf-8") as f:
                    art = json.load(f)
                arc_headline = art.get("headline", "Untitled Headline")
                arc_sub_header = art.get("sub_header", "")
                arc_content = art.get("content", "")
                arc_date = art.get("date", "")
                arc_image = art.get("associated_image", "")
                
                # Split paragraph block dynamically into a clean short overview snippet text string
                snippet_length = 160
                news_snippet = arc_content[:snippet_length] + "..." if len(arc_content) > snippet_length else arc_content
                
                # NO DISPLAY BUTTONS: Click the text hyperlink below to route subpage redirects smoothly
                with st.container(border=True):
                    col_card_txt, col_card_img = st.columns([0.68, 0.32], gap="large")
                    
                    with col_card_txt:
                        st.markdown(f"<h3 style='color:#000000; font-weight:700; margin-top:0px; margin-bottom:5px; font-size:24px;'>{arc_headline}</h3>", unsafe_allow_html=True)
                        if arc_sub_header:
                            st.markdown(f"<p style='color:#555; font-style:italic; font-size:15px; margin-bottom:8px;'>{arc_sub_header}</p>", unsafe_allow_html=True)
                        st.caption(f"📅 తేదీ: {arc_date}")
                        st.write(news_snippet)
                        st.write("") # Spacer
                        
                        # Clean Text Action Redirect Token Link (No buttons on display!)
                        if st.button("👉 ఈ వార్త పూర్తి వివరాల కోసం ఇక్కడ క్లిక్ చేయండి (Read Full Article Subpage)", key=f"main_card_link_{idx}"):
                            st.session_state['current_viewing_article_file'] = file
                            st.rerun()
                            
                    with col_card_img:
                        if arc_image and isinstance(arc_image, str) and (arc_image.startswith("http") or arc_image.startswith("data:image")):
                            st.image(arc_image, use_container_width=True)
        else:
            # Baseline Interactive Fallback Card Layout
            with st.container(border=True):
                st.markdown("##   సీఎం విజయ్ దళపతితో అరకు ఎంపీ దంపతుల భేటీ")
                st.caption("📅 తేదీ: September 2, 2026")
                st.write("పార్లమెంటరీ పట్టణ మరియు అభివృద్ధి అధ్యయన పర్యటనలో భాగంగా తమిళనాడును సందర్శించిన అరకు పార్లమెంట్ సభ్యురాలు దంపతులు ఆ రాష్ట్ర ముఖ్యమంత్రిని కలిశారు...")
                if st.button("👉 ఈ వార్త పూర్తి వివరాల కోసం ఇక్కడ క్లిక్ చేయండి (Read Full Article Subpage)", key="fallback_btn"):
                    st.info("This is a baseline layout placeholder. Create your first live article in admin mode to test subpages!")
