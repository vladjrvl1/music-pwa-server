from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView

from .schema import schema
from .views import stream_audio

urlpatterns = [
    path('graphql/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True, schema=schema))),
    path('stream/<int:song_id>', stream_audio, name='stream_audio'),
]
