import os
import re
import random
import aiohttp
import asyncio
import aiofiles

from config import MUSIC_BOT_NAME, YOUTUBE_IMG_URL
from YukkiMusic import app

from youtubesearchpython.__future__ import VideosSearch
from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps
)


def make_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def change_image_size(max_width, max_height, image):
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    new_image = image.resize((new_width, new_height))
    return new_image


def truncate_text(text):
    text_list = text.split(" ")
    text1 = ""
    text2 = ""
    for i in text_list:
        if len(text1) + len(i) < 30:
            text1 += " " + i
        elif len(text2) + len(i) < 30:
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()
    return [text1, text2]


async def generate_thumbnail(video_id):
    if os.path.isfile(f"cache/{video_id}.png"):
        return f"cache/{video_id}.png"
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        if 1 == 1:
            results = VideosSearch(url, limit=1)
            for result in await results.next():
                try:
                    title = result["title"]
                    title = re.sub("\W+", " ", title)
                    title = title.title()
                except:
                    title = "Unsupported Title"
                try:
                    duration = result["duration"]
                except:
                    duration = "Unknown Mins"
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                try:
                    views = result["viewCount"]["short"]
                except:
                    views = "Unknown Views"
                try:
                    channel = result["channel"]["name"]
                except:
                    channel = "Unknown Channel"

            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://img.youtube.com/vi/{video_id}/maxresdefault.jpg") as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(
                            f"cache/thumb{video_id}.png", mode="wb"
                        )
                        await f.write(await resp.read())
                        await f.close()

            youtube = Image.open(f"cache/thumb{video_id}.png")
            image1 = change_image_size(1280, 720, youtube)
            image2 = image1.convert("RGBA")
            background = image2.filter(filter=ImageFilter.BoxBlur(30))
            enhancer = ImageEnhance.Brightness(background)
            background = enhancer.enhance(0.6)
            image2 = background

            cover = Image.open(f"cache/thumb{video_id}.png")
            cover = cover.convert("RGBA")
            w, h = cover.size
            w = round((w * 720) / h)
            cover = cover.resize((w, 720))

            original = cover
            vertices = [(50, 0), (0, 720), (w, 720), (w, 0)]
            mask = Image.new("L", original.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.polygon(vertices, fill=255, outline=None)
            black = Image.new("RGBA", original.size, 0)
            result = Image.composite(original, black, mask)
            cover = result

            image3 = image2.filter(filter=ImageFilter.GaussianBlur(10))
            black = Image.new("RGB", (1280, 720), "black").convert("RGBA")
            image3 = Image.blend(image3, black, 0.5)

            image3.paste(cover, (1280 - 590, 0), cover)
            image3 = image3.convert("RGB")

            image3 = ImageOps.expand(image3, 20, (255, 255, 255))
            image3 = image3.resize((1280, 720))

            ldraw = ImageDraw.Draw(image3)
            line = [((1280 - w) + 740, 0), ((1280 - w) + 680, 720)]
            ldraw.line(line, (255, 255, 255), 20)

            # fonts
            font1 = ImageFont.truetype('assets/font.ttf', 30)
            font2 = ImageFont.truetype('assets/font2.ttf', 70)
            font3 = ImageFont.truetype('assets/font2.ttf', 40)
            font4 = ImageFont.truetype('assets/font2.ttf', 35)

            image4 = ImageDraw.Draw(image3)
            image4.text((30, 20), "ARCH X AAROHI MUSIC", fill="white", font=font1)
            image4.text((80, 150), "NOW PLAYING", fill="white", font=font2, stroke_width=5, stroke_fill="black")

            # title
            title1 = truncate_text(title)
            image4.text((80, 300), text=title1[0], fill="white", stroke_width=5, stroke_fill="black", font=font3)
            image4.text((80, 350), text=title1[1], fill="white", stroke_width=5, stroke_fill="black", font=font3)

            # description
            views = f"Views: {views}"
            duration = f"Duration: {duration} Mins"
            channel = f"Channel: {channel}"

            image4.text((80, 450), text=views, fill="white", font=font4, align="left")
            image4.text((80, 500), text=duration, fill="white", font=font4, align="left")
            image4.text((80, 550), text=channel, fill="white", font=font4, align="left")

            try:
                os.remove(f"cache/thumb{video_id}.png")
            except:
                pass
            image3.save(f"cache/{video_id}.png")
            file = f"cache/{video_id}.png"
            return file
    except Exception as e:
        print(e)
        return YOUTUBE_IMAGE_URL
