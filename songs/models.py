from django.db import models
import mutagen
import logging

log = logging.getLogger(__name__)


class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    audio = models.FileField(upload_to='songs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

    @property
    def duration(self):
        try:
            audio = mutagen.File(self.audio.path)
            if audio:
                duration = int(audio.info.length)
                minutes = duration // 60
                seconds = duration % 60
                return f"{minutes:02}:{seconds:02}"
            else:
                return None
        except Exception as e:
            log.exception(f"Error calculating Song duration: {e}")
            return None
