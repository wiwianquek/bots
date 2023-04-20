import math
import os
import random
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from components_creator import create_images

DIMENSIONS = (500, 500)
CENTER = (250, 250)
RADIUS = 225
DIAMETER = RADIUS * 2
CENTER_CIRCLE_RADIUS = 100
NUM_SPIN_FRAMES = 100
NUM_BLINK_FRAMES = 50
NUM_TOTAL_FRAMES = NUM_SPIN_FRAMES + NUM_BLINK_FRAMES
# frame durations
DURATIONS = [1000, 300, 200, 130, 80, 60, 40, 30, 25, 20] \
            + [20 for _ in range(NUM_SPIN_FRAMES - 20)] + [20, 25, 30, 40, 60, 80, 130, 200, 300, 1000] \
            + [100 for _ in range(NUM_BLINK_FRAMES)]  # Fastest 20

# import components
try:
    MASK_IMG = Image.open('mask.png')
    CENTER_CIRCLE_MASK_IMG = Image.open('center_circle_mask.png')
    CIRCLE_OUTLINE_IMG = Image.open('circle_outline.png')
    CENTER_CIRCLE_OUTLINE_IMG = Image.open('center_circle_outline.png')
    TRIANGLE_IMG = Image.open('triangle.png')
except FileNotFoundError as e:
    create_images(DIMENSIONS, CENTER, RADIUS, CENTER_CIRCLE_RADIUS)
    MASK_IMG = Image.open('mask.png')
    CENTER_CIRCLE_MASK_IMG = Image.open('center_circle_mask.png')
    CIRCLE_OUTLINE_IMG = Image.open('circle_outline.png')
    CENTER_CIRCLE_OUTLINE_IMG = Image.open('center_circle_outline.png')
    TRIANGLE_IMG = Image.open('triangle.png')
CIRCLE_OUTLINE_IMG_QUANTIZED = CIRCLE_OUTLINE_IMG.convert("RGB").quantize(2)
CENTER_CIRCLE_OUTLINE_IMG_QUANTIZED = CENTER_CIRCLE_OUTLINE_IMG.convert("RGB").quantize(2)
TRIANGLE_IMG_QUANTIZED = TRIANGLE_IMG.convert("RGB").quantize(2)
PASTEL_COLORS = [(220, 214, 255), (214, 240, 255), (222, 255, 239), (255, 250, 240), (255, 237, 237),
                 (255, 222, 222), (247, 246, 207), (182, 216, 242), (244, 207, 223), (87, 132, 186),
                 (154, 200, 235), (204, 212, 191), (231, 203, 169), (238, 186, 178), (245, 243, 231),
                 (245, 226, 228), (245, 191, 210), (229, 219, 156), (208, 188, 172), (190, 180, 197),
                 (230, 165, 126), (33, 139, 130), (154, 217, 219), (229, 219, 217), (152, 212, 187),
                 (235, 150, 170), (198, 201, 208), (229, 179, 187), (196, 116, 130), (249, 150, 139),
                 (118, 205, 205), (123, 146, 170), (228, 206, 224), (161, 93, 152), (220, 130, 143),
                 (247, 206, 118), (140, 115, 134), (156, 147, 89), (165, 114, 131), (232, 213, 149)]


class SpinnerGifMaker:

    def __init__(self, options):
        start = time.time()
        random.shuffle(options)
        self.options = options
        # 200 x 200 pic
        self.center_circle_cover_img = Image.open("images/cover/cat.png")
        folder_path = "images/joy"
        file_list = os.listdir(folder_path)
        image_list = [filename for filename in file_list if filename.endswith(('.png', '.jpg', '.jpeg'))]
        random_image = random.choice(image_list)
        image_path = os.path.join(folder_path, random_image)
        self.center_circle_img = Image.open(image_path).resize((200, 200))
        # self.center_circle_img = Image.open("images/joy/joy_jc.png")
        self.colors = random.sample(PASTEL_COLORS, len(options))
        first_half = [0, -2, -5, -10, -15, -20, -30, -50, -70, -100] + [i * -150 - 150 for i in
                                                                        range(int((NUM_SPIN_FRAMES - 20) / 2))]
        second_half = [i * -150 + 6000 for i in range(int((NUM_SPIN_FRAMES - 20) / 2))] + [100, 70, 50, 30, 20, 15,
                                                                                           10, 5, 2, 0]
        angles = first_half + second_half
        # start and end at unpredictable positions
        start_offset = random.randint(0, 359)
        end_offset = random.randint(0, 359)
        sector_first_half = [angle - start_offset for angle in angles[:50]]
        sector_second_half = [angle - end_offset for angle in angles[50:]]
        self.sector_angles = sector_first_half + sector_second_half
        self.image_angles = angles

        bg_img, spinner_img = self.prepare()

        frame_list = []
        for i in range(NUM_TOTAL_FRAMES):
            # print(f"frame {i}")
            frame = self.getSpinnerFrame(bg_img.copy(), spinner_img, i)
            frame_list.append(frame)
        frame_list[0].save('spinner.gif', format='GIF', append_images=frame_list[1:], save_all=True,
                           duration=DURATIONS, disposal=2, loop=0)
        end = time.time()
        print(f"time taken no mp unposterised: {end - start} seconds")

    def paste(self, bg_img, im, box=None, mask=None):
        # To combine one P image with another
        # add all of the new colors to the palette of the first image
        remap = [0] * 256
        for color, i in im.palette.colors.items():
            remap[i] = bg_img.palette.getcolor(color)
        # then update the palette indexes in the new image
        im = im.point(remap)
        # and paste
        bg_img.paste(im, box, mask)

        # Return the number of free colors left
        return 256 - len(bg_img.palette.colors)

    def prepare(self):
        # 16 colors
        bg_img = Image.open("images/bg/strawberry.png").convert("RGB").quantize(16)
        spinner_img = Image.new('RGB', DIMENSIONS, color=(0, 0, 0))
        # Add color pie slices
        spinner_draw = ImageDraw.Draw(spinner_img, 'RGBA')
        num_sectors = len(self.options)
        for i, option in enumerate(self.options):
            start_angle = i * (360 / num_sectors)
            end_angle = (i + 1) * (360 / num_sectors)
            color = self.colors[i]
            fill = (255,)
            # draw pie slices
            spinner_draw.pieslice(xy=((CENTER[0] - RADIUS, CENTER[1] - RADIUS), (CENTER[0] + RADIUS, CENTER[1] +
                                                                                 RADIUS)),
                                  start=start_angle,
                                  end=end_angle, fill=color + fill, outline='black')

            # Add text options
            font = ImageFont.truetype("arial.ttf", 30)
            _, _, text_width, text_height = spinner_draw.textbbox((0, 0), option, font=font, anchor="lt")
            sector_center_angle = (start_angle + end_angle) / 2
            sector_center_x = CENTER[0] + (RADIUS + CENTER_CIRCLE_RADIUS) * 0.5 * math.cos(sector_center_angle *
                                                                                           math.pi / 180)
            sector_center_y = CENTER[1] + (RADIUS + CENTER_CIRCLE_RADIUS) * 0.5 * math.sin(sector_center_angle *
                                                                                           math.pi / 180)
            text_angle = 180 - sector_center_angle
            text_img = Image.new('RGBA', (text_width, text_height), color=(0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((0, 0), option, fill=(0, 0, 0), font=font, anchor="lt")
            text_img = text_img.rotate(text_angle, expand=True)
            text_width, text_height = text_img.size
            text_center_x = sector_center_x - text_width / 2
            text_center_y = sector_center_y - text_height / 2
            spinner_img.paste(text_img, (int(text_center_x), int(text_center_y)), text_img)
        # 10 colors
        spinner_img = spinner_img.quantize(10)
        return bg_img, spinner_img

    def getSpinnerFrame(self, bg_img, spinner_img, frame_number):
        # Rotate
        if frame_number < NUM_SPIN_FRAMES:
            spinner_img = spinner_img.rotate(self.sector_angles[frame_number], center=CENTER)
            center_circle_cover_img = self.center_circle_cover_img.rotate(self.image_angles[frame_number], center=(100,
                                                                                                                   100))
            center_circle_img = self.center_circle_img.rotate(self.image_angles[frame_number], center=(100, 100))
        # Stop rotation
        else:
            spinner_img = spinner_img.rotate(self.sector_angles[-1], center=CENTER)
            center_circle_cover_img = self.center_circle_cover_img.rotate(self.image_angles[-1], center=(100, 100))
            center_circle_img = self.center_circle_img.rotate(self.image_angles[-1], center=(100, 100))

        self.paste(bg_img, spinner_img, (0, 0), MASK_IMG)

        # created outline image cos the spinner outline is quite wonky
        colors_left = self.paste(bg_img, CIRCLE_OUTLINE_IMG_QUANTIZED,
                                 (int((DIMENSIONS[0] - RADIUS * 2) / 2),
                                  int((DIMENSIONS[1] - RADIUS * 2) /
                                      2)), CIRCLE_OUTLINE_IMG)

        # center circle cover mask that decreases in opacity
        center_circle_cover_mask_size = (CENTER_CIRCLE_RADIUS * 2, CENTER_CIRCLE_RADIUS * 2)
        center_circle_cover_mask_img = Image.new('L', center_circle_cover_mask_size, color=0)
        center_circle_cover_mask_draw = ImageDraw.Draw(center_circle_cover_mask_img)
        if frame_number < 40:
            fill = 255
        elif frame_number >= 60:
            fill = 0
        else:
            fill = int((NUM_TOTAL_FRAMES - frame_number) / NUM_TOTAL_FRAMES * 255)
        center_circle_cover_mask_draw.ellipse((0, 0) + center_circle_cover_mask_size, fill=fill)

        # comment out to see without the cover image
        center_circle_img.paste(center_circle_cover_img, mask=center_circle_cover_mask_img)

        # reserve 1 color for triangle
        if frame_number < NUM_SPIN_FRAMES or frame_number % 2 == 1:
            colors_left -= 1

        self.paste(bg_img, center_circle_img.convert("RGB").quantize(colors_left), (
            int((DIMENSIONS[0] - CENTER_CIRCLE_RADIUS * 2) / 2), int((DIMENSIONS[1] - CENTER_CIRCLE_RADIUS * 2) /
                                                                     2)), CENTER_CIRCLE_MASK_IMG)

        # created outline image cos no center circle outline
        self.paste(bg_img, CENTER_CIRCLE_OUTLINE_IMG_QUANTIZED, (
            int((DIMENSIONS[0] - CENTER_CIRCLE_RADIUS * 2) / 2), int((DIMENSIONS[1] - CENTER_CIRCLE_RADIUS * 2) /
                                                                     2)), CENTER_CIRCLE_OUTLINE_IMG)

        # Add blink effect to triangle image on last frame
        if frame_number < NUM_SPIN_FRAMES or frame_number % 2 == 1:
            self.paste(bg_img, TRIANGLE_IMG_QUANTIZED, mask=TRIANGLE_IMG)

        return bg_img

# for testing
# SpinnerGifMaker(["hi", "play"])