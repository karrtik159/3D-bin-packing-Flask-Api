import flask,os,random
from flask_cors import cross_origin
from py3dbp import Packer, Bin, Item, Painter
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from forms import BoxForm, ItemForm

app = Flask(__name__,template_folder="template",static_folder="static")
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

def randColor(s):
    ''' '''
    random.seed(s)
    color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

    return color

@app.before_request
def create_tables():
    # The following line will remove this handler, making it
    # only run on the first request
    app.before_request_funcs[None].remove(create_tables)

    db.create_all()

class TBox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whd = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    openTop = db.Column(db.String(100), nullable=False)
    coner = db.Column(db.Integer, nullable=False)

class TItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whd = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    updown = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    loadbear = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    color = db.Column(db.Integer, nullable=False)

@app.route('/')
def index2():
    boxes = TBox.query.all()
    items = TItem.query.all()
    return render_template('index2.html', boxes=boxes, items=items)

@app.route('/add_box', methods=['GET', 'POST'])
def add_box():
    form = BoxForm()
    if form.validate_on_submit():
        box = TBox(
            name=form.name.data,
            whd=form.whd.data,
            weight=form.weight.data,
            openTop=form.openTop.data,
            coner=form.coner.data
        )
        db.session.add(box)
        db.session.commit()
        flash(f'Box {form.name.data} added!', 'success')
        return redirect(url_for('index2'))
    return render_template('box_form.html', form=form)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = TItem(
            name=form.name.data,
            whd=form.whd.data,
            count=form.count.data,
            updown=form.updown.data,
            type=form.type.data,
            level=form.level.data,
            loadbear=form.loadbear.data,
            weight=form.weight.data,
            color=form.color.data
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Item {form.name.data} added!', 'success')
        return redirect(url_for('index2'))
    return render_template('item_form.html', form=form)

@app.route('/edit_box/<int:box_id>', methods=['GET', 'POST'])
def edit_box(box_id):
    form = BoxForm()
    box = TBox.query.get_or_404(box_id)
    if request.method == 'GET':
        form.name.data = box.name
        form.whd.data = box.whd
        form.weight.data = box.weight
        form.openTop.data = box.openTop
        form.coner.data = box.coner
    if form.validate_on_submit():
        box.name = form.name.data
        box.whd = form.whd.data
        box.weight = form.weight.data
        box.openTop = form.openTop.data
        box.coner = form.coner.data
        db.session.commit()
        flash(f'Box {form.name.data} updated!', 'success')
        return redirect(url_for('index2'))
    return render_template('box_form.html', form=form, edit=True)

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    form = ItemForm()
    item = TItem.query.get_or_404(item_id)
    if request.method == 'GET':
        form.name.data = item.name
        form.whd.data = item.whd
        form.count.data = item.count
        form.updown.data = item.updown
        form.type.data = item.type
        form.level.data = item.level
        form.loadbear.data = item.loadbear
        form.weight.data = item.weight
        form.color.data = item.color
    if form.validate_on_submit():
        item.name = form.name.data
        item.whd = form.whd.data
        item.count = form.count.data
        item.updown = form.updown.data
        item.type = form.type.data
        item.level = form.level.data
        item.loadbear = form.loadbear.data
        item.weight = form.weight.data
        item.color = form.color.data
        db.session.commit()
        flash(f'Item {form.name.data} updated!', 'success')
        return redirect(url_for('index2'))
    return render_template('item_form.html', form=form, edit=True)

@app.route('/delete_box/<int:box_id>', methods=['POST'])
def delete_box(box_id):
    box = TBox.query.get_or_404(box_id)
    db.session.delete(box)
    db.session.commit()
    flash('Box deleted!', 'success')
    return redirect(url_for('index2'))

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = TItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted!', 'success')
    return redirect(url_for('index2'))

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
        "type": item.typeof,
        "color": item.color,
        "position": pos,
        "rotationType": item.rotation_type,
        "WHD": whd,
        "weight": int(item.weight)
    }
    return r

def getBoxAndItem():
    try:
        packer = Packer()

        # Fetch box data from the database
        box_data = TBox.query.first()
        if not box_data:
            raise ValueError("No box data found in the database.")
        
        # Parse the WHD and openTop fields correctly
        box_whd = list(map(int, box_data.whd.strip('[]').split(',')))
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
            item_whd = list(map(int, item.whd.strip('[]').split(',')))
            for j in range(item.count):
                packer.addItem(Item(
                    partno=item.name + '-{}'.format(str(j+1)),
                    name=item.name,
                    typeof='cylinder' if item.type == 2 else 'cube',
                    WHD=item_whd,
                    weight=item.weight,
                    level=1 if item.level == 1 else 2,
                    loadbear=item.loadbear,
                    updown=bool(item.updown),
                    color=randColor(item.color)
                ))

        # Fetch binding data (hardcoded here, replace with actual logic if needed)
        binding_data = ["Wood_Table", "50_Gal_Oil_Drum"]
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

@app.route('/reset_data', methods=['POST'])
def reset_data():
    data = {
        "box": [
            {
                "name": "40ft High Cube Container",
                "WHD": [1203, 235, 269],
                "weight": 26280,
                "openTop": [1, 2],
                "coner": 15
            }
        ],
        "item": [
            {
                "name": "Dyson_DC34_Animal",
                "WHD": [170, 82, 46],
                "count": 5,
                "updown": 1,
                "type": 1,
                "level": 0,
                "loadbear": 100,
                "weight": 85,
                "color": 1
            },
            {
                "name": "Panasonic_NA-V160GBS",
                "WHD": [85, 60, 60],
                "count": 18,
                "updown": 1,
                "type": 1,
                "level": 0,
                "loadbear": 100,
                "weight": 30,
                "color": 2
            },
            {
                "name": "Superlux_RS921",
                "WHD": [60, 80, 200],
                "count": 15,
                "updown": 1,
                "type": 1,
                "level": 0,
                "loadbear": 10,
                "weight": 30,
                "color": 3
            },
            {
                "name": "Dell_R740",
                "WHD": [70, 100, 30],
                "count": 30,
                "updown": 1,
                "type": 1,
                "level": 0,
                "loadbear": 100,
                "weight": 20,
                "color": 4
            },
            {
                "name": "50_Gal_Oil_Drum",
                "WHD": [80, 80, 120],
                "count": 20,
                "updown": 0,
                "type": 2,
                "level": 0,
                "loadbear": 50,
                "weight": 170,
                "color": 5
            },
            {
                "name": "Moving_Box",
                "WHD": [60, 40, 50],
                "count": 25,
                "updown": 1,
                "type": 1,
                "level": 0,
                "loadbear": 40,
                "weight": 30,
                "color": 6
            },
            {
                "name": "Wood_Table",
                "WHD": [152, 152, 75],
                "count": 2,
                "updown": 1,
                "type": 1,
                "level": 0,
                "loadbear": 50,
                "weight": 70,
                "color": 7
            }
        ],
        "binding": [
            "Wood_Table",
            "50_Gal_Oil_Drum"
        ]
    }
    
    try:
        # Clear the existing data
        db.session.query(TBox).delete()
        db.session.query(TItem).delete()
        db.session.commit()

        # Insert new box data
        box_data = data["box"][0]
        box = TBox(
            name=box_data["name"],
            whd=str(box_data["WHD"]),
            weight=box_data["weight"],
            openTop=str(box_data["openTop"]),
            coner=box_data["coner"]
        )
        db.session.add(box)

        # Insert new item data
        for item_data in data["item"]:
            item = TItem(
                name=item_data["name"],
                whd=str(item_data["WHD"]),
                count=item_data["count"],
                updown=item_data["updown"],
                type=item_data["type"],
                level=item_data["level"],
                loadbear=item_data["loadbear"],
                weight=item_data["weight"],
                color=item_data["color"]
            )
            db.session.add(item)

        db.session.commit()
        return {"Success": True, "Message": "Data reset and inserted successfully"}
    except Exception as e:
        db.session.rollback()
        return {"Success": False, "Message": str(e)}

@app.route("/calPacking", methods=["GET","POST"])
@cross_origin()
def mkResultAPI():
    res = {"Success": False}
    if flask.request.method == "GET":
        try:
            packer, box, binding = getBoxAndItem()
        except:
            res["Reason"] = "input data err"
            return res
        
        try:
            packer.pack(bigger_first=True, distribute_items=False, fix_point=True, binding=binding, number_of_decimals=0)
            box = packer.bins[0]
            
            # Make box dict
            box_r = makeDictBox(box)
            
            # Make item dict
            fitItem, unfitItem = [], []
            for item in box.items:
                fitItem.append(makeDictItem(item))
            
            for item in box.unfitted_items:
                unfitItem.append(makeDictItem(item))
            
            # Make response
            res["Success"] = True
            res["data"] = {
                "box": box_r,
                "fitItem": fitItem,
                "unfitItem": unfitItem
            }
            
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
    else:
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


if __name__ == '__main__':
    app.run(debug=True)
