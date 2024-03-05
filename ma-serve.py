import socket
import struct
import json
import ssl
from _thread import *
from random import randint

cell_size = 12  # pixels
ms = 20  # rows and columns
visited_cells = []
walls = []
revisited_cells = []

# creates a list with 50 x 50 "w" items
maze_map = [['w' for _ in range(ms)] for _ in range(ms)]


def check_neighbours(ccr, ccc):
    neighbours = [
        [ccr, ccc - 1, ccr - 1, ccc - 2, ccr, ccc - 2, ccr + 1, ccc - 2, ccr - 1, ccc - 1, ccr + 1, ccc - 1],  # left
        [ccr, ccc + 1, ccr - 1, ccc + 2, ccr, ccc + 2, ccr + 1, ccc + 2, ccr - 1, ccc + 1, ccr + 1, ccc + 1],  # right
        [ccr - 1, ccc, ccr - 2, ccc - 1, ccr - 2, ccc, ccr - 2, ccc + 1, ccr - 1, ccc - 1, ccr - 1, ccc + 1],  # top
        [ccr + 1, ccc, ccr + 2, ccc - 1, ccr + 2, ccc, ccr + 2, ccc + 1, ccr + 1, ccc - 1, ccr + 1, ccc + 1]]  # bottom

    visitable_neighbours = []
    for i in neighbours:  # find neighbours to visit
        if 0 < i[0] < (ms - 1) and 0 < i[1] < (ms - 1):
            if maze_map[i[2]][i[3]] == 'P' or maze_map[i[4]][i[5]] == 'P' or maze_map[i[6]][i[7]] == 'P' or \
                    maze_map[i[8]][i[9]] == 'P' or maze_map[i[10]][i[11]] == 'P':
                walls.append(i[0:2])
            else:
                visitable_neighbours.append(i[0:2])
    return visitable_neighbours


# StartingPoint

# starting of row
scr = randint(1, ms - 2)  # Adjusted range to fit within maze bounds
# starting random column
scc = randint(1, ms - 2)  # Adjusted range to fit within maze bounds
start_color = 'Green'
# memorize row and column of the starting rectangle
# current color row and current color column
ccr, ccc = scr, scc
x1 = ccr * 12
y1 = ccc * 12

maze_map[ccr][ccc] = 'P'
loop = 1
while loop:
    visitable_neighbours = check_neighbours(ccr, ccc)
    if len(visitable_neighbours) != 0:
        d = randint(1, len(visitable_neighbours)) - 1
        ncr, ncc = visitable_neighbours[d]
        maze_map[ncr][ncc] = 'P'
        visited_cells.append([ncr, ncc])
        ccr, ccc = ncr, ncc
    if len(visitable_neighbours) == 0:
        try:
            ccr, ccc = visited_cells.pop()
            revisited_cells.append([ccr, ccc])

        except:
            loop = 0

canvas_size = ms * cell_size
y1 = scr * cell_size
x1 = scc * cell_size
e = randint(1, len(revisited_cells)) - 1
ecr = revisited_cells[e][0]
ecc = revisited_cells[e][1]
end_color = 'red'

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def handle_client(conn, addr):
    # Wrap the socket with SSL
    ssl_sock = context.wrap_socket(conn, server_side=True)
    print("successful SSL handshake and connection establishment with", addr)

    # JSON serialization and sending
    jsonObj = json.dumps(server_message, indent=2).encode("utf-8")
    data = jsonObj
    send_msg(ssl_sock, data)
    print("sent data to", addr)

    # Receiving data
    received = recv_msg(ssl_sock)
    m = received.decode("utf-8")
    timeTaken = json.loads(m)

    print("Total time taken by", addr, ": ", timeTaken["total_time"])
    ssl_sock.close()

# SSL context creation
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="./server.crt", keyfile="./server.key")

def serve(m):
    # Create a TCP/IP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")


    port = 3423

    s.bind(('', port))
    print("socket binded to %s" % (port))


    global server_running
    while server_running:
        # Put the socket into listening mode
        s.listen(5)
        print("socket is listening")

        try:
            conn, addr = s.accept()
            print('Got connection from', addr)
            # Start a new thread for the client
            start_new_thread(handle_client, (conn, addr))

        except KeyboardInterrupt:
            print("Received signal. Gracefully shutting down the server...")
            s.close()
            server_running = False


server_message = {
    "ms": ms,
    "map": maze_map,
    "cell_size": cell_size,
    "scr": scr,
    "scc": scc,
    "start_color": start_color,
    "ecr": ecr,
    "ecc": ecc,
    "end_color": end_color,
    "canvas_size": canvas_size,
    "x1": x1,
    "y1": y1
}

server_running = True
serve(server_message)
