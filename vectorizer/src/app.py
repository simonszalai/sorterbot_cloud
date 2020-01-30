from flask import Flask, request, jsonify

from vectorizer import Vectorizer


app = Flask(__name__)


@app.route("/vectorize", methods=["POST"])
def vectorize():
    if request.method == "POST":
        vectorizer = Vectorizer(model_name="resnet18", input_dimensions=(224, 224), batch_size=45)
        vectorizer.load_data('/home/simon/dev/sorterbot/images')
        results = vectorizer.start()

        return jsonify({"results": results})


if __name__ == "__main__":
    app.run(port=6000, debug=True)
