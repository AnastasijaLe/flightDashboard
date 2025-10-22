from django.utils import timezone
from datetime import timedelta
from flights.models import Flight, DiscountCode, Delay

def update_flight_statuses():
    now = timezone.now()
    updated_count = 0
    
    flights = Flight.objects.exclude(status__in=["Cancelled", "Landed"])
    
    for flight in flights:
        old_status = flight.status
        new_status = old_status 
        
        if old_status in ["Cancelled", "Landed"]:
            continue
            
        latest_delay = Delay.objects.filter(flight=flight).order_by('-updated_at').first()
        if latest_delay and latest_delay.minutes_delayed > 600:
            new_status = "Cancelled"
        
        elif flight.arrival_time < now:
            new_status = "Landed"
        
        elif flight.departure_time < now:
            if old_status != "Delayed":
                new_status = "In Flight"
        
        else:
            is_delayed = Delay.objects.filter(flight=flight, updated_at__date=now.date()).exists()
            time_until_departure = flight.departure_time - now
            
            if is_delayed:
                new_status = "Delayed"
            elif time_until_departure <= timedelta(minutes=45) and old_status != "Scheduled":
                new_status = "Boarding"
            else:
                new_status = "Scheduled"
        
        if new_status != old_status:
            if old_status == "Boarding" and new_status == "Scheduled":
                continue
            if old_status == "Delayed" and new_status in ["Scheduled", "Boarding"]:
                continue
                
            flight.status = new_status
            flight.save()
            updated_count += 1
            print(f"Updated flight {flight.flight_number} from {old_status} to {new_status}")
    
    return updated_count

def update_discount_codes():
    now = timezone.now().date()
    expired_count = 0
    
    discount_codes = DiscountCode.objects.all()
    
    for discount_code in discount_codes:
        if discount_code.valid_until < now:
            discount_code.delete()
            expired_count += 1
    
    return expired_count