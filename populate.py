import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from flights.models import (
    Airport, Route, Airline, Pilot, Flight, Passenger, Ticket,
    Aircraft, CrewMember, FlightCrew, Gate, Runway, Baggage,
    Booking, Payment, DiscountCode, Maintenance, Delay,
    WeatherReport, SecurityCheck
)

fake = Faker()

def clear_database(): 
    SecurityCheck.objects.all().delete()
    WeatherReport.objects.all().delete()
    Delay.objects.all().delete()
    Maintenance.objects.all().delete()
    DiscountCode.objects.all().delete()
    Payment.objects.all().delete()
    Booking.objects.all().delete()
    Baggage.objects.all().delete()
    Runway.objects.all().delete()
    Gate.objects.all().delete()
    FlightCrew.objects.all().delete()
    CrewMember.objects.all().delete()
    Ticket.objects.all().delete()
    Passenger.objects.all().delete()
    Flight.objects.all().delete()
    Pilot.objects.all().delete()
    Aircraft.objects.all().delete()
    Route.objects.all().delete()
    Airline.objects.all().delete()
    Airport.objects.all().delete()
    
    print("Database cleared successfully!")

def create_airports():
    airports_data = [
        {"code": "RIX", "name": "Riga International Airport", "city": "Riga", "country": "Latvia"},
        {"code": "LHR", "name": "Heathrow Airport", "city": "London", "country": "United Kingdom"},
        {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
        {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "United Arab Emirates"},
        {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan"},
        {"code": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia"},
        {"code": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada"},
        {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
        {"code": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands"},
        {"code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore"},
        {"code": "ICN", "name": "Incheon International Airport", "city": "Seoul", "country": "South Korea"},
        {"code": "MAD", "name": "Adolfo Suárez Madrid–Barajas Airport", "city": "Madrid", "country": "Spain"},
        {"code": "BCN", "name": "Barcelona–El Prat Airport", "city": "Barcelona", "country": "Spain"},
        {"code": "FCO", "name": "Leonardo da Vinci–Fiumicino Airport", "city": "Rome", "country": "Italy"},
        {"code": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand"},
        {"code": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Türkiye"},
        {"code": "JNB", "name": "O.R. Tambo International Airport", "city": "Johannesburg", "country": "South Africa"},
        {"code": "GRU", "name": "Guarulhos International Airport", "city": "São Paulo", "country": "Brazil"},
        {"code": "EZE", "name": "Ministro Pistarini International Airport", "city": "Buenos Aires", "country": "Argentina"},
        {"code": "DOH", "name": "Hamad International Airport", "city": "Doha", "country": "Qatar"},
        {"code": "CPH", "name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark"},
        {"code": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland"},
        {"code": "VIE", "name": "Vienna International Airport", "city": "Vienna", "country": "Austria"},
        {"code": "HEL", "name": "Helsinki-Vantaa Airport", "city": "Helsinki", "country": "Finland"},
        {"code": "OSL", "name": "Oslo Airport, Gardermoen", "city": "Oslo", "country": "Norway"},
        {"code": "ARN", "name": "Stockholm Arlanda Airport", "city": "Stockholm", "country": "Sweden"},
        {"code": "KUL", "name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "country": "Malaysia"},
        {"code": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong"},
        {"code": "MEX", "name": "Benito Juárez International Airport", "city": "Mexico City", "country": "Mexico"},
        {"code": "AKL", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand"},
        {"code": "CAI", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt"}
    ]

    airports = []
    for data in airports_data:
        airport = Airport.objects.create(**data)
        airports.append(airport)
        print(f"Created airport: {airport}")

    return airports

def create_airlines():
    airlines_data = [
        {"name": "Lufthansa", "iata_code": "LH", "country": "Germany"},
        {"name": "Air France", "iata_code": "AF", "country": "France"},
        {"name": "British Airways", "iata_code": "BA", "country": "United Kingdom"},
        {"name": "KLM Royal Dutch Airlines", "iata_code": "KL", "country": "Netherlands"},
        {"name": "Emirates", "iata_code": "EK", "country": "United Arab Emirates"},
        {"name": "Qatar Airways", "iata_code": "QR", "country": "Qatar"},
        {"name": "Singapore Airlines", "iata_code": "SQ", "country": "Singapore"},
        {"name": "Cathay Pacific", "iata_code": "CX", "country": "Hong Kong"},
        {"name": "Qantas", "iata_code": "QF", "country": "Australia"},
        {"name": "Japan Airlines", "iata_code": "JL", "country": "Japan"},
        {"name": "ANA All Nippon Airways", "iata_code": "NH", "country": "Japan"},
        {"name": "Turkish Airlines", "iata_code": "TK", "country": "TÃ¼rkiye"},
        {"name": "Air Canada", "iata_code": "AC", "country": "Canada"},
        {"name": "Swiss International Air Lines", "iata_code": "LX", "country": "Switzerland"},
        {"name": "Korean Air", "iata_code": "KE", "country": "South Korea"},
        {"name": "Ethiopian Airlines", "iata_code": "ET", "country": "Ethiopia"},
        {"name": "Air New Zealand", "iata_code": "NZ", "country": "New Zealand"},
        {"name": "Iberia", "iata_code": "IB", "country": "Spain"},
        {"name": "Virgin Atlantic", "iata_code": "VS", "country": "United Kingdom"},
        {"name": "Scandinavian Airlines (SAS)", "iata_code": "SK", "country": "Sweden"},
        {"name": "Austrian Airlines", "iata_code": "OS", "country": "Austria"},
        {"name": "Thai Airways", "iata_code": "TG", "country": "Thailand"},
        {"name": "EVA Air", "iata_code": "BR", "country": "Taiwan"},
        {"name": "Finnair", "iata_code": "AY", "country": "Finland"},
        {"name": "Air China", "iata_code": "CA", "country": "China"},
        {"name": "Aeromexico", "iata_code": "AM", "country": "Mexico"},
        {"name": "LATAM Airlines", "iata_code": "LA", "country": "Chile"},
        {"name": "Royal Jordanian", "iata_code": "RJ", "country": "Jordan"},
        {"name": "Philippine Airlines", "iata_code": "PR", "country": "Philippines"},
        {"name": "Icelandair", "iata_code": "FI", "country": "Iceland"}
    ]
    
    airlines = []
    for data in airlines_data:
        airline = Airline.objects.create(**data)
        airlines.append(airline)
        print(f"Created airline: {airline}")
    
    return airlines

def create_routes(airports):
 
    routes = []
    for _ in range(240):
        departure = random.choice(airports)
        arrival = random.choice(airports)
        while arrival == departure:
            arrival = random.choice(airports)
        
        route = Route.objects.create(
            departure_airport=departure,
            arrival_airport=arrival
        )
        routes.append(route)
        print(f"Created route: {route}")
    
    return routes

def create_pilots(airlines):
    
    pilots = []
    for _ in range(100):
        pilot = Pilot.objects.create(
            name=fake.first_name_male() if random.choice([True, False]) else fake.first_name_female(),
            surname=fake.last_name(),
            airline=random.choice(airlines)
        )
        pilots.append(pilot)
        print(f"Created pilot: {pilot}")
    
    return pilots

def create_aircraft(airlines):
    
    aircraft_models = [
        {"model": "A320-200", "manufacturer": "Airbus", "capacity": 180 },
        {"model": "737-800", "manufacturer": "Boeing", "capacity": 189 },
        {"model": "A350-900", "manufacturer": "Airbus", "capacity": 325 },
        {"model": "777-300ER", "manufacturer": "Boeing", "capacity": 396 },
        {"model": "CRJ-900", "manufacturer": "Bombardier", "capacity": 90 },
        {"model": "E195-E2", "manufacturer": "Embraer", "capacity": 146 },
        {"model": "A220-300", "manufacturer": "Airbus", "capacity": 150 },
        {"model": "787-9 Dreamliner", "manufacturer": "Boeing", "capacity": 296 },
        {"model": "ATR 72-600", "manufacturer": "ATR", "capacity": 78 },
        {"model": "747-8i", "manufacturer": "Boeing", "capacity": 467 },
        {"model": "A380-800", "manufacturer": "Airbus", "capacity": 575 },
        {"model": "Global 7500", "manufacturer": "Bombardier", "capacity": 19 },
        {"model": "Gulfstream G650", "manufacturer": "Gulfstream Aerospace", "capacity": 18 },
        {"model": "Citation X", "manufacturer": "Cessna", "capacity": 12 },
        {"model": "Airbus A321neo", "manufacturer": "Airbus", "capacity": 244 },
        {"model": "Boeing 737 MAX 10", "manufacturer": "Boeing", "capacity": 230 },
        {"model": "DHC-8-Q400", "manufacturer": "De Havilland Canada", "capacity": 90 },
        {"model": "Falcon 8X", "manufacturer": "Dassault Aviation", "capacity": 16 },
        {"model": "IL-96-300", "manufacturer": "Ilyushin", "capacity": 300 },
        {"model": "Tu-204", "manufacturer": "Tupolev", "capacity": 210 },
        {"model": "SkyRanger 100", "manufacturer": "Aerospace Corp", "capacity": 8 },
        {"model": "Voyager 450", "manufacturer": "Northstar Aviation", "capacity": 110 },
        {"model": "C-212 Aviocar", "manufacturer": "Airtech", "capacity": 28 },
        {"model": "Stratoliner 7", "manufacturer": "Cirrus Aviation", "capacity": 50 },
        {"model": "MD-11", "manufacturer": "McDonnell Douglas", "capacity": 298 },
        {"model": "Concorde", "manufacturer": "BAC/Aérospatiale", "capacity": 120 },
        {"model": "An-148", "manufacturer": "Antonov", "capacity": 85 },
        {"model": "Phenom 300", "manufacturer": "Embraer", "capacity": 11 },
        {"model": "Challenger 350", "manufacturer": "Bombardier", "capacity": 10 },
        {"model": "Legacy 600", "manufacturer": "Embraer", "capacity": 16 }
    ]
    
    aircraft_list = []
    for airline in airlines:
        for i in range(random.randint(2, 4)):
            model_data = random.choice(aircraft_models)
            aircraft = Aircraft.objects.create(
                model=model_data["model"],
                registration_number=fake.unique.bothify(text='??-###').upper(),
                capacity=model_data["capacity"],
                manufacturer=model_data["manufacturer"],
                airline=airline
            )
            aircraft_list.append(aircraft)
            print(f"Created aircraft: {aircraft}")
    
    return aircraft_list

def create_flights(airlines, routes, aircraft_list):
    flights = []
    now = timezone.now()
    
    for i in range(1000):
        airline = random.choice(airlines)
        route = random.choice(routes)
        aircraft = random.choice([a for a in aircraft_list if a.airline == airline] + [None])
        
        base_time = fake.date_time_between(start_date='-5d', end_date='+5d', tzinfo=pytz.UTC)
        flight_duration = timedelta(hours=random.randint(1, 14))
        arrival_time = base_time + flight_duration
        
        if arrival_time < now:
            # past
            if random.random() < 0.9:  # 90% landed successfully
                status = "Landed"
            else:  # 10% cancelled
                status = "Cancelled"
                
        elif base_time > now + timedelta(hours=2):
            # future
            if random.random() < 0.95:  # 95% scheduled
                status = "Scheduled"
            else:  # 5% cancelled in advance
                status = "Cancelled"
                
        elif base_time > now:
            # upcoming
            if random.random() < 0.7:  # 70% boarding
                status = "Boarding"
            elif random.random() < 0.9:  # 20% scheduled
                status = "Scheduled"
            else:  # 10% delayed
                status = "Delayed"
                
        else:
            # current
            if random.random() < 0.8:  # 80% in flight
                status = "In Flight"
            else:  # 20% delayed
                status = "Delayed"
        
        flight = Flight.objects.create(
            flight_number=f"{airline.iata_code}{random.randint(100, 9999)}",
            airline=airline,
            route=route,
            aircraft=aircraft,
            departure_time=base_time,
            arrival_time=arrival_time,
            status=status
        )
        flights.append(flight)
        print(f"Created flight: {flight} (Status: {status}, Dep: {base_time}, Arr: {arrival_time})")
    
    return flights

def create_passengers():
    passengers = []
    for _ in range(2500):
        passenger = Passenger.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            passport_number=fake.unique.bothify(text='??#######').upper()
        )
        passengers.append(passenger)
        print(f"Created passenger: {passenger}")
    return passengers

def create_tickets(passengers, flights):
    seats = [f"{row}{seat}" for row in range(1, 33) for seat in ['A', 'B', 'C', 'D', 'E', 'F']]
    
    tickets = []
    for _ in range(3000):
        passenger = random.choice(passengers)
        flight = random.choice(flights)
        
        ticket = Ticket.objects.create(
            passenger=passenger,
            flight=flight,
            seat=random.choice(seats)
        )
        tickets.append(ticket)
        print(f"Created ticket: {ticket}")
    return tickets

def create_crew_members(airlines):
    roles = ["Flight Attendant", "Senior Flight Attendant", "Purser", "Chief Purser"]
    
    crew_members = []
    for airline in airlines:
        for _ in range(random.randint(5, 8)):
            crew_member = CrewMember.objects.create(
                name=fake.first_name(),
                surname=fake.last_name(),
                role=random.choice(roles),
                airline=airline
            )
            crew_members.append(crew_member)
        print(f"Created crew members for {airline.name}")
    return crew_members

def create_flight_crews(flights, crew_members):
    flight_crews = []
    for flight in flights:
        num_crew = random.randint(3, 8)
        # filter by airline
        airline_crew = [cm for cm in crew_members if cm.airline == flight.airline]
        if airline_crew:
            assigned_crew = random.sample(airline_crew, min(num_crew, len(airline_crew)))
            
            for crew_member in assigned_crew:
                flight_crew = FlightCrew.objects.create(
                    flight=flight,
                    crew_member=crew_member,
                    role_on_flight=crew_member.role
                )
                flight_crews.append(flight_crew)
            print(f"Assigned {len(assigned_crew)} crew members to {flight.flight_number}")
    return flight_crews

def create_delays(flights):
    delays = []
    now = timezone.now()
    
    for flight in flights:
        if flight.status == "Delayed":
            minutes_delayed = random.randint(30, 180)
            reason = random.choice([
                "Weather Conditions",
                "Air Traffic Control",
                "Technical Issues",
                "Late Arriving Aircraft",
                "Crew Scheduling"
            ])
            
            delay = Delay.objects.create(
                flight=flight,
                reason=reason,
                minutes_delayed=minutes_delayed
            )
            delays.append(delay)
            print(f"Created delay: {delay}")
    
    return delays

def create_additional_data(airports, flights, tickets, passengers):
    
    # gates 
    for airport in airports:
        for i in range(1, random.randint(3, 8)):
            Gate.objects.create(
                gate_number=f"{random.choice(['A', 'B', 'C'])}{i}",
                terminal=random.choice(['1', '2', '3']),
                airport=airport
            )
    
    # runways 
    for airport in airports:
        for i in range(1, random.randint(2, 4)):
            Runway.objects.create(
                code=f"{random.choice(['0', '1', '2'])}{i}{random.choice(['L', 'C', 'R'])}",
                length_m=random.randint(2000, 4000),
                airport=airport
            )
    
    # baggage
    for ticket in random.sample(tickets, min(150, len(tickets))):
        Baggage.objects.create(
            ticket=ticket,
            weight=round(random.uniform(10.0, 32.0), 1),
            status=random.choice(["Checked-in", "Loaded", "In Transit", "Delivered"])
        )
    
    # bookings and payments
    for ticket in random.sample(tickets, min(100, len(tickets))):
        booking = Booking.objects.create(
            passenger=ticket.passenger,
            flight=ticket.flight,
            status=random.choice(["Confirmed", "Pending", "Cancelled"]),
            total_price=round(random.uniform(100.0, 2000.0), 2)
        )
        
        Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            method=random.choice(["Credit Card", "Debit Card", "PayPal", "Bank Transfer"]),
            status="Completed"
        )
    
    # discount codes
    airlines_list = list(Airline.objects.all())
    for _ in range(15):
        DiscountCode.objects.create(
            code=fake.unique.bothify(text='DISCOUNT##').upper(),
            discount_percent=random.choice([5, 10, 15, 20, 25]),
            valid_until=fake.date_between(start_date='+30d', end_date='+365d'),
            airline=random.choice(airlines_list + [None])
        )
    
    # maintenance records
    aircraft_list = list(Aircraft.objects.all())
    for aircraft in random.sample(aircraft_list, min(20, len(aircraft_list))):
        Maintenance.objects.create(
            aircraft=aircraft,
            date=fake.date_between(start_date='-60d', end_date='today'),
            type=random.choice(["Routine Check", "Engine Maintenance", "Avionics Update", "Interior Refurbishment"]),
            description=fake.sentence(),
            status=random.choice(["Completed", "In Progress", "Scheduled"])
        )
    
    # weather
    for airport in random.sample(airports, min(15, len(airports))):
        WeatherReport.objects.create(
            airport=airport,
            timestamp=fake.date_time_between(start_date='-7d', end_date='now'),
            temperature=round(random.uniform(-20.0, 40.0), 1),
            visibility=round(random.uniform(1.0, 20.0), 1),
            wind_speed=round(random.uniform(0.0, 50.0), 1),
            conditions=random.choice(["Clear", "Partly Cloudy", "Cloudy", "Rain", "Snow", "Fog"])
        )
    
    # security checks
    for passenger in random.sample(passengers, min(50, len(passengers))):
        SecurityCheck.objects.create(
            passenger=passenger,
            flight=random.choice(flights),
            status=random.choice(["Cleared", "Pending", "Additional Screening Required"])
        )

def main():  
    clear_database()
    
    airports = create_airports()
    airlines = create_airlines()
    routes = create_routes(airports)
    pilots = create_pilots(airlines)
    aircraft_list = create_aircraft(airlines)
    flights = create_flights(airlines, routes, aircraft_list)
    passengers = create_passengers()
    tickets = create_tickets(passengers, flights)
    crew_members = create_crew_members(airlines)
    flight_crews = create_flight_crews(flights, crew_members)
    
    create_additional_data(airports, flights, tickets, passengers)
    
    print("\n" + "="*50)
    print("Database populated successfully!")
    print("="*50)
    
    # Print summary
    print(f"\nSummary of created data:")
    print(f"Airports: {Airport.objects.count()}")
    print(f"Airlines: {Airline.objects.count()}")
    print(f"Routes: {Route.objects.count()}")
    print(f"Pilots: {Pilot.objects.count()}")
    print(f"Aircraft: {Aircraft.objects.count()}")
    print(f"Flights: {Flight.objects.count()}")
    print(f"Passengers: {Passenger.objects.count()}")
    print(f"Tickets: {Ticket.objects.count()}")
    print(f"Crew Members: {CrewMember.objects.count()}")
    print(f"Flight Crew Assignments: {FlightCrew.objects.count()}")

if __name__ == "__main__":
    main()