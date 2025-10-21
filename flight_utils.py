from django.utils import timezone
from datetime import timedelta
from flights.models import Flight

def update_flight_statuses():
    now = timezone.now()
    updated_count = 0
    
    flights = Flight.objects.all()
    for flight in flights:
        old_status = flight.status
        
        # Determine new status based on current time
        if flight.arrival_time < now and flight.status != "Landed" and flight.status != "Cancelled":
            flight.status = "Landed"
        elif flight.departure_time < now < flight.arrival_time and flight.status not in ["In Flight", "Landed", "Cancelled"]:
            flight.status = "In Flight"
        elif flight.departure_time > now + timedelta(hours=2) and flight.status not in ["Scheduled", "Cancelled"]:
            flight.status = "Scheduled"
        elif now <= flight.departure_time <= now + timedelta(hours=2) and flight.status not in ["Boarding", "Delayed", "Cancelled"]:
            flight.status = "Boarding"
        
        if flight.status != old_status:
            flight.save()
            updated_count += 1
    
    return updated_count