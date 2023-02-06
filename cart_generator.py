from PIL import Image, ImageFont, ImageDraw
from bidi.algorithm import get_display
import arabic_reshaper

from qrcode_factory import qrcode_generator


class CardGenerator:
    def __init__(self, base_image_path, qr_code_path, font_path, font_size=38, **kwargs):
        self.base_image = Image.open(base_image_path)
        self.qr_code = Image.open(qr_code_path)
        self.font = ImageFont.truetype(font_path, font_size if font_size else 38)
        self.draw = ImageDraw.Draw(self.base_image)
        self.qr_code_x = kwargs.get('qr_code_x') or 103
        self.qr_code_y = kwargs.get('qr_code_y') or 98
        self.space_between = kwargs.get('space_between') or 20

    def fix_persian_text(self, text):
        unicode_text_reshaped = arabic_reshaper.reshape(text)
        return get_display(unicode_text_reshaped, base_dir='R')

    def paste_qr_code(self):
        self.base_image.paste(self.qr_code, (self.qr_code_x, self.qr_code_y))

    def add_text(self, text, code):
        qr_code_width, qr_code_height = self.qr_code.size

        draw = ImageDraw.Draw(self.base_image)

        text = self.fix_persian_text(text)
        text_width, text_height = draw.textsize(text, self.font)

        if text_width > qr_code_width:
            # split the text into two lines
            words = text.split()
            lines = []
            line = ""
            for word in words:
                line_with_word = line + word + " "
                line_width, _ = draw.textsize(line_with_word, self.font)
                if line_width <= qr_code_width:
                    line = line_with_word
                else:
                    lines.append(line)
                    line = word + " "
            lines.append(line)

            text_height *= len(lines)  # update the text height based on the number of lines
            text_y = self.qr_code_y + qr_code_height + self.space_between  # adjust this value to move the text down
            lines.reverse()  # persian texts fix
            # draw each line of text
            for i, line in enumerate(lines):
                text_x = self.qr_code_x + (qr_code_width - draw.textsize(line, self.font)[0]) / 2
                draw.text((text_x, text_y + i * text_height / len(lines)), line, font=self.font, fill=(0, 0, 0),
                          align='center')
        else:
            text_x = self.qr_code_x + (qr_code_width - text_width) / 2
            text_y = self.qr_code_y + qr_code_height + self.space_between  # adjust this value to move the text down
            draw.text((text_x, text_y), text, font=self.font, fill=(0, 0, 0), align='center')

        code = str(code)
        code_width, code_height = draw.textsize(code, self.font)
        code_x = self.qr_code_x + (qr_code_width - code_width) / 2
        code_y = text_y + text_height + self.space_between  # adjust this value to move the text down

        draw.text((code_x, code_y), code, font=self.font, fill=(0, 0, 0), align='center')

    def save(self, path):
        self.base_image.save(path)


def generate_card(users: list, progress_bar=None, many=False, **kwargs):
    if not many:
        users[0] = users
    for i, user in enumerate(users):
        path = f'cards/{user[2]}.png'
        card = CardGenerator("assets/base_image.png",
                             qrcode_generator(url=user[3], file_name=user[2], box_size=kwargs.get('box_size')),
                             "assets/Vazirmatn-Regular.ttf",
                             font_size=kwargs.get('font_size'),
                             space_between=kwargs.get('space_between'),
                             qr_code_x=kwargs.get('qr_code_x'),
                             qr_code_y=kwargs.get('qr_code_y'),
                             )
        card.paste_qr_code()
        card.add_text(text=user[1], code=user[2])
        card.save(f"cards/{user[2]}.png")
        if progress_bar:
            progress_bar.progressbar.setValue(i)
        if not many:
            return path
