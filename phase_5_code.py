from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Utility function to create a database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname="RideConnect",
        user="postgres",      # replace with your db username
        password="yourpassword",  # replace with your db password
        host="localhost"
    )
    return conn

# -------------------------------
# Endpoint: Request a Ride
# -------------------------------
@app.route('/request_ride', methods=['POST'])
def request_ride():
    data = request.get_json()
    rider_id = data.get('rider_id')
    # Expect pickup and dropoff locations as dictionaries with 'lat' and 'lon'
    pickup_location = data.get('pickup_location')
    dropoff_location = data.get('dropoff_location')
    
    # Connect to the database and start a transaction
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Insert a new ride with status 'requested'
                # Using PostGIS functions to store spatial data
                insert_query = """
                    INSERT INTO Ride (
                        rider_id, pickup_location, dropoff_location, status, request_time
                    )
                    VALUES (
                        %s,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                        'requested',
                        NOW()
                    )
                    RETURNING ride_id;
                """
                cur.execute(insert_query, (rider_id,
                                             pickup_location['lon'], pickup_location['lat'],
                                             dropoff_location['lon'], dropoff_location['lat']))
                ride_id = cur.fetchone()[0]
                return jsonify({
                    "ride_id": ride_id,
                    "message": "Ride requested successfully"
                }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# -------------------------------
# Endpoint: Accept a Ride
# -------------------------------
@app.route('/accept_ride', methods=['POST'])
def accept_ride():
    data = request.get_json()
    ride_id = data.get('ride_id')
    driver_id = data.get('driver_id')
    
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Lock the ride row to prevent concurrent acceptance
                lock_query = """
                    SELECT status 
                    FROM Ride 
                    WHERE ride_id = %s 
                    FOR UPDATE;
                """
                cur.execute(lock_query, (ride_id,))
                row = cur.fetchone()
                if row is None:
                    return jsonify({"error": "Ride not found"}), 404

                current_status = row[0]
                # Only allow acceptance if the ride is still 'requested'
                if current_status != 'requested':
                    return jsonify({"error": "Ride is no longer available"}), 400

                # Update the ride status to 'accepted' and set the driver_id
                update_query = """
                    UPDATE Ride
                    SET status = 'accepted', driver_id = %s, acceptance_time = NOW()
                    WHERE ride_id = %s
                    RETURNING ride_id;
                """
                cur.execute(update_query, (driver_id, ride_id))
                updated_id = cur.fetchone()[0]
                return jsonify({
                    "ride_id": updated_id,
                    "message": "Ride accepted successfully"
                }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
