"""Multilingual Love Heart — Powered by Nurlan Mammadli.

GitHub: https://github.com/nurlancoder/love-you
"""

import math
import random
import tkinter.font
import turtle

HEART_SCALE = 21
HEART_Y_OFFSET = 20
ANIMATION_DURATION_SECONDS = 10
FRAME_INTERVAL_MS = 16
ANIMATION_FRAME_COUNT = 42
TEXT_RISE_DISTANCE = 34
TEXT_GAP = 7
FONT_SIZES = (9, 10, 11, 12)
FONT_FAMILY = "Arial"
BACKGROUND_COLOR = "#060208"

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor(BACKGROUND_COLOR)
screen.title("Love Heart | Powered by Nurlan Mammadli")
screen.tracer(0)

canvas = screen.getcanvas()
random_generator = random.Random(11)

LOVE_PHRASES = [
    "I love you", "Seni seviyorum", "Te amo", "Je t'aime",
    "Ich liebe dich", "Ti amo", "Eu te amo", "Я тебя люблю",
    "사랑해", "愛してる", "我爱你", "मैं तुमसे प्यार करता हूँ",
    "Σ' αγαπώ", "Ik hou van jou", "Jag älskar dig", "Kocham cię",
    "ฉันรักเธอ", "Anh yêu em", "Aku cinta kamu", "Я тебе кохаю",
]

font_cache = {}


def get_font(font_size):
    if font_size not in font_cache:
        font_cache[font_size] = tkinter.font.Font(
            root=canvas, family=FONT_FAMILY, size=font_size, weight="bold"
        )
    return font_cache[font_size]


def heart_point(angle):
    x_coordinate = 16 * (math.sin(angle) ** 3)
    y_coordinate = (
        13 * math.cos(angle)
        - 5 * math.cos(2 * angle)
        - 2 * math.cos(3 * angle)
        - math.cos(4 * angle)
    )
    return (
        x_coordinate * HEART_SCALE,
        y_coordinate * HEART_SCALE + HEART_Y_OFFSET,
    )


def to_hex_color(color):
    return "#%02x%02x%02x" % tuple(
        int(max(0, min(1, channel)) * 255) for channel in color
    )


def blend_colors(first_color, second_color, amount):
    return tuple(
        first + (second - first) * amount
        for first, second in zip(first_color, second_color)
    )


def scale_color(color, factor):
    return tuple(channel * factor for channel in color)


HEART_BOUNDARY = [
    heart_point(2 * math.pi * index / 720) for index in range(720)
]
HEART_EDGES = list(
    zip(HEART_BOUNDARY, HEART_BOUNDARY[1:] + HEART_BOUNDARY[:1])
)
MAX_HEART_Y = max(point[1] for point in HEART_BOUNDARY)
MIN_HEART_Y = min(point[1] for point in HEART_BOUNDARY)
HEART_CENTER_Y = (MAX_HEART_Y + MIN_HEART_Y) / 2


def get_horizontal_spans(y_coordinate):
    x_intersections = []
    for (start_x, start_y), (end_x, end_y) in HEART_EDGES:
        if (start_y <= y_coordinate < end_y) or (
            end_y <= y_coordinate < start_y
        ):
            x_intersections.append(
                start_x
                + (y_coordinate - start_y)
                * (end_x - start_x)
                / (end_y - start_y)
            )
    x_intersections.sort()
    return list(zip(x_intersections[0::2], x_intersections[1::2]))


def intersect_spans(first_spans, second_spans):
    intersections = []
    for first_span in first_spans:
        for second_span in second_spans:
            left = max(first_span[0], second_span[0])
            right = min(first_span[1], second_span[1])
            if right - left > 14:
                intersections.append((left, right))
    return intersections


def cycle_phrases():
    while True:
        phrase_order = LOVE_PHRASES[:]
        random_generator.shuffle(phrase_order)
        yield from phrase_order


def build_heart_text():
    phrase_iterator = cycle_phrases()
    row_height = max(
        get_font(font_size).metrics("linespace") for font_size in FONT_SIZES
    ) + 4
    half_row_height = row_height / 2
    placements = []

    y_coordinate = MAX_HEART_Y - half_row_height
    while y_coordinate > MIN_HEART_Y + half_row_height:
        row_spans = intersect_spans(
            get_horizontal_spans(y_coordinate + half_row_height),
            get_horizontal_spans(y_coordinate - half_row_height),
        )

        for left, right in row_spans:
            left += 4
            right -= 4
            cursor_x = left + random_generator.uniform(0, 8)
            line_placements = []

            while True:
                fitting_phrase = None
                for _ in range(10):
                    phrase = next(phrase_iterator)
                    font_size = random_generator.choice(FONT_SIZES)
                    text_width = get_font(font_size).measure(phrase)
                    if cursor_x + text_width <= right:
                        fitting_phrase = (phrase, font_size, text_width)
                        break
                if not fitting_phrase:
                    break
                phrase, font_size, text_width = fitting_phrase
                line_placements.append(
                    [cursor_x + text_width / 2, phrase, font_size, text_width]
                )
                cursor_x += text_width + TEXT_GAP

            if not line_placements:
                continue

            if len(line_placements) > 1:
                remaining_space = right - (
                    line_placements[-1][0] + line_placements[-1][3] / 2
                )
                for index, placement in enumerate(line_placements):
                    placement[0] += (
                        remaining_space * index / (len(line_placements) - 1)
                    )
            else:
                line_placements[0][0] = (left + right) / 2

            for index, (x_coordinate, phrase, font_size, _) in enumerate(
                line_placements
            ):
                is_edge = index == 0 or index == len(line_placements) - 1
                placements.append(
                    dict(
                        x=x_coordinate,
                        y=y_coordinate,
                        text=phrase,
                        size=font_size,
                        edge=is_edge,
                    )
                )

        y_coordinate -= row_height

    wine_red = (0.58, 0.0, 0.09)
    crimson = (0.90, 0.05, 0.14)
    bright_red = (0.98, 0.10, 0.16)
    for placement in placements:
        normalized_radius = min(
            1.0,
            normalized_heart_distance(placement["x"], placement["y"]),
        )
        base_color = blend_colors(
            wine_red, crimson, 0.25 + 0.75 * normalized_radius
        )
        base_color = blend_colors(
            base_color,
            bright_red,
            random_generator.uniform(0, 0.35)
            + (0.3 if placement["edge"] else 0),
        )
        placement["color"] = tuple(
            min(1, channel) for channel in base_color
        )
        placement["radius"] = normalized_radius

    edge_placements = [item for item in placements if item["edge"]]
    interior_placements = [item for item in placements if not item["edge"]]
    edge_placements.sort(
        key=lambda item: math.atan2(
            item["x"], item["y"] - HEART_CENTER_Y
        ) % (2 * math.pi)
    )
    interior_placements.sort(
        key=lambda item: -item["radius"] + random_generator.uniform(0, 0.08)
    )
    return edge_placements + interior_placements


def normalized_heart_distance(x_coordinate, y_coordinate):
    return math.hypot(
        x_coordinate / (16 * HEART_SCALE),
        (y_coordinate - HEART_CENTER_Y) / (14.5 * HEART_SCALE),
    )


HIGHLIGHT_COLOR = (1.0, 0.78, 0.78)
main_canvas_items = []
active_animations = []


def clamp_unit_interval(value):
    return max(0.0, min(1.0, value))


def create_text_animation(placement):
    x_coordinate = placement["x"]
    y_coordinate = -placement["y"]
    font_size = placement["size"]
    phrase = placement["text"]
    text_color = placement["color"]
    font = (FONT_FAMILY, font_size, "bold")
    larger_font = (FONT_FAMILY, font_size + 1, "bold")

    shadow_id = canvas.create_text(
        x_coordinate + 2,
        y_coordinate + 3,
        text=phrase,
        font=font,
        fill=BACKGROUND_COLOR,
    )
    halo_id = canvas.create_text(
        x_coordinate,
        y_coordinate,
        text=phrase,
        font=larger_font,
        fill=BACKGROUND_COLOR,
    )
    main_text_id = canvas.create_text(
        x_coordinate,
        y_coordinate - TEXT_RISE_DISTANCE,
        text=phrase,
        font=font,
        fill=BACKGROUND_COLOR,
    )

    placement.update(
        shadow_id=shadow_id,
        halo_id=halo_id,
        main_text_id=main_text_id,
        frame=0,
        horizontal_offset=random_generator.uniform(-10, 10),
    )
    main_canvas_items.append((main_text_id, text_color))
    active_animations.append(placement)


def update_text_animation(placement):
    placement["frame"] += 1
    progress = clamp_unit_interval(
        placement["frame"] / ANIMATION_FRAME_COUNT
    )
    eased_progress = 1 - (1 - progress) ** 3
    text_color = placement["color"]
    x_coordinate = placement["x"]
    y_coordinate = -placement["y"]
    remaining_rise = (1 - eased_progress) * TEXT_RISE_DISTANCE
    animated_x = x_coordinate + placement["horizontal_offset"] * (
        1 - eased_progress
    )
    animated_y = y_coordinate - remaining_rise

    canvas.itemconfig(
        placement["shadow_id"],
        fill=to_hex_color(
            blend_colors(
                BACKGROUND_RGB, scale_color(text_color, 0.30), eased_progress
            )
        ),
    )
    canvas.itemconfig(
        placement["halo_id"],
        fill=to_hex_color(
            blend_colors(
                BACKGROUND_RGB,
                scale_color(text_color, 0.20),
                eased_progress * eased_progress,
            )
        ),
    )
    canvas.coords(placement["halo_id"], animated_x, animated_y)

    highlight_strength = 0.75 * half_sine(
        clamp_unit_interval((progress - 0.55) / 0.45)
    )
    animated_color = blend_colors(
        blend_colors(BACKGROUND_RGB, text_color, eased_progress ** 1.5),
        HIGHLIGHT_COLOR,
        highlight_strength,
    )
    canvas.itemconfig(
        placement["main_text_id"], fill=to_hex_color(animated_color)
    )
    canvas.coords(placement["main_text_id"], animated_x, animated_y)

    if progress >= 1:
        canvas.coords(placement["halo_id"], x_coordinate, y_coordinate)
        canvas.coords(placement["main_text_id"], x_coordinate, y_coordinate)
        canvas.itemconfig(
            placement["main_text_id"], fill=to_hex_color(text_color)
        )
        return False
    return True


def half_sine(value):
    return math.sin(math.pi * value)


BACKGROUND_RGB = tuple(
    int(BACKGROUND_COLOR[index:index + 2], 16) / 255
    for index in (1, 3, 5)
)
DRAW_ORDER = build_heart_text()
placement_iterator = iter(DRAW_ORDER)
SPAWN_RATE = len(DRAW_ORDER) / (
    ANIMATION_DURATION_SECONDS * 1000 / FRAME_INTERVAL_MS
)
spawn_accumulator = 0.0
is_spawning = True


def animation_tick():
    global is_spawning, spawn_accumulator
    if is_spawning:
        spawn_accumulator += SPAWN_RATE
        try:
            while spawn_accumulator >= 1:
                spawn_accumulator -= 1
                create_text_animation(next(placement_iterator))
        except StopIteration:
            is_spawning = False

    active_animations[:] = [
        placement
        for placement in active_animations
        if update_text_animation(placement)
    ]

    if not is_spawning and not active_animations:
        run_shimmer_animation()
        return
    canvas.after(FRAME_INTERVAL_MS, animation_tick)


def set_canvas_item_color(item_id, color):
    try:
        canvas.itemconfig(item_id, fill=to_hex_color(color))
    except Exception:
        pass


def run_shimmer_animation():
    for _ in range(1):
        item_id, color = random_generator.choice(main_canvas_items)
        set_canvas_item_color(
            item_id, blend_colors(color, HIGHLIGHT_COLOR, 0.6)
        )
        canvas.after(
            260,
            lambda item_id=item_id, color=color: set_canvas_item_color(
                item_id, color
            ),
        )
    canvas.after(140, run_shimmer_animation)


try:
    canvas.after(200, animation_tick)
    turtle.done()
except (turtle.Terminator, Exception):
    pass