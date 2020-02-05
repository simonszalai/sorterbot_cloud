"""
A Flask application to expose the vectorizer functionality as a REST API endpoint.

"""


from flask import Flask, request
from dotenv import load_dotenv

from detectron import Detectron
from vectorizer.vectorizer import Vectorizer
from postgres import Postgres


# base_path = "/home/simon/dev/sorterbot/images"
base_path = "/Users/simonszalai/dev/sorterbot/images"

app = Flask(__name__)

load_dotenv()

postgres = Postgres()
detectron = Detectron(base_path=base_path, config_file="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
vectorizer = Vectorizer(base_path=base_path, model_name="resnet18", input_dimensions=(224, 224), batch_size=1)


@app.route("/process_image", methods=["POST"])
def process_image():
    # Retrieve query parameters from the request
    session_id = request.args.get("session_id")
    img_name = request.args.get("image_name")
    is_final = request.args.get("is_final")

    # Open postgres connection and create table for current session if it does not exist yet
    postgres.open()
    postgres.create_table(table_name=session_id)

    # Run detectron to get bounding boxes
    results = detectron.predict(img_name=img_name)

    # Insert bounding box locations to postgres
    postgres.insert_results(results)

    if is_final:
        # Get list of unique image names in current session
        unique_images = postgres.get_unique_images()

        # Get objects belonging to each unique image from postgres
        images_with_objects = []
        for image_name in unique_images:
            images_with_objects.append({
                "image_name": image_name,
                "objects": postgres.get_objects_of_image(image_name=image_name)
            })

        # Terminate postgres connection as it's no longer needed
        postgres.close()

        # Run vectorizer to assign each object to a cluster
        pairings = vectorizer.run(bucket_name=session_id, images=images_with_objects)
        print(pairings)

    return 'ok'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
