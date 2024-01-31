from qrcode import QRCode, constants
import enum


class QRResult(enum.Enum):
    SUCCESS = enum.auto()
    FAILURE = enum.auto()


def tqr(text: str) -> QRResult:
    try:
        qr = QRCode(
            version=10,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=20,
            border=1,
        )
        qr.add_data(text.strip())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.show()
        return QRResult.SUCCESS

    except Exception:
        return QRResult.FAILURE
