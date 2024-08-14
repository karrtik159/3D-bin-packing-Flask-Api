import random, os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from py3dbp import Packer, Bin, Item#, Painter
def randColor(s):
    ''' '''
    random.seed(s)
    color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

    return color

def makeDictBox(box):
    position = (int(box.width)/2, int(box.height)/2, int(box.depth)/2)
    r = {
        "partNumber": box.partno,
        "position": position,
        "WHD": (int(box.width), int(box.height), int(box.depth)),
        "weight": int(box.max_weight),
        "gravity": box.gravity
    }
    return [r]

def makeDictItem(item):
    if item.rotation_type == 0:
        pos = (int(item.position[0]) + int(item.width)//2, int(item.position[1]) + int(item.height)//2, int(item.position[2]) + int(item.depth)//2)
        whd = (int(item.width), int(item.height), int(item.depth))
    elif item.rotation_type == 1:
        pos = (int(item.position[0]) + int(item.height)//2, int(item.position[1]) + int(item.width)//2, int(item.position[2]) + int(item.depth)//2)
        whd = (int(item.height), int(item.width), int(item.depth))
    elif item.rotation_type == 2:
        pos = (int(item.position[0]) + int(item.height)//2, int(item.position[1]) + int(item.depth)//2, int(item.position[2]) + int(item.width)//2)
        whd = (int(item.height), int(item.depth), int(item.width))
    elif item.rotation_type == 3:
        pos = (int(item.position[0]) + int(item.depth)//2, int(item.position[1]) + int(item.height)//2, int(item.position[2]) + int(item.width)//2)
        whd = (int(item.depth), int(item.height), int(item.width))
    elif item.rotation_type == 4:
        pos = (int(item.position[0]) + int(item.depth)//2, int(item.position[1]) + int(item.width)//2, int(item.position[2]) + int(item.height)//2)
        whd = (int(item.depth), int(item.width), int(item.height))
    elif item.rotation_type == 5:
        pos = (int(item.position[0]) + int(item.width)//2, int(item.position[1]) + int(item.depth)//2, int(item.position[2]) + int(item.height)//2)
        whd = (int(item.width), int(item.depth), int(item.height))
    
    r = {
        "partNumber": item.partno,
        "name": item.name,
        # "type": item.typeof,
        "color": item.color,
        "position": pos,
        "rotationType": item.rotation_type,
        "WHD": whd,
        "weight": int(item.weight)
    }
    return r

def getBoxAndItem(TBox, TItem):
    try:
        packer = Packer()

        # Fetch box data from the database
        boxes = TBox.query.all()
        if not boxes:
            raise ValueError("No box data found in the database.")
        for box_data in boxes:
            # Parse the WHD and openTop fields correctly
            box_whd = list(map(float, box_data.whd.strip('[]').split(',')))
            box_openTop = list(map(int, box_data.openTop.strip('[]').split(',')))
            
            box = Bin(
                partno=box_data.name,
                WHD=box_whd,
                max_weight=box_data.weight,
                corner=box_data.coner,
                put_type=box_openTop[0]
            )
            packer.addBin(box)

            # Fetch item data from the database
            item_data = TItem.query.all()
            if not item_data:
                raise ValueError("No item data found in the database.")

            color_dict = {
                1: 'red',
                2: 'yellow',
                3: 'blue',
                4: 'green',
                5: 'purple',
                6: 'brown',
                7: 'orange'
            }

            for item in item_data:
                item_whd = list(map(float, item.whd.strip('[]').split(',')))
                for j in range(item.count):
                    packer.addItem(Item(
                        partno=item.name + '-{}'.format(str(j+1)),
                        name=item.name,
                        # typeof='cylinder' if item.type == 2 else 'cube',
                        WHD=item_whd,
                        weight=item.weight,
                        level=1 if item.level == 1 else 2,
                        loadbear=item.loadbear,
                        updown=bool(item.updown),
                        color=randColor(item.color)
                    ))

            # Fetch binding data (hardcoded here, replace with actual logic if needed)
            # binding_data = ["Wood_Table", "50_Gal_Oil_Drum"]
            binding_data=[]
            binding = []
            if binding_data:
                for i in binding_data:
                    binding.append(tuple(i))
        
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
    unfitted_name = ''

    for item in box.items:
        volume_t += float(item.width) * float(item.height) * float(item.depth)

    for item in box.unfitted_items:
        volume_f += float(item.width) * float(item.height) * float(item.depth)
        unfitted_name += '{},'.format(item.partno)

    box_stats = {
        'space_utilization': round(volume_t / float(volume) * 100, 2),
        'residual_volume': float(volume) - volume_t,
        'unfitted_items': unfitted_name.strip(','),
        'unfitted_volume': volume_f,
        'gravity_distribution': box.gravity
    }

    results.append(box_stats)

    return results
