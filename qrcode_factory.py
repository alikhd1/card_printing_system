import os

import qrcode


def qrcode_generator(url, file_name='qr_code', **kwargs):
    qr = qrcode.QRCode(
        version=1,
        error_correction=kwargs.get('error_correction') or qrcode.constants.ERROR_CORRECT_H,
        box_size=kwargs.get('box_size') or 9,
        border=0,
    )

    # Add your data
    qr.add_data(url)
    qr.make(fit=True)

    # Generate the QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image to a specific folder
    folder_path = "qr"
    img_path = os.path.join(folder_path, f"{file_name}.png")

    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    img.save(img_path)
    # Save the QR code image
    return img_path
