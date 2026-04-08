import streamlit as st
import pandas as pd

st.set_page_config(page_title="SustainOps AI", layout="centered")

st.title("🚚 SustainOps AI - Fleet Optimization Assistant")
st.write("Analyze Petrol vs EV vs CNG based on cost, usage & sustainability")

# =========================
# CONSTANTS
# =========================
MONTHS = 60
PETROL_EMISSION = 2.3
EV_EMISSION = 0.7
CNG_EMISSION = 2.0

# =========================
# CALCULATION FUNCTION
# =========================
def calculate(distance, days, fleet, petrol_price, electricity_price, cng_price,
              petrol_vehicle_cost, ev_vehicle_cost, cng_vehicle_cost,
              petrol_mileage, ev_efficiency, cng_mileage):

    total_km = distance * days * fleet

    petrol_month = (total_km / petrol_mileage) * petrol_price
    ev_month = (total_km * ev_efficiency) * electricity_price
    cng_month = (total_km / cng_mileage) * cng_price

    petrol_5yr = petrol_month * MONTHS + petrol_vehicle_cost * fleet
    ev_5yr = ev_month * MONTHS + ev_vehicle_cost * fleet
    cng_5yr = cng_month * MONTHS + cng_vehicle_cost * fleet

    petrol_em = (total_km / petrol_mileage) * PETROL_EMISSION
    ev_em = (total_km * ev_efficiency) * EV_EMISSION
    cng_em = (total_km / cng_mileage) * CNG_EMISSION

    return petrol_5yr, ev_5yr, cng_5yr, petrol_em, ev_em, cng_em, total_km


# =========================
# 🟢 MANUAL INPUT
# =========================
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
days = st.number_input("Operating days/month", value=26)
fleet = st.number_input("Fleet size", value=5)

petrol_price = st.number_input("Petrol price (₹)", value=100)
cng_price = st.number_input("CNG price (₹/kg)", value=80)
electricity_price = st.number_input("Electricity price (₹)", value=8)

petrol_vehicle_cost = st.number_input("Petrol vehicle cost (₹)", value=600000)
ev_vehicle_cost = st.number_input("EV vehicle cost (₹)", value=900000)
cng_vehicle_cost = st.number_input("CNG vehicle cost (₹)", value=650000)

if st.button("Analyze Manual Data"):

    petrol_5yr, ev_5yr, cng_5yr, petrol_em, ev_em, cng_em, total_km = calculate(
        distance, days, fleet,
        petrol_price, electricity_price, cng_price,
        petrol_vehicle_cost, ev_vehicle_cost, cng_vehicle_cost,
        petrol_mileage, ev_efficiency, cng_mileage
    )

    st.subheader("📊 Cost Comparison (5 Years)")
    st.write(f"🚗 Petrol: ₹{petrol_5yr:,.0f}")
    st.write(f"⚡ EV: ₹{ev_5yr:,.0f}")
    st.write(f"🟢 CNG: ₹{cng_5yr:,.0f}")

    st.subheader("🌍 Emissions")
    st.write(f"Petrol: {petrol_em:.1f} kg CO2")
    st.write(f"EV: {ev_em:.1f} kg CO2")
    st.write(f"CNG: {cng_em:.1f} kg CO2")

    st.subheader("📏 Usage Analysis")
    st.write(f"Total KM per month: {total_km:,.0f} km")
    st.write(f"Total KM over 5 years: {total_km * MONTHS:,.0f} km")

    # Recommendation
    costs = {"Petrol": petrol_5yr, "EV": ev_5yr, "CNG": cng_5yr}
    best = min(costs, key=costs.get)

    st.subheader("🤖 Recommendation")
    st.success(f"Best Option: {best}")

    if best == "EV":
        st.write("⚡ EV is recommended because:")
        st.write("- High daily usage → low running cost advantage")
        st.write("- Maximum savings over 5 years")
        st.write("- Lower emissions (sustainable option)")

    elif best == "CNG":
        st.write("🟢 CNG is recommended because:")
        st.write("- Moderate fuel cost compared to petrol")
        st.write("- Suitable for medium usage businesses")

    else:
        st.write("🚗 Petrol is recommended because:")
        st.write("- Lower upfront investment")
        st.write("- Suitable for low distance usage")


# =========================
# 🟡 FILE UPLOAD
# =========================
st.subheader("📂 Upload Business Dataset")

file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if file is not None:

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.write("📄 Preview Data")
    st.dataframe(df.head())

    st.subheader("📊 Results from Uploaded Data")

    for i, row in df.iterrows():

        if row["vehicle_type"] == "Tata Ace":
            petrol_mileage = 18
            ev_efficiency = 0.12
            cng_mileage = 25
        else:
            petrol_mileage = 15
            ev_efficiency = 0.15
            cng_mileage = 22

        petrol_5yr, ev_5yr, cng_5yr, petrol_em, ev_em, cng_em, total_km = calculate(
            row["distance"], row["days"], row["fleet"],
            row["petrol_price"], row["electricity_price"], row["cng_price"],
            row["petrol_vehicle_cost"], row["ev_vehicle_cost"], row["cng_vehicle_cost"],
            petrol_mileage, ev_efficiency, cng_mileage
        )

        st.write(f"### {row['business_name']} ({row['city']}, {row['state']})")

        st.write(f"🚗 Petrol: ₹{petrol_5yr:,.0f}")
        st.write(f"⚡ EV: ₹{ev_5yr:,.0f}")
        st.write(f"🟢 CNG: ₹{cng_5yr:,.0f}")

        st.write(f"📏 Monthly KM: {total_km:,.0f}")
        st.write(f"📏 5-Year KM: {total_km * MONTHS:,.0f}")

        costs = {"Petrol": petrol_5yr, "EV": ev_5yr, "CNG": cng_5yr}
        best = min(costs, key=costs.get)

        st.success(f"Best Option: {best}")

        if best == "EV":
            st.write("Reason: High usage → EV gives maximum savings")
        elif best == "CNG":
            st.write("Reason: Moderate usage → CNG is cost-efficient")
        else:
            st.write("Reason: Low usage → Petrol is better option")

        st.write("---")