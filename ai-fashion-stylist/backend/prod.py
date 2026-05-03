import streamlit as st
import serpapi
import pandas as pd
from datetime import datetime
import razorpay
from streamlit_searchbox import st_searchbox # Optional for better UX
import streamlit.components.v1 as components
import json
import os
from datetime import datetime

# -------------------------------
# ⚡ PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="StyleVerse AI | Partner Edition",
    page_icon="👕",
    layout="wide"
)



# -------------------------------
# 🎨 UI STYLING
# -------------------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f8f9fa, #e9ecef); }
.product-card {
    background: white;
    border-radius: 15px;
    padding: 15px;
    transition: 0.3s;
    border: 1px solid #eee;
}
.sponsored-card {
    border: 2px solid gold !important;
    background: #fffdf0 !important;
}
.price-tag { color: #2ecc71; font-weight: bold; font-size: 1.2rem; }
.badge {
    background: gold;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🏦 DATABASE SIMULATION
# -------------------------------
# In a real app, this would be a SQL Database (SQLite/PostgreSQL)
if "partner_inventory" not in st.session_state:
    st.session_state.partner_inventory = []

# -------------------------------
# 🛠️ MERCHANT ONBOARDING LOGIC
# -------------------------------
def partner_portal():
    st.header("🤝 Brand Partner Portal")
    st.info("Submit your product to be featured in the 'Sponsored' section.")
    
    with st.form("merchant_onboarding"):
        st.subheader("Step 1: Seller Verification")
        col1, col2 = st.columns(2)
        with col1:
            brand_name = st.text_input("Brand Name")
            gst_number = st.text_input("Tax ID / GST Number")
        with col2:
            store_url = st.text_input("Official Store URL")
            contact_email = st.text_input("Business Email")
            
        st.subheader("Step 2: Product Information")
        p_name = st.text_input("Product Title")
        p_price = st.number_input("Price (INR)", min_value=100)
        p_img = st.text_input("Image URL (Direct Link)")
        p_cat = st.selectbox("Category", ["Outfit", "Footwear", "Accessory"])
        
        st.subheader("Step 3: Promotion Plan")
        plan = st.radio("Select Plan", ["Basic (7 Days) - ₹1999", "Premium (30 Days) - ₹4999"])
        
        submitted = st.form_submit_button("Verify & Pay")
        
        if submitted:
            # --- AUTHENTICITY CHECK LOGIC ---
            if brand_name and gst_number and p_img:
                # 1. Validation check (Simulated)
                with st.spinner("Verifying Seller Authenticity..."):
                    # Here you would call a Tax API or check Store URL reputation
                    pass
                
                # 2. Append to 'Database'
                new_item = {
                    "name": f"⭐ {p_name}",
                    "price": f"₹{p_price}",
                    "image": p_img,
                    "link": store_url,
                    "source": brand_name,
                    "category": p_cat,
                    "is_sponsored": True,
                    "expiry": datetime.now()
                }
                st.session_state.partner_inventory.append(new_item)
                st.success(f"✅ Payment Successful! {brand_name} is now live.")
            else:
                st.error("Please fill all fields for verification.")

# -------------------------------
# 🔥 API FUNCTION
# -------------------------------
def get_products_serpapi(query):
    client = serpapi.Client(api_key="cd0500d57fe76691dda83d380f41d4d7a72ed24459143acf43616c16db2335d3")
    try:
        results = client.search({"engine": "google_shopping", "q": query, "hl": "en", "gl": "in"})
        items = []
        for product in results.get("shopping_results", [])[:8]:
            items.append({
                "name": product.get("title"),
                "price": product.get("price", "N/A"),
                "image": product.get("thumbnail"),
                "link": product.get("link"),
                "source": product.get("source", "Store"),
                "is_sponsored": False
            })
        return items
    except:
        return []

# -------------------------------
# 📂 MAIN APP NAVIGATION
# -------------------------------
menu = st.sidebar.selectbox("Navigate", ["Customer Stylist", "Merchant Portal"])

if menu == "Merchant Portal":
    partner_portal()
else:
    st.title("StyleVerse AI")
    
    # User Preferences
    with st.sidebar:
        gender = st.selectbox("Gender", ["Male", "Female"])
        style = st.selectbox("Style", ["Casual", "Formal", "Streetwear"])
        cat = st.selectbox("Type", ["Outfit", "Footwear", "Accessory"])
        outfits_type = st.selectbox("Type", ["shirt", "tshirt", "jeans"])
        budget = st.slider("Budget", 500, 20000, 5000)
        btn = st.button("✨ Get Suggestions")

    if btn:
        with st.spinner("Fetching best matches..."):
            # 1. Get Live Data
            live_items = get_products_serpapi(f"{gender} {style} {cat} {outfits_type} under {budget}")
            
            # 2. Inject Partner Data (Paid Promotion)
            # We filter partner data based on the user's category choice
            partners = [p for p in st.session_state.partner_inventory if p["category"] == cat]
            
            # Combine (Partners first!)
            st.session_state.final_results = partners + live_items

    # Display Results
   # 1. Initialize at the start (under your other session_state lines)
if "final_results" not in st.session_state:
    st.session_state.final_results = []

# 2. Wrap the display in a safety check
if st.session_state.final_results:
    st.subheader("Selected for You")
    cols = st.columns(4)
    for i, item in enumerate(st.session_state.final_results):
        with cols[i % 4]:
            # Standard safety checks for item content
            prod_name = item.get('name') or "Fashion Item"
            prod_price = item.get('price') or "N/A"
            prod_img = item.get('image') or ""
            
            st.markdown(f"""
            <div class="product-card" style="border:1px solid #ddd; padding:10px; border-radius:12px; background:white;">
                <img src="{prod_img}" style="width:100%; height:180px; object-fit:contain;">
                <p style="font-weight:600; margin-top:5px; height:45px; overflow:hidden;">{prod_name}</p>
                <p style="color:green; font-weight:bold;">{prod_price}</p>
            </div>
            """, unsafe_allow_html=True)

            # URL Safety Logic
            # 1. Improved URL Extraction (Prioritizing the direct store link)
            raw_url = item.get('link') or item.get('product_link') or item.get('fallback')

# 2. Final Safety Check
# If all API keys are missing, we still need a string to prevent a crash
            if not raw_url:
                safe_url = "https://www.google.com/search?q=" + item.get('name', 'fashion').replace(" ", "+")
            else:
                safe_url = str(raw_url)

# 3. Create the button
            st.link_button("🛒 View Product", safe_url, use_container_width=True)
else:
    # Visual placeholder before search
    st.write("---")
    st.caption("Enter your preferences in the sidebar to generate your custom style board.")
                




# -------------------------------
# ⚡ RAZORPAY CONFIG
# -------------------------------
# Replace with your actual Test/Live keys from Razorpay Dashboard
RAZORPAY_KEY_ID = "rzp_test_your_key_id"
RAZORPAY_KEY_SECRET = "rzp_test_RofXEvG9kr0gHC"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# -------------------------------
# 🎨 UI STYLING
# -------------------------------


st.markdown("""
<style>
    .stApp { background: #f4f7f6; }
    .product-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #eee;
    }
    .sponsored-border { border: 2px solid #FFD700 !important; background: #FFFDF0 !important; }
    .badge { background: #FFD700; color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 10px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🧠 DATABASE & SESSION
# -------------------------------
if "partner_inventory" not in st.session_state:
    st.session_state.partner_inventory = []

# -------------------------------
# 💳 PAYMENT & VERIFICATION FUNCTION
# -------------------------------
def trigger_razorpay_payment(amount, brand_name, product_data):
    """Creates a Razorpay order and embeds the JS checkout."""
    
    # Amount is in paise (100 paise = 1 INR)
    data = {
        "amount": amount * 100, 
        "currency": "INR",
        "receipt": f"receipt_{brand_name[:3]}",
        "payment_capture": 1 # Auto-capture payment
    }
    
    try:
        order = client.order.create(data=data)
        order_id = order['id']
        
        # HTML/JS for Razorpay Checkout
        razorpay_checkout_html = f"""
        <button id="pay-btn" style="background-color: #3399cc; color: white; padding: 15px 32px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold;">
            Proceed to Secure Payment (₹{amount})
        </button>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <script>
            var options = {{
                "key": "{RAZORPAY_KEY_ID}",
                "amount": "{amount * 100}",
                "currency": "INR",
                "name": "StyleVerse AI",
                "description": "Featured Listing for {brand_name}",
                "order_id": "{order_id}",
                "handler": function (response){{
                    // If payment is successful, send a message back to Streamlit
                    window.parent.postMessage({{
                        type: 'payment_success',
                        payment_id: response.razorpay_payment_id,
                        order_id: response.razorpay_order_id
                    }}, "*");
                }},
                "theme": {{ "color": "#3399cc" }}
            }};
            var rzp1 = new Razorpay(options);
            document.getElementById('pay-btn').onclick = function(e){{
                rzp1.open();
                e.preventDefault();
            }}
        </script>
        """
        components.html(razorpay_checkout_html, height=100)
        
    except Exception as e:
        st.error(f"Razorpay Error: {e}")

# -------------------------------
# 📂 MERCHANT PORTAL
# -------------------------------
def merchant_portal():
    st.header("🤝 Seller Onboarding & Payment")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("Brand Name", placeholder="e.g. Nike")
            gst = st.text_input("GST/Tax ID", placeholder="Verified ID")
            p_name = st.text_input("Product Title")
        with col2:
            p_img = st.text_input("Image URL")
            p_price = st.number_input("Product Price (₹)", min_value=1)
            p_link = st.text_input("Store Link (URL)")
        
        category = st.selectbox("Category", ["Outfit", "Footwear", "Accessory"])
        plan = st.selectbox("Promotion Plan", [("Standard (7 Days)", 1999), ("Pro (30 Days)", 4999)])
        
        if st.button("Verify & Generate Invoice"):
            if brand and gst and p_img:
                st.session_state.pending_product = {
                    "name": f"⭐ {p_name}",
                    "price": f"₹{p_price}",
                    "image": p_img,
                    "link": p_link,
                    "source": brand,
                    "category": category,
                    "is_sponsored": True
                }
                st.success("Verification Complete! Now proceed to payment below.")
                trigger_razorpay_payment(plan[1], brand, st.session_state.pending_product)
            else:
                st.warning("Please fill in all seller and product details.")

# -------------------------------
# 🔥 MAIN NAVIGATION
# -------------------------------
menu = st.sidebar.radio("Navigation", ["Style Home", "Partner Portal"])

if menu == "Partner Portal":
    merchant_portal()
    
    # LISTEN FOR PAYMENT SUCCESS (Via Component Communication)
    # Note: In a real production app, use a webhook for security.
    # This simulates the callback:
    if st.checkbox("Simulate Successful Payment (For Testing)"):
        if "pending_product" in st.session_state:
            st.session_state.partner_inventory.append(st.session_state.pending_product)
            del st.session_state.pending_product
            st.balloons()
            st.success("Product is now LIVE on the main page!")

elif menu == "Style Home":
    st.title("👕 StyleVerse AI")
    
    # Get standard results from SerpApi (Mocked here for brevity)
    # Search logic remains same as your previous code...
    
    st.subheader("Your Curated Look")
    
    # DISPLAY SPONSORED PRODUCTS FIRST
    if st.session_state.partner_inventory:
        st.markdown("### 💎 Featured Styles")
        cols = st.columns(4)
        for i, item in enumerate(st.session_state.partner_inventory):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="product-card sponsored-border">
                    <span class="badge">PROMOTED</span>
                    <img src="{item['image']}" style="width:100%; height:150px; object-fit:contain;">
                    <p style="color:gray; font-size:12px; margin:0;">{item['source']}</p>
                    <p style="font-weight:bold; margin-bottom:0;">{item['name']}</p>
                    <p style="color:green; font-weight:bold;">{item['price']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("View Deal", item['link'], use_container_width=True)
    
    st.info("No more sponsored products to show. Search to find more!")




# -------------------------------
# 💾 DATABASE LOGIC (Local JSON)
# -------------------------------
DB_FILE = "sponsored_products.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_to_db(item):
    db = load_db()
    db.append(item)
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

# -------------------------------
# ⚡ PAGE CONFIG
# -------------------------------

# -------------------------------
# 📂 MERCHANT PORTAL
# -------------------------------
def merchant_portal():
    st.header("🏢 Merchant Onboarding")
    
    with st.form("payment_form"):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("Brand Name")
            seller_id = st.text_input("GST/Seller ID (This is your Unique ID)")
        with col2:
            p_name = st.text_input("Product Name")
            p_img = st.text_input("Image URL")
        
        p_link = st.text_input("Purchase Link")
        p_price = st.text_input("Price (e.g. ₹1,999)")
        category = st.selectbox("Category", ["Outfit", "Footwear", "Accessory"])
        
        submitted = st.form_submit_button("Verify & Pay (Razorpay Simulation)")
        
        if submitted:
            if brand and seller_id and p_img:
                # Create the product object
                new_product = {
                    "seller_id": seller_id,
                    "name": p_name,
                    "price": p_price,
                    "image": p_img,
                    "link": p_link,
                    "source": brand,
                    "category": category,
                    "is_sponsored": True,
                    "timestamp": str(datetime.now())
                }
                # SAVE TO FILE (Permanent)
                save_to_db(new_product)
                st.balloons()
                st.success(f"Payment Verified! Product linked to Seller ID: {seller_id}")
            else:
                st.error("Missing information!")

# -------------------------------
# 🏠 MAIN DISPLAY
# -------------------------------
def main_app():
    st.title("👕 StyleVerse AI")
    
    # Load from the permanent database
    sponsored_items = load_db()
    
    if sponsored_items:
        st.subheader("💎 Featured Partners")
        cols = st.columns(4)
        for i, item in enumerate(sponsored_items):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="border:2px solid #FFD700; padding:10px; border-radius:15px; background:white;">
                    <img src="{item['image']}" style="width:100%; height:150px; object-fit:contain;">
                    <h4>{item['name']}</h4>
                    <p style="color:green; font-weight:bold;">{item['price']}</p>
                    <p style="font-size:10px; color:gray;">Seller: {item['seller_id']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("Buy Now", item['link'], use_container_width=True)

# -------------------------------
# 🚀 ROUTING
# -------------------------------
page = st.sidebar.selectbox("Go to", ["Home", "Merchant Portal"])

if page == "Home":
    main_app()
else:
    merchant_portal()    