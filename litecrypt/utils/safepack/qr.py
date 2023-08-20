from typing import Union

import qrcode


def tqr(text: str) -> Union[int, tuple]:
    try:
        qr = qrcode.QRCode(
            version=10,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=1,
        )
        qr.add_data(text.strip())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.show()
        return 1

    except Exception as e:
        return 0, e
