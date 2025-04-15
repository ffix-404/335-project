import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# Establish connection to your PostgreSQL database
conn = psycopg2.connect(
    dbname="RideConnect",  
    user="postgres",  
    password="admin",  
    host="localhost",  
    port="5432"  
)


cur = conn.cursor()


fake = Faker()


def insert_fake_riders(num_records):
    rider_ids = []
    for _ in range(num_records):
        name = fake.name()
        contact_details = fake.email()
        cur.execute("""
            INSERT INTO Rider (name, contact_details)
            VALUES (%s, %s) RETURNING rider_id
        """, (name, contact_details))
        rider_ids.append(cur.fetchone()[0])  
    conn.commit()
    return rider_ids  

def insert_fake_drivers(num_records):
    for _ in range(num_records):
        name = fake.name()
        contact_details = fake.email()
        vehicle_make = fake.company()
        vehicle_model = fake.word()
        vehicle_color = fake.color_name()
        plate_number = fake.license_plate()
        license_number = fake.bothify(text="??-##########")
        status = random.choice(['online', 'busy', 'offline', 'suspended'])
        cur.execute("""
            INSERT INTO Driver (name, contact_details, vehicle_make, vehicle_model, vehicle_color, plate_number, license_number, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, contact_details, vehicle_make, vehicle_model, vehicle_color, plate_number, license_number, status))
    conn.commit()


def insert_fake_rides(num_records,):
    for _ in range(num_records):
        rider_id = random.randint(21, 31)
        driver_id = random.randint(21, 31)
        pickup_location = fake.address()
        dropoff_location = fake.address()
        start_time = fake.date_this_year()
        end_time = start_time + timedelta(minutes=random.randint(10, 60))
        distance_km = round(random.uniform(1, 50), 2)
        status = random.choice(['requested', 'accepted', 'in_progress', 'completed', 'cancelled'])
        cur.execute("""
            INSERT INTO Ride (rider_id, driver_id, pickup_location, dropoff_location, start_time, end_time, distance_km, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (rider_id, driver_id, pickup_location, dropoff_location, start_time, end_time, distance_km, status))
    conn.commit()


def insert_fake_pricing(num_records):
    for _ in range(num_records):
        vehicle_type = random.choice(['economy', 'premium', 'family'])
        base_rate = round(random.uniform(5.0, 20.0), 2)  
        surge_multiplier = round(random.uniform(1.0, 2.5), 2)  
        cur.execute("""
            INSERT INTO Pricing (vehicle_type, base_rate, surge_multiplier)
            VALUES (%s, %s, %s)
        """, (vehicle_type, base_rate, surge_multiplier))
    conn.commit()


def insert_fake_requests(num_records):
    for _ in range(num_records):
        rider_id = random.randint(21, 31)  
        pickup_location = fake.address()
        dropoff_location = fake.address()
        requested_time = fake.date_time_this_year()
        cur.execute("""
            INSERT INTO Request (rider_id, pickup_location, dropoff_location, requested_time)
            VALUES (%s, %s, %s, %s)
        """, (rider_id, pickup_location, dropoff_location, requested_time))
    conn.commit()


def insert_fake_ride_offers(num_records):
    for _ in range(num_records):
        ride_id = random.randint(24, 34)  
        driver_id = random.randint(21, 31)  
        status = random.choice(['pending', 'accepted', 'declined'])
        offer_time = fake.date_time_this_year()
        cur.execute("""
            INSERT INTO Ride_Offer (ride_id, driver_id, status, offer_time)
            VALUES (%s, %s, %s, %s)
        """, (ride_id, driver_id, status, offer_time))
    conn.commit()


def insert_fake_bills(num_records):
    for _ in range(num_records):
        ride_id = random.randint(24, 34)  
        total_fare = round(random.uniform(10, 100), 2)  
        payment_method = random.choice(['credit_card', 'cash', 'wallet'])
        payment_status = random.choice(['pending', 'paid', 'failed'])
        surge_multiplier = round(random.uniform(1.0, 2.5), 2)  
        vehicle_type = random.choice(['economy', 'premium', 'family'])
        cur.execute("""
            INSERT INTO Bill (ride_id, total_amount, payment_method, payment_status, surge_multiplier, vehicle_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (ride_id, total_fare, payment_method, payment_status, surge_multiplier, vehicle_type))
    conn.commit()


def insert_fake_ratings(num_records):
    for _ in range(num_records):
        ride_id = random.randint(24, 34)  
        rider_id = random.randint(21, 31)  
        driver_id = random.randint(21, 31)  
        rating_value = random.randint(1, 5)  
        feedback = fake.text(max_nb_chars=200)
        rating_time = fake.date_this_year()
        cur.execute("""
            INSERT INTO Rating (ride_id, rider_id, driver_id, rating_value, feedback, rating_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (ride_id, rider_id, driver_id, rating_value, feedback, rating_time))
    conn.commit()


insert_fake_rides(10) 
insert_fake_requests(10)  
insert_fake_ride_offers(10)  
insert_fake_bills(10)  
insert_fake_ratings(10)
cur.close()
conn.close()
print("Fake data inserted successfully!")