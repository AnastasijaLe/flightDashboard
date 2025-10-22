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
    
    from flight_utils import update_flight_statuses, update_discount_codes
    
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
    ["Overview", "Flights", "Passengers", "Aircraft", "Crew", "Financial", "Weather"]
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

# Crew Section
elif section == "Crew":
    st.header("👨‍✈️ Crew Management")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Crew", safe_query(lambda: CrewMember.objects.count(), 0))
    with col2:
        st.metric("Pilots", safe_query(lambda: Pilot.objects.count(), 0))
    with col3:
        st.metric("Active Assignments", safe_query(lambda: FlightCrew.objects.count(), 0))
    
    st.subheader("🏆 Top 10 Pilots by Flight Hours")
    
    def get_top_pilots_by_hours():
        pilots_data = []
        for pilot in Pilot.objects.all():
            pilot_assignments = FlightCrew.objects.filter(
                pilot=pilot
            ).select_related('flight', 'flight__route')
            
            total_hours = 0
            flight_count = 0
            
            for assignment in pilot_assignments:
                flight = assignment.flight
                if flight and flight.departure_time and flight.arrival_time:
                    duration = flight.arrival_time - flight.departure_time
                    hours = duration.total_seconds() / 3600
                    total_hours += hours
                    flight_count += 1
            
            if flight_count > 0:
                pilots_data.append({
                    'Pilot': f"{pilot.name} {pilot.surname}",
                    'Airline': pilot.airline.name,
                    'Total Hours': round(total_hours, 1),
                    'Flights': flight_count,
                    'Avg Hours per Flight': round(total_hours / flight_count, 1)
                })
        
        pilots_data.sort(key=lambda x: x['Total Hours'], reverse=True)
        return pd.DataFrame(pilots_data[:10])
    
    top_pilots_data = safe_query(get_top_pilots_by_hours, pd.DataFrame())
    
    if not top_pilots_data.empty:
        fig = px.bar(
            top_pilots_data,
            x='Total Hours',
            y='Pilot',
            orientation='h',
            title="Top Pilots by Flight Hours",
            labels={'Total Hours': 'Total Flight Hours', 'Pilot': 'Pilot'},
            color='Total Hours',
            color_continuous_scale='viridis',
            hover_data=['Airline', 'Flights', 'Avg Hours per Flight']
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            top_pilots_data,
            use_container_width=True,
            column_config={
                'Pilot': st.column_config.TextColumn('Pilot Name'),
                'Airline': st.column_config.TextColumn('Airline'),
                'Total Hours': st.column_config.NumberColumn('Total Hours', format='%.1f h'),
                'Flights': st.column_config.NumberColumn('Flights Count'),
                'Avg Hours per Flight': st.column_config.NumberColumn('Avg Hours/Flight', format='%.1f h')
            }
        )
    else:
        st.info("No pilot flight data available")
    
    st.subheader("👩‍✈️ Top 10 Cabin Crew by Number of Flights")
    
    def get_top_cabin_crew():
        from django.db.models import Count
        
        cabin_crew_data = CrewMember.objects.annotate(
            flight_count=Count('flightcrew')
        ).order_by('-flight_count')[:10]
        
        data = []
        for crew in cabin_crew_data:
            data.append({
                'crew_member': f"{crew.name} {crew.surname}",
                'role': crew.role,
                'airline': crew.airline.name,
                'flight_count': crew.flight_count
            })
        
        return pd.DataFrame(data)
    
    top_cabin_crew_data = safe_query(get_top_cabin_crew, pd.DataFrame())
    
    if not top_cabin_crew_data.empty:
        fig = px.bar(
            top_cabin_crew_data,
            x='flight_count',
            y='crew_member',
            orientation='h',
            title="Top Cabin Crew by Number of Flights",
            labels={'flight_count': 'Number of Flights', 'crew_member': 'Crew Member'},
            color='flight_count',
            color_continuous_scale='plasma'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            top_cabin_crew_data[['crew_member', 'role', 'airline', 'flight_count']],
            use_container_width=True,
            column_config={
                'crew_member': 'Crew Member',
                'role': 'Role',
                'airline': 'Airline',
                'flight_count': 'Flights Count'
            }
        )
    else:
        st.info("No cabin crew flight data available")

# Financial Section
elif section == "Financial":
    st.header("💰 Financial Dashboard")
    
    def get_financial_data():
        total_revenue = sum(float(payment.amount) for payment in Payment.objects.all())
        total_bookings = Booking.objects.count()
        active_discounts = DiscountCode.objects.filter(valid_until__gte=datetime.now().date()).count()
        avg_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
        return total_revenue, total_bookings, active_discounts, avg_booking_value
    
    revenue, bookings, discounts, avg_value = safe_query(get_financial_data, (0, 0, 0, 0))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"${revenue:,.2f}")
    with col2:
        st.metric("Total Bookings", bookings)
    with col3:
        st.metric("Active Discounts", discounts)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 Recent Payments")
        
        def get_recent_payments():
            payments = Payment.objects.all().select_related('booking').order_by('-payment_date')[:15]
            data = []
            for payment in payments:
                data.append({
                    'Amount': f"${float(payment.amount):,.2f}",
                    'Method': payment.method,
                    'Status': payment.status,
                    'Date': payment.payment_date.strftime("%Y-%m-%d"),
                    'Booking ID': f"#{payment.booking.id}"
                })
            return pd.DataFrame(data)
        
        payments_data = safe_query(get_recent_payments, pd.DataFrame())
        
        if not payments_data.empty:
            styled_payments = payments_data.style.set_properties(**{
                'background-color': "#01040a",
                'color': "#faf9f9",
                'border-color': 'white'
            })
            
            st.dataframe(
                styled_payments,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("No payment data available")
    
    with col2:
        st.subheader("🎫 Active Discount Codes")
        
        def get_active_discounts():
            discounts = DiscountCode.objects.filter(valid_until__gte=datetime.now().date())
            data = []
            for discount in discounts:
                days_valid = (discount.valid_until - datetime.now().date()).days
                data.append({
                    'Code': discount.code,
                    'Discount': f"{discount.discount_percent}%",
                    'Valid Until': discount.valid_until.strftime("%Y-%m-%d"),
                    'Days Left': days_valid,
                    'Airline': discount.airline.name if discount.airline else "All"
                })
            return pd.DataFrame(data)
        
        discounts_data = safe_query(get_active_discounts, pd.DataFrame())
        
        if not discounts_data.empty:
            def color_days_left(days):
                if days < 7:
                    return 'color: #EF5350'  
                elif days < 30:
                    return 'color: #FFA726' 
                else:
                    return 'color: #4CAF50' 
            
            styled_discounts = discounts_data.style.map(
                color_days_left, subset=['Days Left']
            )
            
            st.dataframe(
                styled_discounts,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("No active discount codes")
          
st.divider()
st.caption("Airport Operations Dashboard • Built with Streamlit & Django")