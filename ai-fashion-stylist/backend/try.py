import streamlit as st
import serpapi

# -------------------------------
# ⚡ PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="StyleVerse AI | Premium Fashion",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# 🎨 NEXT-LEVEL UI STYLING (CSS)
# -------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* Premium Card Design */
    .product-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.3s ease-in-out;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        position: relative;
    }

    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
        background: white;
    }

    /* Sponsored Badge */
    .sponsored-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: #ffd700;
        color: #000;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        z-index: 10;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #eee;
    }

    /* Button Styling */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #000000;
        color: white;
        border: none;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #333;
        color: #fff;
        transform: scale(1.02);
    }

    .price-tag {
        color: #2ecc71;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .source-tag {
        color: #888;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 🧠 API FUNCTION (With Sponsored detection)
# -------------------------------
def get_products_serpapi(query):
    client = serpapi.Client(api_key="cd0500d57fe76691dda83d380f41d4d7a72ed24459143acf43616c16db2335d3")
    try:
        results = client.search({
            "engine": "google_shopping",
            "q": query,
            "hl": "en",
            "gl": "in"
        })
        
        items = []
        # SerpApi marks sponsored items in tags or separate arrays, 
        # we check the main results for the 'tag' attribute.
        for product in results.get("shopping_results", [])[:12]:
            items.append({
                "name": product.get("title"),
                "price": product.get("price", "N/A"),
                "image": product.get("thumbnail"),
                "link": product.get("link"),
                "fallback": product.get("product_link"),
                "source": product.get("source", "Store"),
                # Detect if the product is paid/sponsored
                "is_sponsored": "Sponsored" in product.get("tag", "") or product.get("sponsored", False)
            })
        return items
    except Exception:
        return []

# -------------------------------
# 📂 SIDEBAR CONTROLS
# -------------------------------
with st.sidebar:
    st.markdown("# 👕 StyleVerse")
    st.caption("AI-Powered Personal Stylist")
    st.markdown("---")
    
    gender = st.radio("Gender", ["Male", "Female"], horizontal=True)
    style = st.selectbox("Aesthetic", ["Casual", "Formal", "Streetwear", "Minimal"])
    occasion = st.selectbox("Occasion", ["College", "Office", "Party", "Date Night"])
    
    st.markdown("### Item Selection")
    product_type = st.selectbox("Top/Bottom", ["T-shirt", "Shirt", "Jeans", "Trousers"])
    footwear_type = st.selectbox("Footwear", ["Sneakers", "Formal Shoes", "Loafers"])
    accessories_type = st.selectbox("Accessory", ["Watch", "Sunglasses", "Bag"])

    budget = st.slider("Budget (₹)", 500, 20000, 5000)
    
    st.markdown("---")
    generate_btn = st.button("✨ FIND MY STYLE")

# -------------------------------
# 🧠 SESSION STATE
# -------------------------------
if "outfits" not in st.session_state: st.session_state.outfits = []
if "footwear" not in st.session_state: st.session_state.footwear = []
if "accessories" not in st.session_state: st.session_state.accessories = []

# 🚀 ACTION TRIGGER
if generate_btn:
    with st.spinner("Curating your look..."):
        st.session_state.outfits = get_products_serpapi(f"{gender} {style} {product_type} {occasion} under {budget}")
        st.session_state.footwear = get_products_serpapi(f"{gender} {style} {footwear_type} {occasion}")
        st.session_state.accessories = get_products_serpapi(f"{gender} {style} {accessories_type} {occasion}")

# -------------------------------
# 🏛️ MAIN DISPLAY
# -------------------------------
st.title("StyleVerse Personal Curation")

if st.session_state.outfits:
    # Filter Section
    all_items = st.session_state.outfits + st.session_state.footwear + st.session_state.accessories
    brands = list(set([p["source"] for p in all_items if p["source"]]))
    selected_brand = st.selectbox("🏷️ Filter by Store/Brand", ["All Stores"] + brands)

    tab1, tab2, tab3 = st.tabs(["👕 Outfits", "👟 Footwear", "🕶️ Accessories"])

    def display_grid(items, filter_brand):
        if filter_brand != "All Stores":
            items = [p for p in items if p["source"] == filter_brand]
        
        if not items:
            st.info("No items found for this filter.")
            return

        cols = st.columns(4)
        for i, item in enumerate(items):
            with cols[i % 4]:
                # Check for sponsored status to add badge
                badge_html = '<div class="sponsored-badge">Promoted</div>' if item.get("is_sponsored") else ""
                
                st.markdown(f"""
                <div class="product-card">
                    {badge_html}
                    <img src="{item['image']}" style="width:100%; height:180px; object-fit:contain; border-radius:10px;">
                    <div style="margin-top:10px;">
                        <span class="source-tag">{item['source']}</span>
                        <p style="font-weight:600; font-size:0.9rem; margin:5px 0; height:40px; overflow:hidden;">{item['name']}</p>
                        <p class="price-tag">{item['price']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                link = item["link"] if item["link"] else item["fallback"]
                st.link_button("🛒 View Product", link, use_container_width=True)

    with tab1: display_grid(st.session_state.outfits, selected_brand)
    with tab2: display_grid(st.session_state.footwear, selected_brand)
    with tab3: display_grid(st.session_state.accessories, selected_brand)
else:
    st.info("Use the sidebar to start your style discovery.")






RAZORPAY_KEY_ID = "rzp_test_SUmBWHk4qBiscQ"
RAZORPAY_SECRET = "Jom65YvEZbYYrfq9NYvOBG3c"