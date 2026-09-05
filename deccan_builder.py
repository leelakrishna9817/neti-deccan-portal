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
# 🔒 ADMIN CREDENTIALS CONFIGURATION
# ====================================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if 'active_image_stream' not in st.session_state:
    st.session_state['active_image_stream'] = None

url_parameters = st.query_params
current_viewing_file = url_parameters.get("article", None)
is_admin_url = url_parameters.get("mode") == "admin"

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

# ====================================================================
# FACE 1: PRIVATE EDITING WORKSPACE GATEWAY (Activated via ?mode=admin)
# ====================================================================
if is_admin_url:
    # 🏛️ Standard centered header for the administrative workspace view face
    st.markdown("<div style='text-align:center;'><h2>నేటి డెక్కన్ - EDIT CONTROL PANEL</h2></div><hr>", unsafe_allow_html=True)
    
    st.sidebar.title("🔐 Secure Login Gateway")
    if not st.session_state["authenticated"]:
        user_input = st.text_input("Username:", placeholder="Type user id...", key="adm_user_in")
        pass_input = st.text_input("Password:", type="password", placeholder="Type secure key...", key="adm_pass_in")
        if st.button("🔒 Login", use_container_width=True):
            if user_input == ADMIN_USERNAME and pass_input == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect credentials.")
    else:
        st.sidebar.success("🟢 Authenticated Admin")
        if st.sidebar.button("🚪 Log Out"):
            st.session_state["authenticated"] = False
            st.rerun()
            
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
            default_image_log = loaded_data.get("associated_image", "")
            if default_image_log:
                st.session_state['active_image_stream'] = default_image_log
        else:
            default_headline = ""
            default_sub_header = ""
            default_body = ""
            default_date = datetime.now().strftime("%B %d, %Y")
            default_image_log = ""

        headline_input = st.text_input(label="Main Headline:", value=default_headline, key="main_head_form")
        sub_header_input = st.text_input(label="Sub-Header Option:", value=default_sub_header, key="sub_head_form")
        body_input = st.text_area(label="News Content:", value=default_body, height=200, key="body_txt_form")
        date_input = st.text_input(label="Publish Date:", value=default_date, key="pub_date_form")

        image_option = st.radio("Choose Image Input Method:", ("📋 Paste Copied Photo (Ctrl+V)", "📤 Upload Local File from Device", "Use Web Image URL"))
        if image_option == "📋 Paste Copied Photo (Ctrl+V)":
            pasted_stream_result = st.components.v1.html('<div id="c-paste" style="border:2px dashed #999; padding:20px; text-align:center;">[ CLICK HERE & CTRL+V ]</div><script>document.addEventListener("paste",function(e){var items=e.clipboardData.items;for(var i=0;i<items.length;i++){if(items[i].type.indexOf("image")!==-1){var blob=items[i].getAsFile();var reader=new FileReader();reader.onload=function(ev){window.parent.postMessage({type:"streamlit:setComponentValue",value:ev.target.result},"*");};reader.readAsDataURL(blob);}}});</script>', height=95)
            if pasted_stream_result and pasted_stream_result.startswith("data:image"):
                st.session_state['active_image_stream'] = pasted_stream_result
        elif image_option == "📤 Upload Local File from Device":
            file_device_upload = st.file_uploader("Select image file:", type=["jpg", "jpeg", "png"])
            if file_device_upload:
                st.session_state['active_image_stream'] = convert_file_to_cache_data(file_device_upload)
        else:
            initial_url = default_image_log if default_image_log and default_image_log.startswith("http") else "https://unsplash.com"
            image_url = st.text_input("Paste Image URL:", value=initial_url, key="img_url_form")
            if image_url:
                st.session_state['active_image_stream'] = image_url

        if st.button("🚀 Save and Publish Article", use_container_width=True):
            if not headline_input.strip():
                st.error("❌ Heading cannot be blank!")
            else:
                timestamp_str = active_file.replace("article_", "").replace(".json", "") if is_edit_mode else datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"{SAVE_FOLDER}/article_{timestamp_str}.json"
                article_data = {"headline": headline_input, "sub_header": sub_header_input, "content": body_input, "date": date_input, "associated_image": st.session_state['active_image_stream'] if st.session_state['active_image_stream'] else "", "exported_at": timestamp_str}
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(article_data, f, ensure_ascii=False, indent=4)
                st.success("🎉 Article Published!")
                st.session_state['active_image_stream'] = None
                st.rerun()

# ====================================================================
# FACE 2: PREMIUM PUBLIC NEWS READER (Top-Left Title + Scrollable Columns)
# ====================================================================
else:
    # UPGRADED ADVANCED CSS: Moves Title to Top-Left, creates side-by-side grids, and hides dev app bars completely
    st.markdown(
        """
        <style>
            iframe[src*="host-service"], iframe[title="Manage app"], [data-testid="stDeploymentButton"], footer, [data-testid="stHeader"] {
                display: none !important; visibility: hidden !important; height: 0px !important; opacity: 0 !important;
            }
            .news-card-anchor { text-decoration: none !important; color: inherit !important; display: block !important; margin-bottom: 15px; }
            
            /* Horizontal Scroll Tracker Styling */
            .horizontal-scroll-container {
                display: flex !important; overflow-x: auto !important; white-space: nowrap !important; gap: 15px !important; padding: 10px 0 !important; scroll-behavior: smooth;
            }
            .horizontal-scroll-container::-webkit-scrollbar { height: 6px; }
            .horizontal-scroll-container::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
            
            .scroll-card-box {
                inline-size: 260px; min-width: 260px; background: #fff; border: 1px solid #e2e8f0; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s;
            }
            .scroll-card-box:hover { transform: translateY(-3px); box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
            
            /* Left Sidebar Masthead Typography layout configuration mapping rules */
            .left-branding-title { font-size: 42px; font-weight: 900; color: #000000; margin: 0; padding: 0; line-height: 1.1; }
            .left-branding-sub { font-size: 18px; font-weight: 600; color: #555; letter-spacing: 2px; margin-top: 5px; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------------
    # SUBPAGE CONTROLLER: ARTICLE FULL VIEW PAGE RENDER
    # ----------------------------------------------------------------
    if current_viewing_file is not None:
        if not os.path.exists(os.path.join(SAVE_FOLDER, current_viewing_file)):
            st.query_params.clear()
            st.rerun()
            
        with open(os.path.join(SAVE_FOLDER, current_viewing_file), "r", encoding="utf-8") as f:
            full_art = json.load(f)
            
        if st.button("⬅️ తిరిగి హోమ్‌పేజీకి (Back to Homepage)", type="primary"):
            st.query_params.clear()
            st.rerun()
            
        st.markdown(f"<h1 style='font-size:36px; font-weight:800; color:#000; margin-top:15px;'>{full_art.get('headline')}</h1>", unsafe_allow_html=True)
        st.caption(f"📅 తేదీ: {full_art.get('date')}")
        st.markdown("<hr style='border-top:2px solid #222;'>", unsafe_allow_html=True)
        
        c_l, c_r = st.columns([0.65, 0.35], gap="large")
        with c_l:
            st.markdown(f"<p style='font-size:18px; line-height:1.75;'>{full_art.get('content')}</p>", unsafe_allow_html=True)
        with c_r:
            f_img = full_art.get('associated_image')
            if f_img:
                st.image(f_img, use_container_width=True)

    # ----------------------------------------------------------------
    # MAIN PORTAL HOMEPAGE: UPGRADED TOP-LEFT TITLE + HORIZONTAL SCROLL COLUMNS
    # ----------------------------------------------------------------
    else:
        # Split screen into a Top-Left Branding Block (25%) and Content Blocks (75%)
        col_brand_left, col_news_right = st.columns([0.25, 0.75], gap="large")
        
        with col_brand_left:
            # Top-Left Branding Masthead Box
            st.markdown(
                """
                <div style='background-color: #fcfcfc; padding: 20px; border-left: 5px solid #c00000; border-radius: 4px; position: sticky; top: 20px;'>
                    <h1 class='left-branding-title'>నేటి<br>డెక్కన్</h1>
                    <div class='left-branding-sub'>NETI DECCAN</div>
                    <hr style='margin: 15px 0;'>
                    <p style='font-size:13px; color:#666; line-height:1.4;'>సమగ్ర వార్తా కథనాలు మరియు నిరంతర నిజ సమయ తాజా సమాచారం.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("") # Spacer
            search_query = st.text_input("🔍 వెతకండి (Search Headline):", placeholder="Type keywords...").strip()

        with col_news_right:
            st.markdown("<h3 style='margin-top:0; font-weight:800; color:#c00000; border-bottom:2px solid #c00000; padding-bottom:5px;'>📰 తాజా ముఖ్యాంశాలు (Latest News updates)</h3>", unsafe_allow_html=True)
            st.write("") # Spacer
            
            if all_articles:
                st.markdown("#### 🔄 స్క్రోల్ చేయండి (Swipe / Scroll horizontally to browse articles):")
                
                scroll_cards_html = ""
                for headline, file in all_articles.items():
                    if search_query and search_query.lower() not in headline.lower():
                        continue
                        
                    with open(os.path.join(SAVE_FOLDER, file), "r", encoding="utf-8") as f:
                        art = json.load(f)
                        
                    s_head = art.get("headline", "")
                    s_date = art.get("date", "")
                    s_img = art.get("associated_image", "https://unsplash.com")
                    if not s_img.startswith("http") and not s_img.startswith("data:image"):
                        s_img = "https://unsplash.com"
                    
                    scroll_cards_html += f"""
                    <a href="?article={file}" target="_self" class="news-card-anchor">
                        <div class="scroll-card-box">
                            <img src="{s_img}" style="width:100%; height:130px; object-fit:cover; border-radius:4px; margin-bottom:8px;"/>
                            <p style="font-size:14px; font-weight:700; color:#111; line-height:1.3; white-space:normal; height:55px; overflow:hidden;">{s_head[:65]}...</p>
                            <span style="font-size:11px; color:#888;">📅 {s_date}</span>
                        </div>
                    </a>
                    """
                
                st.markdown(f'<div class="horizontal-scroll-container">{scroll_cards_html}</div>', unsafe_allow_html=True)
                st.markdown("<br><hr><br>", unsafe_allow_html=True)
                
                st.markdown("#### 📌 అన్ని ప్రధాన వార్తలు (All Published News Grid):")
                for headline, file in all_articles.items():
                    if search_query and search_query.lower() not in headline.lower():
                        continue
                        
                    with open(os.path.join(SAVE_FOLDER, file), "r", encoding="utf-8") as f:
                        art = json.load(f)
                        
                    arc_headline = art.get("headline", "")
                    arc_sub_header = art.get("sub_header", "")
                    arc_content = art.get("content", "")
                    arc_date = art.get("date", "")
                    arc_image = art.get("associated_image", "")
                    
                    news_snippet = arc_content[:150] + "..." if len(arc_content) > 150 else arc_content
                    img_tag_html = f'<img src="{arc_image}" style="width:100%; max-height:150px; object-fit:cover; border-radius:4px;"/>' if arc_image else ''
                    sub_tag_html = f'<p style="color:#555; font-style:italic; font-size:14px; margin-top:2px;">{arc_sub_header}</p>' if arc_sub_header else ''
                    
                    st.markdown(
                        f"""
                        <a href="?article={file}" target="_self" class="news-card-anchor">
                            <div class="news-clickable-box">
                                <table style="width:100%; border-collapse:collapse; border:none;">
                                    <tr>
                                        <td style="width:70%; vertical-align:top; border:none; padding:0; padding-right:15px;">
                                            <h4 style="color:#000; font-weight:700; margin:0; font-size:20px; line-height:1.3;">{arc_headline}</h4>
                                            {sub_tag_html}
                                            <p style="color:#999; font-size:11px; margin:4px 0;">📅 తేదీ: {arc_date}</p>
                                            <p style="font-size:14px; color:#333; margin:0; line-height:1.5;">{news_snippet}</p>
                                        </td>
                                        <td style="width:30%; vertical-align:top; border:none; padding:0;">
                                            {img_tag_html}
                                        </td>
                                    </tr>
                                </table>
                            </div>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("ప్రస్తుతానికి ఎటువంటి వార్తలు లేవు. వార్తలను జోడించడానికి అడ్మిన్ లాగిన్ ఉపయోగించండి.")
