# import wifi module
import wifi
import socketpool
import asyncio
from adafruit_httpserver import (
    Server,
    REQUEST_HANDLED_RESPONSE_SENT,
    Request,
    FileResponse,
)


# set access point credentials and start AP
ap_ssid = "Python Vlada Smitka"
ap_password = ""

wifi.radio.start_ap(ssid=ap_ssid, authmode=[wifi.AuthMode.OPEN])

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

# DNS Server
async def dns_server():
    ip_address = bytes([192, 168, 4, 1])
    buffer = bytearray(512)

    def extract_dns_name(packet):
        # Skip the header and question type fields to get to the queried name
        pointer = 12  # DNS header is 12 bytes
        name = []
        while True:
            length = packet[pointer]
            if length == 0:
                break
            pointer += 1
            label = packet[pointer:pointer+length]
            name.append(label.decode('utf-8'))
            pointer += length
        return '.'.join(name)

    # Initialize a UDP socket for the DNS server
    with pool.socket(pool.AF_INET, pool.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", 53))

        while True:
            bytes_received, addr = sock.recvfrom_into(buffer)

            if bytes_received:
                data = buffer[:bytes_received]

                # Extract queried DNS name
                queried_name = extract_dns_name(data)
                print("Queried DNS name:", queried_name)

                # Generate a DNS response
                response = data[:2] + b'\x81\x80'
                response += data[4:6] + data[4:6] + b'\x00\x00\x00\x00'
                response += data[12:]
                response += b'\xc0\x0c'
                response += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'
                response += ip_address

                sock.sendto(response, addr)


            await asyncio.sleep(0)

# HTTP Server
async def http_server():
    @server.route("/")
    def base(request: Request):
        print(f"Requested URL: {request.path}")
        return FileResponse(request, "index.html")

    @server.route("/hotspot.html")
    def apple_captive(request: Request):
        print(f"Requested URL: {request.path}")
        content = "<html><body><h1>Success</h1></body></html>"
        return content, "text/html", 200

    server.start('0.0.0.0')

    while True:
        try:
            server.poll()

        except OSError as error:
            print(error)
            continue

loop = asyncio.get_event_loop()
loop.create_task(dns_server())
loop.create_task(http_server())
loop.run_forever()
