import pygame
import socket
import time
import json
import gzip
import sys

port = 5000
#ip = "localhost"

clientS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientS.connect((ip, port))
print(f"connected to {ip}:{port}")
#clientS.setblocking(False)

# print("running client (client-side)")
# while True:
# 	#message = input("enter a message: ")
# 	message = "hello there"
# 	message = message.encode()
# 	clientS.send(message)
# 	print("server received:", True if clientS.recv(2048).decode() else False)
# 	time.sleep(1)
	

# for i in range(0, 100):
# 	message = ("message - " + str(i)).encode()
# 	clientS.send(message)

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
selfId = -1

class Player():
	def __init__(this, x, y, w, h):
		this.x = x
		this.y = y
		this.w = w
		this.h = h

		this.speed = 5

	def move(this):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_w]:
			this.y -= this.speed
		
		if keys[pygame.K_s]:
			this.y += this.speed

		if keys[pygame.K_a]:
			this.x -= this.speed
		
		if keys[pygame.K_d]:
			this.x += this.speed

	def render(this, screen):
		pygame.draw.rect(screen, (0, 255, 0), (this.x, this.y, this.w, this.h))
		text = defaultFont.render(str(selfId), True, (0, 0, 0))
		screen.blit(text, (this.x + this.w / 2 - text.get_width() / 2, this.y + this.h / 2 - text.get_height() / 2))


defaultFont = pygame.font.Font(pygame.font.get_default_font())
def renderOtherPlayer(screen: pygame.Surface, packet, id):
	pygame.draw.rect(screen, (255, 0, 0), (packet["x"], packet["y"], packet["w"], packet["h"]))
	text = defaultFont.render(str(id), True, (0, 0, 0))
	screen.blit(text, (packet["x"] + packet["w"] / 2 - text.get_width() / 2, packet["y"] + packet["h"] / 2 - text.get_height() / 2))

def main(playerId: int):
	global running
	global selfId

	print(f"starting client with playerId: {playerId}")

	player = Player(0, 0, 50, 50)
	selfId = playerId
	players = {}


	while running:
		# poll for events
		# pygame.QUIT event means the user clicked X to close your window
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		# fill the screen with a color to wipe away anything from last frame
		screen.fill("grey")
		player.move()

		packet = {
			"id": selfId,
			"x": player.x,
			"y": player.y,
			"w": player.w,
			"h": player.h
		}

		#send my data
		packet = json.dumps(packet)
		packet = gzip.compress(packet.encode())
		clientS.send(packet)

		#get other player's data
		try:
			data = gzip.decompress(clientS.recv(2048))
			players = json.loads(data.decode())
		except socket.error:
			pass # no data available



		# RENDER YOUR GAME HERE
		for iD, op in players.items():
			if iD != selfId:
				renderOtherPlayer(screen, op, iD)

		player.render(screen)
		screen.blit(defaultFont.render(f"fps: {round(clock.get_fps(), 2)}", 0, (0, 0, 0)), (5, 5))

		# flip() the display to put your work on screen
		pygame.display.flip()

		clock.tick(60)  # limits FPS to 60

	pygame.quit()


if __name__ == "__main__":
	if len(sys.argv) > 1:
		main(int(sys.argv[1]))
	else:
		main(input("enter player id: "))