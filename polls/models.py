from django.db import models

# Create your models here.
from django.db import models

class Airport(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.city}"


class Route(models.Model):
    departure_airport = models.ForeignKey(Airport, related_name="routes_from", on_delete=models.CASCADE, null=True, blank=True)
    arrival_airport = models.ForeignKey(Airport, related_name="routes_to", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.departure_airport} → {self.arrival_airport}"


class Airline(models.Model):
    name = models.CharField(max_length=200)
    iata_code = models.CharField(max_length=3, unique=True)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.iata_code})"


class Pilot(models.Model):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    airline = models.ForeignKey(Airline, related_name="pilots", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} {self.surname}"


class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="flights")
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    aircraft = models.ForeignKey("Aircraft", on_delete=models.SET_NULL, null=True, blank=True)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=50, default="Scheduled")

    def __str__(self):
        return f"{self.flight_number} ({self.route})"


class Passenger(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    passport_number = models.CharField(max_length=20, unique=True)
    flights = models.ManyToManyField(Flight, through="Ticket")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Ticket(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat = models.CharField(max_length=5)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.seat} for {self.passenger} on {self.flight}"


class Aircraft(models.Model):
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()
    manufacturer = models.CharField(max_length=100)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.registration_number} ({self.model})"


class CrewMember(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    role = models.CharField(max_length=100)  # e.g. "Flight Attendant", "Engineer"
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.role})"


class FlightCrew(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    crew_member = models.ForeignKey(CrewMember, on_delete=models.CASCADE)
    role_on_flight = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.crew_member} on {self.flight}"


class Gate(models.Model):
    gate_number = models.CharField(max_length=10)
    terminal = models.CharField(max_length=10)
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    def __str__(self):
        return f"Gate {self.gate_number} ({self.terminal})"


class Runway(models.Model):
    code = models.CharField(max_length=10)
    length_m = models.IntegerField()
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.airport.code} Runway {self.code}"


class Baggage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    weight = models.FloatField()
    status = models.CharField(max_length=50, default="Checked-in")

    def __str__(self):
        return f"Baggage for {self.ticket}"


class Booking(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Booking {self.id} - {self.passenger}"


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Completed")

    def __str__(self):
        return f"Payment {self.amount} for {self.booking}"


class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField()
    valid_until = models.DateField()
    airline = models.ForeignKey(Airline, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.code} (-{self.discount_percent}%)"


class Maintenance(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, default="Completed")

    def __str__(self):
        return f"Maintenance {self.aircraft} on {self.date}"


class Delay(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    reason = models.CharField(max_length=200)
    minutes_delayed = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delay {self.minutes_delayed} min ({self.reason})"


class WeatherReport(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    temperature = models.FloatField()
    visibility = models.FloatField()
    wind_speed = models.FloatField()
    conditions = models.CharField(max_length=200)

    def __str__(self):
        return f"Weather at {self.airport.code} - {self.conditions}"

class SecurityCheck(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Cleared")
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SecurityCheck for {self.passenger} ({self.status})"
