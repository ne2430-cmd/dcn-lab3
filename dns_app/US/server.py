from flask import Flask, request
import socket
import urllib.request
import urllib.error

app = Flask(__name__)


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():

    # Get all required parameters
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    # Check if any parameter is missing
    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Bad Request", 400

    # Convert ports to integers
    try:
        fs_port = int(fs_port)
        as_port = int(as_port)
    except ValueError:
        return "Bad Request", 400

    # --------------------------------------------------
    # STEP 1: Ask the Authoritative Server for the IP
    # --------------------------------------------------

    dns_query = f"TYPE=A\nNAME={hostname}"

    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.settimeout(5)

        udp_socket.sendto(
            dns_query.encode("utf-8"),
            (as_ip, as_port)
        )

        data, address = udp_socket.recvfrom(4096)

        udp_socket.close()

        dns_response = data.decode("utf-8")

        print("Received from AS:")
        print(dns_response)

    except Exception as e:
        print("Error contacting AS:", e)
        return "Authoritative Server Error", 500

    # --------------------------------------------------
    # STEP 2: Extract the IP address from AS response
    # --------------------------------------------------

    # Expected response:
    # TYPE=A
    # NAME=fibonacci.com VALUE=127.0.0.1 TTL=10

    fs_ip = None

    for line in dns_response.splitlines():
        if line.startswith("NAME=") and "VALUE=" in line:
            parts = line.split()

            for part in parts:
                if part.startswith("VALUE="):
                    fs_ip = part.replace("VALUE=", "")

    if not fs_ip:
        return "Hostname not found", 404

    print("FS IP:", fs_ip)

    # --------------------------------------------------
    # STEP 3: Ask Fibonacci Server for the number
    # --------------------------------------------------

    fs_url = (
        f"http://{fs_ip}:{fs_port}"
        f"/fibonacci?number={number}"
    )

    print("Requesting:", fs_url)

    try:
        response = urllib.request.urlopen(fs_url, timeout=5)

        result = response.read().decode("utf-8")

        return result, 200

    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8"), e.code

    except Exception as e:
        print("Error contacting FS:", e)
        return "Fibonacci Server Error", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)