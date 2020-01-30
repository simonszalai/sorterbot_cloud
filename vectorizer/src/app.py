import os
from flask import Flask, request, jsonify
import boto3

from vectorizer import Vectorizer


app = Flask(__name__)
s3 = boto3.resource("s3")
vectorizer = Vectorizer(model_name="resnet18", input_dimensions=(224, 224), batch_size=45)


@app.route("/vectorize", methods=["POST"])
def vectorize():
    if request.method == "POST":
        # Check if file is already downloaded
        if not os.path.isfile("/home/simon/dev/sorterbot/images/aws/image8.jpg"):
            # Download image from S3 if not
            print('File does not exists, downloading from S3...')
            s3.Bucket("sorterbot").download_file("image8.jpg", "/home/simon/dev/sorterbot/images/aws/image8.jpg")

        vectorizer.load_data("/home/simon/dev/sorterbot/images")
        results = vectorizer.start()

        return jsonify({"results": results})


if __name__ == "__main__":
    app.run(port=6000, debug=True)


example = [
    {
        "image_name": "image8.jpg",
        "objects": [
            {"type": "item", "x": 0.5423, "y": 0.2457, "w": 0.0457, "h": 0.0247}
        ],
    }
]
