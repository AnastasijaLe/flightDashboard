from django.contrib import admin
from .models import Airport, Airline, Flight, Passenger,Ticket, Route, Pilot, Aircraft, CrewMember, FlightCrew, Gate, Runway, Baggage, Booking, Payment, DiscountCode, Maintenance, Delay, WeatherReport, SecurityCheck
# Register your models here.

admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Airline)
admin.site.register(Pilot)
admin.site.register(Flight)
admin.site.register(Passenger)
admin.site.register(Ticket)
admin.site.register(Aircraft)
admin.site.register(CrewMember)
admin.site.register(FlightCrew)
admin.site.register(Gate)
admin.site.register(Runway)
admin.site.register(Baggage)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(DiscountCode)
admin.site.register(Maintenance)
admin.site.register(Delay)
admin.site.register(WeatherReport)
admin.site.register(SecurityCheck)
