"""
A Flask application to expose the vectorizer functionality as a REST API endpoint.

"""


import os
from flask import Flask, request, jsonify
from sklearn.cluster import KMeans

from detectron import Detectron
from vectorizer import Vectorizer
from preprocessor import PreProcessor
from postgres import Postgres


host = "0.0.0.0"
port = 6000
# base_path = "/home/simon/dev/sorterbot/images"
base_path = "/Users/simonszalai/dev/sorterbot/images"

app = Flask(__name__)

detectron = Detectron(base_path=base_path, config_file="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
preprocessor = PreProcessor(base_path=base_path, bucket_name="sorterbot")
vectorizer = Vectorizer(model_name="resnet18", input_dimensions=(224, 224), batch_size=1)
db = Postgres()


@app.route("/run_locator", methods=["POST"])
def run_locator():
    db.open()
    db.create_table()
    results = detectron.predict("000000001503.jpg")
    db.insert_results(results)
    db.close()

    return 'ok'


@app.route("/compute_clusters", methods=["POST"])
def compute_clusters():
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
                            "y": 0.7215,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    },
                    {
                        "id": 2,
                        "type": "item",
                        "bbox_dims": {
                            "x": 0.5423,
                            "y": 0.5846,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    }
                ]
            }, {
                "image_name": "image8.jpg",
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
                    }, {
                        "id": 1,
                        "type": "item",
                        "bbox_dims": {
                            "x": 0.2145,
                            "y": 0.2457,
                            "w": 0.6845,
                            "h": 0.0247
                        }
                    }, {
                        "id": 2,
                        "type": "container",
                        "bbox_dims": {
                            "x": 0.5423,
                            "y": 0.2457,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    }, {
                        "id": 3,
                        "type": "container",
                        "bbox_dims": {
                            "x": 0.5423,
                            "y": 0.2457,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    }, {
                        "id": 4,
                        "type": "container",
                        "bbox_dims": {
                            "x": 0.5423,
                            "y": 0.2457,
                            "w": 0.0457,
                            "h": 0.0247
                        }
                    }, {
                        "id": 5,
                        "type": "container",
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

        n_containers = 0
        for image in images:
            # Download image
            preprocessor.download_image(image["image_name"])

            # Crop all items and count containers
            n_containers_of_image = preprocessor.crop_all_objects(image["image_name"], image["objects"])

            # Accumulate container count across images
            n_containers += n_containers_of_image

        # Create dataset for vectorization
        vectorizer.load_data(os.path.join(base_path, "cropped"))

        # Run vectorizer
        filenames, vectors = vectorizer.start()

        # Compute clusters
        clusters = KMeans(n_clusters=n_containers).fit_predict(vectors)

        # Convert numpy int32 to int so they are JSON serializable
        clusters = [int(cluster) for cluster in clusters]
        results = zip(filenames, clusters)

        return jsonify({"results": [{"filename": result[0], "cluster": result[1]} for result in results]})


if __name__ == "__main__":
    app.run(host=host, port=port, debug=True)
