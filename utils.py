import requests
from PyQt5.QtCore import QByteArray, QBuffer
import requests
import time

def get_random_fact():
    url = 'https://uselessfacts.jsph.pl/random.json?language=en'

    try:
        response = requests.get(url)
        fact_data = response.json()

        if 'text' in fact_data:
            fact = fact_data['text']
            return fact
        else:
            return "Failed to fetch random fact."
    except Exception as e:
        return f"An error occurred: {str(e)}"

"""
        #Segoe UI Variable Display Light
        #Sitka Banner
        #Century Schoolbook
        #Perpetua Titling MT
        #Sitka Heading Semibold
        #Rockwell Extra Bold
        #Microsoft YaHei Light
"""

def pixmap_to_png_bytes(pixmap):
        """
        Convert a QPixmap to a bytes object representing a PNG image.
        """
        if not pixmap:
            return None

        image = pixmap.toImage()
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QBuffer.WriteOnly)
        image.save(buffer, "PNG")
        return byte_array.data()