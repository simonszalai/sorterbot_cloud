import os
import sys
import json
import pytest
import numpy as np

sys.path.append(os.path.abspath('src'))
from vectorizer.vectorizer import Vectorizer  # noqa: E402


class TestVectorizer:
    @pytest.fixture(autouse=True, scope='function')
    def init(self):
        self.base_img_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../test_images/vectorizable"))
        self.vectorizer = Vectorizer(base_img_path=self.base_img_path, model_name="resnet18", input_dimensions=(224, 224), batch_size=512)

    def test_vectorize(self):
        self.vectorizer.load_data(self.base_img_path)

        _, vectors = self.vectorizer.compute_vectors()

        vectors_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../vectors.txt"))
        with open(vectors_path, "r") as f:
            expected_vectors = json.load(f)

        abs_difference = np.absolute(np.array(vectors) - np.array(expected_vectors))

        assert (abs_difference < 0.0001).all()
