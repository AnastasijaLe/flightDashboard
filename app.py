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
    from django.utils import timezone as django_timezone

    from flights.models import (
        Airport, Route, Airline, Pilot, Flight, Passenger, Ticket,
        Aircraft, CrewMember, FlightCrew, Gate, Runway, Baggage, 
        Booking, Payment, DiscountCode, Maintenance, Delay, 
        WeatherReport, SecurityCheck
    )
    
    from flight_utils import update_flight_statuses
    
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

# sidebar
st.sidebar.title("Navigation")
if DJANGO_AVAILABLE:
    st.sidebar.success("✅ Django Available")
else:
    st.sidebar.warning("⚠️ Database Not Available")

# update flight statuses
if DJANGO_AVAILABLE:
    updated_count = update_flight_statuses()

section = st.sidebar.selectbox(
    "Select Section:",
    ["Overview", "Flights", "Passengers", "Aircraft", "Crew", "Operations", "Financial", "Weather"]
)

# overview
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
        airport_filter = st.selectbox("Airport", ["All"] + list(safe_query(lambda: [airport.city for airport in Airport.objects.all()], [])))
    
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

# passengers section
elif section == "Passengers":
    st.header("👤 Passenger Information")
    
    now = django_timezone.now() if DJANGO_AVAILABLE else datetime.now()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Passengers", safe_query(lambda: Passenger.objects.count(), 0))
    with col2:
        # currently in flight
        def get_passengers_in_sky():
            current_flights = Flight.objects.filter(
                departure_time__lte=now,
                arrival_time__gte=now,
                status__in=["In Flight", "Delayed"]
            )
            tickets = Ticket.objects.filter(flight__in=current_flights)
            return tickets.values('passenger').distinct().count()
        
        in_sky_count = safe_query(get_passengers_in_sky, 0)
        st.metric("Passengers in Sky", in_sky_count)
    with col3:
        # passengers with recently cancelled flights
        def get_passengers_cancelled_flights():
            week_ago = now - timedelta(days=7)
            cancelled_flights = Flight.objects.filter(
                status="Cancelled",
                departure_time__gte=week_ago
            )
            tickets = Ticket.objects.filter(flight__in=cancelled_flights)
            return tickets.values('passenger').distinct().count()
        
        cancelled_count = safe_query(get_passengers_cancelled_flights, 0)
        st.metric("Recent Cancellations (7d)", cancelled_count)

    # current flights with passengers
    st.subheader("🛫 Currently Flying Passengers")
    
    def get_current_flights_data():
        current_flights = Flight.objects.filter(
            departure_time__lte=now,
            arrival_time__gte=now,
            status__in=["In Flight", "Delayed"]
        ).select_related('route', 'route__departure_airport', 'route__arrival_airport')
        
        data = []
        for flight in current_flights:
            passenger_count = Ticket.objects.filter(flight=flight).count()
            if passenger_count > 0:
                data.append({
                    'flight_number': flight.flight_number,
                    'route': f"{flight.route.departure_airport.city} → {flight.route.arrival_airport.city}",
                    'departure': flight.departure_time.strftime('%H:%M'),
                    'arrival': flight.arrival_time.strftime('%H:%M'),
                    'passengers': passenger_count,
                    'status': flight.status
                })
        return pd.DataFrame(data)
    
    current_flights_data = safe_query(get_current_flights_data, pd.DataFrame())
    if not current_flights_data.empty:
        st.dataframe(current_flights_data, use_container_width=True)
    else:
        st.info("No flights currently in progress")

    st.subheader("🏆 Top 10 Frequent Flyers")
    
    def get_top_passengers():
        passengers = Passenger.objects.annotate(
            ticket_count=models.Count('ticket')
        ).order_by('-ticket_count')[:10]
        
        data = []
        for passenger in passengers:
            frequent_routes = Ticket.objects.filter(
                passenger=passenger
            ).values(
                'flight__route__arrival_airport__city'
            ).annotate(
                count=models.Count('id')
            ).order_by('-count')[:1]
            
            favorite_destination = frequent_routes[0]['flight__route__arrival_airport__city'] if frequent_routes else "N/A"
            
            data.append({
                'name': f"{passenger.first_name} {passenger.last_name}",
                'total_tickets': passenger.ticket_count,
                'favorite_destination': favorite_destination,
                'status': "Frequent Flyer" if passenger.ticket_count > 5 else "Regular"
            })
        return pd.DataFrame(data)

    top_passengers_data = safe_query(get_top_passengers, pd.DataFrame())
    if not top_passengers_data.empty:
        st.dataframe(top_passengers_data, use_container_width=True)

        fig = px.bar(
            top_passengers_data, 
            x='name', 
            y='total_tickets',
            title="Top Passengers by Number of Flights",
            color='status',
            color_discrete_map={"Frequent Flyer": "#03E7F3", "Regular": "#F3FB0E"}
        )
        fig.update_layout(xaxis_title="Passenger", yaxis_title="Number of Flights")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No passenger data available")

    # baggage info
    st.subheader("💼 Baggage Tracking - Current Flights")
    
    def get_current_baggage_data():
        current_flights = Flight.objects.filter(
            departure_time__lte=now,
            arrival_time__gte=now,
            status__in=["In Flight", "Delayed"]
        )
        current_tickets = Ticket.objects.filter(flight__in=current_flights)
        baggage = Baggage.objects.filter(
            ticket__in=current_tickets
        ).select_related('ticket__passenger', 'ticket__flight')[:20]
        
        data = []
        for bag in baggage:
            data.append({
                'passenger': f"{bag.ticket.passenger.first_name} {bag.ticket.passenger.last_name}",
                'flight': bag.ticket.flight.flight_number,
                'route': f"{bag.ticket.flight.route.departure_airport.city} → {bag.ticket.flight.route.arrival_airport.city}",
                'weight': f"{bag.weight}kg",
                'status': bag.status
            })   
        return pd.DataFrame(data)
    
    baggage_data = safe_query(get_current_baggage_data, pd.DataFrame())
    if not baggage_data.empty:
        st.dataframe(baggage_data, use_container_width=True)
    else:
        st.info("No baggage data for current flights")

# Aircraft Section
elif section == "Aircraft":
    st.header("✈️ Aircraft & Maintenance")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Aircraft", safe_query(lambda: Aircraft.objects.count(), 0))
    with col2:
        st.metric("In Maintenance", safe_query(lambda: Maintenance.objects.filter(status="In Progress").count(), 0))
    with col3:
        st.metric("Gates", safe_query(lambda: Gate.objects.count(), 0))
    with col4:
        st.metric("Runways", safe_query(lambda: Runway.objects.count(), 0))
    
    def get_aircraft_data():
        aircrafts = Aircraft.objects.all()
        data = []
        for aircraft in aircrafts:
            data.append({
                'registration': aircraft.registration_number,
                'model': aircraft.model,
                'airline': aircraft.airline.name,
                'capacity': aircraft.capacity
            })
        return pd.DataFrame(data)
    
    aircraft_data = safe_query(get_aircraft_data, pd.DataFrame())
    if not aircraft_data.empty:
        st.dataframe(aircraft_data, use_container_width=True)
    
    st.subheader("Maintenance Records")
    def get_maintenance_data():
        maintenance = Maintenance.objects.all().select_related('aircraft')[:20]
        data = []
        for maint in maintenance:
            data.append({
                'aircraft': maint.aircraft.registration_number,
                'date': maint.date,
                'type': maint.type,
                'status': maint.status
            })
        return pd.DataFrame(data)
    
    maintenance_data = safe_query(get_maintenance_data, pd.DataFrame())
    if not maintenance_data.empty:
        st.dataframe(maintenance_data, use_container_width=True)        
        
st.divider()
st.caption("Airport Operations Dashboard • Built with Streamlit & Django")