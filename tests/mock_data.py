"""
List of tuples, where:
    tuple[0]: image name
    tuple[1]: Detector's expected output after processing images specified by image_name.

"""

exp_val_detectron = [
    (
        "1200.jpg",
        [{'image_name': '1200.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 1182, 'y1': 240, 'x2': 1355, 'y2': 408}, {'image_name': '1200.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 545, 'y1': 358, 'x2': 767, 'y2': 502}, {'image_name': '1200.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 374, 'y1': 14, 'x2': 525, 'y2': 181}]  # noqa: E501
    ), (
        "1500.jpg",
        [{'image_name': '1500.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 715, 'y1': 68, 'x2': 865, 'y2': 275}, {'image_name': '1500.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 1321, 'y1': 480, 'x2': 1511, 'y2': 644}, {'image_name': '1500.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 1311, 'y1': 103, 'x2': 1451, 'y2': 271}, {'image_name': '1500.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 9, 'y1': 193, 'x2': 141, 'y2': 385}]  # noqa: E501
    ), (
        "1700.jpg",
        [{'image_name': '1700.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 86, 'y1': 13, 'x2': 324, 'y2': 177}, {'image_name': '1700.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 1282, 'y1': 152, 'x2': 1415, 'y2': 371}, {'image_name': '1700.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 577, 'y1': 75, 'x2': 699, 'y2': 268}, {'image_name': '1700.jpg', 'image_width': 1640, 'image_height': 1232, 'class': 0, 'x1': 0, 'y1': 320, 'x2': 219, 'y2': 548}]  # noqa: E501
    ),
]


"""
List of tuples, where:
    tuple[0]: image name
    tuple[1]: Dict containing id, type and bounding box dimensions as relative coorindates. Mocks outputs of Detectron. Bbox coordinates represent top left and bottom right quarters.  # noqa: E501
    tuple[2]: MD5 hashes of the top left and bottom right quarters of the original images, respectively. To be compared with the output of vectorizer.

"""

sample_preprocessor = [
    (
        "000000000139.jpg",
        [{'id': 0, 'type': 1, 'bbox_dims': {'x1': '0', 'y1': '0', 'x2': '0.5', 'y2': '0.5'}}, {'id': 1, 'type': 1, 'bbox_dims': {'x1': '0.5', 'y1': '0.5', 'x2': '1', 'y2': '1'}}, {'id': 2, 'type': 'container'}],  # noqa: E501
        ("6b9646dc57d44dfe50744bf880e26f9e", "42c756903069dc53b4aa90cece907519")
    ), (
        "000000002153.jpg",
        [{'id': 0, 'type': 1, 'bbox_dims': {'x1': '0', 'y1': '0', 'x2': '0.5', 'y2': '0.5'}}, {'id': 1, 'type': 1, 'bbox_dims': {'x1': '0.5', 'y1': '0.5', 'x2': '1', 'y2': '1'}}, {'id': 2, 'type': 'container'}],  # noqa: E501
        ("9849c0663f46b49bcc6be7323d665ca0", "9203e8ed212f6ac38e072202ae6b851d")
    ), (
        "000000003156.jpg",
        [{'id': 0, 'type': 1, 'bbox_dims': {'x1': '0', 'y1': '0', 'x2': '0.5', 'y2': '0.5'}}, {'id': 1, 'type': 1, 'bbox_dims': {'x1': '0.5', 'y1': '0.5', 'x2': '1', 'y2': '1'}}, {'id': 2, 'type': 'container'}],  # noqa: E501
        ("d9559fc17c3838287e13650e2bb1b417", "13c942eba8ecf32b6ddc8d3b9b5590fd")
    ),
]


"""
List of dict's containing the following keys: `image_name`, `class`, `rel_x1`, `rel_y1`, `rel_x2`, `rel_y2`.

"""

sample_data_for_postgres = [
    ({'image_name': 'sample_image_1.jpg', 'image_width': 640, 'image_height': 480, 'class': 0, 'x1': 1256, 'y1': 854, 'x2': 741, 'y2': 125}),
    ({'image_name': 'sample_image_2.jpg', 'image_width': 640, 'image_height': 480, 'class': 0, 'x1': 1452, 'y1': 698, 'x2': 874, 'y2': 198}),
    ({'image_name': 'sample_image_3.jpg', 'image_width': 640, 'image_height': 480, 'class': 1, 'x1': 1985, 'y1': 554, 'x2': 965, 'y2': 654}),
    ({'image_name': 'sample_image_2.jpg', 'image_width': 640, 'image_height': 480, 'class': 0, 'x1': 1425, 'y1': 421, 'x2': 854, 'y2': 426})
]

expected_unique_images = ['sample_image_2.jpg', 'sample_image_3.jpg', 'sample_image_1.jpg']

expected_objects_of_image_1 = [{'id': 1, 'class': 0, 'img_dims': (640, 480), 'bbox_dims': {'x1': 1256, 'y1': 854, 'x2': 741, 'y2': 125}}]  # noqa: E501

expected_main_results = [{'filename': 'corrupted_image.jpg/item_19.jpg', 'cluster': 0}, {'filename': 'corrupted_image.jpg/item_20.jpg', 'cluster': 0}, {'filename': 'corrupted_image.jpg/item_21.jpg', 'cluster': 0}, {'filename': 'corrupted_image.jpg/item_22.jpg', 'cluster': 1}, {'filename': 'corrupted_image.jpg/item_23.jpg', 'cluster': 0}, {'filename': 'corrupted_image.jpg/item_24.jpg', 'cluster': 1}, {'filename': 'missing_image.jpg/item_25.jpg', 'cluster': 0}, {'filename': 'missing_image.jpg/item_26.jpg', 'cluster': 0}, {'filename': 'missing_image.jpg/item_27.jpg', 'cluster': 0}, {'filename': 'missing_image.jpg/item_28.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_1.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_10.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_11.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_12.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_13.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_14.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_15.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_16.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_17.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_18.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_2.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_3.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_4.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_5.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_6.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_7.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_8.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_9.jpg', 'cluster': 0}]  # noqa: E501
