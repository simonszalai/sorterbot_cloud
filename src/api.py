"""
A Flask application to expose the vectorizer functionality as a REST API endpoint.

"""

from main import Main
from flask import Flask, request

app = Flask(__name__)
main = Main()


@app.route("/process_image", methods=["POST"])
def process_image():
    # Retrieve query parameters from the request
    session_id = request.args.get("session_id")
    img_name = request.args.get("image_name")
    is_final = request.args.get("is_final")

    main.process_image(session_id, img_name, is_final)

    if is_final:
        main.vectorize_session_images(session_id)

    return 'ok'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
