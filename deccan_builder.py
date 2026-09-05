import streamlit as st
import json
import os
from datetime import datetime

# 1. Initialize page configuration to wide layout format
st.set_page_config(page_title="Neti Deccan - నేటి డెక్కన్", layout="wide")

SAVE_FOLDER = "NetiDeccan_Articles"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# ====================================================================
# 🔒 ADMIN CREDENTIALS CONFIGURATION
# ====================================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@123"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if 'active_image_stream' not in st.session_state:
    st.session_state['active_image_stream'] = None

# Core Router: Read query parameters to determine face routing paths
url_parameters = st.query_params
current_viewing_file = url_parameters.get("article", None)
selected_category = url_parameters.get("category", "Casual News")
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
# 🎨 GLOBAL BRAND STYLING & LOOK-AND-FEEL MANAGEMENT
# ====================================================================
st.markdown(
    """
    <style>
        .block-container { padding-top: 0.5rem !important; padding-bottom: 2rem !important; }
        
        /* CORRECTED STYLES: Hides the default deploy widget frame while preserving sidebar toggle arrows */
        iframe[src*="host-service"], iframe[title="Manage app"], footer, [data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            opacity: 0 !important;
        }
        [data-testid="stHeader"] {
            background-color: transparent !important;
            background: none !important;
        }
        /* Completely hides the "Deploy" button row while keeping sidebar elements active */
        .stAppDeployButton, [data-testid="stDeploymentButton"] {
            display: none !important;
            visibility: hidden !important;
        }
        
        .news-card-anchor { text-decoration: none !important; color: inherit !important; display: block !important; margin-bottom: 15px; }
        
        .news-clickable-box {
            border: 1px solid #e2e8f0; padding: 18px; border-radius: 6px; background-color: #ffffff; transition: box-shadow 0.2s, border-color 0.2s; margin-bottom: 15px;
        }
        .news-clickable-box:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.06); border-color: #cbd5e1; background-color: #fafafa; }
        
        .sidebar-clickable-card {
            border: 1px solid #e2e8f0; padding: 10px; border-radius: 4px; background-color: #ffffff; margin-bottom: 10px; transition: background-color 0.2s;
        }
        .sidebar-clickable-card:hover { background-color: #fafafa; border-color: #cbd5e1; }
        
        /* Tight tracking distance for NETIDECCAN header text */
        .logo-english-sub {
            font-size: 28px !important; font-weight: 800 !important; color: #111111 !important; letter-spacing: -0.5px !important; margin: 4px 0 2px 0 !important; font-family: 'Arial Black', Gadget, sans-serif;
        }
        
        .breaking-marquee-box {
            background-color: #fff8f8; border-top: 1px solid #ffcdd2; border-bottom: 1px solid #ffcdd2; padding: 6px 0; margin-top: 10px; margin-bottom: 25px;
        }
        .marquee-text-style { font-size: 18px; font-weight: 700; color: #c62828; font-family: sans-serif; }
        
        /* Streamlined single e-paper layout block button containing logo on left and text on right */
        .single-epaper-button-card {
            display: inline-block !important;
            background-color: #ffffff !important;
            border: 2px solid #0d47a1 !important;
            border-radius: 6px !important;
            padding: 6px 12px !important;
            cursor: pointer !important;
            text-decoration: none !important;
            transition: background-color 0.2s, transform 0.1s;
            margin-bottom: 20px !important;
            width: 100% !important;
            max-width: 310px !important;
        }
        .single-epaper-button-card:hover { background-color: #f8fafc !important; transform: translateY(-1px); }
        
        /* Decreased distance vertical margin gap padding heights between news type selection cards */
        .custom-category-btn-box {
            border: 1px solid #e2e8f0; border-radius: 5px; padding: 6px 12px; margin-bottom: 5px !important; font-size: 15px; font-weight: 700; color: #334155; transition: all 0.2s; background-color: #f8fafc; text-align: left;
        }
        .custom-category-btn-box:hover { background-color: #f1f5f9; border-color: #cbd5e1; color: #0d47a1; }
        .category-active { background-color: #e0f2fe !important; border-color: #0284c7 !important; color: #0369a1 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

def render_unified_branding_masthead():
    if os.path.exists("official_logo.png"):
        st.image("official_logo.png", width=320)
    else:
        st.markdown("<h1 style='color:#0d47a1; font-size:48px; margin:0;'>డెక్కన్</h1><p style='color:#d32f2f; margin:0;'>ప్రజలకు, అధికారులకు మధ్య వారధి</p>", unsafe_allow_html=True)
    st.markdown("<div class='logo-english-sub'>NETIDECCAN</div>", unsafe_allow_html=True)
    st.markdown("<div class='breaking-marquee-box'><marquee behavior='scroll' direction='left' scrollamount='6'><span class='marquee-text-style'>🔥 నేటి డెక్కన్ వార్తలకు స్వాగతం తాజా రాజకీయ, ఆర్థిక, క్రీడా వార్తలు మీ కోసం ప్రతి క్షణం నిజమైన సమాచారం నేటి డెక్కన్ – మీ నమ్మకమైన వార్తా వేదిక.</span></marquee></div>", unsafe_allow_html=True)

# Render identical brand headers across both public/admin interfaces
render_unified_branding_masthead()

# ====================================================================
# FACE 1: PRIVATE EDITING WORKSPACE GATEWAY (Activated via ?mode=admin)
# ====================================================================
if is_admin_url:
    st.sidebar.markdown("### ⚙️ System Terminal")
    
    if not st.session_state["authenticated"]:
        st.markdown("<div style='background-color:#f1f5f9; padding:10px; border-radius:4px; text-align:center;'><h4>🔒 ADMIN WORKSPACE SECURE SIGN-IN</h4></div><br>", unsafe_allow_html=True)
        user_input = st.text_input("Username:", placeholder="Type user id...", key="adm_user_in")
        pass_input = st.text_input("Password:", type="password", placeholder="Type secure key...", key="adm_pass_in")
        if st.button("🔒 Unlock Dashboard", use_container_width=True):
            if user_input == ADMIN_USERNAME and pass_input == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("❌ Incorrect username or password combination.")
            
    else:
        st.sidebar.success("🟢 Authenticated Admin Active")
        if st.sidebar.button("🚪 Log Out of System Panel"):
            st.session_state["authenticated"] = False
            st.session_state['active_image_stream'] = None
            st.rerun()
            
        # ------------------------------------------------------------
        # 📁 SIDEBAR HISTORICAL SEARCH & ARTIFACT SELECTION ENGINE
        # ------------------------------------------------------------
        st.sidebar.markdown("---")
        st.sidebar.subheader("📁 పాత వార్తలు (History Manager)")
        
        admin_search_query = st.sidebar.text_input("🔍 వెతకండి (Search past article title):", placeholder="Type title keywords...").strip()
        
        editor_map = {"--- ➕ Create New Article (కొత్త వార్త రాయండి) ---": None}
        for headline, file in all_articles.items():
            if admin_search_query and admin_search_query.lower() not in headline.lower(): continue
            editor_map[headline] = file
            
        selected_headline = st.sidebar.radio("Choose Article to Load:", list(editor_map.keys()))
        active_file = editor_map[selected_headline]
        is_edit_mode = active_file is not None

        if is_edit_mode:
            with open(os.path.join(SAVE_FOLDER, active_file), "r", encoding="utf-8") as f: loaded_data = json.load(f)
            default_headline = loaded_data.get("headline", "")
            default_sub_header = loaded_data.get("sub_header", "")
            default_body = loaded_data.get("content", "")
            default_date = loaded_data.get("date", "")
            default_category = loaded_data.get("category", "Casual News")
            default_image_log = loaded_data.get("associated_image", "")
            page_header = f"📝 Editing Past Article: {selected_headline}"
            button_label = "💾 Update and Save Changes to This Article"
            if default_image_log and not st.session_state['active_image_stream']: st.session_state['active_image_stream'] = default_image_log
        else:
            default_headline = ""
            default_sub_header = ""
            default_body = ""
            default_date = datetime.now().strftime("%B %d, %Y")
            default_category = "Casual News"
            default_image_log = ""
            page_header = "➕ Create and Format a New Article"
            button_label = "🚀 Publish and Save New Article to Archives"

        # Content Form Layout Canvas Fields
        st.markdown(f"### {page_header}")
        headline_input = st.text_input(label="Main Headline:", value=default_headline, key="main_head_form")
        sub_header_input = st.text_input(label="Sub-Header Option (Optional):", value=default_sub_header, key="sub_head_form")
        
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
                    if isinstance(val, str) and val.startswith("data:image"): st.session_state['active_image_stream'] = val
                except Exception: pass
        elif image_option == "📤 Upload Local File from Device":
            file_device_upload = st.file_uploader("Select image file:", type=["jpg", "jpeg", "png"])
            if file_device_upload: st.session_state['active_image_stream'] = convert_file_to_cache_data(file_device_upload)
        else:
            initial_url = default_image_log if default_image_log and default_image_log.startswith("http") else "https://unsplash.com"
            image_url = st.text_input("Paste Image URL:", value=initial_url, key="img_url_form")
            if image_url: st.session_state['active_image_stream'] = image_url

        # Database Action Save vs Erase Row Buttons
        st.write("### 💾 Database Control Actions")
        col_save, col_delete = st.columns([0.5, 0.5])
        with col_save:
            if st.button(button_label, type="primary", use_container_width=True, key="save_art_btn"):
                if not headline_input.strip(): st.error("❌ Heading cannot be blank!")
                else:
                    timestamp_str = active_file.replace("article_", "").replace(".json", "") if is_edit_mode else datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_path = f"{SAVE_FOLDER}/article_{timestamp_str}.json"
                    article_data = {"headline": headline_input, "sub_header": sub_header_input, "category": category_input, "content": body_input, "date": date_input, "associated_image": st.session_state['active_image_stream'] if st.session_state['active_image_stream'] else "", "exported_at": timestamp_str}
                    with open(file_path, "w", encoding="utf-8") as f: json.dump(article_data, f, ensure_ascii=False, indent=4)
                    st.success("🎉 Article Saved and Synced Successfully!")
                    st.session_state['active_image_stream'] = None
                    st.rerun()
        with col_delete:
            if is_edit_mode:
                if st.button("🗑️ Delete This Article Permanently (తొలగించండి)", type="secondary", use_container_width=True, key="del_art_btn"):
                    file_to_remove = os.path.join(SAVE_FOLDER, active_file)
                    if os.path.exists(file_to_remove): os.remove(file_to_remove)
                    st.session_state['active_image_stream'] = None
                    st.success("💥 Article Deleted!")
                    st.rerun()
            else: st.button("🗑️ Delete Option Unavailable", disabled=True, use_container_width=True, key="disabled_del_btn")

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
                if st.session_state['active_image_stream']: st.image(st.session_state['active_image_stream'], use_container_width=True)

# --------------------------------------------------------------------
# CONFIGURATION B: STANDARD PUBLIC PORTAL NEWS READER VIEW
# --------------------------------------------------------------------
else:
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
        if full_art.get('sub_header'): st.markdown(f"<h3 style='color:#55; font-style:italic; font-size:18px; margin-top:4px;'>{full_art.get('sub_header')}</h3>", unsafe_allow_html=True)
        st.caption(f"📅 తేదీ: {full_art.get('date')} | 🏷️ వర్గం: {full_art.get('category', 'Casual News')}")
        st.markdown("<hr style='border-top:2px solid #222;'>", unsafe_allow_html=True)
        c_l, c_r = st.columns([0.65, 0.35], gap="large")
        with c_l: st.markdown(f"<p style='font-size:18px; line-height:1.75;'>{full_art.get('content')}</p>", unsafe_allow_html=True)
        with c_r:
            f_img = full_art.get('associated_image')
            if f_img: st.image(f_img, use_container_width=True)
    else:
        b64_epaper_logo = ""
        if os.path.exists("e-paper_logo.png"):
            import base64
            with open("e-paper_logo.png", "rb") as logo_file: b64_epaper_logo = f"data:image/png;base64,{base64.b64encode(logo_file.read()).decode('utf-8')}"
        elif os.path.exists("official_logo.png"):
            import base64
            with open("official_logo.png", "rb") as logo_file: b64_epaper_logo = f"data:image/png;base64,{base64.b64encode(logo_file.read()).decode('utf-8')}"
        else: b64_epaper_logo = "https://unsplash.com"

        col_ctrl_btn, col_ctrl_search = st.columns([0.35, 0.65], gap="large")
        with col_ctrl_btn:
            st.markdown(
                f"""
                <a href="http://netideccan.com" class="single-epaper-button-card" target="_blank">
                    <table style="width:100%; border-collapse:collapse; border:none; background:none; padding:0; margin:0;">
                        <tr style="border:none; background:none;">
                            <td style="width:75px; border:none; padding:0; padding-right:12px; vertical-align:middle; background:none;">
                                <img src="{b64_epaper_logo}" style="width:100%; height:auto; display:block; border-radius:3px;"/>
                            </td>
                            <td style="border:none; padding:0; vertical-align:middle; text-align:left; background:none;">
                                <span style="font-size:18px; font-weight:700; color:#0d47a1; font-family:Arial,sans-serif; line-height:1.2; display:block;">Read Print<br>E-Paper</span>
                            </td>
                        </tr>
                    </table>
                </a>
                """,
                unsafe_allow_html=True
            )
        with col_ctrl_search:
            search_query = st.text_input("🔍 వెతకండి (Search news by headline keyword):", placeholder="Type keywords here to filter articles...", key="news_search_reader_field").strip()
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_left_categories, col_center_news, col_right_trending = st.columns([0.22, 0.51, 0.27], gap="medium")
        
        with col_left_categories:
            st.markdown("<h4 style='margin-top:0; font-weight:700; color:#333; border-bottom:2px solid #ccc; padding-bottom:5px;'>📰 వార్తా వర్గాలు</h4>", unsafe_allow_html=True)
            
            available_categories = {
                "Casual News": "📰",
                "Politics": "⚖️",
                "Sports": "🏆",
                "Cinema": "🎬",
                "International": "🌍",
                "National": "🇮🇳",
                "Business": "💼"
            }
            for cat_name, cat_icon in available_categories.items():
                is_active = (selected_category == cat_name)
                active_class = "category-active" if is_active else ""
                st.markdown(f'<a href="?category={cat_name}" target="_self" style="text-decoration:none;"><div class="custom-category-btn-box {active_class}">{cat_icon} {cat_name}</div></a>', unsafe_allow_html=True)

        with col_center_news:
            st.markdown(f"<h3 style='margin-top:0; font-weight:800; border-bottom:2px solid #333; padding-bottom:5px;'>📰 {selected_category} Updates</h3>", unsafe_allow_html=True)
            st.write("") 
            
            visible_articles_count = 0
            if all_articles:
                for headline, file in all_articles.items():
                    if search_query and search_query.lower() not in headline.lower(): continue
                    with open(os.path.join(SAVE_FOLDER, file), "r", encoding="utf-8") as f: art = json.load(f)
                    
                    art_category = art.get("category", "Casual News")
                    if art_category != selected_category: continue
                        
                    visible_articles_count += 1
                    arc_headline = art.get("headline", "")
                    arc_sub_header = art.get("sub_header", "")
                    arc_content = art.get("content", "")
                    arc_date = art.get("date", "")
                    arc_image = art.get("associated_image", "")
                    
                    news_snippet = arc_content[:160] + "..." if len(arc_content) > 160 else arc_content
                    img_tag_html = f'<img src="{arc_image}" style="width:100%; max-height:150px; object-fit:cover; border-radius:4px;"/>' if arc_image else ''
                    sub_tag_html = f'<p style="color:#555; font-style:italic; font-size:14px; margin-top:2px; margin-bottom:4px;">{arc_sub_header}</p>' if arc_sub_header else ''
                    
                    st.markdown(f'<a href="?category={selected_category}&article={file}" target="_self" class="news-card-anchor"><div class="news-clickable-box"><table style="width:100%; border-collapse:collapse; border:none;"><tr><td style="width:68%; vertical-align:top; border:none; padding:0; padding-right:15px;"><h4 style="color:#000; font-weight:700; margin:0; font-size:22px; line-height:1.3;">{arc_headline}</h4>{sub_tag_html}<p style="color:#999; font-size:11px; margin:4px 0;">📅 తేదీ: {arc_date}</p><p style="font-size:15px; color:#333; margin:0; line-height:1.5;">{news_snippet}</p></td><td style="width:32%; vertical-align:top; border:none; padding:0;">{img_tag_html}</td></tr></table></div></a>', unsafe_allow_html=True)
            
            if visible_articles_count == 0:
                st.info(f"ప్రస్తుతానికి '{selected_category}' విభాగంలో ఎటువంటి వార్తలు లేవు.")

        with col_right_trending:
            st.markdown("<h3 style='margin-top:0; color:#c00000; border-bottom:2px solid #c00000; padding-bottom:5px;'>🔥 ముఖ్యాంశాలు</h3>", unsafe_allow_html=True)
            st.write("") 
            if all_articles:
                for side_headline, side_file in list(all_articles.items())[:6]:
                    with open(os.path.join(SAVE_FOLDER, side_file), "r", encoding="utf-8") as f: s_art = json.load(f)
                    s_head = s_art.get("headline", "")
                    s_sub = s_art.get("sub_header", "")
                    s_img = s_art.get("associated_image", "")
                    
                    img_html = f'<img src="{s_img}" style="width:100%; border-radius:4px; aspect-ratio:4/3; object-fit:cover;"/>' if s_img else ''
                    s_sub_val = s_sub if s_sub else ""
                    sub_html = f'<p style="font-size:11px; color:#666; margin-top:3px; margin-bottom:0; line-height:1.2;">{s_sub_val[:40]}...</p>' if s_sub_val else ''
                    st.markdown(f'<a href="?category={selected_category}&article={side_file}" target="_self" class="news-card-anchor"><div class="sidebar-clickable-card"><table style="width:100%; border-collapse:collapse; border:none;"><tr><td style="width:70%; vertical-align:top; border:none; padding:0; padding-right:8px;"><p style="font-size:15px; font-weight:700; line-height:1.3; color:#111; margin:0;">{s_head}</p>{sub_html}</td><td style="width:30%; vertical-align:middle; border:none; padding:0;">{img_html}</td></tr></table></div></a>', unsafe_allow_html=True)
            else:
                st.caption("No trending headlines recorded in archives yet.")
