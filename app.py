from PIL import Image, ImageDraw, ImageFont
import pandas as pd
df = pd.read_csv('list.csv')
font = ImageFont.truetype('arial.ttf', 60)
for index, j in df.iterrows():
    img = Image.open('cert.jpeg')
    name = j['name']
    W, H = (1280, 1005)
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(name, font=font)
    draw.text(((W-w)/2, 360), name, fill="black", font=font)
    img.save('pictures/{}.jpg'.format(name))
