import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

st.set_page_config(
    page_title="Flight Management System",
    page_icon="✈️",
    layout="wide"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

DJANGO_AVAILABLE = False
django_modules = {}

try:
    import django
    django.setup()
    
    from flights.models import (
        Airport, Route, Airline, Flight, Passenger, Ticket,
        Aircraft, CrewMember, Delay, WeatherReport
    )
    
    django_modules = {
        'Airport': Airport,
        'Route': Route,
        'Airline': Airline,
        'Flight': Flight,
        'Passenger': Passenger,
        'Ticket': Ticket,
        'Aircraft': Aircraft,
        'CrewMember': CrewMember,
        'Delay': Delay,
        'WeatherReport': WeatherReport
    }
    DJANGO_AVAILABLE = True
except Exception as e:
    DJANGO_AVAILABLE = False
    st.sidebar.error(f"Django not available: {e}")

st.title("✈️ Flight Management Dashboard")
st.markdown("---")

def safe_db_query(query_func, default_value=None):
    try:
        return query_func()
    except Exception as e:
        st.error(f"Database error: {e}")
        return default_value

def get_flight_status_counts():
    def query():
        flights = django_modules['Flight'].objects.all()
        status_counts = {}
        for flight in flights:
            status = flight.status
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    return safe_db_query(query, {})

def get_recent_flights(hours=24):
    def query():
        time_threshold = datetime.now() - timedelta(hours=hours)
        return list(django_modules['Flight'].objects.filter(
            departure_time__gte=time_threshold
        ).order_by('departure_time')[:10])
    return safe_db_query(query, [])

# sidebar
st.sidebar.title("Navigation")
if DJANGO_AVAILABLE:
    st.sidebar.success("✅ Django Connected")
else:
    st.sidebar.warning("⚠️ Using Demo Data")

section = st.sidebar.radio(
    "Select section:",
    ["📊 Overview", "🛫 Flights", "👥 Passengers", "✈️ Aircraft", "🌤️ Weather"]
)

# overwiev
if section == "📊 Overview":
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_flights = safe_db_query(lambda: django_modules['Flight'].objects.count(), 0)
        st.metric("Total Flights", total_flights)
    
    with col2:
        total_passengers = safe_db_query(lambda: django_modules['Passenger'].objects.count(), 0)
        st.metric("Total Passengers", total_passengers)
    
    with col3:
        total_airports = safe_db_query(lambda: django_modules['Airport'].objects.count(), 0)
        st.metric("Airports", total_airports)
    
    with col4:
        total_airlines = safe_db_query(lambda: django_modules['Airline'].objects.count(), 0)
        st.metric("Airlines", total_airlines)
    
    st.markdown("---")
    
st.markdown("---")
st.markdown("**Flight Management System**")