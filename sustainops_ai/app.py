import streamlit as st
import pandas as pd

st.set_page_config(page_title="SustainOps AI", layout="centered")

st.title("🤖 SustainOps AI - Agentic Fleet Decision System")
st.write("AI agent that analyzes, decides, and recommends fleet strategy")

# =========================
# INPUT MODE
# =========================
mode = st.radio("Choose Mode", ["Manual Input", "Upload Dataset"])

# =========================
# CALCULATION FUNCTION
# =========================
def calculate(distance, days, fleet, petrol_price, electricity_price, cng_price,
              petrol_vehicle_cost, ev_vehicle_cost, cng_vehicle_cost,
              petrol_mileage, ev_efficiency, cng_mileage, months):

    total_km = distance * days * fleet

    petrol_month = (total_km / petrol_mileage) * petrol_price
    ev_month = (total_km * ev_efficiency) * electricity_price
    cng_month = (total_km / cng_mileage) * cng_price

    petrol_total = petrol_month * months + petrol_vehicle_cost * fleet
    ev_total = ev_month * months + ev_vehicle_cost * fleet
    cng_total = cng_month * months + cng_vehicle_cost * fleet

    return petrol_total, ev_total, cng_total, total_km


# =========================
# 🟢 MANUAL INPUT
# =========================
if mode == "Manual Input":

    st.subheader("Enter Business Details")

    vehicle_type = st.selectbox("Vehicle Type", ["Generic", "Tata Ace"])

    if vehicle_type == "Tata Ace":
        petrol_mileage = 18
        ev_efficiency = 0.12
        cng_mileage = 25
    else:
        petrol_mileage = 15
        ev_efficiency = 0.15
        cng_mileage = 22

    distance = st.number_input("Distance per day (km)", value=50)
    days = st.number_input("Days per month", value=26)
    fleet = st.number_input("Fleet size", value=5)

    years = st.number_input("Years for analysis", value=5)
    months = years * 12

    petrol_price = st.number_input("Petrol price (₹)", value=100)
    cng_price = st.number_input("CNG price (₹)", value=80)
    electricity_price = st.number_input("Electricity price (₹)", value=8)

    petrol_cost = st.number_input("Petrol vehicle cost (₹)", value=600000)
    ev_cost = st.number_input("EV vehicle cost (₹)", value=900000)
    cng_cost = st.number_input("CNG vehicle cost (₹)", value=650000)

    if st.button("Run Analysis"):

        petrol, ev, cng, total_km = calculate(
            distance, days, fleet,
            petrol_price, electricity_price, cng_price,
            petrol_cost, ev_cost, cng_cost,
            petrol_mileage, ev_efficiency, cng_mileage, months
        )

        st.subheader("📊 Results")

        st.write(f"🚗 Petrol: ₹{petrol:,.0f}")
        st.write(f"⚡ EV: ₹{ev:,.0f}")
        st.write(f"🟢 CNG: ₹{cng:,.0f}")

        st.write(f"📏 Monthly KM: {total_km:,.0f}")
        st.write(f"📏 {years} Year KM: {total_km * months:,.0f}")

        best = min({"Petrol": petrol, "EV": ev, "CNG": cng},
                   key={"Petrol": petrol, "EV": ev, "CNG": cng}.get)

        st.subheader("🤖 Recommendation")
        st.success(f"Best Option: {best}")

        if best == "EV":
            st.write("⚡ High usage → EV gives maximum savings and lower emissions")
        elif best == "CNG":
            st.write("🟢 Moderate usage → CNG is cost-efficient")
        else:
            st.write("🚗 Low usage → Petrol is better due to low upfront cost")


# =========================
# 🟡 UPLOAD DATASET
# =========================
else:

    st.subheader("📂 Upload Dataset")

    file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

    if file:

        # ✅ FIXED FILE READING (STREAMLIT CLOUD SAFE)
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.stop()

        st.write("📄 Preview Data")
        st.dataframe(df.head())

        total_km_all = 0
        total_fleet = 0
        ev_count = 0
        cng_count = 0
        petrol_count = 0

        st.subheader("📊 AI Analysis")

        for _, row in df.iterrows():

            if row["vehicle_type"] == "Tata Ace":
                petrol_mileage = 18
                ev_efficiency = 0.12
                cng_mileage = 25
            else:
                petrol_mileage = 15
                ev_efficiency = 0.15
                cng_mileage = 22

            months = row["years"] * 12

            petrol, ev, cng, total_km = calculate(
                row["distance"], row["days"], row["fleet"],
                row["petrol_price"], row["electricity_price"], row["cng_price"],
                row["petrol_vehicle_cost"], row["ev_vehicle_cost"], row["cng_vehicle_cost"],
                petrol_mileage, ev_efficiency, cng_mileage, months
            )

            total_km_all += total_km
            total_fleet += row["fleet"]

            best = min({"Petrol": petrol, "EV": ev, "CNG": cng},
                       key={"Petrol": petrol, "EV": ev, "CNG": cng}.get)

            if best == "EV":
                ev_count += 1
            elif best == "CNG":
                cng_count += 1
            else:
                petrol_count += 1

            st.write(f"🔹 {row['business_name']} → Best: {best}")

        # =========================
        # 🤖 AGENT SUMMARY
        # =========================
        st.subheader("🤖 AI Agent Summary")

        st.write(f"Total Fleet Size: {total_fleet}")
        st.write(f"Total Monthly KM: {total_km_all:,.0f}")

        st.write(f"⚡ EV Best: {ev_count}")
        st.write(f"🟢 CNG Best: {cng_count}")
        st.write(f"🚗 Petrol Best: {petrol_count}")

        # =========================
        # 🚀 ACTION RECOMMENDATION
        # =========================
        st.subheader("🚀 Recommended Action")

        total = ev_count + cng_count + petrol_count

        if ev_count > cng_count and ev_count > petrol_count:
            percent = int((ev_count / total) * 100)
            st.success(f"👉 Switch approx {percent}% fleet to EV")

        elif cng_count > petrol_count:
            percent = int((cng_count / total) * 100)
            st.success(f"👉 Use CNG for approx {percent}% fleet")

        else:
            st.success("👉 Continue Petrol for low usage scenarios")

        # =========================
        # 💬 SIMPLE AI CHAT
        # =========================
        st.subheader("💬 Ask AI")

        q = st.text_input("Ask: Should I switch to EV?")

        if q:
            q = q.lower()

            if "ev" in q:
                st.write("🤖 EV is best for high daily usage and long-term savings.")
            elif "cng" in q:
                st.write("🤖 CNG is good for moderate usage and cost balance.")
            else:
                st.write("🤖 Decision depends on usage, fleet size, and cost.")