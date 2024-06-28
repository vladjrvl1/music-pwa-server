import mimetypes
import os

from django.conf import settings
from django.http import HttpResponse, FileResponse

from songs.models import Song


def parse_range_header(range_header, file_size):
    """
    Parse the Range HTTP header into a list of (start, end) byte ranges.
    Returns None if the header is invalid or can't be parsed.
    """
    try:
        ranges = []
        units, range_specs = range_header.split('=')
        if units.strip().lower() != 'bytes':
            return None

        for spec in range_specs.split(','):
            start, end = spec.split('-')
            start = int(start) if start else None
            end = int(end) if end else None

            if start is None and end is None:
                return None
            if start is not None and end is not None and start > end:
                return None

            if start is None:
                start = max(0, file_size - end)
                end = file_size - 1
            elif end is None:
                end = file_size - 1

            ranges.append((start, end))

        return ranges

    except Exception:
        return None


def stream_audio(request, song_id):
    try:
        song = Song.objects.get(id=song_id)
    except Song.DoesNotExist:
        return HttpResponse(status=404)

    fullpath = os.path.join(settings.MEDIA_ROOT, song.audio.name)

    # Check if the file exists
    if not os.path.exists(fullpath):
        return HttpResponse(status=404)

    # Open the file for streaming
    file = open(fullpath, 'rb')

    # Get file size
    file_size = os.path.getsize(fullpath)

    # Content-Type header
    content_type, encoding = mimetypes.guess_type(fullpath)
    if not content_type:
        content_type = 'application/octet-stream'

    response = FileResponse(file, content_type=content_type)

    # Set headers for range requests
    response['Accept-Ranges'] = 'bytes'

    # Handle range requests
    if 'HTTP_RANGE' in request.META:
        range_header = request.META['HTTP_RANGE']
        ranges = parse_range_header(range_header, file_size)

        if ranges is None:
            response.status_code = 416  # Requested range not satisfiable
            return response

        start, end = ranges[0]

        # Set the appropriate Content-Length for the response
        response['Content-Length'] = (end - start) + 1

        # Set the Content-Range header
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'

        # Seek to the requested position in the file
        file.seek(start)

        # Set the file to stream
        response.file_to_stream = file

        # Set the status code to 206 to indicate partial content
        response.status_code = 206

    return response
