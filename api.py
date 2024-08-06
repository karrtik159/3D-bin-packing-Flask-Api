
import flask, json, random,os
from py3dbp import Packer, Bin, Item, Painter
from flask_cors import cross_origin

# init flask
app = flask.Flask(__name__,template_folder="template")

# load data
with open('widadvance.json',encoding='utf-8') as f:
    alldata = json.load(f)

# a simple page that says hello
@app.route('/')
@cross_origin()
def hello():

    hello_world ='''
    Welcome to 3D BIN Packing API <br>
    <br>
    '''
    return hello_world


# get all item and box information
@app.route("/getAllData", methods=["POST", "GET"])
@cross_origin()
def get_all_item_and_box_api():
    """
    API endpoint to get all item and box information.

    This endpoint supports both POST and GET methods.

    Parameters:
        None

    Returns:
        On successful POST request, returns a JSON response with all item and box information.
        On unsuccessful GET request, returns a JSON response with a failure message.
    """

    # Check the request method
    if flask.request.method == "POST":
        # Mark the success flag in the response data
        alldata["Success"] = True
        # Return the response data as a JSON
        return flask.jsonify(alldata)
    else:
        # Return a failure message for unsuccessful GET request
        return {"Success": False, "Reason": "can't use GET"}


@app.route("/viewPacking", methods=["POST"])
@cross_origin()
def ViewPackingAPI():
    return flask.render_template("packing.html",context="")
# cal packing 
@app.route("/calPacking", methods=["POST"])
@cross_origin()
def mkResultAPI():
    '''
    '''
    res = {"Success": False}
    if flask.request.method == "POST":
        q= eval(flask.request.data.decode('utf-8'))
        if 'box' in q.keys() and 'item' in q.keys() and 'binding' in q.keys():
            try :
                packer,box,binding = getBoxAndItem(q)
            except :
                res["Reason"] = "input data err"
                return res
            try :
                # calculate packing
                packer.pack(bigger_first=True,distribute_items=False,fix_point=True,binding=binding,
                number_of_decimals=0)
                box = packer.bins[0]
                # make box dict
                box_r = makeDictBox(box)
                # make item dict
                fitItem,unfitItem = [],[]
                for item in box.items:
                    fitItem.append(makeDictItem(item))
                
                for item in box.unfitted_items:
                    unfitItem.append(makeDictItem(item))

                # for unfitem in box
                # make response
                res["Success"] = True
                res["data"] = {
                    "box" : box_r,
                    "fitItem" : fitItem,
                    "unfitItem": unfitItem
                }
                # print(len(res["data"]["unfitItem"]))
                # Initialize Painter
                painter = Painter(box)
                fig = painter.plotBoxAndItems(
                    title=box.partno,
                    alpha=0.2,
                    write_num=True,
                    fontsize=10
                )
                 # Define base directory and plot filename
                base_dir = os.path.dirname(os.path.abspath(__file__))
                plot_filename = f"plot_{box.partno}.html"
                plot_filepath = os.path.join(base_dir, "static", plot_filename)

                # Ensure static directory exists
                if not os.path.exists(os.path.join(base_dir, "static")):
                    os.makedirs(os.path.join(base_dir, "static"))

                # Save plot to HTML
                fig.write_html(plot_filepath)

                # Provide URL to the plot
                plot_url = flask.url_for('static', filename=plot_filename, _external=True)
                res["plot_url"] = plot_url


                return res
            except Exception as e:
                res['Reason'] = 'cal packing err'
                return res
        else :
            res['Reason'] = 'box or item not in input data'
            return res
    else :
        res['Reason'] = 'method not POST'
        return res


def makeDictBox(box):
    position = (int(box.width)/2,int(box.height)/2,int(box.depth)/2)
    r = {
            "partNumber" : box.partno,
            "position" : position,
            "WHD" : (int(box.width),int(box.height),int(box.depth)),
            "weight" : int(box.max_weight),
            "gravity" : box.gravity
        }
    return [r]


def makeDictItem(item):
    ''' '''

    if item.rotation_type == 0:
        pos = (int(item.position[0]) + int(item.width)//2,int(item.position[1])+ int(item.height)//2,int(item.position[2])+ int(item.depth)//2)
        whd = (int(item.width),int(item.height),int(item.depth))
    elif item.rotation_type == 1:
        pos = (int(item.position[0])+ int(item.height)//2,int(item.position[1]) + int(item.width)//2,int(item.position[2])+ int(item.depth)//2)
        whd = (int(item.height),int(item.width),int(item.depth))
    elif item.rotation_type == 2:
        pos = (int(item.position[0])+ int(item.height)//2,int(item.position[1])+ int(item.depth)//2,int(item.position[2]) + int(item.width)//2)
        whd = (int(item.height),int(item.depth),int(item.width))
    elif item.rotation_type == 3:
        pos = (int(item.position[0])+ int(item.depth)//2,int(item.position[1])+ int(item.height)//2,int(item.position[2]) + int(item.width)//2)
        whd = (int(item.depth),int(item.height),int(item.width))
    elif item.rotation_type == 4:
        pos = (int(item.position[0])+ int(item.depth)//2,int(item.position[1]) + int(item.width)//2,int(item.position[2])+ int(item.height)//2)
        whd = (int(item.depth),int(item.width),int(item.height))
    elif item.rotation_type == 5:
        pos = (int(item.position[0]) + int(item.width)//2,int(item.position[1])+ int(item.depth)//2,int(item.position[2])+ int(item.height)//2)
        whd = (int(item.width),int(item.depth),int(item.height))
    
    r = {
        "partNumber" : item.partno,
        "name" : item.name,
        "type" : item.typeof,
        "color" : item.color,
        "position" : pos,
        "rotationType" : item.rotation_type,
        "WHD" : whd,
        "weight" : int(item.weight)
    }

    return r


def getBoxAndItem(data):
    ''' '''
    # init packer
    packer = Packer()
    # get bin data
    box_data = data["box"][0]
    box = Bin(
        partno=box_data['name'],
        WHD=box_data['WHD'],
        max_weight=box_data['weight'],
        corner=box_data['coner'],
        put_type=box_data['openTop'][0]
        )
    packer.addBin(box)
    # get item data  TODO
    item_data = data["item"]
    color_dict = {
        1:'red',
        2:'yellow',
        3:'blue',
        4:'green',
        5:'purple',
        6:'brown',
        7:'orange'
    }
    for i in item_data :
        for j in range(i['count']) :
            packer.addItem(Item(
            partno = i['name']+'-{}'.format(str(j+1)),
            name = i['name'],
            typeof = 'cylinder' if i['type'] == 2 else 'cube',
            WHD = i['WHD'], 
            weight = i['weight'],
            level = 1 if i['level'] == 1 else 2,
            loadbear = i['loadbear'],
            updown = bool(i['updown']),
            color = randColor(i['color']))
        )
    binding_data = data['binding']
    binding = []
    if len(binding_data) != 0:
        for i in binding_data :
            binding.append(tuple(i))

    return packer,box,binding


def randColor(s):
    ''' '''
    random.seed(s)
    color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

    return color



if __name__ == "__main__":
    '''
    1. get all item
    2. return choose item
    3. return result
    '''

    # start the web server
    print("* Starting web service...")
    app.run(host = '0.0.0.0',port = 5555,debug=True)