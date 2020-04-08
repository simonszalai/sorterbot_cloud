import math
import numpy as np
from pathlib import Path

from utils.logger import logger


def object_to_polar(image_name, obj):
    # Define arm specific contants
    r = 1500
    degree_angle_range = 130
    pulse_width_angle_range = 2200 - 800
    pulse_width_dist_min = 1100
    pulse_width_dist_max = 2000

    # Retrieve image center's base rotation as pulse width
    img_base_angle = int(Path(image_name).stem)

    # Retrieve image dimensions
    half_w, half_h = obj["img_dims"][0] / 2, obj["img_dims"][1] / 2

    # Calculate bbox center points
    x = int((obj["bbox_dims"]["x1"] + obj["bbox_dims"]["x2"]) / 2)
    y = int((obj["bbox_dims"]["y1"] + obj["bbox_dims"]["y2"]) / 2)

    # Calculate intermediate values
    a = abs(half_w - x)  # Location's x distance from middle of the image
    b = half_h - y  # Location's y distance from middle of the image

    # Calculate target values as polar coordinates
    gamma_rad = math.atan(a / (b + r))
    gamma = math.degrees(gamma_rad)
    try:
        dist = a / math.sin(gamma_rad)
    except ZeroDivisionError:
        dist = b + r

    # Convert rotation coordinate to servo position
    delta_rot_pulse_width = pulse_width_angle_range * gamma / degree_angle_range
    if x > half_w:
        delta_rot_pulse_width *= -1  # Subtract delta_rot_pulse_width if x position is bigger than half_w
    servo_0_pos = img_base_angle + delta_rot_pulse_width

    # Convert distance target value to servo1 position
    pw_range = pulse_width_dist_max - pulse_width_dist_min
    r_at_bottom = r - half_h
    servo_1_pos = (pw_range * (dist - r_at_bottom) / obj["img_dims"][1]) + pulse_width_dist_min

    return {
        "img_base_angle": img_base_angle,
        "obj_id": obj["id"],
        "polar_coords": (servo_0_pos, servo_1_pos,),
        "bbox_dims": obj["bbox_dims"]
    }


def filter_duplicates(objects, threshold=150):
    def in_range(loc, loc_in, idx):
        return (loc[idx] - threshold) < loc_in[idx] and loc_in[idx] < (loc[idx] + threshold)

    # locations = [obj["polar_coords"] for obj in objects]

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
