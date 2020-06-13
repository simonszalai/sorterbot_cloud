"""
Functions to convert bounding box coordinates from relative to absolute.

"""

import math
import numpy as np
from pathlib import Path


def object_to_polar(arm_constants, image_name, obj):
    """
    Converts bounding box coordinates relative to the image frame to absolute polar coordinates, relative to the robotic arm.

    Parameters
    ----------
    arm_constants : dict
        Dictionary containing the arm's constants that are saved in the arm's config file and sent with the request.
    image_name : str
        Name of the image, which also corresponds to the robot arm's rotation, expressed in pulse width.
    obj : dict
        Dictionary contining the relative coordinates of the bounding box.

    Returns
    -------
    abs_coords : dict
        Dictionary contining the computed absolute coordinates, the rotation as pulse width, the object ID and the bounding box dimensions.

    """

    # Retrieve image center's base rotation (when the picture was taken) as pulse width from the filename
    img_base_angle = int(Path(image_name).stem)

    # Retrieve image dimensions
    half_w, half_h = obj["img_dims"][0] / 2, obj["img_dims"][1] / 2

    # Calculate bbox center points
    x = int((obj["bbox_dims"]["x1"] + obj["bbox_dims"]["x2"]) / 2)
    y = int((obj["bbox_dims"]["y1"] + obj["bbox_dims"]["y2"]) / 2)

    # Calculate intermediate values
    a = abs(half_w - x)  # Location's x distance from middle of the image
    b = half_h - y  # Location's y distance from middle of the image

    # Calculate target values as polar coordinates (gamma is target's deviance from image base angle)
    gamma_rad = math.atan(a / (b + arm_constants["arm_radius"]))
    gamma = math.degrees(gamma_rad)
    try:
        dist = a / math.sin(gamma_rad)
    except ZeroDivisionError:
        dist = b + arm_constants["arm_radius"]

    # Convert rotation coordinate to pulse width
    delta_rotation_as_pw = arm_constants["rotation_range_as_pw"] * gamma / arm_constants["rotation_range_as_deg"]
    if x > half_w:
        delta_rotation_as_pw *= -1  # Subtract delta_rotation_as_pw if x position is bigger than half_w
    servo_0_pos = img_base_angle + delta_rotation_as_pw

    # Convert distance target value to servo1 position
    dist_range_as_pw = arm_constants["dist_max_as_pw"] - arm_constants["dist_min_as_pw"]
    r_at_bottom = arm_constants["arm_radius"] - half_h
    servo_1_pos = (dist_range_as_pw * (dist - r_at_bottom) / obj["img_dims"][1]) + arm_constants["dist_min_as_pw"]

    return {
        "img_base_angle": img_base_angle,
        "obj_id": obj["id"],
        "polar_coords": (servo_0_pos, servo_1_pos,),
        "bbox_dims": obj["bbox_dims"]
    }


def filter_duplicates(objects, threshold=150):
    """
    Filters out the bounding boxes that belong to the same object, but showed up on a different image.

    Parameters
    ----------
    objects : list
        List of dicts, containing the absolute coordinates of the objects.
    threshold: int
        Distance within that objects are considered the same.

    Returns
    -------
    filtered_objs : list
        List of the absolute coordinates of the unique objects.

    """

    def in_range(loc, loc_in, idx):
        return (loc[idx] - threshold) < loc_in[idx] and loc_in[idx] < (loc[idx] + threshold)

    filtered_objs = []
    for obj in objects:
        loc = obj["polar_coords"]

        # Skip iteration if current location was already processed
        if loc is None:
            continue

        # Initialize current cluster with outer location
        locs_in_range = [loc]

        # Loop through on the location once for each element to check if they belong to the same object
        for obj_in in objects:
            loc_in = obj_in["polar_coords"]

            # Skip iteration if current location was already processed or is the same as the outer one
            if loc == loc_in or loc_in is None:
                continue

            # If both coordinates are within range
            if in_range(loc, loc_in, 0) and in_range(loc, loc_in, 1):
                # Add item to current cluster
                locs_in_range.append(loc_in)
                # Remove processed inner location from locations
                obj_in_idx = objects.index(obj_in)
                objects[obj_in_idx]["polar_coords"] = None

        # Remove processed outer location from locations
        obj_idx = objects.index(obj)
        objects[obj_idx]["polar_coords"] = None

        # Append cluster to results
        filtered_objs.append({
            "img_base_angle": obj["img_base_angle"],
            "obj_id": obj["obj_id"],
            "avg_polar_coords": tuple(np.average(np.array(locs_in_range), axis=0)),
            "bbox_dims": obj["bbox_dims"],
        })

    return filtered_objs
