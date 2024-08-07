from flask_cors import cross_origin
from flask import render_template, request, redirect, url_for, flash

# from . import db
from .forms import BoxForm, ItemForm
from .utils import *


# Ensure that routes are registered only after the app is created
# from . import create_app

# app = create_app()
from flask import Blueprint
example = Blueprint('example', __name__)

@example.route('/')
def index2():
    # boxes = TBox.query.all()
    # items = TItem.query.all()
    # return render_template('index2.html', boxes=boxes, items=items)
    return render_template('index2.html')

# @app.route('/add_box', methods=['GET', 'POST'])
# def add_box():
#     form = BoxForm()
#     if form.validate_on_submit():
#         box = TBox(
#             name=form.name.data,
#             whd=form.whd.data,
#             weight=form.weight.data,
#             openTop=form.openTop.data,
#             coner=form.coner.data
#         )
#         db.session.add(box)
#         db.session.commit()
#         flash(f'Box {form.name.data} added!', 'success')
#         return redirect(url_for('index2'))
#     return render_template('box_form.html', form=form)

# @app.route('/add_item', methods=['GET', 'POST'])
# def add_item():
#     form = ItemForm()
#     if form.validate_on_submit():
#         item = TItem(
#             name=form.name.data,
#             whd=form.whd.data,
#             count=form.count.data,
#             updown=form.updown.data,
#             type=form.type.data,
#             level=form.level.data,
#             loadbear=form.loadbear.data,
#             weight=form.weight.data,
#             color=form.color.data
#         )
#         db.session.add(item)
#         db.session.commit()
#         flash(f'Item {form.name.data} added!', 'success')
#         return redirect(url_for('index2'))
#     return render_template('item_form.html', form=form)

# @app.route('/edit_box/<int:box_id>', methods=['GET', 'POST'])
# def edit_box(box_id):
#     form = BoxForm()
#     box = TBox.query.get_or_404(box_id)
#     if request.method == 'GET':
#         form.name.data = box.name
#         form.whd.data = box.whd
#         form.weight.data = box.weight
#         form.openTop.data = box.openTop
#         form.coner.data = box.coner
#     if form.validate_on_submit():
#         box.name = form.name.data
#         box.whd = form.whd.data
#         box.weight = form.weight.data
#         box.openTop = form.openTop.data
#         box.coner = form.coner.data
#         db.session.commit()
#         flash(f'Box {form.name.data} updated!', 'success')
#         return redirect(url_for('index2'))
#     return render_template('box_form.html', form=form, edit=True)

# @app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
# def edit_item(item_id):
#     form = ItemForm()
#     item = TItem.query.get_or_404(item_id)
#     if request.method == 'GET':
#         form.name.data = item.name
#         form.whd.data = item.whd
#         form.count.data = item.count
#         form.updown.data = item.updown
#         form.type.data = item.type
#         form.level.data = item.level
#         form.loadbear.data = item.loadbear
#         form.weight.data = item.weight
#         form.color.data = item.color
#     if form.validate_on_submit():
#         item.name = form.name.data
#         item.whd = form.whd.data
#         item.count = form.count.data
#         item.updown = form.updown.data
#         item.type = form.type.data
#         item.level = form.level.data
#         item.loadbear = form.loadbear.data
#         item.weight = form.weight.data
#         item.color = form.color.data
#         db.session.commit()
#         flash(f'Item {form.name.data} updated!', 'success')
#         return redirect(url_for('index2'))
#     return render_template('item_form.html', form=form, edit=True)

# @app.route('/delete_box/<int:box_id>', methods=['POST'])
# def delete_box(box_id):
#     box = TBox.query.get_or_404(box_id)
#     db.session.delete(box)
#     db.session.commit()
#     flash('Box deleted!', 'success')
#     return redirect(url_for('index2'))

# @app.route('/delete_item/<int:item_id>', methods=['POST'])
# def delete_item(item_id):
#     item = TItem.query.get_or_404(item_id)
#     db.session.delete(item)
#     db.session.commit()
#     flash('Item deleted!', 'success')
#     return redirect(url_for('index2'))


# @app.route('/reset_data', methods=['POST'])
# def reset_data():
#     data = {
#         "box": [
#             {
#                 "name": "40ft High Cube Container",
#                 "WHD": [1203, 235, 269],
#                 "weight": 26280,
#                 "openTop": [1, 2],
#                 "coner": 15
#             }
#         ],
#         "item": [
#             {
#                 "name": "Dyson_DC34_Animal",
#                 "WHD": [170, 82, 46],
#                 "count": 5,
#                 "updown": 1,
#                 "type": 1,
#                 "level": 0,
#                 "loadbear": 100,
#                 "weight": 85,
#                 "color": 1
#             },
#             {
#                 "name": "Panasonic_NA-V160GBS",
#                 "WHD": [85, 60, 60],
#                 "count": 18,
#                 "updown": 1,
#                 "type": 1,
#                 "level": 0,
#                 "loadbear": 100,
#                 "weight": 30,
#                 "color": 2
#             },
#             {
#                 "name": "Superlux_RS921",
#                 "WHD": [60, 80, 200],
#                 "count": 15,
#                 "updown": 1,
#                 "type": 1,
#                 "level": 0,
#                 "loadbear": 10,
#                 "weight": 30,
#                 "color": 3
#             },
#             {
#                 "name": "Dell_R740",
#                 "WHD": [70, 100, 30],
#                 "count": 30,
#                 "updown": 1,
#                 "type": 1,
#                 "level": 0,
#                 "loadbear": 100,
#                 "weight": 20,
#                 "color": 4
#             },
#             {
#                 "name": "50_Gal_Oil_Drum",
#                 "WHD": [80, 80, 120],
#                 "count": 20,
#                 "updown": 0,
#                 "type": 2,
#                 "level": 0,
#                 "loadbear": 50,
#                 "weight": 170,
#                 "color": 5
#             },
#             {
#                 "name": "Moving_Box",
#                 "WHD": [60, 40, 50],
#                 "count": 25,
#                 "updown": 1,
#                 "type": 1,
#                 "level": 0,
#                 "loadbear": 40,
#                 "weight": 30,
#                 "color": 6
#             },
#             {
#                 "name": "Wood_Table",
#                 "WHD": [152, 152, 75],
#                 "count": 2,
#                 "updown": 1,
#                 "type": 1,
#                 "level": 0,
#                 "loadbear": 50,
#                 "weight": 70,
#                 "color": 7
#             }
#         ],
#         "binding": [
#             "Wood_Table",
#             "50_Gal_Oil_Drum"
#         ]
#     }
    
#     try:
#         # Clear the existing data
#         db.session.query(TBox).delete()
#         db.session.query(TItem).delete()
#         db.session.commit()

#         # Insert new box data
#         for box_data in data["box"]:
#             # Check if the box data is compatible
#             if "name" not in box_data or "WHD" not in box_data or "weight" not in box_data or "openTop" not in box_data or "coner" not in box_data:
#                 continue

#             box = TBox(
#                 name=box_data["name"],
#                 whd=str(box_data["WHD"]),
#                 weight=box_data["weight"],
#                 openTop=str(box_data["openTop"]),
#                 coner=box_data["coner"]
#             )
#             db.session.add(box)
#         box_data = data["box"][0]
#         box = TBox(
#             name=box_data["name"],
#             whd=str(box_data["WHD"]),
#             weight=box_data["weight"],
#             openTop=str(box_data["openTop"]),
#             coner=box_data["coner"]
#         )
#         db.session.add(box)

#         # Insert new item data
#         for item_data in data["item"]:
#             item = TItem(
#                 name=item_data["name"],
#                 whd=str(item_data["WHD"]),
#                 count=item_data["count"],
#                 updown=item_data["updown"],
#                 type=item_data["type"],
#                 level=item_data["level"],
#                 loadbear=item_data["loadbear"],
#                 weight=item_data["weight"],
#                 color=item_data["color"]
#             )
#             db.session.add(item)

#         db.session.commit()
#         return {"Success": True, "Message": "Data reset and inserted successfully"}
#     except Exception as e:
#         db.session.rollback()
#         return {"Success": False, "Message": str(e)}

# @app.route('/insert_data', methods=["GET","POST"])
# def insert_data():
#     res = {"Success": False}
#     if request.method == "POST":
#         q= request.get_json()
#         data = q
#         try:
#             # Clear the existing data
#             db.session.query(TBox).delete()
#             db.session.query(TItem).delete()
#             db.session.commit()

#             # Insert new box data
#             for box_data in data["box"]:
#                 # Check if the box data is compatible
#                 print(box_data)
#                 box = TBox(
#                     name=box_data["name"],
#                     whd=str(box_data["WHD"]),
#                     weight=box_data["weight"],
#                     openTop=str(box_data["openTop"]),
#                     coner=box_data["coner"]
#                 )
#                 db.session.add(box)
            
#             # Insert new item data
#             for item_data in data["item"]:
#                 item = TItem(
#                     name=item_data["name"],
#                     whd=str(item_data["WHD"]),
#                     count=item_data.get("count", 1) if item_data else 1,
#                     # count=item_data["count"] or 1,
#                     updown=item_data["updown"],
#                     type=item_data["type"],
#                     level=item_data["level"],
#                     loadbear=item_data["loadbear"],
#                     weight=item_data["weight"],
#                     color=item_data["color"],
                    
#                 )
#                 db.session.add(item)

#             db.session.commit()
#             return {"Success": True, "Message": "Data reset and inserted successfully"}
#         except Exception as e:
#             db.session.rollback()
#             return {"Success": False, "Message": str(e)}
#     else:
#         return render_template('insert_data.html')

@app.route("/calPacking", methods=["GET","POST"])
@cross_origin()
def mkResultAPI():
    res = {"Success": False}
    if  request.method == "GET":
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
            plot_url =  url_for('static', filename=plot_filename, _external=True)
            res["plot_url"] = plot_url
            
            return res
        except Exception as e:
            res['Reason'] = 'cal packing err'
            return res
    else:
        q= eval( request.data.decode('utf-8'))
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
                plot_url =  url_for('static', filename=plot_filename, _external=True)
                res["plot_url"] = plot_url


                return res
            except Exception as e:
                res['Reason'] = 'cal packing err'
                return res
        else :
            res['Reason'] = 'box or item not in input data'
            return res
