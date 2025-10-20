import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

st.set_page_config(
    page_title="Airport Operations Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

DJANGO_AVAILABLE = False
try:
    import django
    django.setup()
    
    from django.db import models

    from flights.models import (
        Airport, Route, Airline, Pilot, Flight, Passenger, Ticket,
        Aircraft, CrewMember, FlightCrew, Gate, Runway, Baggage, 
        Booking, Payment, DiscountCode, Maintenance, Delay, 
        WeatherReport, SecurityCheck
    )
    DJANGO_AVAILABLE = True
except Exception as e:
    DJANGO_AVAILABLE = False
    st.sidebar.error(f"Django not available: {e}")

st.title("✈️ Airport Operations Dashboard")

def safe_query(query_func, default=None):
    try:
        return query_func()
    except Exception as e:
        st.error(f"Database error: {e}")
        return default

# Sidebar
st.sidebar.title("Navigation")
if DJANGO_AVAILABLE:
    st.sidebar.success("✅ Django Available")
else:
    st.sidebar.warning("⚠️ Database Not Available")

section = st.sidebar.selectbox(
    "Select Section:",
    ["Overview", "Flights", "Passengers", "Aircraft", "Crew", "Operations", "Financial", "Weather"]
)

# overwiev
if section == "Overview":
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        flights_count = safe_query(lambda: Flight.objects.count(), 0)
        st.metric("Total Flights", flights_count)
    
    with col2:
        passengers_count = safe_query(lambda: Passenger.objects.count(), 0)
        st.metric("Total Passengers", passengers_count)
    
    with col3:
        airlines_count = safe_query(lambda: Airline.objects.count(), 0)
        st.metric("Airlines", airlines_count)
    
    with col4:
        airports_count = safe_query(lambda: Airport.objects.count(), 0)
        st.metric("Airports", airports_count)
    
    st.divider()
    
    
    col1, col2 = st.columns(2)
    # flight status diagram
    with col1:
        st.subheader("Flight Status")
        def get_flight_status():
            flights = Flight.objects.all()
            status_counts = {}
            for flight in flights:
                status_counts[flight.status] = status_counts.get(flight.status, 0) + 1
            return status_counts
        
        status_data = safe_query(get_flight_status, {})
        if status_data:
            fig = px.pie(values=list(status_data.values()), names=list(status_data.keys()))
            st.plotly_chart(fig, use_container_width=True)
    
    # top airlines
    with col2:
        st.subheader("Airlines by Flight Count")
        def get_airline_flights():
            airlines = Airline.objects.all()
            data = []
            for airline in airlines:
                data.append({
                    'airline': airline.name,
                    'flights': airline.flights.count()
                })
            return pd.DataFrame(data)
        
        airline_data = safe_query(get_airline_flights, pd.DataFrame())
        if not airline_data.empty:
            fig = px.bar(airline_data.nlargest(10, 'flights'), x='airline', y='flights')
            st.plotly_chart(fig, use_container_width=True)

# Flights Section
elif section == "Flights":
    st.header("🛫 Flight Operations")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        date_filter = st.date_input("Select Date", datetime.now().date())
    with col2:
        status_filter = st.selectbox("Status", ["All", "Scheduled", "Boarding", "In Flight", "Landed", "Delayed", "Cancelled"])
    with col3:
        airport_filter = st.selectbox("Airport", ["All"] + list(safe_query(lambda: [airport.code for airport in Airport.objects.all()], [])))
    
    def get_flights_data():
        flights = Flight.objects.filter(departure_time__date=date_filter)
        if status_filter != "All":
            flights = flights.filter(status=status_filter)
        if airport_filter != "All":
            flights = flights.filter(route__departure_airport__code=airport_filter) | flights.filter(route__arrival_airport__code=airport_filter)
        
        data = []
        for flight in flights:
            departure_time = flight.departure_time.strftime("%H:%M") if flight.departure_time else "N/A"
            arrival_time = flight.arrival_time.strftime("%H:%M") if flight.arrival_time else "N/A"
            data.append({
                'flight_number': flight.flight_number,
                'airline': flight.airline.name,
                'route': f"{flight.route.departure_airport.code} → {flight.route.arrival_airport.code}",
                'departure_airport': f"{flight.route.departure_airport.country}",
                'arrival_airport':  f"{flight.route.arrival_airport.country}",
                'departure': departure_time,
                'arrival': arrival_time,
                'status': flight.status,
                'aircraft': flight.aircraft.registration_number if flight.aircraft else "N/A"
            })
        return pd.DataFrame(data)
    
    flights_data = safe_query(get_flights_data, pd.DataFrame())
    if not flights_data.empty:
        st.dataframe(flights_data, use_container_width=True)
    else:
        st.info("No flight data available")

st.divider()
st.caption("Airport Operations Dashboard • Built with Streamlit & Django")