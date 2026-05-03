import streamlit as st
from serpapi import GoogleSearch
import os
import datetime

# -------------------------------
# ⚡ PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="StyleVerse AI | Premium Fashion",
    page_icon="👕",
    layout="wide"
)

# -------------------------------
# 🎨 UI STYLING
# -------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
}
.product-card {
    background: rgba(255,255,255,0.85);
    border-radius: 18px;
    padding: 12px;
    transition: 0.3s;
}
.product-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.08);
}
.price-tag {
    color: #2ecc71;
    font-weight: bold;
}
.source-tag {
    font-size: 12px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 💰 SPONSORED BRANDS
# -------------------------------
sponsored_brands = ["Nike", "Adidas", "Puma", "Zara"]

# -------------------------------
# 🔥 API FUNCTION (CORRECT)
# -------------------------------
def get_products_serpapi(query):
    try:
        params = {
            "engine": "google_shopping",
            "q": f"{query} site:myntra.com OR site:ajio.com OR site:amazon.in",
            "hl": "en",
            "gl": "in",
            "api_key": os.getenv("SERPAPI_KEY")  # MUST set in secrets
        }

        search = GoogleSearch(params)
        results = search.get_dict()

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

    except Exception as e:
        st.error(f"API Error: {e}")
        return []

# -------------------------------
# 📂 SIDEBAR
# -------------------------------
with st.sidebar:
    st.title("StyleVerse")

    gender = st.selectbox("Gender", ["Male", "Female"])
    style = st.selectbox("Style", ["Casual", "Formal", "Streetwear"])
    occasion = st.selectbox("Occasion", ["College", "Office", "Party"])

    product_type = st.selectbox("Outfit", ["T-shirt", "Shirt", "Jeans"])
    footwear_type = st.selectbox("Footwear", ["Sneakers", "Shoes"])
    accessories_type = st.selectbox("Accessory", ["Watch", "Bag"])

    budget = st.slider("Budget (₹)", 500, 20000, 5000)
    generate_btn = st.button("✨ Find My Style")

# -------------------------------
# 🧠 SESSION DATA
# -------------------------------
if "outfits" not in st.session_state:
    st.session_state.outfits = []
if "footwear" not in st.session_state:
    st.session_state.footwear = []
if "accessories" not in st.session_state:
    st.session_state.accessories = []
if "products" not in st.session_state:
    st.session_state.products = []

# -------------------------------
# 🚀 FETCH PRODUCTS
# -------------------------------
if generate_btn:
    st.session_state.outfits = get_products_serpapi(
        f"{gender} {style} {product_type} {occasion} under {budget}"
    )
    st.session_state.footwear = get_products_serpapi(
        f"{gender} {style} {footwear_type} under {budget}"
    )
    st.session_state.accessories = get_products_serpapi(
        f"{gender} {style} {accessories_type} under {budget}"
    )

# -------------------------------
# 🧠 SELLER FILTER
# -------------------------------
active_seller_products = []

for p in st.session_state.get("products", []):
    if p.get("expiry") and p["expiry"] > datetime.datetime.now():
        active_seller_products.append(p)

all_items = (
    st.session_state.outfits +
    st.session_state.footwear +
    st.session_state.accessories +
    active_seller_products
)

if all_items:
    brands = list(set([p["source"] for p in all_items if p.get("source")]))
    selected_brand = st.selectbox("Filter by Brand", ["All"] + brands)
else:
    selected_brand = "All"

# -------------------------------
# 🔥 DISPLAY FUNCTION
# -------------------------------
def display_products(items):

    items = items + active_seller_products

    if selected_brand != "All":
        items = [p for p in items if p["source"] == selected_brand]

    if not items:
        st.info("No products found")
        return

    sponsored = [p for p in items if p["source"] in sponsored_brands]
    normal = [p for p in items if p["source"] not in sponsored_brands]

    # Sponsored
    if sponsored:
        st.subheader("💎 Sponsored")
        cols = st.columns(4)

        for i, item in enumerate(sponsored):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="product-card" style="border:2px solid gold;">
                    <img src="{item['image']}" style="width:100%;height:180px;object-fit:contain;">
                    <p class="source-tag">{item['source']}</p>
                    <p>{item['name']}</p>
                    <p class="price-tag">{item['price']}</p>
                    <p style="color:gold;">Sponsored</p>
                </div>
                """, unsafe_allow_html=True)

                link = item["link"] or item["fallback"]
                if link:
                    st.link_button("Buy", link, use_container_width=True)

    # Normal
    st.subheader("🛍️ Products")
    cols = st.columns(4)

    for i, item in enumerate(normal):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="product-card">
                <img src="{item['image']}" style="width:100%;height:180px;object-fit:contain;">
                <p class="source-tag">{item['source']}</p>
                <p>{item['name']}</p>
                <p class="price-tag">{item['price']}</p>
            </div>
            """, unsafe_allow_html=True)

            link = item["link"] or item["fallback"]
            if link:
                st.link_button("Buy", link, use_container_width=True)

# -------------------------------
# 📊 TABS
# -------------------------------
tab1, tab2, tab3 = st.tabs(["Outfits", "Footwear", "Accessories"])

with tab1:
    display_products(st.session_state.outfits)

with tab2:
    display_products(st.session_state.footwear)

with tab3:
    display_products(st.session_state.accessories)
