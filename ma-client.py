import socket             
import struct
import time
import json
from tkinter import *
 
# Create a set object 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# Define the port on which you want to connect 
port = 3423               
 
s.connect(('127.0.0.1', port)) 

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

def create():
    "Create a rectangle with draw function (below) with random color"
    for row in range(ms):
        for col in range(ms):
            if map[row][col] == 'P':
                color = 'White'
            elif map[row][col] == 'w':
                color = 'black'
            draw(row, col, color)

def draw(row, col, color):
    x1 = col * cell_size
    y1 = row * cell_size
    x2 = x1 + cell_size
    y2 = y1 + cell_size
    ffs.create_rectangle(x1, y1, x2, y2, fill=color)

received = recv_msg(s)
m = received.decode("utf-8")
msg= json.loads(m)

ms =msg["ms"]
map =msg["map"]
cell_size=msg["cell_size"]
scr=msg["scr"]
scc=msg["scc"]
start_color=msg["start_color"]
ecr=msg["ecr"]
ecc=msg["ecc"]
end_color=msg["end_color"]
canvas_size=msg["canvas_size"]
x1=msg["x1"]
y1=msg["y1"]

window = Tk()
window.title('Maze')
ffs = Canvas(window, width = canvas_size, height = canvas_size, bg = 'grey')
ffs.pack()

create()
draw(scr, scc, start_color)
draw(ecr, ecc, end_color)

start_time = time.time()

def draw_rect():
    ffs.create_rectangle((x1, y1, x1 + 12, y1 + 12), fill="green")

def del_rect():
    ffs.create_rectangle((x1, y1, x1 + 12, y1 + 12), fill="white")

def move(event):
    global x1, y1
    del_rect()
    col = w = x1//cell_size
    row = h = y1//cell_size
    if event.char == "a":
        if map[row][col - 1] == "P":
            x1 -= cell_size
    elif event.char == "d":
        if map[row][col + 1] == "P":
            x1 += cell_size
    elif event.char == "w":
        if map[row - 1][col] == "P":
            y1 -= cell_size
    elif event.char == "s":
        if map[row + 1][col] == "P":
            y1 += cell_size

    draw_rect()
    col = w = x1//cell_size
    row = h = y1//cell_size
    if(w == ecc and h == ecr):
        print("GameOver")
        total_time = round((time.time() - start_time), 2)
        print("Time taken:",total_time)

        timeTaken = {"total_time": total_time}
        jsonObj = json.dumps(timeTaken, indent=2).encode("utf-8")

        data = jsonObj

        send_msg(s, data)
        window.destroy()

def cl():
    s.close()

window.bind("<Key>", move)


window.mainloop()
