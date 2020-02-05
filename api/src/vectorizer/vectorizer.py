"""
Vectorizer module is intended to load files from disk and calculate feature vectors from them.
These feature vectors are used later for clustering. Vectorizer is built on PyTorch/Torchvision.
Any model from torchvision.models can be used for vectorization.

"""

import os
import time

import torch
import torchvision.models as vision_models
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from sklearn.cluster import KMeans

from preprocessor import PreProcessor


class ImageFolderWithPaths(datasets.ImageFolder):
    """
    Extends torchvision.datasets.ImageFolder to add image paths to the dataset.
    Implements an override for the __getitem__ method, which is called when the
    `dataloader` accesses an item from the `dataset`

    """

    def __getitem__(self, index):
        # Get what ImageFolder normally returns
        original_tuple = super().__getitem__(index)
        # Get image path
        path = self.imgs[index][0]
        # Make a new tuple that includes the original data plus the path
        tuple_with_path = original_tuple + (path,)

        return tuple_with_path


class Vectorizer:
    """
    This class initiates the chosen neural network, loads the specified images,
    and computes feature vectors from them. The computation is executed in batches
    to increase efficiency.

    Parameters
    ----------
    model_name : str
        Name of the neural network architecture to be used for vectorization.
        Has to be one of the available models of
        `torchvision.models <https://pytorch.org/docs/stable/torchvision/models.html>`_.
    input_dimensions : tuple
        Dimensions of the input tensor required by the network architecture.
        The processed images will be resized to these dimensions. Networks
        usually require square-shaped images.
    output_layer : str, optional
        The layer of interest's name in the neural net. The specified layer's outputs
        are the vectors, which will be copied from the network and returned as results.
        To get a model summary with names, simply print the model, like: ``print(model)``
    output_length : int, optional
        The length of the output vector.
    mean : dict, optional
        Dict with 2 keys: ``mean`` and ``std``. The corresponding values are both lists
        of 3 elements representing the 3 color channels of images. Specify here the
        means and standard deviations of the training set on which the used model was trained.
        Defaults to ImageNet stats.
    batch_size : int, optional
        Specifies how many images a batch should contain. Use a higher number, preferably a
        power of 2 for faster processing. Keep in mind that one batch has to fit in memory
        at once.
    num_workers : int, optional
        User by PyTorch's DataLoader to determine how many subprocesses to use for data
        loading. Use 0 to load everything on the main process, use a higher number for
        parallel loading.

    """

    def __init__(
            self,
            base_path,
            model_name,
            input_dimensions,
            output_layer="avgpool",
            output_length=512,
            stats=None,
            batch_size=1024,
            num_workers=4):

        # Assign mutable default value here to avoid unexpected behavior
        if stats is None:
            stats = {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]}

        # Store parameters
        self.base_path = base_path
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.output_length = output_length

        # Init PreProcessor
        self.preprocessor = PreProcessor(base_path=base_path)

        # Retrieve selected model
        model_factory = getattr(vision_models, model_name)

        # Load the pretrained model
        self.model = model_factory(pretrained=True)

        # Select the output layer
        self.layer = self.model._modules.get(output_layer)

        # Set model to evaluation mode
        self.model.eval()

        # Set up transforms based on the selected model
        self.data_transforms = transforms.Compose(
            [
                transforms.Resize(input_dimensions),
                transforms.ToTensor(),
                transforms.Normalize(mean=stats["mean"], std=stats["std"])
            ]
        )

    def run(self, bucket_name, images):
        # Create dataset for vectorization
        self.load_data(os.path.join(self.base_path, "cropped"))

        # Download and crop images around bounding boxes
        n_containers = self.preprocessor.run(bucket_name, images)

        # Run vectorizer
        filenames, vectors = self.compute_vectors()

        # Compute clusters
        clusters = KMeans(n_clusters=n_containers).fit_predict(vectors)

        # Convert numpy int32 to int so they are JSON serializable
        clusters = [int(cluster) for cluster in clusters]
        results = zip(filenames, clusters)

        return [{"filename": result[0], "cluster": result[1]} for result in results]

    def load_data(self, data_path):
        """
        Loads images from disk.

        This function first creates a dataset using ImageFolderWithPaths, which is an
        extension of PyTorch's `ImageFolder <https://pytorch.org/docs/stable/torchvision/datasets.html#imagefolder>`_,
        then it creates a dataloader.

        Parameters
        ----------
        data_path : str
            Specifies the location of the images to be loaded. Given the way ImageFolder works,
            the images has to be in another folder inside the specified folder. The name of that
            folder would be the label for training, but in case of inference, it's irrelevant.
        """

        self.dataset = ImageFolderWithPaths(data_path, self.data_transforms)
        self.dataloader = torch.utils.data.DataLoader(
            self.dataset, batch_size=self.batch_size, shuffle=False, num_workers=self.num_workers
        )

    def compute_vectors(self):
        """
        This function runs the inference on the loaded pictures using the previously selected model.

        Returns
        -------
        filenames : list
            List of filenames of cropped images. Also contains the name of the original image and corresponds
            to the location of the image in the 'cropped' folder.
        vectors : list
            List of resulting vectors.

        """

        # Loop through batches and accumulate results
        filenames = []
        vectors = []
        for inputs, labels, paths in self.dataloader:
            # Get filenames and object names from paths
            batch_filenames = [f"{self.dataset.classes[label]}/{os.path.basename(path)}" for label, path in zip(labels, paths)]

            # Start timer
            start_time = time.time()

            # Create zero-filled vectors to store results
            batch_vectors = torch.zeros((inputs.shape[0], self.output_length))

            # Define function to copy outputs of a layer
            def copy_data(model, input, output):
                batch_vectors.copy_(output.data.squeeze())

            # Register copy function to the specified layer
            hook = self.layer.register_forward_hook(copy_data)

            # Run inference
            self.model(inputs)

            hook.remove()

            # Print time spent
            time_total = time.time() - start_time
            time_per_img_in_ms = time_total * 1000 / inputs.shape[0]
            print(f"{len(inputs)} image vectorized @ {time_per_img_in_ms:.2f}ms / image ({time_total:.2f}s total)")

            # Append batch filenames to global filenames list
            filenames.append(*batch_filenames)

            # Append batch vectors to global vector list and convert tensors to lists
            vectors.append(*[batch_vector.numpy().tolist() for batch_vector in batch_vectors])

        return filenames, vectors
