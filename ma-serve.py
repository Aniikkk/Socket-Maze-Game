import socket			 
from random import randint
import json
import struct

cell_size = 12 #pixels
ms = 10 # rows and columns
visited_cells = []
walls = []
revisited_cells = []

# creates a list with 50 x 50 "w" items
map = [['w' for _ in range(ms)] for _ in range(ms)]

def  check_neighbours(ccr, ccc):
    neighbours = [[ ccr, ccc - 1, ccr - 1, ccc - 2, ccr, ccc - 2, ccr + 1, ccc - 2, ccr - 1, ccc - 1, ccr + 1, ccc - 1 ], #left
                [ccr, ccc + 1, ccr - 1, ccc + 2, ccr, ccc + 2, ccr + 1, ccc + 2, ccr - 1, ccc + 1, ccr + 1, ccc + 1], #right
                [ccr - 1, ccc, ccr - 2, ccc - 1, ccr - 2, ccc, ccr - 2, ccc + 1, ccr - 1, ccc - 1, ccr - 1, ccc + 1], #top
                [ccr + 1, ccc, ccr + 2, ccc - 1, ccr + 2, ccc, ccr + 2, ccc + 1, ccr + 1, ccc-1, ccr + 1, ccc + 1]] #bottom

    visitable_neighbours = []           
    for i in neighbours:                                                                        #find neighbours to visit
        if i[0] > 0 and i[0] < (ms-1) and i[1] > 0 and i[1] < (ms-1):
            if map[i[2]][i[3]] == 'P' or map[i[4]][i[5]] == 'P' or map[i[6]][i[7]] == 'P' or map[i[8]][i[9]] == 'P' or map[i[10]][i[11]] == 'P':
                walls.append(i[0:2])                                                                                               
            else:
                visitable_neighbours.append(i[0:2])
    return visitable_neighbours

#StartingPoint

# starting color of row
scr = randint(1, ms)
# starting random column
scc = randint(1, ms)
start_color = 'Green'
# memorize row and column of the starting rectangle
# current color row and current color column
ccr, ccc = scr, scc
x1 = ccr * 12
y1 = ccc * 12
print(scr, scc)
print(ccr, ccc)

map[ccr][ccc] = 'P'
loop = 1
while loop:
    visitable_neighbours = check_neighbours(ccr, ccc)
    if len(visitable_neighbours) != 0:
        d = randint(1, len(visitable_neighbours))-1
        ncr, ncc = visitable_neighbours[d]
        map[ncr][ncc] = 'P'
        visited_cells.append([ncr, ncc])
        ccr, ccc = ncr, ncc
    if len(visitable_neighbours) == 0:
        try:
            ccr, ccc = visited_cells.pop()
            revisited_cells.append([ccr, ccc])

        except:
            loop = 0


canvas_size = ms*cell_size
y1 = scr * cell_size 
x1 = scc * cell_size
e = randint(1, len(revisited_cells))-1
ecr = revisited_cells[e][0]
ecc = revisited_cells[e][1]
end_color = 'red'

m = { 
     "ms" :ms, 
     "map" :map,
     "cell_size": cell_size,
     "scr": scr,
     "scc": scc,
     "start_color": start_color,
     "ecr": ecr,
     "ecc":ecc,
     "end_color": end_color,
     "canvas_size": canvas_size,
     "x1": x1,
     "y1":y1
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket successfully created")
     
    port = 3423               
     
    s.bind(('', port))         
    print ("socket binded to %s" %(port)) 

    while True:

        # put the socket into listening mode 
        s.listen(5)     
        print ("socket is listening")            

        jsonObj = json.dumps(m, indent=2).encode("utf-8")

        data = jsonObj

        c, addr = s.accept()     
        print ('Got connection from', addr )

        send_msg(c, data)
        print("sent data")

        received = recv_msg(c)
        m = received.decode("utf-8")
        timeTaken= json.loads(m)

        print("Total time taken: ",timeTaken["total_time"])

serve(m)
