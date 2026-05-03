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
    }

    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
        background: white;
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

    /* Price tag color */
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
# 🧠 API FUNCTION (Original Logic)
# -------------------------------
def get_products_serpapi(query):
    # Using your provided API key
    client = serpapi.Client(api_key="cd0500d57fe76691dda83d380f41d4d7a72ed24459143acf43616c16db2335d3")
    try:
        results = client.search({
            "engine": "google_shopping",
            "q": query,
            "hl": "en",
            "gl": "in"
        })
        
        items = []
        for product in results.get("shopping_results", [])[:12]:
            items.append({
                "name": product.get("title"),
                "price": product.get("price", "N/A"),
                "image": product.get("thumbnail"),
                "link": product.get("link"),
                "fallback": product.get("product_link"),
                "source": product.get("source", "Store")
            })
        return items
    except Exception:
        st.error("⚠️ API limit reached or connection error.")
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
# 🧠 SESSION STATE MANAGEMENT
# -------------------------------
if "outfits" not in st.session_state: st.session_state.outfits = []
if "footwear" not in st.session_state: st.session_state.footwear = []
if "accessories" not in st.session_state: st.session_state.accessories = []

# -------------------------------
# 🚀 ACTION TRIGGER
# -------------------------------
if generate_btn:
    with st.spinner("Curating your personalized look..."):
        outfit_query = f"{gender} {style} {product_type} {occasion} under {budget}"
        footwear_query = f"{gender} {style} {footwear_type} {occasion} under {budget}"
        accessory_query = f"{gender} {style} {accessories_type} {occasion} under {budget}"

        st.session_state.outfits = get_products_serpapi(outfit_query)
        st.session_state.footwear = get_products_serpapi(footwear_query)
        st.session_state.accessories = get_products_serpapi(accessory_query)

# -------------------------------
# 🏛️ MAIN DISPLAY AREA
# -------------------------------

st.title("StyleVerse Personal Curation")
if generate_btn:
    with st.spinner("Curating your personalized look..."):
        outfit_query = f"{gender} {style} {product_type} {occasion} under {budget}"
        footwear_query = f"{gender} {style} {footwear_type} {occasion}"
        accessory_query = f"{gender} {style} {accessories_type} {occasion}"

        st.session_state.outfits = get_products_serpapi(outfit_query)
        st.session_state.footwear = get_products_serpapi(footwear_query)
        st.session_state.accessories = get_products_serpapi(accessory_query)
st.markdown(f"**Current Profile:** {gender} | {style} | {occasion}")



if st.session_state.outfits:
    # Filter Section (Merged Brand Logic)
    all_items = st.session_state.outfits + st.session_state.footwear + st.session_state.accessories
    brands = list(set([p["source"] for p in all_items if p["source"]]))
    selected_brand = st.selectbox("🏷️ Filter by Store/Brand", ["All Stores"] + brands)

    # UI Tabs
    tab1, tab2, tab3 = st.tabs(["👕 Outfits", "👟 Footwear", "🕶️ Accessories"])

    def display_grid(items, filter_brand):
        # Apply filter logic
        if filter_brand != "All Stores":
            items = [p for p in items if p["source"] == filter_brand]
        
        if not items:
            st.info("No items found for this filter.")
            return

        cols = st.columns(4)
        for i, item in enumerate(items):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="product-card">
                    <img src="{item['image']}" style="width:100%; height:180px; object-fit:contain; border-radius:10px;">
                    <div style="margin-top:10px;">
                        <span class="source-tag">{item['source']}</span>
                        <p style="font-weight:600; font-size:0.9rem; margin:5px 0; height:40px; overflow:hidden;">{item['name']}</p>
                        <p class="price-tag">{item['price']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Button link
                link = item["link"] if item["link"] else item["fallback"]
                st.link_button("🛒 View Product", link, use_container_width=True)

    with tab1: display_grid(st.session_state.outfits, selected_brand)
    with tab2: display_grid(st.session_state.footwear, selected_brand)
    with tab3: display_grid(st.session_state.accessories, selected_brand)

else:
    # Empty State for a clean look on launch
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("https://cdn-icons-png.flaticon.com/512/3050/3050232.png", width=100)
        st.subheader("Your fashion journey starts here.")
        st.write("Adjust your preferences in the sidebar and click **Find My Style** to see real-time shopping recommendations.")

st.sidebar.markdown("---")
st.sidebar.caption("Powered by SerpApi & Streamlit Glass")