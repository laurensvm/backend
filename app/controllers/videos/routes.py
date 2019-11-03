from flask import jsonify, g, request, send_file

from . import videos
from ..authentication import auth
from ..statuscodes import bad_request, not_found, unauthorized, success
from ...models import Video, Type, Directory
from ...exceptions import IOException


@videos.route("/", methods=["GET"])
@auth.login_required
def get_latest_videos():
    try:
        amount = int(request.args.get("amount"))
    except ValueError as e:
        return bad_request("Could not convert amount to integer")
    except TypeError:
        amount = 30

    videos = Video.get_latest(amount)

    for video in videos:
        if not g.current_user in video.directory.users_with_rights:
            videos.remove(video)

    return jsonify({'videos': [video.json() for video in videos]})

@videos.route("/latest/id/", methods=["GET"])
def get_latest_video_ids():
    try:
        amount = int(request.args.get("amount"))
    except ValueError as e:
        return bad_request("Could not convert amount to integer")
    except TypeError:
        amount = 30

    videos = Video.get_latest(amount)

    for video in videos:
        if not g.current_user in video.directory.users_with_rights:
            videos.remove(video)

    return jsonify({'videos': [video.id for video in videos]})

@videos.route("/thumbnail/<int:id>/", methods=["GET"])
@auth.login_required
def get_thumbnail_image(id):
    video = Video.get_by_id(id)

    if not g.current_user in video.directory.users_with_rights:
        return unauthorized()

    if not video:
        return not_found("Video not found")

    if not video.thumbnail_path:
        return not_found("Video has no thumbnail image")

    return send_file(video.thumbnail_path)


@videos.route("/upload/", methods=["POST"])
@auth.login_required
def upload_file():
    files = request.files.getlist("file")

    if len(files) > 2:
        return bad_request("Request contains more than two files")
    elif len(files) == 1 and not "video" in files[0].content_type:
        return bad_request("No video content type found in files")
    elif not files:
        return bad_request("No file is sent in this request")


    for file in files:
        if "image" in file.content_type:
            thumbnail = file
        elif "video" in file.content_type:
            video = file

    if video is None:
        return bad_request("No video file is found in the files")

    type = request.form.get("type") or None
    directory_id = request.form.get("directory_id")
    description = request.form.get("description") or None
    latitude = request.form.get("latitude") or None
    longitude = request.form.get("longitude") or None
    device = request.form.get("device") or None
    resolution = request.form.get("resolution") or None
    local_id = request.form.get("local_identifier")
    length = request.form.get("length") or None

    if not directory_id:
        return bad_request("No directory id is given in request")

    if type not in [Type.video, None]:
        return bad_request("Please use the endpoint for {0}".format(type))

    d = Directory.get_by_id(directory_id)

    if not d:
        return not_found("Directory does not exist")

    if not g.current_user in d.users_with_rights:
        return unauthorized()

    v = Video(
        name=video.filename,
        directory=d,
        user=g.current_user,
        latitude=latitude,
        longitude=longitude,
        device=device,
        resolution=resolution,
    )

    if description:
        v.description = description

    if length:
        v.length = length

    if local_id:
        v.local_id = local_id

    if thumbnail:
        v.save_thumbnail(thumbnail)

    try:
        v.save(video)
    except IOException as e:
        return jsonify(e.json())

    return success("Video successfully uploaded.")

@videos.route("/download/<int:id>/", methods=["GET"])
@auth.login_required
def download_video(id):
    v = Video.get_by_id(id)

    if not v:
        return not_found("Video with id {0} not found".format(id))

    if not g.current_user in v.directory.users_with_rights:
        return unauthorized()

    return send_file(v.internal_path)


@videos.route("/<int:id>/", methods=["GET"])
@auth.login_required
def get_video(id):
    v = Video.get_by_id(id)

    if not v:
        return not_found("Video with id {0} not found".format(id))

    if not g.current_user in v.directory.users_with_rights:
        return unauthorized()

    return jsonify(v.json())