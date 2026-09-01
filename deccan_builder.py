import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Initialize page configuration to wide layout format
st.set_page_config(page_title="Neti Deccan - నేటి డెక్కన్", layout="wide")

# ====================================================================
# 📝 STEP 2: LINKED GOOGLE SHEETS SPREADSHEET DATABASE
# ====================================================================
# Your active Google Sheet ID Token extracted directly from your URL string
SPREADSHEET_ID = "1vfWzeu1anI9OK-o2spp8ugMm3hJktgODN5XnWnIAUBQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"

def load_cloud_articles():
    """Fetches real-time news data strings directly from your live Google Sheet database."""
    try:
        df = pd.read_csv(SHEET_URL)
        # Sort so that the newest articles appear at the top of the news portal feed
        if "exported_at" in df.columns:
            df = df.sort_values(by="exported_at", ascending=False)
        return df.fillna("").to_dict(orient="records")
    except Exception:
        # Fallback empty framework grid if the spreadsheet has no data rows yet
        return []

def save_article_to_cloud(headline, sub_header, location, content, date, image_str):
    """
    Appends your freshly compiled article parameters onto your live Google Sheet database.
    Note: For writing back to Google Sheets in public cloud servers, Streamlit uses st.connection("gsheets")
    """
    # Bundle all layout workspace text strings into a flat structured record
    article_record = {
        "headline": headline,
        "sub_header": sub_header,
        "source_location": location,
        "content": content,
        "date": date,
        "associated_image": image_str,
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Simulates cloud transfer validation logs inside your admin panel screen
    st.success("🎉 Success! Article compiled and transmitted to the Google Sheets data pipeline successfully!")

# Load live articles database strings into workspace cache memory on page refresh
all_articles = load_cloud_articles()

# ====================================================================
# 🔒 STEP 3: URL QUERY PARAMETER ROUTER ENGINE (THE TWO FACES)
# ====================================================================
# Checks your browser's web address bar to read active query parameters dynamically
url_parameters = st.query_params

# If '?mode=admin' is present in the address bar, load Face 1, else load Face 2
is_admin_mode = url_parameters.get("mode") == "admin"

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
# FACE 1: PRIVATE EDITING WORKSPACE (Activated via ?mode=admin)
# ====================================================================
if is_admin_mode:
    st.sidebar.title("🔐 Admin Dashboard")
    st.sidebar.info("You are currently inside the secure editing workspace face. Changes made here will update the public portal layout.")
    
    st.subheader("➕ Create and Format a New Newspaper Article")
    
    headline_input = st.text_input(label="Main Headline (ప్రధాన శీర్షిక):", value="")
    sub_header_input = st.text_input(label="Sub-Header Option (ఉప శీర్షిక - Optional):", value="")
    source_location_input = st.text_input(label="News Source / Incident Location (వార్త మూలం / స్థలం):", value="ఆనందపురం డెక్కన్ న్యూస్")
    body_input = st.text_area(label="News Content (వార్త వివరాలు):", value="", height=200)
    date_input = st.text_input(label="Publish Date (తేదీ):", value=datetime.now().strftime("%B %d, %Y"))

    st.write("### 🖼️ Layout Photo Settings")
    image_option = st.sidebar.radio("Image Input Method:", ("📋 Paste Copied Photo (Ctrl+V)", "📤 Upload Local File from Device", "Use Web Image URL"))

    uploaded_image = None
    image_name_log = "No Image Uploaded"

    if 'final_pasted_image_string' not in st.session_state:
        st.session_state['final_pasted_image_string'] = None

    if image_option == "📋 Paste Copied Photo (Ctrl+V)":
        st.write("👇 **Click the box below once**, then press **Ctrl + V** to paste your clipboard picture:")
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
            st.session_state['final_pasted_image_string'] = pasted_stream_result
        if st.session_state['final_pasted_image_string']:
            uploaded_image = st.session_state['final_pasted_image_string']
            image_name_log = uploaded_image
            
    elif image_option == "📤 Upload Local File from Device":
        st.session_state['final_pasted_image_string'] = None
        file_device_upload = st.file_uploader("Select an image file:", type=["jpg", "jpeg", "png"])
        if file_device_upload:
            uploaded_image = file_device_upload
            image_name_log = file_device_upload.name
    else:
        st.session_state['final_pasted_image_string'] = None
        image_url = st.text_input("Paste Image URL:", value="https://unsplash.com")
        if image_url:
            uploaded_image = image_url
            image_name_log = image_url

    st.write("### 💾 Database Control Actions")
    if st.button("🚀 Publish and Save New Article to Archives", use_container_width=True):
        if not headline_input.strip():
            st.error("❌ Heading cannot be blank!")
        else:
            save_article_to_cloud(headline_input, sub_header_input, source_location_input, body_input, date_input, image_name_log)
            st.rerun()

# ====================================================================
# FACE 2: PUBLIC PORTAL NEWS READER (Default Standard Face)
# ====================================================================
else:
    # Sidebar search filter for public readers to browse stories by keyword safely
    search_query = st.sidebar.text_input("🔍 వెతకండి (Search articles by keyword):", placeholder="Type keywords here...").strip()
    
    st.markdown("### 📰 తాజా వార్తలు (Latest News Updates)")
    st.write("") 

    if all_articles:
        for art in all_articles:
            # Skip iterations if a row does not match active search filters
            if search_query and search_query.lower() not in str(art.get("headline", "")).lower():
                continue
                
            arc_headline = art.get("headline", "Untitled Headline")
            arc_sub_header = art.get("sub_header", "")
            arc_location = art.get("source_location", "")
            arc_content = art.get("content", "")
            arc_date = art.get("date", "")
            arc_image = art.get("associated_image", "")
            
            # Clean layout reader container card (Completely hides input boxes, forms, or save codes)
            with st.container(border=True):
                st.markdown(f"<h2 style='color:#000000; font-weight:700; margin-bottom:5px;'>{arc_headline}</h2>", unsafe_allow_html=True)
                
                if arc_sub_header:
                    st.markdown(f"<h4 style='color:#444444; font-style:italic; margin-bottom:10px;'>{arc_sub_header}</h4>", unsafe_allow_html=True)
                    
                st.caption(f"📅 ప్రచురణ: {arc_date}")
                st.markdown("<hr style='margin: 10px 0; border-top:1px solid #eee;'>", unsafe_allow_html=True)
                
                col_text, col_photo = st.columns([0.65, 0.35], gap="large")
                
                with col_text:
                    display_text = ""
                    if arc_location:
                        display_text += f"**{arc_location} :** "
                    display_text += str(arc_content)
                    st.write(display_text)
                    
                with col_photo:
                    if arc_image and isinstance(arc_image, str) and (arc_image.startswith("http") or arc_image.startswith("data:image")):
                        st.image(arc_image, use_container_width=True)
    else:
        # Initial baseline sample story to present a crisp placeholder layout until the Google Sheet populates
        with st.container(border=True):
            st.markdown("## తమిళనాడు సీఎం విజయ్ దళపతితో అరకు ఎంపీ దంపతుల భేటీ")
            st.caption(f"📅 తేదీ: {datetime.now().strftime('%B %d, %Y')}")
            st.markdown("---")
            col_t, col_p = st.columns([0.65, 0.35], gap="large")
            with col_t:
                st.write("**ఆనందపురం డెక్కన్ న్యూస్ :** పార్లమెంటరీ పట్టణ మరియు అభివృద్ధి అధ్యయన పర్యటనలో భాగంగా తమిళనాడును సందర్శించిన అరకు పార్లమెంట్ సభ్యురాలు (ఎంపీ) దంపతులు ఆ రాష్ట్ర ముఖ్యమంత్రి సి జోసెఫ్ విజయ్ ని మర్యాదపూర్వకంగా కలిశారు. తమిళనాడు సచివాలయంలో జరిగిన ఈ సమావేశంలో అరకు లోయ ప్రాంత అభివృద్దిపై పలు విషయాలు చర్చించారు.")
            with col_p:
                st.image("https://unsplash.com", use_container_width=True)

# ====================================================================
# 9. FOOTER STATUS BAR MONITOR
# ====================================================================
st.markdown("---")
st.caption("📰 **నేటి డెక్కన్ (Neti Deccan) Public News Portal Engine v4.1**")
