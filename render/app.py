# Imports
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from db_config import source_database
from datetime import datetime, timedelta

# Create flask app
app = Flask("Forage Solutions")

# Allows forage to access the data CORS = Cross-origin resource sharing
CORS(app)


# Returns number of rows
def count_rows_in_responses(connection_config):
    try:
        connection = psycopg2.connect(**connection_config)
        cursor = connection.cursor()
        # Query to count rows in the pisa table
        cursor.execute("SELECT COUNT(*) FROM pisa;")
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return {"count": count}
    except (psycopg2.Error, Exception) as e:
        # So I know why it's throwning an error
        print(f"Error occurred while connecting to the database: {e}")
        return None


# Calculates the learning hours per week + links to a country
def calculate_average_tmins_by_country(connection_config):
    try:
        connection = psycopg2.connect(**connection_config)
        cursor = connection.cursor()
        # Query to calculate average 'tmins' divided by 60 for each country
        cursor.execute(
            "SELECT cnt, AVG(tmins/60) AS avg_hours_per_week FROM pisa WHERE tmins IS NOT NULL GROUP BY cnt ORDER BY avg_hours_per_week DESC;"
        )
        results = cursor.fetchall()
        output = {"datasets": []}  # to store the output
        for country, average_tmins in results:
            # Convert the average tmins to a decimal with 1 decimal place
            average_tmins = round(float(average_tmins), 1)
            # Add country and average_tmins to the tmins datasets
            output["datasets"].append({"country": country, "hours": average_tmins})
        cursor.close()
        connection.close()
        return output
    except (psycopg2.Error, Exception) as e:
        # So I know why it's throwning an error
        print(f"Error occurred while connecting to the database: {e}")
        return None


def calculate_escs(connection_config):
    try:
        connection = psycopg2.connect(**connection_config)
        cursor = connection.cursor()
        # Query to select average 'escs' for each country
        cursor.execute(
            "SELECT cnt, AVG(escs) FROM pisa WHERE escs IS NOT NULL GROUP BY cnt;"
        )
        results = cursor.fetchall()
        output = {"datasets": []}  # to store the result
        for id, average_escs in results:
            # Convert average_escs to an decimal and round to 1dp
            average_escs = round(float(average_escs), 1)
            # Add country and average_escs to the escs datasets
            output["datasets"].append({"id": id, "value": average_escs})
        cursor.close()
        connection.close()
        return output  # Return result directly
    except (psycopg2.Error, Exception) as e:
        # So I know why it's throwning an error
        print(f"Error occurred while connecting to the database: {e}")
        return None


def calculate_eeb(connection_config):
    try:
        connection = psycopg2.connect(**connection_config)
        cursor = connection.cursor()
        # Select 'DURECEC', 'BELONG', and count of submissions for each country
        cursor.execute(
            "SELECT cnt, AVG(durecec), AVG(belong), COUNT(*) AS submissions FROM pisa WHERE durecec IS NOT NULL AND belong IS NOT NULL GROUP BY cnt ORDER BY submissions DESC;"
        )
        results = cursor.fetchall()
        output = {"datasets": []}  # to store the result
        for country, durecec, belong, submissions in results:
            # Convert 'durecec' to float and round to 2 decimal places
            durecec = round(float(durecec), 2)
            # Convert 'belong' to float and round to 4 decimal places
            belong = round(float(belong), 4)
            # Add country data to eeb datasets
            output["datasets"].append(
                {
                    "id": country,
                    "data": [{"x": durecec, "y": belong, "submissions": submissions}],
                }
            )
        cursor.close()
        connection.close()
        return output  # Return result directly
    except (psycopg2.Error, Exception) as e:
        # So I know why it's throwning an error
        print(f"Error occurred while connecting to the database: {e}")
        return None


def get_entries_per_hour(connection_config):
    try:
        connection = psycopg2.connect(**connection_config)
        cursor = connection.cursor()
        # Calculate the start time (24 hours ago from now)
        start_time = datetime.now() - timedelta(hours=24)
        # Select number of entries per hour, order chronologically
        cursor.execute(
            "SELECT to_char(time_submitted, 'HH24:00') AS hour, COUNT(*) AS entry_count FROM pisa WHERE time_submitted >= %s GROUP BY hour ORDER BY hour;",
            (start_time,)
        )
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        # Format data
        data = [{"x": entry[0], "y": entry[1]} for entry in results]
        output = {"datasets": [{"id": "Submissions", "data": data}]}
        return output
    except (psycopg2.Error, Exception) as e:
        # So I know why it's throwning an error
        print(f"Error occurred while connecting to the database: {e}")
        return None


# Function to configure dashboard menu which filters graph by country
# Added is_tmins arg as the spec for tmins uses the key "country" to store country value (eg. "ALB") whereas other metrics use "id"
def filter_by_country_menu(metric, is_tmins=False):
    # Select the diff parameters from the 'countries' part of the get query request
    countries_param = request.args.get("countries")
    if countries_param:
        # Need to split into 3 letter country codes to correlate with 'cnt' column
        countries = countries_param.split(",")
        # Filter the data based on what countries were in the query
        filtered_data = {
            "datasets": [
                country_data
                for country_data in metric["datasets"]
                if country_data["country" if is_tmins else "id"] in countries
            ]
        }
    else:
        # Get all if no specific country is selected
        filtered_data = metric
    return filtered_data


# --- Routes ---


# Total submission count
@app.route("/submissions", methods=["GET"])
def handle_submissions():
    if request.method == "GET":
        submission_count = count_rows_in_responses(source_database)
        return jsonify(submission_count)


# Avg learning hours per week
@app.route("/tmins", methods=["GET"])
def handle_tmins():
    if request.method == "GET":
        tmins = calculate_average_tmins_by_country(source_database)
        filtered_tmins = filter_by_country_menu(tmins, is_tmins=True)
        return jsonify(filtered_tmins)


# Economic, social and cultural score
@app.route("/escs", methods=["GET"])
def handle_escs():
    if request.method == "GET":
        escs = calculate_escs(source_database)
        filtered_escs = filter_by_country_menu(escs)
        return jsonify(filtered_escs)


# Early education and sense of belonging
@app.route("/eeb", methods=["GET"])
def handle_eeb():
    if request.method == "GET":
        eeb = calculate_eeb(source_database)
        filtered_eeb = filter_by_country_menu(eeb)
        return jsonify(filtered_eeb)


# Submissions over time
@app.route("/sot", methods=["GET"])
def handle_sot():
    if request.method == "GET":
        sot = get_entries_per_hour(source_database)
        return jsonify(sot)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
