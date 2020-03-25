"""
A Flask application to expose the `/process_image` REST API endpoint.

"""

import os
import json
from flask import Flask, Response, request

from main import Main
from utils.helpers import is_session_id_invalid

app = Flask(__name__)
main = Main(db_name="sorterbot", base_img_path=os.path.abspath(os.path.join(os.path.abspath(__file__), "../../images")))


@app.route("/process_image", methods=["POST"])
def process_image():
    """
    This endpoint exposes image processing functionality.

    Parameters
    ----------
    session_id : str
        Datetime based unique identifier of the current session. It is generated by the Raspberry Pi and passed
        with the POST request.
    image_name : str
        Name of the image to be processed. The image has to be uploaded to the s3 bucket. Value is passed
        with the POST request.
    is_final : bool
        Boolean value indicating if the current image is the last of the session. If it is, all of the session's
        images will be cropped, vectorized and clustered.

    """

    # Retrieve query parameters from the request
    session_id = request.args.get("session_id")
    image_name = request.args.get("image_name")
    is_final = request.args.get("is_final")

    sess_id_invalid = is_session_id_invalid(session_id)
    if sess_id_invalid:
        raise Exception(f"Session ID ({session_id}) is invalid: {sess_id_invalid}")

    # Detect objects on image and save bounding boxes to the database
    main.process_image(session_id, image_name)

    main.postgres.close()

    # If the image is the last of a session, crop and vectorize all objects in current session
    if is_final:
        images_with_objects, pairings = main.vectorize_session_images()
        res = {
            "objects": images_with_objects,
            "pairings": pairings
        }
        return Response(json.dumps(res), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"result": f"'{image_name}' of session '{session_id}' successfully processed!"}), status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
