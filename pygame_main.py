import os
import json
import pygame

ASSET_DIR = os.path.join("textures", "default_texture")
FONT_NAME = pygame.font.get_default_font()


class Map:
    def __init__(self, name):
        with open(os.path.join("maps", f"{name}.json")) as fh:
            data = json.load(fh)
        self.size = data.get("map_size", 9)
        path = data.get("valid_path", "").split("/")
        self.path = []
        for p in path:
            if not p:
                continue
            x, y = p.split(".")
            self.path.append((int(x), int(y)))
        img_path = os.path.join("maps", f"{name}.png")
        self.image = pygame.image.load(img_path).convert_alpha()

    def is_path(self, tile):
        return tile in self.path


class Unit:
    def __init__(self, name):
        with open(os.path.join("units", f"{name}.json")) as fh:
            data = json.load(fh)
        attrs = data["attributes"]
        self.speed = attrs.get("speed", 1) * 2
        self.health = attrs.get("health", 10)
        self.value = attrs.get("value", 1)
        self.strength = attrs.get("strength", 1)
        img = os.path.join(ASSET_DIR, "units", data["texture_name"])
        self.texture = pygame.image.load(img).convert_alpha()
        self.path = []
        self.index = 0
        self.pos = (0, 0)

    def start(self, path, tile):
        self.path = [((x + 0.5) * tile, (y + 0.5) * tile) for x, y in path]
        self.pos = self.path[0]
        self.index = 0

    def update(self):
        if self.health <= 0:
            return False
        if self.index + 1 >= len(self.path):
            return False
        tx, ty = self.path[self.index + 1]
        x, y = self.pos
        dx, dy = tx - x, ty - y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        step = self.speed
        if dist <= step:
            self.pos = (tx, ty)
            self.index += 1
        else:
            self.pos = (x + dx / dist * step, y + dy / dist * step)
        return True

    def draw(self, screen):
        rect = self.texture.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        screen.blit(self.texture, rect)


class Projectile:
    def __init__(self, data, origin, target):
        img = os.path.join(ASSET_DIR, "towers", "projectiles", data["texture_name"])
        self.texture = pygame.image.load(img).convert_alpha()
        self.speed = data.get("speed", 1) * 4
        self.damage = data.get("damage", 1)
        self.pos = list(origin)
        self.target = target

    def update(self):
        if not self.target or self.target.health <= 0:
            return False
        tx, ty = self.target.pos
        x, y = self.pos
        dx, dy = tx - x, ty - y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        if dist <= 5:
            self.target.health -= self.damage
            return False
        self.pos[0] += dx / dist * self.speed
        self.pos[1] += dy / dist * self.speed
        return True

    def draw(self, screen):
        rect = self.texture.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        screen.blit(self.texture, rect)


class Tower:
    def __init__(self, name, pos, tile):
        with open(os.path.join("towers", f"{name}.json")) as fh:
            data = json.load(fh)
        attrs = data["attributes"]
        img = os.path.join(ASSET_DIR, "towers", data["texture_name"])
        self.texture = pygame.image.load(img).convert_alpha()
        self.range = attrs.get("range", 1) * tile
        self.rate = attrs.get("rate_of_fire", 1)
        self.cost = attrs.get("cost", 100)
        self.projectile_data = attrs["projectile"]
        self.pos = pos
        self.cooldown = 0

    def update(self, units, projectiles, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
            return
        target = None
        closest = self.range + 1
        for u in units:
            dx = u.pos[0] - self.pos[0]
            dy = u.pos[1] - self.pos[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < closest and u.health > 0:
                closest = dist
                target = u
        if target and closest <= self.range:
            projectiles.append(Projectile(self.projectile_data, self.pos, target))
            self.cooldown = 60 / max(0.1, self.rate)

    def draw(self, screen):
        rect = self.texture.get_rect(center=self.pos)
        screen.blit(self.texture, rect)


class Game:
    def __init__(self, map_name="Brigade"):
        pygame.init()
        self.map = Map(map_name)
        self.tile = self.map.image.get_width() // self.map.size
        self.screen = pygame.display.set_mode(
            (self.map.image.get_width(), self.map.image.get_height())
        )
        pygame.display.set_caption("PyDefence Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 20)
        self.towers = []
        self.units = []
        self.projectiles = []
        self.money = 5000
        self.base_health = 100
        self.spawn_timer = 60
        self.wave_number = 1
        self.spawn_index = 0
        self.wave_size = 5

    def spawn_unit(self):
        u = Unit("farmer")
        u.start(self.map.path, self.tile)
        self.units.append(u)

    def place_tower(self, pos):
        tile_x = int(pos[0] // self.tile)
        tile_y = int(pos[1] // self.tile)
        if self.map.is_path((tile_x, tile_y)):
            return
        for t in self.towers:
            if int(t.pos[0] // self.tile) == tile_x and int(t.pos[1] // self.tile) == tile_y:
                return
        tower = Tower("archer_tower", (tile_x * self.tile + self.tile // 2, tile_y * self.tile + self.tile // 2), self.tile)
        if self.money >= tower.cost:
            self.money -= tower.cost
            self.towers.append(tower)

    def update_waves(self):
        if self.spawn_index < self.wave_size:
            if self.spawn_timer <= 0:
                self.spawn_unit()
                self.spawn_index += 1
                self.spawn_timer = 60
            else:
                self.spawn_timer -= 1
        elif not self.units:
            self.wave_number += 1
            self.wave_size += 2
            self.spawn_index = 0
            self.spawn_timer = 120

    def draw_hud(self):
        text = f"Money: {self.money}  Base HP: {self.base_health}  Wave: {self.wave_number}"
        surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(surface, (10, 10))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.place_tower(event.pos)

            self.update_waves()

            self.screen.blit(self.map.image, (0, 0))

            for tower in self.towers:
                tower.update(self.units, self.projectiles, 1)
                tower.draw(self.screen)

            for u in list(self.units):
                if not u.update():
                    self.units.remove(u)
                    self.base_health -= u.strength
                if u.health <= 0:
                    if u in self.units:
                        self.units.remove(u)
                        self.money += u.value
                else:
                    u.draw(self.screen)

            for p in list(self.projectiles):
                if not p.update():
                    self.projectiles.remove(p)
                else:
                    p.draw(self.screen)

            self.draw_hud()

            if self.base_health <= 0:
                running = False

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    Game().run()
