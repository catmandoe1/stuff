import pygame
import socket
import json
import gzip
import time

port = 5000
ip = socket.gethostbyname(socket.gethostname())
#ip = "localhost"

print("starting server")
serverS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"binded to {ip}:{port}")
serverS.bind((ip, port))
serverS.listen(10)

serverClients: dict[str, socket.socket] = {}


print("waiting for players [2]")
# first
clientS, address = serverS.accept()
serverClients[address] = clientS

print("p1 connected:", address)

# second
clientS, address = serverS.accept()
serverClients[address] = clientS

print("p2 connected:", address)

#serverS.setblocking(False)
players = {}

# packet = {
# 		"id": id,
# 		"x": player.x,
# 		"y": player.y,
# 		"w": player.w,
# 		"h": player.h
# 	}

print("listening (server-side)")
tickCount = 0
lastPrintedTime = time.time()
while True:
	tickCount += 1
	startTime = time.time()
	for client in serverClients.values():
		try:
			data = client.recv(2048)
			# if data is None:
			# 	continue


			inPacket = json.loads(gzip.decompress(data).decode())
			players[inPacket["id"]] = {
				"x": inPacket["x"],
				"y": inPacket["y"],
				"w": inPacket["w"],
				"h": inPacket["h"]
			}
		# except EOFError:
		# 	pass # packet is incomplete
		# except json.JSONDecodeError:
		# 	pass # incomplete packet still
		except socket.error:
			pass # no data
		


		outPacket = gzip.compress(json.dumps(players).encode())
		client.send(outPacket)

	deltaTime = time.time() - startTime
	if time.time() - lastPrintedTime >= 1:
		print(f"{round(tickCount / (time.time() - lastPrintedTime), 2)} tps")
		lastPrintedTime = time.time()
		tickCount = 0
		
	#time.sleep(0.1)