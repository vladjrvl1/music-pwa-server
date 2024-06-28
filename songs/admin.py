from django.contrib import admin

from songs.models import Song


# Register your models here.
@admin.register(Song)
class SongsAdmin(admin.ModelAdmin):
    pass
