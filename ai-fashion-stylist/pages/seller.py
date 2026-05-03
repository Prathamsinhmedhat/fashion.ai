import streamlit as st
import razorpay
import datetime

# -------------------------------
# ⚡ PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Seller Dashboard", layout="wide")

st.title("🛍️ StyleVerse Seller Dashboard")

# -------------------------------
# 🔐 SESSION DATABASE
# -------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# -------------------------------
# 🔑 RAZORPAY CONFIG
# -------------------------------
RAZORPAY_KEY_ID = "rzp_test_SUmBWHk4qBiscQ"
RAZORPAY_SECRET = "Jom65YvEZbYYrfq9NYvOBG3c"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))

# -------------------------------
# 🧾 LOGIN / REGISTER
# -------------------------------
menu = ["Login", "Register"]
choice = st.sidebar.radio("Navigation", menu)

# -------------------------------
# 🆕 REGISTER
# -------------------------------
if choice == "Register":
    st.subheader("🆕 Create Seller Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if username in st.session_state.users:
            st.error("User already exists")
        else:
            st.session_state.users[username] = {
                "password": password,
                "subscription": None,
                "products": []
            }
            st.success("✅ Account created! Go to Login")

# -------------------------------
# 🔐 LOGIN
# -------------------------------
elif choice == "Login":
    st.subheader("🔐 Seller Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = st.session_state.users.get(username)

        if user and user["password"] == password:
            st.session_state.logged_in_user = username
            st.success(f"Welcome {username}")
            st.rerun()
        else:
            st.error("Invalid credentials")

# -------------------------------
# 🏠 DASHBOARD
# -------------------------------
if st.session_state.logged_in_user:

    user = st.session_state.users[st.session_state.logged_in_user]
    st.sidebar.success(f"Logged in as {st.session_state.logged_in_user}")

    now = datetime.datetime.now()

    # -------------------------------
    # 💳 SUBSCRIPTION
    # -------------------------------
    if not user["subscription"] or user["subscription"] < now:

        st.warning("⚠️ No Active Subscription")

        st.subheader("💳 Buy Subscription (₹199)")

        # Create Razorpay order
        if st.button("Pay Now"):

            order = client.order.create({
                "amount": 19900,
                "currency": "INR",
                "payment_capture": 1
            })

            order_id = order["id"]

            # Razorpay Checkout
            st.components.v1.html(f"""
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
            <script>
            var options = {{
                "key": "{RAZORPAY_KEY_ID}",
                "amount": "19900",
                "currency": "INR",
                "name": "StyleVerse",
                "description": "Seller Subscription",
                "order_id": "{order_id}",
                "handler": function (response){{
                    window.location.href = "?payment_id=" + response.razorpay_payment_id;
                }}
            }};
            var rzp = new Razorpay(options);
            rzp.open();
            </script>
            """, height=300)

        # -------------------------------
        # 🔍 VERIFY PAYMENT (FIXED)
        # -------------------------------
        params = st.query_params

        if "payment_id" in params:
            payment_id = params["payment_id"]

            try:
                payment = client.payment.fetch(payment_id)

                if payment["status"] == "captured":
                    # ✅ SAVE SUBSCRIPTION
                    user["subscription"] = now + datetime.timedelta(days=30)

                    st.success("✅ Payment Successful! Subscription Activated")

                    # 🔥 IMPORTANT FIX
                    st.query_params.clear()
                    st.rerun()

                else:
                    st.error("❌ Payment Failed")

            except Exception as e:
                st.error(f"Payment Error: {str(e)}")

    # -------------------------------
    # 🟢 ACTIVE SUBSCRIPTION
    # -------------------------------
    else:
        st.success(f"✅ Subscription Active till {user['subscription']}")

        # -------------------------------
        # 📦 ADD PRODUCT
        # -------------------------------
        st.markdown("## 📦 Add Product")

        name = st.text_input("Product Name")
        price = st.text_input("Price")
        image = st.text_input("Image URL")
        link = st.text_input("Product Link")

        if st.button("Add Product"):
            user["products"].append({
                "name": name,
                "price": price,
                "image": image,
                "link": link
            })
            st.success("✅ Product Added")

        # -------------------------------
        # 🛍️ SHOW PRODUCTS
        # -------------------------------
        st.markdown("## 🛍️ Your Products")

        if user["products"]:
            cols = st.columns(3)

            for i, p in enumerate(user["products"]):
                with cols[i % 3]:
                    st.image(p["image"])
                    st.write(f"**{p['name']}**")
                    st.write(p["price"])
                    st.link_button("View Product", p["link"])
        else:
            st.info("No products added yet")

    # -------------------------------
    # 🚪 LOGOUT
    # -------------------------------
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_user = None
        st.rerun()