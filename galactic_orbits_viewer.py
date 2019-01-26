import pyglet
import json
import os
from pyglet.window import key

viewer_window = pyglet.window.Window(1024, 768)
UPDATE_RATE = 120.0


class Game():
    update_rate = 60
    viewer_window = None

    orbital_objects = []
    orbital_object_sprite = None

    camera_zoom = 1
    camera_zoom_ratio = 0.001
    camera_zoom_minimum = 1
    camera_offset_x = 2
    camera_offset_y = 2
    camera_direction_x = 0
    camera_direction_y = 0
    camera_movement_speed = 5

    data_folder = "data"
    orbital_files = []
    orbital_data = None
    step = 0

    galaxy_width = 0
    galaxy_height = 0
    light_speed = 0
    light_year = 0

    def __init__(self, window, rate, galaxy_width, galaxy_height, light_speed):
        self.viewer_window = window
        self.update_rate = rate
        self.galaxy_width = galaxy_width
        self.galaxy_height = galaxy_height
        self.light_speed = light_speed
        self.light_year = light_speed * 31540000
        pyglet.clock.schedule_interval(self.update, 1 / self.update_rate)

    def draw(self):
        viewer_window.clear()
        for orbital_object in self.orbital_objects:
            orbital_object.scale *= self.camera_zoom * self.camera_zoom_ratio
            orbital_object.x += self.camera_offset_x
            orbital_object.y += self.camera_offset_y

            #camera zoom
            orbital_object.x *= (self.camera_zoom / self.camera_zoom_minimum)
            orbital_object.y *= (self.camera_zoom / self.camera_zoom_minimum)
            orbital_object.draw()

    def mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.camera_zoom += scroll_y
        if self.camera_zoom < self.camera_zoom_minimum:
            self.camera_zoom = self.camera_zoom_minimum

    def create_orbital(self, x, y, sprite):
        x /= self.light_year
        y /= self.light_year
        x *= viewer_window.height / self.galaxy_width
        y *= viewer_window.height / self.galaxy_height
        x -= (viewer_window.height - viewer_window.width) / 2
        sprite = pyglet.sprite.Sprite(img=sprite, x=x, y=y)
        sprite.scale = 4
        return sprite

    def update(self, delta):
        self.step += 1
        if self.step > len(self.orbital_files) - 1:
            self.step = 0
        self.create_orbital_objects_for_step(self.step)
        self.camera_offset_x += self.camera_direction_x
        self.camera_offset_y += self.camera_direction_y

    def initialize_objects(self):
        self.create_orbital_objects_for_step(0)

    def create_orbital_objects_for_step(self, step):
        data = self.get_step_data(step)
        self.orbital_objects.clear()
        for galactic_object in data:
            self.orbital_objects.append(
                self.create_orbital(galactic_object['x'], galactic_object['y'], self.orbital_object_sprite))

    def get_step_data(self, step):
        with open(self.data_folder + "/" + self.orbital_files[step]) as json_file:
            return json.load(json_file)

    def key_press(self, key_pressed, key_modifiers):
        if key_pressed == key.A:
            self.camera_direction_x = self.camera_movement_speed
        elif key_pressed == key.D:
            self.camera_direction_x = -self.camera_movement_speed
        elif key_pressed == key.W:
            self.camera_direction_y = -self.camera_movement_speed
        elif key_pressed == key.S:
            self.camera_direction_y = self.camera_movement_speed

    def key_release(self, key_released, key_modifiers):
        if key_released == key.A:
            self.camera_direction_x = 0
        elif key_released == key.D:
            self.camera_direction_x = 0
        elif key_released == key.W:
            self.camera_direction_y = 0
        elif key_released == key.S:
            self.camera_direction_y = 0

    def start(self):
        self.orbital_object_sprite = pyglet.resource.image('sprite.png')
        self.orbital_object_sprite.anchor_x = self.orbital_object_sprite.width / 2
        self.orbital_object_sprite.anchor_y = self.orbital_object_sprite.height / 2

        for file_json_name in os.listdir(self.data_folder):
            self.orbital_files.append(file_json_name)

        self.orbital_files.sort(key=lambda x: os.path.getmtime(self.data_folder + "/" + x))

        self.initialize_objects()

        pyglet.app.run()


@viewer_window.event
def on_draw():
    game.draw()


@viewer_window.event
def on_key_press(key_pressed, key_modifiers):
    game.key_press(key_pressed, key_modifiers)


@viewer_window.event
def on_key_release(key_released, key_modifiers):
    game.key_release(key_released, key_modifiers)



@viewer_window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    game.mouse_scroll(x, y, scroll_x, scroll_y)


if __name__ == "__main__":
    game = Game(viewer_window, UPDATE_RATE, 52000, 52000, 299792458)
    game.start()
