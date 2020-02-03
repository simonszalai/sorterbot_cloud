import os
from flask import Flask, request, jsonify

from vectorizer import Vectorizer
from preprocessor import PreProcessor


# base_path = "/home/simon/dev/sorterbot/images"
base_path = "/Users/simonszalai/dev/sorterbot/images"

app = Flask(__name__)

vectorizer = Vectorizer(model_name="resnet18", input_dimensions=(224, 224), batch_size=45)
preprocessor = PreProcessor(base_path=base_path, bucket_name="sorterbot")


@app.route("/vectorize", methods=["POST"])
def vectorize():
    if request.method == "POST":
        images = [
            {
                "image_name": "IMG_20190630_082354.jpg",
                "objects": [
                    {
                        "id": 0,
                        "type": "item",
                        "bbox_dims": {
                            "x": 0.5423,
                            "y": 0.2457,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    },
                    {
                        "id": 1,
                        "type": "item",
                        "bbox_dims": {
                            "x": 0.5423,
                            "y": 0.2457,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    },
                    {
                        "id": 2,
                        "type": "item",
                        "bbox_dims": {
                            "x": 0.5423,
                            "y": 0.2457,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    }
                ]
            }, {
                "image_name": "image8.jpg",
                "objects": [
                    {
                        "id": 1,
                        "type": "item",
                        "bbox_dims": {
                            "x": 0.5423,
                            "y": 0.2457,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    }
                ]
            }
        ]

        for image in images:
            preprocessor.download_image(image["image_name"])
            preprocessor.crop_all_objects(image["image_name"], image["objects"])

        vectorizer.load_data(os.path.join(base_path, "cropped"))
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
