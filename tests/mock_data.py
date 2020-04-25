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
        [{'obj_id': 0, 'type': 1, 'bbox_dims': {'x1': 0, 'y1': 0, 'x2': 320, 'y2': 320}}, {'obj_id': 1, 'type': 1, 'bbox_dims': {'x1': 320, 'y1': 320, 'x2': 400, 'y2': 400}}],  # noqa: E501
        ("75eaf8c9b8b5b006bba492a3af45dbb1", "399a207c4548eabaab1cde0833503f2e")
    ), (
        "000000002153.jpg",
        [{'obj_id': 0, 'type': 1, 'bbox_dims': {'x1': 0, 'y1': 0, 'x2': 320, 'y2': 320}}, {'obj_id': 1, 'type': 1, 'bbox_dims': {'x1': 320, 'y1': 320, 'x2': 400, 'y2': 400}}],  # noqa: E501
        ("6412d0b2ecf702156ecf62a2df9e1114", "25543590b91115971816fd79b06492dd")
    ), (
        "000000003156.jpg",
        [{'obj_id': 0, 'type': 1, 'bbox_dims': {'x1': 0, 'y1': 0, 'x2': 320, 'y2': 320}}, {'obj_id': 1, 'type': 1, 'bbox_dims': {'x1': 320, 'y1': 320, 'x2': 400, 'y2': 400}}],  # noqa: E501
        ("560d639f5e777cac5a202a9f38244cbe", "5142a935e63638dab461742c48ac2a15")
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

expected_main_results = [{'image_id': 1250, 'obj_id': 25, 'cluster': 0}, {'image_id': 1450, 'obj_id': 36, 'cluster': 1}, {'image_id': 1450, 'obj_id': 37, 'cluster': 0}, {'image_id': 1450, 'obj_id': 38, 'cluster': 0}, {'image_id': 1450, 'obj_id': 39, 'cluster': 0}, {'image_id': 1750, 'obj_id': 12, 'cluster': 0}, {'image_id': 1750, 'obj_id': 15, 'cluster': 0}]  # noqa: E501

expected_stitched_md5 = "30683891f6ec175a822c584a60c16b62"
