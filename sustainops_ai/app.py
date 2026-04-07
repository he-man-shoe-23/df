import streamlit as st
import pandas as pd

# --- CONSTANTS ---
KM_PER_LITER_PETROL = 15
ELECTRICITY_CONSUMPTION_EV = 0.15  # kWh/km
MONTHS_IN_5_YEARS = 60
PETROL_EMISSION_FACTOR = 2.3 #kg CO2 per liter petrol
EV_EMISSION_FACTOR = 0.7 #kg CO2 per kWh

st.set_page_config(page_title="SustainOps AI", layout="centered")

st.title("🚚 SustainOps AI - EV Decision Assistant")
st.write("AI tool to help businesses evaluate Petrol vs EV over 5 years")

# --- OPTION ---
option = st.radio("Choose Input Method", ["Manual Entry", "Upload File"])

# --- CALCULATION FUNCTION ---
def calculate(daily_distance_km, operating_days_per_month, fleet_size, petrol_price, electricity_price, petrol_vehicle_cost, ev_vehicle_cost):
    """
    Calculates the total cost and emissions for petrol and EV vehicles over 5 years.

    Args:
        daily_distance_km (float): Daily distance traveled by each vehicle in km.
        operating_days_per_month (int): Number of operating days per month.
        fleet_size (int): Number of vehicles in the fleet.
        petrol_price (float): Price of petrol per liter.
        electricity_price (float): Price of electricity per kWh.
        petrol_vehicle_cost (float): Cost of a petrol vehicle.
        ev_vehicle_cost (float): Cost of an EV vehicle.

    Returns:
        tuple: (petrol_total_5yr, ev_total_5yr, petrol_emissions, ev_emissions, savings_5yr, payback)
    """

    total_km = daily_distance_km * operating_days_per_month * fleet_size

    petrol_cost_month = (total_km / KM_PER_LITER_PETROL) * petrol_price
    ev_cost_month = (total_km * ELECTRICITY_CONSUMPTION_EV) * electricity_price

    petrol_total_5yr = petrol_cost_month * MONTHS_IN_5_YEARS + (petrol_vehicle_cost * fleet_size)
    ev_total_5yr = ev_cost_month * MONTHS_IN_5_YEARS + (ev_vehicle_cost * fleet_size)

    petrol_emissions = (total_km / KM_PER_LITER_PETROL) * PETROL_EMISSION_FACTOR
    ev_emissions = (total_km * ELECTRICITY_CONSUMPTION_EV) * EV_EMISSION_FACTOR

    savings_5yr = petrol_total_5yr - ev_total_5yr

    extra_cost = (ev_vehicle_cost - petrol_vehicle_cost) * fleet_size
    monthly_savings = petrol_cost_month - ev_cost_month

    if monthly_savings > 0:
        payback = extra_cost / monthly_savings
    else:
        payback = None

    return petrol_total_5yr, ev_total_5yr, petrol_emissions, ev_emissions, savings_5yr, payback


# --- RECOMMENDATION ---
def recommend(savings_5yr, payback):
    """
    Recommends whether to switch to EV based on savings and payback period.

    Args:
        savings_5yr (float): Total savings over 5 years.
        payback (float): Payback period in months.

    Returns:
        str: Recommendation string.
    """
    if savings_5yr > 0 and payback is not None and payback < 36:
        return "✅ Strongly switch to EV"
    elif savings_5yr > 0:
        return "⚡ EV beneficial long-term"
    else:
        return "⛽ Stay with Petrol"


# =========================
# 🟢 MANUAL INPUT
# =========================
if option == "Manual Entry":

    st.subheader("Enter Business Details")

    daily_distance_km = st.number_input("Distance per day (km)", value=50, min_value=0)
    operating_days_per_month = st.number_input("Operating days/month", value=26, min_value=1, max_value=31)
    fleet_size = st.number_input("Fleet size", value=5, min_value=1)

    petrol_price = st.number_input("Petrol price (₹)", value=100, min_value=0)
    electricity_price = st.number_input("Electricity price (₹)", value=8, min_value=0)

    petrol_vehicle_cost = st.number_input("Petrol vehicle cost (₹)", value=600000, min_value=0)
    ev_vehicle_cost = st.number_input("EV vehicle cost (₹)", value=900000, min_value=0)

    if st.button("Analyze"):
        try:
            petrol_total_5yr, ev_total_5yr, petrol_emissions, ev_emissions, savings_5yr, payback = calculate(
                daily_distance_km, operating_days_per_month, fleet_size, petrol_price, electricity_price, petrol_vehicle_cost, ev_vehicle_cost
            )

            st.subheader("📊 Results")

            st.write(f"Petrol 5-Year Cost: ₹{petrol_total_5yr:,.0f}")
            st.write(f"EV 5-Year Cost: ₹{ev_total_5yr:,.0f}")
            st.write(f"Savings: ₹{savings_5yr:,.0f}")

            if payback is not None:
                st.write(f"Payback: {payback:.1f} months")
            else:
                st.write("No payback")

            st.write("Recommendation:", recommend(savings_5yr, payback))

        except Exception as e:
            st.error(f"An error occurred during calculation: {e}")


# =========================
# 🟡 FILE UPLOAD (CSV + EXCEL)
# =========================
else:

    st.subheader("Upload CSV or Excel File")

    file = st.file_uploader("Upload file", type=["csv", "xlsx"])

    if file:
        try:
            # Detect file type
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                raise ValueError("Invalid file type. Only CSV and Excel files are supported.")

            st.write("Preview Data")
            st.write(df.head())

            required_columns = ["distance", "days", "fleet", "petrol_price", "electricity_price", "petrol_vehicle_cost", "ev_vehicle_cost", "business_name", "city", "state"]
            for col in required_columns:
                if col not in df.columns:
                    raise KeyError(f"Required column '{col}' is missing in the uploaded file.")

            for i, row in df.iterrows():
                try:
                    petrol_total_5yr, ev_total_5yr, petrol_emissions, ev_emissions, savings_5yr, payback = calculate(
                        row["distance"], row["days"], row["fleet"],
                        row["petrol_price"], row["electricity_price"],
                        row["petrol_vehicle_cost"], row["ev_vehicle_cost"]
                    )

                    st.write(f"### {row['business_name']} ({row['city']}, {row['state']})")

                    st.write(f"Petrol Cost: ₹{petrol_total_5yr:,.0f}")
                    st.write(f"EV Cost: ₹{ev_total_5yr:,.0f}")
                    st.write(f"Savings: ₹{savings_5yr:,.0f}")

                    if payback is not None:
                        st.write(f"Payback: {payback:.1f} months")
                    else:
                        st.write("No payback")

                    st.write("Recommendation:", recommend(savings_5yr, payback))
                    st.markdown("---")  # Visual separation

                except Exception as e:
                    st.error(f"Error processing row {i+2}: {e}") #i+2 as i starts from 0 and the header is row 1

        except FileNotFoundError:
            st.error("File not found. Please upload a valid file.")
        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty.")
        except KeyError as e:
            st.error(str(e))
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

              