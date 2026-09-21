import json
import os
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "settings.json"
)
DEFAULT_SETTINGS = {"quality": "Medium", "difficulty": "Normal"}

QUALITY_PARTICLES = {"Low": 0, "Medium": 12, "High": 28}
QUALITY_FPS = {"Low": 30, "Medium": 45, "High": 60}
DIFFICULTY_SPEED = {"Easy": 260, "Normal": 340, "Hard": 440}


def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
                DEFAULT_SETTINGS.update(data)
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f)
    except Exception:
        pass


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(Label(text="[b]Car Dodge[/b]", markup=True, font_size=48))
        start_btn = Button(text="Start Game", size_hint=(1, 0.2), font_size=28)
        start_btn.bind(on_release=lambda x: setattr(self.manager, "current", "game"))
        settings_btn = Button(text="Settings", size_hint=(1, 0.2), font_size=28)
        settings_btn.bind(
            on_release=lambda x: setattr(self.manager, "current", "settings")
        )
        layout.add_widget(Widget())
        layout.add_widget(start_btn)
        layout.add_widget(settings_btn)
        layout.add_widget(Widget())
        self.add_widget(layout)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = load_settings()
        self.layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        self.layout.add_widget(Label(text="Settings", font_size=36))

        self.layout.add_widget(Label(text="Graphics quality"))
        row1 = BoxLayout(size_hint=(1, 0.2), spacing=10)
        for q in ("Low", "Medium", "High"):
            b = Button(text=q)
            b.bind(on_release=lambda btn, q=q: self.set_quality(q))
            row1.add_widget(b)
        self.layout.add_widget(row1)

        self.layout.add_widget(Label(text="Difficulty"))
        row2 = BoxLayout(size_hint=(1, 0.2), spacing=10)
        for d in ("Easy", "Normal", "Hard"):
            b = Button(text=d)
            b.bind(on_release=lambda btn, d=d: self.set_difficulty(d))
            row2.add_widget(b)
        self.layout.add_widget(row2)

        self.status = Label(text=self._status_text())
        self.layout.add_widget(self.status)

        back_btn = Button(text="Back", size_hint=(1, 0.2))
        back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "menu"))
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def _status_text(self):
        return "Quality: {}   Difficulty: {}".format(
            self.settings["quality"], self.settings["difficulty"]
        )

    def set_quality(self, q):
        self.settings["quality"] = q
        save_settings(self.settings)
        self.status.text = self._status_text()

    def set_difficulty(self, d):
        self.settings["difficulty"] = d
        save_settings(self.settings)
        self.status.text = self._status_text()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = None

    def on_enter(self):
        self.clear_widgets()
        self.game_widget = GameWidget()
        self.add_widget(self.game_widget)

    def on_leave(self):
        if self.game_widget:
            self.game_widget.stop()


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = load_settings()
        self.quality = self.settings.get("quality", "Medium")
        self.difficulty = self.settings.get("difficulty", "Normal")

        self.car_w, self.car_h = 60, 100
        self.car_x = Window.width / 2 - self.car_w / 2
        self.car_speed = 0
        self.obstacles = []  # list of [x, y, w, h]
        self.particles = []  # background road particles
        self.score = 0
        self.alive = True
        self.spawn_timer = 0
        self.fall_speed = DIFFICULTY_SPEED.get(self.difficulty, 340)

        n_particles = QUALITY_PARTICLES.get(self.quality, 12)
        for _ in range(n_particles):
            self.particles.append(
                [random.uniform(0, Window.width), random.uniform(0, Window.height)]
            )

        self.score_label = Label(
            text="Score: 0",
            pos=(10, Window.height - 40),
            size=(200, 40),
            font_size=22,
        )
        self.add_widget(self.score_label)

        self.left_btn = Button(
            text="<", size_hint=(0.15, 0.15), pos=(10, 10), opacity=0.6
        )
        self.right_btn = Button(
            text=">",
            size_hint=(0.15, 0.15),
            pos=(Window.width - Window.width * 0.15 - 10, 10),
            opacity=0.6,
        )
        self.left_btn.bind(on_press=self.press_left, on_release=self.release_steer)
        self.right_btn.bind(on_press=self.press_right, on_release=self.release_steer)
        self.add_widget(self.left_btn)
        self.add_widget(self.right_btn)

        fps = QUALITY_FPS.get(self.quality, 45)
        self._event = Clock.schedule_interval(self.update, 1.0 / fps)

    def press_left(self, *a):
        self.car_speed = -420

    def press_right(self, *a):
        self.car_speed = 420

    def release_steer(self, *a):
        self.car_speed = 0

    def on_touch_down(self, touch):
        if touch.x < Window.width / 2:
            self.press_left()
        else:
            self.press_right()
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.release_steer()
        return super().on_touch_up(touch)

    def stop(self):
        if self._event:
            self._event.cancel()

    def update(self, dt):
        if not self.alive:
            return

        self.car_x += self.car_speed * dt
        self.car_x = max(0, min(Window.width - self.car_w, self.car_x))

        for p in self.particles:
            p[1] -= self.fall_speed * 0.6 * dt
            if p[1] < 0:
                p[1] = Window.height
                p[0] = random.uniform(0, Window.width)

        self.spawn_timer += dt
        spawn_interval = max(0.5, 1.2 - self.score * 0.01)
        if self.spawn_timer > spawn_interval:
            self.spawn_timer = 0
            ox = random.uniform(0, Window.width - 60)
            self.obstacles.append([ox, Window.height, 60, 90])

        for ob in self.obstacles:
            ob[1] -= self.fall_speed * dt
        self.obstacles = [ob for ob in self.obstacles if ob[1] > -100]

        car_rect = (self.car_x, 80, self.car_w, self.car_h)
        for ob in self.obstacles:
            if self._collide(car_rect, ob):
                self.alive = False
                self.score_label.text = "Crashed! Score: {}  (tap to menu)".format(
                    int(self.score)
                )
                self.bind(on_touch_down=self._end_touch)
                break
        else:
            self.score += dt * 10
            self.score_label.text = "Score: {}".format(int(self.score))

        self.redraw()

    def _end_touch(self, *a):
        self.parent.manager.current = "menu"

    def _collide(self, a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

    def redraw(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.15, 0.15, 0.18, 1)
            Rectangle(pos=(0, 0), size=Window.size)
            Color(0.35, 0.35, 0.4, 1)
            for p in self.particles:
                Rectangle(pos=(p[0], p[1]), size=(4, 20))
            Color(0.85, 0.2, 0.2, 1)
            Rectangle(pos=(self.car_x, 80), size=(self.car_w, self.car_h))
            Color(0.9, 0.75, 0.1, 1)
            for ob in self.obstacles:
                Rectangle(pos=(ob[0], ob[1]), size=(ob[2], ob[3]))


class CarGameApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.12, 1)
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(GameScreen(name="game"))
        return sm


if __name__ == "__main__":
    CarGameApp().run()
