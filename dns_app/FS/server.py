from flask import Flask, request
import socket

app = Flask(__name__)


def fibonacci(n):
    if n == 0:
        return 0

    if n == 1:
        return 1

    a = 0
    b = 1

    for _ in range(2, n + 1):
        a, b = b, a + b

    return b


@app.route("/register", methods=["PUT"])
def register():

    data = request.get_json()

    if not data:
        return "Bad Request", 400

    hostname = data.get("hostname")
    ip = data.get("ip")
    as_ip = data.get("as_ip")
    as_port = data.get("as_port")

    if not hostname or not ip or not as_ip or not as_port:
        return "Bad Request", 400

    message = (
        f"TYPE=A\n"
        f"NAME={hostname} VALUE={ip} TTL=10\n"
    )

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp_socket.sendto(
        message.encode("utf-8"),
        (as_ip, int(as_port))
    )

    udp_socket.close()

    return "Registered successfully", 201


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():

    number = request.args.get("number")

    try:
        number = int(number)
    except (TypeError, ValueError):
        return "Invalid number", 400

    result = fibonacci(number)

    return str(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)