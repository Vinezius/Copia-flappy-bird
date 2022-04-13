import  pygame
import os
import random

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 500


PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
GROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))

BIRD_IMG = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
SCORE_FONT = pygame.font.SysFont('roboto', 50)


class Bird:
    IMGS = BIRD_IMG
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.imgs = 0
        self.img = self.IMGS[0]
    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def movement(self):
        self.time += 1
        move = 1.5 * (self.time**2) + self.speed * self.time

        if move > 16:
            move = 16
        elif move < 0:
            move -= 2

        self.y += move

        if move < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def draw_bird(self, screen):
        self.imgs += 1

        if self.imgs < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.imgs < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.imgs < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.imgs < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.imgs < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[1]
            self.imgs = 0

    #TechWithTim
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        img_center = self.img.get_rect(topleft =(self.x, self.y)).center
        rectangle = rotated_img.get_rect(center=img_center)
        screen.blit(rotated_img,rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    DISTANCE = 200
    PIPE_SPEED = 5

    def __init__(self, x):
        self.x = x
        self.pipe_height = 0
        self.pipe_top_pos = 0
        self.pipe_bottom_pos = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.behind_bird = False
        self.def_height()

    def def_height(self):
        self.pipe_height = random.randrange(50, 600)
        self.pipe_top_pos = self.pipe_height - self.PIPE_TOP.get_height()
        self.pipe_bottom_pos = self.pipe_height + self.DISTANCE

    def move(self):
        self.x -= self.PIPE_SPEED

    def draw_pipe(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.pipe_top_pos))
        screen.blit(self.PIPE_BOTTOM, (self.x, self.pipe_bottom_pos))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_distance = (self.x - bird.x, self.pipe_top_pos - round(bird.y))
        bottom_distance = (self.x - bird.x, self.pipe_bottom_pos - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_distance)
        bottom_point = bird_mask.overlap(bottom_mask, bottom_distance)

        if top_point or bottom_point:
            return True
        else:
            return False


class Ground:
    GROUND_SPEED = 5
    GROUND_WIDTH = GROUND_IMG.get_width()
    GROUND_IMAGE = GROUND_IMG

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.GROUND_WIDTH

    def move(self):
        self.x0 -= self.GROUND_SPEED
        self.x1 -= self.GROUND_SPEED

        if self.x0 + self.GROUND_WIDTH < 0:
            self.x0 = self.x1 + self.GROUND_WIDTH
        if self.x1 + self.GROUND_WIDTH < 0:
            self.x1 = self.x0 + self.GROUND_WIDTH

    def draw_ground(self, screen):
        screen.blit(self.GROUND_IMAGE, (self.x0, self.y))
        screen.blit(self.GROUND_IMAGE, (self.x1, self.y))


def draw_screen(screen, birds, pipes, ground, score):
    screen.blit(BACKGROUND_IMG, (0, 0))
    for bird in birds:
        bird.draw_bird(screen)
    for pipe in pipes:
        pipe.draw_pipe(screen)

    text = SCORE_FONT.render(f"Pontuação: {score}", 0, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    ground.draw_ground(screen)
    pygame.display.update()


def main():
    birds = [Bird(230, 350)]
    ground = Ground(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    score = 0
    clock = pygame.time.Clock()
    
    playing = True
    while playing:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        for bird in birds:
            bird.movement()
        ground.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                if not pipe.behind_bird and bird.x > pipe.x:
                    pipe.behind_bird = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)
        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.img.get_height()) > ground.y or bird.y < 0:
                birds.pop(i)

        draw_screen(screen, birds, pipes, ground, score)


if __name__ == '__main__':
    main()
