"""
List of tuples, where:
    tuple[0]: image name
    tuple[1]: Detector's expected output after processing images specified by image_name.

"""

exp_val_detectron = [
    (
        "000000000139.jpg",
        [{'image_name': '000000000139.jpg', 'class': 0, 'rel_x1': 0.6386, 'rel_y1': 0.3704, 'rel_x2': 0.7272, 'rel_y2': 0.6959}, {'image_name': '000000000139.jpg', 'class': 56, 'rel_x1': 0.4585, 'rel_y1': 0.5197, 'rel_x2': 0.5492, 'rel_y2': 0.7404}, {'image_name': '000000000139.jpg', 'class': 62, 'rel_x1': 0.0095, 'rel_y1': 0.3893, 'rel_x2': 0.2427, 'rel_y2': 0.6275}, {'image_name': '000000000139.jpg', 'class': 56, 'rel_x1': 0.5738, 'rel_y1': 0.5102, 'rel_x2': 0.6872, 'rel_y2': 0.7449}, {'image_name': '000000000139.jpg', 'class': 74, 'rel_x1': 0.7018, 'rel_y1': 0.284, 'rel_x2': 0.7208, 'rel_y2': 0.3321}, {'image_name': '000000000139.jpg', 'class': 75, 'rel_x1': 0.3759, 'rel_y1': 0.4632, 'rel_x2': 0.3975, 'rel_y2': 0.4998}, {'image_name': '000000000139.jpg', 'class': 72, 'rel_x1': 0.7664, 'rel_y1': 0.4063, 'rel_x2': 0.802, 'rel_y2': 0.675}, {'image_name': '000000000139.jpg', 'class': 39, 'rel_x1': 0.8592, 'rel_y1': 0.7011, 'rel_x2': 0.918, 'rel_y2': 0.9399}, {'image_name': '000000000139.jpg', 'class': 72, 'rel_x1': 0.6932, 'rel_y1': 0.3936, 'rel_x2': 0.7997, 'rel_y2': 0.6836}, {'image_name': '000000000139.jpg', 'class': 62, 'rel_x1': 0.8709, 'rel_y1': 0.4912, 'rel_x2': 1.0, 'rel_y2': 0.6877}, {'image_name': '000000000139.jpg', 'class': 56, 'rel_x1': 0.63, 'rel_y1': 0.5134, 'rel_x2': 0.691, 'rel_y2': 0.7252}, {'image_name': '000000000139.jpg', 'class': 58, 'rel_x1': 0.3609, 'rel_y1': 0.4096, 'rel_x2': 0.4155, 'rel_y2': 0.5011}, {'image_name': '000000000139.jpg', 'class': 0, 'rel_x1': 0.5993, 'rel_y1': 0.4047, 'rel_x2': 0.6287, 'rel_y2': 0.4942}, {'image_name': '000000000139.jpg', 'class': 60, 'rel_x1': 0.7236, 'rel_y1': 0.8203, 'rel_x2': 0.9949, 'rel_y2': 0.9904}, {'image_name': '000000000139.jpg', 'class': 58, 'rel_x1': 0.522, 'rel_y1': 0.413, 'rel_x2': 0.5831, 'rel_y2': 0.5423}, {'image_name': '000000000139.jpg', 'class': 56, 'rel_x1': 0.4841, 'rel_y1': 0.5097, 'rel_x2': 0.532, 'rel_y2': 0.5431}, {'image_name': '000000000139.jpg', 'class': 75, 'rel_x1': 0.5484, 'rel_y1': 0.4758, 'rel_x2': 0.5645, 'rel_y2': 0.5125}, {'image_name': '000000000139.jpg', 'class': 75, 'rel_x1': 0.2613, 'rel_y1': 0.549, 'rel_x2': 0.2902, 'rel_y2': 0.6276}]  # noqa: E501
    ), (
        "000000002153.jpg",
        [{'image_name': '000000002153.jpg', 'class': 0, 'rel_x1': 0.4457, 'rel_y1': 0.581, 'rel_x2': 0.7296, 'rel_y2': 0.9363}, {'image_name': '000000002153.jpg', 'class': 0, 'rel_x1': 0.2713, 'rel_y1': 0.0033, 'rel_x2': 0.3766, 'rel_y2': 0.2486}, {'image_name': '000000002153.jpg', 'class': 0, 'rel_x1': 0.4345, 'rel_y1': 0.6326, 'rel_x2': 0.5836, 'rel_y2': 0.9218}, {'image_name': '000000002153.jpg', 'class': 34, 'rel_x1': 0.6055, 'rel_y1': 0.3817, 'rel_x2': 0.7186, 'rel_y2': 0.4808}, {'image_name': '000000002153.jpg', 'class': 0, 'rel_x1': 0.577, 'rel_y1': 0.4283, 'rel_x2': 0.6837, 'rel_y2': 0.7219}, {'image_name': '000000002153.jpg', 'class': 35, 'rel_x1': 0.4887, 'rel_y1': 0.6252, 'rel_x2': 0.5309, 'rel_y2': 0.6872}]  # noqa: E501
    ), (
        "000000003156.jpg",
        [{'image_name': '000000003156.jpg', 'class': 0, 'rel_x1': 0.0138, 'rel_y1': 0.0127, 'rel_x2': 0.9027, 'rel_y2': 1.0}, {'image_name': '000000003156.jpg', 'class': 61, 'rel_x1': 0.7637, 'rel_y1': 0.3876, 'rel_x2': 1.0, 'rel_y2': 0.8801}, {'image_name': '000000003156.jpg', 'class': 61, 'rel_x1': 0.5354, 'rel_y1': 0.5735, 'rel_x2': 0.9962, 'rel_y2': 0.9646}, {'image_name': '000000003156.jpg', 'class': 26, 'rel_x1': 0.1549, 'rel_y1': 0.8363, 'rel_x2': 0.3934, 'rel_y2': 0.9983}]  # noqa: E501
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
    ({'image_name': 'sample_image_1.jpg', 'class': 0, 'rel_x1': 0.6386, 'rel_y1': 0.3704, 'rel_x2': 0.7272, 'rel_y2': 0.6959}),
    ({'image_name': 'sample_image_1.jpg', 'class': 56, 'rel_x1': 0.4585, 'rel_y1': 0.5197, 'rel_x2': 0.5492, 'rel_y2': 0.7404}),
    ({'image_name': 'sample_image_2.jpg', 'class': 62, 'rel_x1': 0.0095, 'rel_y1': 0.3893, 'rel_x2': 0.2427, 'rel_y2': 0.6275}),
    ({'image_name': 'sample_image_3.jpg', 'class': 56, 'rel_x1': 0.5738, 'rel_y1': 0.5102, 'rel_x2': 0.6872, 'rel_y2': 0.7449})
]

exprected_unique_images = ['sample_image_2.jpg', 'sample_image_3.jpg', 'sample_image_1.jpg']

expected_objects_of_image_1 = [{'id': 1, 'type': '0', 'bbox_dims': {'x1': '0.6386', 'y1': '0.3704', 'x2': '0.7272', 'y2': '0.6959'}}, {'id': 2, 'type': '56', 'bbox_dims': {'x1': '0.4585', 'y1': '0.5197', 'x2': '0.5492', 'y2': '0.7404'}}]  # noqa: E501

expected_main_results = [{'filename': 'corrupted_image.jpg/item_19.jpg', 'cluster': 0}, {'filename': 'corrupted_image.jpg/item_20.jpg', 'cluster': 0}, {'filename': 'corrupted_image.jpg/item_21.jpg', 'cluster': 0}, {'filename': 'corrupted_image.jpg/item_22.jpg', 'cluster': 1}, {'filename': 'corrupted_image.jpg/item_23.jpg', 'cluster': 0}, {'filename': 'corrupted_image.jpg/item_24.jpg', 'cluster': 1}, {'filename': 'missing_image.jpg/item_25.jpg', 'cluster': 0}, {'filename': 'missing_image.jpg/item_26.jpg', 'cluster': 0}, {'filename': 'missing_image.jpg/item_27.jpg', 'cluster': 0}, {'filename': 'missing_image.jpg/item_28.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_1.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_10.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_11.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_12.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_13.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_14.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_15.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_16.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_17.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_18.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_2.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_3.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_4.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_5.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_6.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_7.jpg', 'cluster': 1}, {'filename': 'valid_image.jpg/item_8.jpg', 'cluster': 0}, {'filename': 'valid_image.jpg/item_9.jpg', 'cluster': 0}]  # noqa: E501