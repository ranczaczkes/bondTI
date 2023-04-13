"""
This part handles all the "success" flight logic.
"""
import csv
import logging
from _csv import writer

import pandas as pd

from constants import (
    MAX_SUCC_FLIGHT_NUM,
    FLIGHT_ID,
    SUCCESS,
    ARRIVAL,
    DEPARTURE,
    FAIL,
    EMPTY_STR_CSV,
)


class SuccessfulFlights:
    def __init__(self, touch_file=False):
        self.database_filename = "flights_files/flights.csv"
        self.success_column_file = "flights_files/success_column.csv"

        self.threshold = 180
        # reading the file into data frame
        self.num_success = 0

        self.touch_file = touch_file
        self.dataf = pd.read_csv(self.database_filename)

        self.success_flights = self.update_success_column()

        keys = self.dataf.keys().values
        self.keys = dict(zip(keys, range(len(keys))))
        self.db_been_updated = False

    def get_info(self, flight_id):
        """
        returns some details about the flight : [Arrival time, Departure time, Success/Fail - if data available]
        :param flight_id:
        :return:
        """
        with open(self.database_filename, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[self.keys[FLIGHT_ID]] == flight_id:
                    if row[self.keys[SUCCESS]] == EMPTY_STR_CSV:
                        return [
                            row[self.keys[FLIGHT_ID]],
                            row[self.keys[ARRIVAL]],
                            row[self.keys[DEPARTURE]],
                        ]
                    return row
            return []

    def add_flight(self, flight_id: str, arrival: str, departure: str):
        with open(self.database_filename, "a") as file:
            w = writer(file)
            row = f"{flight_id},{arrival},{departure},``"
            w.writerow(row)

    def update_csv_json(self, flight_data):
        try:
            self.update_csv(
                flight_data[FLIGHT_ID], flight_data[ARRIVAL], flight_data[DEPARTURE]
            )
        except ValueError:
            logging.error(msg="The data in the request is not compatible. ")

    def update_csv(self, flight_id, arrival=None, departure=None):
        if not arrival and not departure:
            logging.info(msg="Its seems nothing is changed, try again.")
        else:
            updated_rows, old_time = self._update_row(
                flight_id=flight_id, arrival=arrival, departure=departure
            )
            write_rows_to_csv(file_name=self.database_filename, rows=updated_rows)

            logging.info(
                msg=f"Updated flight {flight_id}.\n Old Times - Arrival : {old_time[0]} , Departure : {old_time[1]}\n"
                f" New Times  - Arrival : {arrival} , Departure : {departure}\n"
            )

            self.db_been_updated = True

    def _update_row(self, flight_id, arrival=None, departure=None):
        """
        Gets flight id arrival and departure - update the data and return list of "rows"
        and the old value
        :param flight_id:
        :param arrival:
        :param departure:
        :return:
        """
        old_time = -1
        updated_rows = []
        with open(self.database_filename, "r") as file:
            reader = csv.reader(file)

            for row in reader:
                if row[self.keys[FLIGHT_ID]] == flight_id:
                    old_time = [row[self.keys[ARRIVAL]], row[self.keys[DEPARTURE]]]
                    row[self.keys[ARRIVAL]] = (
                        arrival if arrival else row[self.keys[ARRIVAL]]
                    )
                    row[self.keys[DEPARTURE]] = (
                        departure if departure else row[self.keys[DEPARTURE]]
                    )
                updated_rows.append(row)

        return updated_rows, old_time

    def update_success_column(self):
        """
        Updates the csv file with success and fail value and counts how many success flights.
        :return:
        """
        data = self.dataf.to_numpy()
        success_ids = []
        updated_rows = []
        for index, row in enumerate(data):
            if self.check_success(arrival=row[1], departure=row[2]):
                row[3] = SUCCESS
                success_ids.append(index)
            else:
                row[3] = FAIL
            updated_rows.append(row)

        # update the db with success/fail status
        # write_rows_to_csv(file_name=self.database_filename, rows=updated_rows)
        return success_ids

    def create_success_column(self):
        """
        Creates success flights column
        :return:
        """
        if self.db_been_updated:
            self.update_success_column()

        if len(self.success_flights) > MAX_SUCC_FLIGHT_NUM:
            logging.info(
                "There are more then 20 success flights, which mean There are no success flights today"
            )
            return
        data = self.get_successful_flights_data()
        write_rows_to_csv(file_name=self.success_column_file, rows=data)
        return data

    def get_successful_flights_data(self):
        """
        Gets list of all the data rows of success flighs
        :return:
        """
        data = self.dataf.to_numpy()
        success_data = []
        for sid in self.success_flights:
            success_data.append(data[sid])

        success_data = sorted(success_data, key=lambda x: x[0])
        return success_data

    def check_success(self, arrival, departure):
        """
        Gets arrival time and departure time and determine if they are more than 180 min apart
        :param arrival:
        :param departure:
        :return:
        """
        arrival_min_count = time_to_min(arrival)
        departure_min_count = time_to_min(departure)

        if arrival_min_count > departure_min_count:
            min_num_in_day = 1440
            return (
                min_num_in_day - arrival_min_count + departure_min_count
            ) >= self.threshold
        return (departure_min_count - arrival_min_count) >= self.threshold


def time_to_min(time):
    """
    Gets time in "HH:MM" format and returns the amount of min that have passed since 00:00
    """
    ftr = [60, 1]
    return sum([a * b for a, b in zip(ftr, map(int, time.split(":")))])


def write_rows_to_csv(file_name, rows):
    """
    Write rows to the csv file
    :param file_name:
    :param rows:
    :return:
    """
    with open(file_name, "w", newline="") as file:
        w = csv.writer(file)
        w.writerows(rows)


if __name__ == "__main__":
    new_db = SuccessfulFlights()
    new_db.create_success_column()
