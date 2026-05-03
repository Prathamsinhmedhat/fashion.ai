import streamlit as st
import serpapi

# -------------------------------
# 🔥 PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="StyleVerse AI", layout="wide")

# -------------------------------
# 🎨 UI STYLE
# -------------------------------
st.markdown("""
<style>
.stApp {background-color: #ffffff; color: #111;}
.block-container {padding-top: 2rem;}

.stButton>button {
    background-color: black;
    color: white;
    border-radius: 8px;
    padding: 10px 18px;
}
</style>
""", unsafe_allow_html=True)

st.title("👕 StyleVerse - AI Fashion Stylist")

# -------------------------------
# 🔥 API FUNCTION
# -------------------------------
def get_products_serpapi(query):
    client = serpapi.Client(api_key="cd0500d57fe76691dda83d380f41d4d7a72ed24459143acf43616c16db2335d3")

    results = client.search({
        "engine": "google_shopping",
        "q": query,
        "hl": "en",
        "gl": "in"
    })

    items = []

    try:
        for product in results["shopping_results"][:12]:
            items.append({
                "name": product.get("title"),
                "price": product.get("price", "N/A"),
                "image": product.get("thumbnail"),
                "link": product.get("link"),
                "fallback": product.get("product_link"),
                "source": product.get("source", "Store")
            })
    except:
        st.warning("⚠️ API error or limit reached")

    return items

# -------------------------------
# 🎯 INPUTS
# -------------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    gender = st.selectbox("Gender", ["Male", "Female"])

with col2:
    style = st.selectbox("Style", ["Casual", "Formal", "Streetwear", "Minimal"])

with col3:
    budget = st.slider("Budget (₹)", 500, 10000, 2000)

with col4:
    product_type = st.selectbox("Outfit", ["T-shirt", "Shirt", "Jeans"])

with col5:
    footwear_type = st.selectbox("Footwear", ["Shoes", "Sneakers"])

with col6:
    accessories_type = st.selectbox("Accessory", ["Watch", "Sunglasses", "Bag"])

occasion = st.selectbox("Occasion", ["College", "Office", "Party"])

# -------------------------------
# 🧠 SESSION STATE
# -------------------------------
if "outfits" not in st.session_state:
    st.session_state.outfits = []

if "footwear" not in st.session_state:
    st.session_state.footwear = []

if "accessories" not in st.session_state:
    st.session_state.accessories = []

# -------------------------------
# 🚀 BUTTON
# -------------------------------
if st.button("✨ Get Suggestions"):

    outfit_query = f"{gender} {style} {product_type} {occasion}"
    footwear_query = f"{gender} {style} {footwear_type} {occasion}"
    accessory_query = f"{gender} {style} {accessories_type} {occasion}"

    st.session_state.outfits = get_products_serpapi(outfit_query)
    st.session_state.footwear = get_products_serpapi(footwear_query)
    st.session_state.accessories = get_products_serpapi(accessory_query)

# -------------------------------
# 📦 LOAD DATA
# -------------------------------
outfits = st.session_state.outfits
footwear = st.session_state.footwear
accessories = st.session_state.accessories

# -------------------------------
# 🔥 BRAND FILTER (WORKING)
# -------------------------------
if outfits:

    brands = list(set([p["source"] for p in outfits if p["source"]]))
    selected_brand = st.selectbox("Filter by Brand", ["All"] + brands)

    if selected_brand != "All":
        outfits = [p for p in outfits if p["source"] == selected_brand]

    st.write(f"Showing {len(outfits)} products")

if footwear:

    brands = list(set([p["source"] for p in footwear if p["source"]]))
    selected_brand = st.selectbox("Filter by Brand", ["All"] + brands)

    if selected_brand != "All":
        outfits = [p for p in footwear if p["source"] == selected_brand]

    st.write(f"Showing {len(footwear)} products")

if accessories:

    brands = list(set([p["source"] for p in accessories if p["source"]]))
    selected_brand = st.selectbox("Filter by Brand", ["All"] + brands)

    if selected_brand != "All":
        outfits = [p for p in accessories if p["source"] == selected_brand]

    st.write(f"Showing {len(accessories)} products")    
# -------------------------------
# 🧾 TABS
# -------------------------------
tab1, tab2, tab3 = st.tabs(["👕 Outfits", "👟 Footwear", "🕶️ Accessories"])

# 👕 OUTFITS
with tab1:
    cols = st.columns(4)
    for i, item in enumerate(outfits):
        with cols[i % 4]:
            st.image(item["image"])
            st.write(item["name"])
            st.write(item["price"])
            st.caption(item["source"])

            if item["link"]:
                st.link_button("🛒 Buy", item["link"])
            else:
                st.link_button("🔎 View", item["fallback"])

# 👟 FOOTWEAR
with tab2:
    cols = st.columns(4)
    for i, item in enumerate(footwear):
        with cols[i % 4]:
            st.image(item["image"])
            st.write(item["name"])
            st.write(item["price"])
            st.caption(item["source"])

            if item["link"]:
                st.link_button("🛒 Buy", item["link"])
            else:
                st.link_button("🔎 View", item["fallback"])

# 🕶️ ACCESSORIES
with tab3:
    cols = st.columns(4)
    for i, item in enumerate(accessories):
        with cols[i % 4]:
            st.image(item["image"])
            st.write(item["name"])
            st.write(item["price"])
            st.caption(item["source"])

            if item["link"]:
                st.link_button("🛒 Buy", item["link"])
            else:
                st.link_button("🔎 View", item["fallback"])