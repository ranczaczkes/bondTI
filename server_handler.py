import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from constants import FLIGHT_ID, ARRIVAL, DEPARTURE
from successful_flights import SuccessfulFlights


class ServerHandler(BaseHTTPRequestHandler):
    def _end_response(self, response_type: int, content_type="text/html", data=None):
        self.send_response(response_type, data)
        self.send_header(
            "Content-type",
            content_type,
        )
        self.end_headers()

    def do_GET(self):
        logging.info(
            "GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers)
        )
        file = SuccessfulFlights()
        url_parts = urlparse(self.path)
        query_params = parse_qs(url_parts.query)
        flight_id = query_params.get("flight_id", None)[0]
        info = file.get_info(flight_id=flight_id)

        self._end_response(200, content_type="text/html", data=info)
        self.wfile.write("GET request for {} is ".format(self.path).encode("utf-8"))
        self.wfile.write(json.dumps(info).encode("utf-8"))

    def do_POST(self):
        content_type = self.headers.get("Content-Type")
        content_length = int(self.headers["Content-Length"])

        file = SuccessfulFlights()

        logging.info(
            "POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
            str(self.path),
            str(self.headers),
        )

        if content_type == "application/json":
            self.do_post_json(file, content_length)
        else:
            self.do_post_text(file, content_length)

        self.wfile.write("POST request for {}".format(self.path).encode("utf-8"))

    def do_post_text(self, file, content_length):
        post_data = self.rfile.read(content_length).decode("utf-8")

        logging.info(msg=post_data)
        flight_id, direction, time_hour, time_min = post_data.split("_")
        time = time_hour + ":" + time_min

        file.update_csv(flight_id=flight_id, direction=direction, time=time)

        self._end_response(
            200,
            content_type="text/html",
        )

    def do_post_json(self, file, content_length):
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data)
        file.update_csv(
            flight_id=json_data[FLIGHT_ID],
            arrival=json_data[ARRIVAL],
            departure=json_data[DEPARTURE],
        )
        self._end_response(200, content_type="application/json", data=json_data)


def run(server_class=HTTPServer, handler_class=ServerHandler, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
