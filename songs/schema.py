import graphene
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.urls import reverse
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload

from .models import Song


class SongType(DjangoObjectType):
    audio_url = graphene.String()
    image_url = graphene.String()

    class Meta:
        model = Song

    def resolve_audio_url(self, info):
        if self.audio:
            return info.context.build_absolute_uri(reverse('stream_audio', args=[self.id]))
        return None

    def resolve_image_url(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return None

    duration = graphene.String()


class UploadSong(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        artist = graphene.String()
        audio = Upload(required=True)
        image = Upload(required=True)

    success = graphene.Boolean()
    song = graphene.Field(SongType)

    def mutate(self, info, audio, image, title, artist):
        song_path = default_storage.save(f'songs/{audio.name}', ContentFile(audio.read()))
        image_path = default_storage.save(f'images/{image.name}', ContentFile(image.read()))

        song = Song.objects.create(title=title, artist=artist, audio=song_path, image=image_path)
        song.save()

        return UploadSong(success=True, song=song)


class Query(graphene.ObjectType):
    songs = graphene.List(SongType)

    def resolve_songs(self, info):
        return Song.objects.all()


class Mutation(graphene.ObjectType):
    upload_song = UploadSong.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
