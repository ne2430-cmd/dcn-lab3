import socket

HOST = "0.0.0.0"
PORT = 53533
DATABASE_FILE = "database.txt"


def load_records():
    records = {}

    try:
        with open(DATABASE_FILE, "r") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                # Expected:
                # fibonacci.com 172.18.0.2 10
                parts = line.split()

                if len(parts) == 3:
                    hostname = parts[0]
                    ip = parts[1]
                    ttl = parts[2]
                    records[hostname] = (ip, ttl)

    except FileNotFoundError:
        pass

    return records


def save_record(hostname, ip, ttl):
    with open(DATABASE_FILE, "a") as file:
        file.write(f"{hostname} {ip} {ttl}\n")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_socket.bind((HOST, PORT))

    print(f"Authoritative Server listening on UDP port {PORT}")

    while True:
        data, client_address = server_socket.recvfrom(4096)

        message = data.decode("utf-8").strip()

        print("\nReceived:")
        print(message)

        # Registration request
        if "VALUE=" in message:

            lines = message.split("\n")

            name = None
            value = None
            ttl = None

            for line in lines:

                if line.startswith("NAME="):
                    name = line.split("=", 1)[1].split()[0]

                if "VALUE=" in line:
                    value = line.split("VALUE=", 1)[1].split()[0]

                if "TTL=" in line:
                    ttl = line.split("TTL=", 1)[1].split()[0]

            if name and value and ttl:

                save_record(name, value, ttl)

                print(f"Registered: {name} -> {value}")

        # DNS query
        elif "NAME=" in message:

            name = None

            for line in message.split("\n"):
                if line.startswith("NAME="):
                    name = line.split("=", 1)[1].strip()

            records = load_records()

            if name in records:

                ip, ttl = records[name]

                response = (
                    f"TYPE=A\n"
                    f"NAME={name} VALUE={ip} TTL={ttl}\n"
                )

                server_socket.sendto(
                    response.encode("utf-8"),
                    client_address
                )

                print("Sent:")
                print(response)

            else:
                print(f"Hostname not found: {name}")


if __name__ == "__main__":
    main()