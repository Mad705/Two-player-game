import pygame
import socket
import time

class Player():
    width = height = 20

    def __init__(self, startx, starty, color):
        self.x = startx
        self.y = starty
        self.velocity = 2
        self.color = color

    def draw(self, g):
        pygame.draw.circle(g, self.color ,(self.x, self.y),self.width, 10)

    def move(self, dirn):
        if dirn == 0:
            self.x += self.velocity
        elif dirn == 1:
            self.x -= self.velocity
        elif dirn == 2:
            self.y -= self.velocity
        else:
            self.y += self.velocity

class Canvas:

    def __init__(self, w, h, name="None"):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w,h))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        pygame.display.update()

    def draw_text(self, text, size, x, y):
        pygame.font.init()
        font = pygame.font.SysFont("copperplate", size)
        render = font.render(text, 1, (255,255,255))
        self.screen.blit(render, (x,y))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        self.screen.fill((0,0,0))

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.0.100"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(2048).decode()

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)

class Game:

    def __init__(self, w, h):
        self.net = Network()
        self.width = w
        self.height = h
        self.player = Player(50, 50,(0,255,255))
        self.player2 = Player(450,450,(255,102,102))
        self.canvas = Canvas(self.width, self.height, "TWO PLAYER GAME")
        self.points = [0, 0]  # Initialize points for each player

    def run(self):
        clock = pygame.time.Clock()
        run = True
        last_point_time = time.time()
        while run:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.K_ESCAPE:
                    run = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                if self.player.x <= self.width - self.player.velocity:
                    self.player.move(0)

            if keys[pygame.K_LEFT]:
                if self.player.x >= self.player.velocity:
                    self.player.move(1)

            if keys[pygame.K_UP]:
                if self.player.y >= self.player.velocity:
                    self.player.move(2)

            if keys[pygame.K_DOWN]:
                if self.player.y <= self.height - self.player.velocity:
                    self.player.move(3)

            # Send Network Stuff
            self.player2.x, self.player2.y, points, collision = self.parse_data(self.send_data())

            if abs(self.player.x-self.player2.x)<50 and  abs(self.player.y-self.player2.y)<50  :
                print("Collision detected! Blue player gets a point.")
                self.points[0] += 1
                self.player.x=50
                self.player.y=50
                self.player2.x = 200
                self.player2.y = 200
                collision = 0

            if time.time() - last_point_time >= 20:
                print("Red player gets a point.")
                self.points[1] += 1
                last_point_time = time.time()

            # Update Canvas
            self.canvas.draw_background()
            self.player.draw(self.canvas.get_canvas())
            self.player2.draw(self.canvas.get_canvas())

            # Draw points
            self.canvas.draw_text("Blue player points: " + str(self.points[0]), 20, 10, 10)
            self.canvas.draw_text("Red player points: " + str(self.points[1]), 20, 10, 30)

            self.canvas.update()

        pygame.quit()

    def send_data(self):
        data = str(self.net.id) + ":" + str(self.player.x) + "," + str(self.player.y) + ":" + str(self.points[0]) + ":" + str(self.points[1]) + ":" + str(0)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")
            return int(d[1].split(",")[0]), int(d[1].split(",")[1]), int(d[2]), int(d[3])
        except:
            return 0, 0, 0, 0

if __name__ == "__main__":
    pygame.init()
    g = Game(500,500)
    g.run()
