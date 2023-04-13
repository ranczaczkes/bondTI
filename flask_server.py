"""
Simple Server written with Flask - has GET and POST methods.
"""
from flask import Flask, request, jsonify, Response
import csv

from constants import FLIGHT_ID
from successful_flights import SuccessfulFlights


app = Flask(__name__)

DB_FILE = "flights_files/flights.csv"
FIELDNAMES = ["flight ID", "Arrival", "Departure", "success"]
flights_db = SuccessfulFlights()


@app.route("/success", methods=["GET"])
def get_success_column():
    """
    Returns a file with the success columns
    :return:
    """
    file = SuccessfulFlights()
    file.create_success_column()

    with open(file.success_column_file, mode="r") as file:
        reader = csv.DictReader(file, fieldnames=FIELDNAMES)
        # Convert the CSV data into a list of dictionaries
        data = [str(row) + "\n" for row in reader]

    headers = {"Content-Disposition": "attachment; filename=success_columns.txt"}
    return Response(data, mimetype="text/plain", headers=headers)


@app.route("/flights/<flight_id>", methods=["GET"])
def get_flight_info(flight_id):
    """
    Get method
    :param flight_id:
    :return:
    """
    info = flights_db.get_info(flight_id)
    return jsonify(info) if info else jsonify({"error": "Flight not found"})


@app.route("/flights/<flight_id>", methods=["POST"])
def update_flight(flight_id):
    """
    Post method
    :param flight_id:
    :return:
    """
    data = request.form.to_dict()
    data[FLIGHT_ID] = flight_id
    flights_db.update_csv_json(data)
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=False, port=8080)
