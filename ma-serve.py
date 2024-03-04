import socket
import struct
import time
import json
import ssl
from random import randint

cell_size = 10  # pixels
ms = 10  # rows and columns
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

# starting color of row
scr = randint(1, ms - 2)  # Adjusted range to fit within maze bounds
# starting random column
scc = randint(1, ms - 2)  # Adjusted range to fit within maze bounds
start_color = 'Green'
# memorize row and column of the starting rectangle
# current color row and current color column
ccr, ccc = scr, scc
x1 = ccr * 12
y1 = ccc * 12
print(scr, scc)
print(ccr, ccc)

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

m = {
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


def serve(m):
    # Create a TCP/IP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")

    # SSL context creation
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="/Users/windows/projects/Socket-Maze-Game/server.crt", keyfile="/Users/windows/projects/Socket-Maze-Game/server.key")

    port = 3423

    s.bind(('', port))
    print("socket binded to %s" % (port))

    while True:
        # Put the socket into listening mode
        s.listen(5)
        print("socket is listening")

        # Wait for a connection
        c, addr = s.accept()
        print('Got connection from', addr)

        # Wrap the socket with SSL
        ssl_sock = context.wrap_socket(c, server_side=True)
        print("successful SSL handshake and connection establishment")

        # JSON serialization and sending
        jsonObj = json.dumps(m, indent=2).encode("utf-8")
        data = jsonObj
        send_msg(ssl_sock, data)
        print("sent data")

        # Receiving data
        received = recv_msg(ssl_sock)
        m = received.decode("utf-8")
        timeTaken = json.loads(m)

        print("Total time taken: ", timeTaken["total_time"])

        # Close the SSL socket
        ssl_sock.close()


serve(m)
