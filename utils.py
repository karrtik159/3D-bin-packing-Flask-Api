import random, os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from py3dbp import Packer, Bin, Item  # , Painter


def randColor(s):
    """ """
    random.seed(s)
    color = "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])

    return color


def makeDictPallet(pallet):
    """
    This function creates a dictionary for a pallet, including its ID, name, and the list of boxes it contains.
    """
    r = {
        "palletID": pallet.id,
        "palletName": pallet.name,
        # "boxes": boxes_data
    }
    return r


def makeDictBox(box):
    position = (int(box.width) / 2, int(box.height) / 2, int(box.depth) / 2)
    r = {
        "partNumber": box.partno,
        "position": position,
        "WHD": (int(box.width), int(box.height), int(box.depth)),
        "weight": int(box.max_weight),
        "gravity": box.gravity,
    }
    return [r]


def makeDictItem(item):
    if item.rotation_type == 0:
        pos = (
            int(item.position[0]) + int(item.width) // 2,
            int(item.position[1]) + int(item.height) // 2,
            int(item.position[2]) + int(item.depth) // 2,
        )
        whd = (int(item.width), int(item.height), int(item.depth))
    elif item.rotation_type == 1:
        pos = (
            int(item.position[0]) + int(item.height) // 2,
            int(item.position[1]) + int(item.width) // 2,
            int(item.position[2]) + int(item.depth) // 2,
        )
        whd = (int(item.height), int(item.width), int(item.depth))
    elif item.rotation_type == 2:
        pos = (
            int(item.position[0]) + int(item.height) // 2,
            int(item.position[1]) + int(item.depth) // 2,
            int(item.position[2]) + int(item.width) // 2,
        )
        whd = (int(item.height), int(item.depth), int(item.width))
    elif item.rotation_type == 3:
        pos = (
            int(item.position[0]) + int(item.depth) // 2,
            int(item.position[1]) + int(item.height) // 2,
            int(item.position[2]) + int(item.width) // 2,
        )
        whd = (int(item.depth), int(item.height), int(item.width))
    elif item.rotation_type == 4:
        pos = (
            int(item.position[0]) + int(item.depth) // 2,
            int(item.position[1]) + int(item.width) // 2,
            int(item.position[2]) + int(item.height) // 2,
        )
        whd = (int(item.depth), int(item.width), int(item.height))
    elif item.rotation_type == 5:
        pos = (
            int(item.position[0]) + int(item.width) // 2,
            int(item.position[1]) + int(item.depth) // 2,
            int(item.position[2]) + int(item.height) // 2,
        )
        whd = (int(item.width), int(item.depth), int(item.height))

    r = {
        "partNumber": item.partno,
        "name": item.name,
        # "type": item.typeof,
        "color": item.color,
        "position": pos,
        "rotationType": item.rotation_type,
        "WHD": whd,
        "weight": int(item.weight),
    }
    return r


def getBoxAndItem(selected_boxes, selected_items):
    try:
        packer = Packer()

        # Dictionary to map color codes to color names
        color_dict = {
            1: "red",
            2: "yellow",
            3: "blue",
            4: "green",
            5: "purple",
            6: "brown",
            7: "orange",
        }

        # Process each selected box
        for box_data in selected_boxes:
            # Parse the WHD and openTop fields
            whd_list = list(map(float, box_data.whd.strip("[]").split(",")))
            width, height, depth = whd_list
            openTop = int(box_data.openTop.strip("[]").split(",")[0])

            # Create a Bin object (which represents a box)
            box = Bin(
                partno=box_data.name,
                WHD=(width, height, depth),
                max_weight=box_data.weight,
                corner=box_data.corner,
                put_type=openTop,
            )

            # Add the Bin object to the packer
            packer.addBin(box)

        # Process each selected item
        for item_data in selected_items:
            item_whd = list(map(float, item_data.whd.strip("[]").split(",")))
            item_width, item_height, item_depth = item_whd

            # Add each item to the packer as many times as specified by the count
            for j in range(item_data.count):
                item = Item(
                    partno=item_data.name + f"-{j+1}",
                    name=item_data.name,
                    WHD=(item_width, item_height, item_depth),
                    weight=item_data.weight,
                    level=1 if item_data.level == 1 else 2,
                    loadbear=item_data.loadbear,
                    updown=bool(item_data.updown),
                    color=color_dict.get(
                        item_data.color, "gray"
                    ),  # Default to 'gray' if color not found
                )

                # Add the Item object to the packer
                packer.addItem(item)

        # Assuming binding data is optional or not used in this context
        binding = []

        return packer, box, binding

    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        raise
    except ValueError as e:
        print(f"Data error: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def Stats(box):
    results = []

    # for box in packer.bins:
    volume = box.width * box.height * box.depth
    volume_t = 0
    volume_f = 0
    unfitted_name = ""

    for item in box.items:
        volume_t += float(item.width) * float(item.height) * float(item.depth)

    for item in box.unfitted_items:
        volume_f += float(item.width) * float(item.height) * float(item.depth)
        unfitted_name += "{},".format(item.partno)

    try:
        box_stats = {
            "space_utilization": round(volume_t / float(volume) * 100, 2),
            "residual_volume": float(volume) - volume_t,
            "unfitted_items": unfitted_name.strip(","),
            "unfitted_volume": volume_f,
            "gravity_distribution": box.gravity,
        }
    except ZeroDivisionError:
        box_stats = {
            "space_utilization": 0,
            "residual_volume": 0,
            "unfitted_items": "",
            "unfitted_volume": 0,
            "gravity_distribution": box.gravity,
        }

    results.append(box_stats)

    return results
