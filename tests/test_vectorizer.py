import json
import numpy as np
from pathlib import Path

from vectorizer.vectorizer import Vectorizer


class TestVectorizer:
    @classmethod
    def setup_class(cls):
        cls.base_img_path = Path(__file__).parent.joinpath("test_images", "test_vectorizer")
        cls.vectorizer = Vectorizer(base_img_path=cls.base_img_path, model_name="resnet18", input_dimensions=(224, 224), batch_size=512)

    def test_vectorize(self):
        self.vectorizer.load_data(self.base_img_path)

        _, vectors = self.vectorizer.compute_vectors()

        vectors_path = Path(__file__).parent.joinpath("vectors.txt")
        with open(vectors_path, "r") as f:
            expected_vectors = json.load(f)

        abs_difference = np.absolute(np.array(vectors) - np.array(expected_vectors))

        assert (abs_difference < 0.0001).all()
