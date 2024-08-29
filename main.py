import markdown
import flask, os, random, json
from flask_cors import cross_origin
import pandas as pd
from py3dbp import Packer, Bin, Item  # , Painter
from exp_py3dbp import (
    Packer as exp_packer,
    Bin as exp_bin,
    Item as exp_item,
)  # , Painter

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from utils import (
    makeDictPallet,
    makeDictBox,
    makeDictItem,
    getBoxAndItem,
    standard_getBoxAndItem,
    Stats,
)
from pygments.formatters import HtmlFormatter

# from models import TBox, TItem
from forms import BoxForm, ItemForm, PalletForm

app = Flask(__name__, template_folder="template", static_folder="static")
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Containers.db"

db = SQLAlchemy()

db.app = app
db.init_app(app)


class Pallet(db.Model):
    __tablename__ = "pallet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    containers = db.relationship(
        "TBox", backref="pallet", cascade="all, delete-orphan", lazy=True
    )
    items = db.relationship(
        "TItem", backref="pallet", cascade="all, delete-orphan", lazy=True
    )


class TBox(db.Model):
    __tablename__ = "t_box"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whd = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    openTop = db.Column(db.String(100), nullable=False)
    corner = db.Column(db.Integer, nullable=False)
    pallet_id = db.Column(db.Integer, db.ForeignKey("pallet.id"), nullable=False)


class TItem(db.Model):
    __tablename__ = "t_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whd = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    updown = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    loadbear = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    color = db.Column(db.Integer, nullable=False)
    pallet_id = db.Column(db.Integer, db.ForeignKey("pallet.id"), nullable=False)


@app.before_request
def create_tables():
    # The following line will remove this handler, making it
    # only run on the first request
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()


@app.route("/")
def index():
    # Fetch all pallets
    pallets = Pallet.query.all()
    selected_pallet = None

    pallet_id = request.args.get("pallet_id")
    if pallet_id:
        selected_pallet = Pallet.query.filter_by(id=pallet_id).first()

    return render_template(
        "index.html", pallets=pallets, selected_pallet=selected_pallet
    )


@app.route("/create_pallet", methods=["POST"])
def create_pallet():
    pallet_name = request.form.get("pallet_name")

    # Validate the form inputs
    if not pallet_name:
        flash("Pallet name is required", "danger")
        return redirect(url_for("manage_pallets"))  # Adjust to the correct route

    # Create a new Pallet object
    new_pallet = Pallet(name=pallet_name)

    try:
        # Add the new pallet to the database
        db.session.add(new_pallet)
        db.session.commit()
        flash("Pallet created successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating pallet: {str(e)}", "danger")

    return redirect(url_for("index"))  # Adjust to the correct route


@app.route("/delete_pallet/<int:pallet_id>", methods=["POST"])
def delete_pallet(pallet_id):
    pallet = Pallet.query.get_or_404(pallet_id)

    try:
        # Delete the pallet, which will also delete associated TBox and TItem records due to cascade
        db.session.delete(pallet)
        db.session.commit()
        flash(
            "Pallet and all associated boxes and items deleted successfully!", "success"
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting pallet: {str(e)}", "danger")

    return redirect(url_for("index"))


@app.route("/add_box", methods=["GET", "POST"])
def add_box():
    pallet_id = request.args.get("pallet_id")
    form = BoxForm()
    form.pallet_id.choices = [(p.id, p.name) for p in Pallet.query.all()]
    if pallet_id:
        form.pallet_id.default = (
            pallet_id  # Set default value to the pallet_id from the URL
        )
    form.process()
    if form.validate_on_submit():
        box = TBox(
            name=form.name.data,
            whd=form.whd.data,
            weight=form.weight.data,
            openTop=form.openTop.data,
            corner=form.corner.data,
            pallet_id=form.pallet_id.data,
        )
        try:
            db.session.add(box)
            db.session.commit()
            flash(f"Box {form.name.data} added successfully!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while adding the box: {str(e)}", "danger")

    # Flash field-specific errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{form[field].label.text}: {error}", "danger")

    return render_template("box_form.html", form=form)


@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    form = ItemForm()
    # Load the CSV once when the app starts
    form.pallet_id.choices = [(p.id, p.name) for p in Pallet.query.all()]
    df = pd.read_csv("./static/Book1.csv")
    if request.method == "GET":

        pallet_id = request.args.get("pallet_id")
        # Populate the pallet choices
        form.pallet_id.default = (
            pallet_id  # Set default value to the pallet_id from the URL
        )
        form.process()  # This processes the form and applies the default value
        # Sample a random row from the dataframe
        random_row = df.sample(1).iloc[0]
        form.name.data = random_row["Item Name"]
        form.whd.data = [
            random_row["Width (in)"],
            random_row["Height (in)"],
            random_row["Breadth (in)"],
        ]
        form.color.default = random_row["Color"]
        form.count.data = 1
        form.level.data = 1
        form.loadbear.data = 100
        form.weight.data = 1
    # return render_template("item_form.html", form=form)
    if form.validate_on_submit():
        try:
            item = TItem(
                name=form.name.data,
                whd=form.whd.data,
                count=form.count.data,
                updown=form.updown.data,
                level=form.level.data,
                loadbear=form.loadbear.data,
                weight=form.weight.data,
                color=form.color.data,
                pallet_id=form.pallet_id.data,
            )
            # Create a new item instance with the form data

            # Add the item to the database session
            db.session.add(item)

            # Commit the session to save the item to the database
            db.session.commit()
            flash(f"Item {form.name.data} added!", "success")
            return redirect(url_for("index", pallet_id=form.pallet_id.data))

        except Exception as e:
            # Rollback the session in case of an error
            db.session.rollback()
            flash(f"An error occurred while adding the item: {str(e)}", "danger")

    # If form validation failed, flash specific errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{form[field].label.text}: {error}", "danger")

    # Render the form, showing any errors that occurred
    return render_template("item_form.html", form=form)


@app.route("/edit_box/<int:box_id>", methods=["GET", "POST"])
def edit_box(box_id):
    box = TBox.query.get_or_404(box_id)
    form = BoxForm()

    # Populate the pallet choices
    form.pallet_id.choices = [(p.id, p.name) for p in Pallet.query.all()]

    if request.method == "GET":
        form.name.data = box.name
        form.whd.data = box.whd
        form.weight.data = box.weight
        form.openTop.data = box.openTop
        form.corner.data = box.corner
        form.pallet_id.data = box.pallet_id

    if form.validate_on_submit():
        try:
            box.name = form.name.data
            box.whd = form.whd.data
            box.weight = form.weight.data
            box.openTop = form.openTop.data
            box.corner = form.corner.data
            box.pallet_id = form.pallet_id.data
            db.session.commit()
            flash(f"Box {form.name.data} updated!", "success")
            return redirect(url_for("index", pallet_id=box.pallet_id))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the item: {str(e)}", "danger")

    # If form validation failed, flash specific errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{form[field].label.text}: {error}", "danger")

    return render_template("box_form.html", form=form, edit=True)


@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    item = TItem.query.get_or_404(item_id)
    form = ItemForm()

    # Populate the pallet choices
    form.pallet_id.choices = [(p.id, p.name) for p in Pallet.query.all()]

    if request.method == "GET":
        form.name.data = item.name
        form.whd.data = item.whd
        form.count.data = item.count
        form.updown.data = item.updown
        form.level.data = item.level
        form.loadbear.data = item.loadbear
        form.weight.data = item.weight
        form.color.data = item.color
        form.pallet_id.data = item.pallet_id

    if form.validate_on_submit():
        try:
            item.name = form.name.data
            item.whd = form.whd.data
            item.count = form.count.data
            item.updown = form.updown.data
            item.level = form.level.data
            item.loadbear = form.loadbear.data
            item.weight = form.weight.data
            item.color = form.color.data
            item.pallet_id = form.pallet_id.data

            db.session.commit()
            flash(f"Item {form.name.data} updated!", "success")
            return redirect(url_for("index", pallet_id=item.pallet_id))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the item: {str(e)}", "danger")

    # If form validation failed, flash specific errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{form[field].label.text}: {error}", "danger")

    return render_template("item_form.html", form=form, edit=True)


@app.route("/delete_box/<int:box_id>", methods=["POST"])
def delete_box(box_id):
    box = TBox.query.get_or_404(box_id)
    pallet_id = box.pallet_id
    db.session.delete(box)
    db.session.commit()
    flash("Box deleted!", "success")
    return redirect(url_for("index", pallet_id=pallet_id))


@app.route("/delete_item/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    item = TItem.query.get_or_404(item_id)
    pallet_id = item.pallet_id
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted!", "success")
    return redirect(url_for("index", pallet_id=pallet_id))


@app.route("/reset_data", methods=["GET", "POST"])
def reset_data():
    fetch_and_save_pallet_data()
    data = {
        "pallet": [
            {"name": "Container 1"},
            {"name": "Container 2"},
            {"name": "Container 3"},
            {"name": "Container 4"},
            {"name": "Container 5"},
            {"name": "Container 6"},
            {"name": "Container 7"},
            {"name": "Container 8"},
            {"name": "Container 9"},
            {"name": "Container 10"},
        ],
        "box": [
            {
                "name": "Pallet 1",
                "WHD": [1300, 255, 275],
                "weight": 26280,
                "openTop": [1, 2],
                "corner": 0,
                "pallet": "1",  # Link to Pallet 1
            },
            {
                "name": "Pallet 2",
                "WHD": [1300, 255, 275],
                "weight": 26280,
                "openTop": [1, 2],
                "corner": 0,
                "pallet": "1",  # Link to Pallet 1
            },
        ],
        "item": [
            {
                "name": "Dyson_DC34_Animal",
                "WHD": [170, 82, 46],
                "count": 5,
                "updown": 1,
                "level": 0,
                "loadbear": 200,
                "weight": 85,
                "color": 1,
                "pallet": "1",  # Link to Pallet 1
            },
            {
                "name": "Panasonic_NA-V160GBS",
                "WHD": [85, 60, 60],
                "count": 18,
                "updown": 1,
                "level": 0,
                "loadbear": 200,
                "weight": 30,
                "color": 2,
                "pallet": "1",  # Link to Pallet 2
            },
            # Add other items similarly with pallet references
        ],
    }

    try:
        # Clear the existing data
        db.session.query(TBox).delete()
        db.session.query(TItem).delete()
        db.session.query(Pallet).delete()
        db.session.commit()

        # Insert new pallet data
        pallets = {}
        for pallet_data in data["pallet"]:
            pallet = Pallet(name=pallet_data["name"])
            db.session.add(pallet)
            db.session.commit()
            pallets[pallet.name] = pallet.id  # Store the pallet ID for reference

        # Insert new box data linked to pallets
        for box_data in data["box"]:
            if (
                "name" not in box_data
                or "WHD" not in box_data
                or "weight" not in box_data
                or "openTop" not in box_data
                or "corner" not in box_data
                or "pallet" not in box_data
            ):
                continue

            pallet_id = pallets.get(box_data["pallet"])
            if pallet_id:
                box = TBox(
                    name=box_data["name"],
                    whd=str(box_data["WHD"]),
                    weight=box_data["weight"],
                    openTop=str(box_data["openTop"]),
                    corner=box_data["corner"],
                    pallet_id=pallet_id,
                )
                db.session.add(box)

        # Insert new item data linked to pallets
        for item_data in data["item"]:
            pallet_id = pallets.get(item_data["pallet"])
            if pallet_id:
                item = TItem(
                    name=item_data["name"],
                    whd=str(item_data["WHD"]),
                    count=item_data["count"],
                    updown=item_data["updown"],
                    level=item_data["level"],
                    loadbear=item_data["loadbear"],
                    weight=item_data["weight"],
                    color=item_data["color"],
                    pallet_id=pallet_id,
                )
                db.session.add(item)

        db.session.commit()
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        return {"Success": False, "Message": str(e)}


@app.route("/delete_data", methods=["GET"])
def delete_data():
    try:
        db.session.query(TBox).delete()
        db.session.query(TItem).delete()
        db.session.query(Pallet).delete()
        db.session.commit()
        flash("All data deleted successfully!", "success")
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        return {"Success": False, "Message": str(e)}


@app.route("/insert_data", methods=["GET", "POST"])
def insert_data():
    res = {"Success": False}
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return {"Success": False, "Message": "No data provided."}, 400

        try:
            # Validate the existence of pallet data
            pallet_data = data.get("pallet", [])
            if (
                not pallet_data
                or not isinstance(pallet_data, list)
                or not pallet_data[0]
            ):
                return {
                    "Success": False,
                    "Message": "Pallet data is missing or invalid.",
                }, 400

            pallet_data = pallet_data[0]
            pallet_id = pallet_data.get("id")

            if pallet_id:
                # Update existing pallet or create a new one if not found
                pallet = Pallet.query.get(pallet_id)
                if pallet:
                    pallet.name = pallet_data.get("name", pallet.name)
                else:
                    pallet = Pallet(name=pallet_data.get("name", "Default Pallet"))
                    db.session.add(pallet)
                    db.session.commit()  # Save to get the new pallet ID
                    pallet_data["id"] = pallet.id
            else:
                # Create a new pallet if ID is not provided
                pallet = Pallet(name=pallet_data.get("name", "Default Pallet"))
                db.session.add(pallet)
                db.session.commit()
                pallet_data["id"] = pallet.id

            # Clear existing boxes and items only if new data is provided
            if data.get("box"):
                TBox.query.filter_by(pallet_id=pallet.id).delete()

            if data.get("item"):
                TItem.query.filter_by(pallet_id=pallet.id).delete()

            db.session.commit()

            # Insert or update box data associated with the pallet
            for box_data in data.get("box", []):
                box = TBox(
                    name=box_data["name"],
                    whd=str(box_data["WHD"]),
                    weight=box_data["weight"],
                    openTop=int(box_data["openTop"]),
                    corner=box_data["corner"],
                    pallet_id=pallet.id,
                )
                db.session.add(box)

            # Insert or update item data associated with the pallet
            for item_data in data.get("item", []):
                item = TItem(
                    name=item_data["name"],
                    whd=str(item_data["WHD"]),
                    count=item_data.get("count", 1),
                    updown=item_data["updown"],
                    level=item_data["level"],
                    loadbear=item_data["loadbear"],
                    weight=item_data["weight"],
                    color=item_data["color"],
                    pallet_id=pallet.id,
                )
                db.session.add(item)

            db.session.commit()
            return {
                "Success": True,
                "Message": f"Data reset and inserted successfully in Pallet id: {pallet.id}",
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"Success": False, "Message": str(e)}, 500

    else:
        # Handling the GET request to load the sample files
        try:
            sample_files = [
                f for f in os.listdir("static/pallet_backups") if f.endswith(".json")
            ]
        except FileNotFoundError:
            sample_files = []
        return render_template("insert_data.html", sample_files=sample_files)


def parse_whd(whd_str):
    # Attempt to clean and convert the WHD string to a list of integers
    try:
        # Remove any unwanted characters like brackets and spaces
        whd_str = whd_str.replace("[", "").replace("]", "").replace(" ", "")
        return [float(dim) for dim in whd_str.split(",")]
    except ValueError:
        # If conversion fails, log an error and return a default value or empty list
        print(f"Error parsing WHD: {whd_str}")
        return []


def parse_int_field(field_str):
    # Attempt to clean and convert a string field to an integer
    try:
        # Remove any unwanted characters like brackets and spaces
        field_str = field_str.replace("[", "").replace("]", "").strip()
        return int(field_str) or float(field_str)
    except ValueError:
        # If conversion fails, log an error and return a default value, such as 0
        print(f"Error parsing integer field: {field_str}")
        return 0


# @app.route("/Backup", methods=["GET", "POST"])
def fetch_and_save_pallet_data():
    pallets = Pallet.query.all()
    backup_dir = "static/pallet_backups"

    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    for pallet in pallets:
        # Fetch all associated boxes and items
        boxes = TBox.query.filter_by(pallet_id=pallet.id).all()
        items = TItem.query.filter_by(pallet_id=pallet.id).all()

        # Convert data to match the required JSON structure
        pallet_data = {
            "pallet": [{"id": str(pallet.id), "name": str(pallet.name)}],
            "box": [
                {
                    "name": box.name,
                    # "WHD": [int(dim) for dim in box.whd.split(",")],
                    "WHD": parse_whd(box.whd),
                    "weight": box.weight,
                    "openTop": parse_int_field(box.openTop),
                    "corner": int(box.corner),
                    "pallet": str(pallet.id),
                }
                for box in boxes
            ],
            "item": [
                {
                    "name": item.name,
                    # "WHD": [int(dim) for dim in item.whd.split(",")],
                    "WHD": parse_whd(item.whd),
                    "count": item.count,
                    "updown": item.updown,
                    "level": item.level,
                    "loadbear": item.loadbear,
                    "weight": item.weight,
                    "color": item.color,
                    "pallet": str(pallet.id),
                }
                for item in items
            ],
        }

        # Save to JSON file
        file_name = f"Container_{pallet.id}.json"
        file_path = os.path.join(backup_dir, file_name)
        with open(file_path, "w") as json_file:
            json.dump(pallet_data, json_file, indent=4)

        # print(f"Backup for Pallet ID {pallet.id} saved to {file_path}")


@app.route("/calPacking", methods=["GET", "POST"])
@cross_origin()
def mkResultAPI():
    res = {"Success": False}

    if request.method == "GET":
        # Fetch all pallets, boxes, and items to display in the template
        return render_template(
            "packing.html",
            pallets=Pallet.query.all(),
            boxes=TBox.query.all(),
            items=TItem.query.all(),
        )

    else:
        try:
            # Get selected pallet_id from the form
            pallet_id = request.form.get("pallet_id")
            binding = request.form.getlist("binding")
            # print(binding)
            # Fetch only the boxes and items associated with the selected pallet
            if pallet_id:
                selected_pallet = Pallet.query.get(pallet_id)
                selected_boxes = TBox.query.filter_by(pallet_id=pallet_id).all()
                selected_items = TItem.query.filter_by(pallet_id=pallet_id).all()
            else:
                # If no pallet is selected, use all pallets, boxes, and items
                selected_pallet = None
                selected_boxes = TBox.query.all()
                selected_items = TItem.query.all()
            # print(selected_boxes,selected_items)
            # Initialize packer with selected boxes and items
            packer, box, binding = getBoxAndItem(
                selected_boxes, selected_items, binding
            )

            # print(binding)
            # Get form parameters
            bigger_first = bool(request.form.get("bigger_first"))
            distribute_items = bool(request.form.get("distribute_items"))
            fix_point = bool(request.form.get("fix_point"))
            check_stable = bool(request.form.get("check_stable"))
            gap_on = bool(request.form.get("gap_on"))
            gap = request.form.get("slider_Gap")
            use_greedy = False
            use_combinations = True

            support_surface_ratio_str = request.form.get("slider")
            support_surface_ratio = (
                float(support_surface_ratio_str)
                if support_surface_ratio_str
                else float(0.75)
            )

            number_of_decimals_str = request.form.get("number_of_decimals")
            number_of_decimals = (
                int(number_of_decimals_str) if number_of_decimals_str else 0
            )
            selected_boxes = TBox.query.filter_by(pallet_id=pallet_id).all()

            if len(selected_boxes) > 1:
                # Number of elements is greater than 1
                distribute_items = True
                use_combinations = True
                print("distribute_items = ", distribute_items)

        except Exception as e:
            res["Reason"] = "input data err " + (str(e) if e else "no error")
            return res

        # try:
        sample = []
        # Pack using the parameters from the form
        packer.pack(
            bigger_first=bigger_first,
            distribute_items=distribute_items,
            fix_point=fix_point,
            check_stable=check_stable,
            support_surface_ratio=support_surface_ratio,
            binding=binding,
            number_of_decimals=number_of_decimals,
            gap_on=gap_on,
            gap=gap,
            use_greedy=use_greedy,
            use_combinations=use_combinations,
        )
        for idx, box in enumerate(packer.bins):
            # Make box dict

            box_r = makeDictBox(box)

            # Make item dict
            fitItem, unfitItem = [], []
            for item in box.items:
                fitItem.append(makeDictItem(item))

            for item in box.unfitted_items:
                unfitItem.append(makeDictItem(item))

            # Initialize Plot
            fig = box._plot()

            # Define base directory and plot filename
            base_dir = os.path.dirname(os.path.abspath(__file__))
            plot_filename = f"{selected_pallet.name}_{idx+1}.html"
            plot_filepath = os.path.join(base_dir, "static", "assets", plot_filename)

            # Ensure static directory exists
            if not os.path.exists(os.path.join(base_dir, "static")):
                os.makedirs(os.path.join(base_dir, "static"))

            # Save plot to HTML
            fig.write_html(plot_filepath)

            plot_url_name = f"View Pallet {idx+1}"
            # Make response
            res["Success"] = True
            boxname = f"box_{idx+1}"
            sample.append(
                {
                    boxname: box_r,
                    "fitItem": fitItem,
                    "unfitItem": unfitItem,
                    "stats": Stats(box),
                    plot_url_name: "assets/" + plot_filename,
                }
            )

        # If a pallet was selected, store the pallet information with the box data
        if selected_pallet:
            pallets_data = []
            # boxes_data = [makeDictBox(box) for box in packer.bins]
            pallets_data.append(makeDictPallet(selected_pallet))
            res["pallets"] = pallets_data
        else:
            # If no specific pallet was selected, store information for all pallets
            pallets_data = []
            for pallet in Pallet.query.all():
                # boxes_data = [makeDictBox(box) for box in pallet.containers]
                pallets_data.append(makeDictPallet(pallet))
            res["pallets"] = pallets_data

        res["data"] = sample
        return render_template("result.html", response=res)
        # except ZeroDivisionError:
        #     res["Reason"] = "ZeroDivisionError"
        #     return res
        # except Exception as e:
        #     res["Reason"] = "cal packing err " + str(e)
        #     return res


@app.route("/standard/calPacking", methods=["GET", "POST"])
@cross_origin()
def Standalone_mkResultAPI():
    res = {"Success": False}

    if request.method == "GET":
        # Fetch all pallets, boxes, and items to display in the template
        return render_template(
            "standard_packing.html",
            pallets=Pallet.query.all(),
            boxes=TBox.query.all(),
            items=TItem.query.all(),
        )

    else:
        try:
            # Get selected pallet_id from the form
            pallet_id = request.form.get("pallet_id")
            binding = request.form.getlist("binding")
            # print(binding)

            # Fetch only the boxes and items associated with the selected pallet
            if pallet_id:
                selected_pallet = Pallet.query.get(pallet_id)
                selected_boxes = TBox.query.filter_by(pallet_id=pallet_id).all()
                selected_items = TItem.query.filter_by(pallet_id=pallet_id).all()
            else:
                # If no pallet is selected, use all pallets, boxes, and items
                selected_pallet = None
                selected_boxes = TBox.query.all()
                selected_items = TItem.query.all()
            # print(selected_boxes,selected_items)
            # Initialize packer with selected boxes and items
            packer, box, binding = standard_getBoxAndItem(
                selected_boxes, selected_items, binding
            )

            # Get form parameters
            bigger_first = bool(request.form.get("bigger_first"))
            distribute_items = bool(request.form.get("distribute_items"))
            fix_point = bool(request.form.get("fix_point"))
            check_stable = bool(request.form.get("check_stable"))
            gap_on = bool(request.form.get("gap_on"))
            gap = request.form.get("slider_Gap")

            support_surface_ratio_str = request.form.get("slider")
            support_surface_ratio = (
                float(support_surface_ratio_str)
                if support_surface_ratio_str
                else float(0.75)
            )

            number_of_decimals_str = request.form.get("number_of_decimals")
            number_of_decimals = (
                int(number_of_decimals_str) if number_of_decimals_str else 0
            )
            selected_boxes = TBox.query.filter_by(pallet_id=pallet_id).all()

            if len(selected_boxes) > 1:
                # Number of elements is greater than 1
                distribute_items = True
                print("distribute_items = ", distribute_items)

        except Exception as e:
            res["Reason"] = "input data err " + (str(e) if e else "no error")
            return res

        # try:
        sample = []

        # Pack using the parameters from the form
        packer.pack(
            bigger_first=bigger_first,
            distribute_items=distribute_items,
            fix_point=fix_point,
            check_stable=check_stable,
            support_surface_ratio=support_surface_ratio,
            binding=binding,
            number_of_decimals=number_of_decimals,
            gap_on=gap_on,
            gap=gap,
        )
        for idx, box in enumerate(packer.bins):
            # Make box dict

            box_r = makeDictBox(box)

            # Make item dict
            fitItem, unfitItem = [], []
            for item in box.items:
                fitItem.append(makeDictItem(item))

            for item in box.unfitted_items:
                unfitItem.append(makeDictItem(item))

            # Initialize Plot
            fig = box._plot()

            # Define base directory and plot filename
            base_dir = os.path.dirname(os.path.abspath(__file__))
            plot_filename = f"Standard_{selected_pallet.name}_{idx+1}.html"
            # plot_filename = f"stnadard_plot_{box.partno}.html"
            plot_filepath = os.path.join(base_dir, "static", "assets", plot_filename)

            # Ensure static directory exists
            if not os.path.exists(os.path.join(base_dir, "static")):
                os.makedirs(os.path.join(base_dir, "static"))

            # Save plot to HTML
            fig.write_html(plot_filepath)

            # plot_url_name = f"plot_url_{idx}"
            plot_url_name = f"View Pallet {idx+1}"
            # Make response
            res["Success"] = True
            boxname = f"box_{idx+1}"
            sample.append(
                {
                    boxname: box_r,
                    "fitItem": fitItem,
                    "unfitItem": unfitItem,
                    "stats": Stats(box),
                    plot_url_name: "assets/" + plot_filename,
                }
            )

        # If a pallet was selected, store the pallet information with the box data
        if selected_pallet:
            pallets_data = []
            # boxes_data = [makeDictBox(box) for box in packer.bins]
            pallets_data.append(makeDictPallet(selected_pallet))
            res["pallets"] = pallets_data
        else:
            # If no specific pallet was selected, store information for all pallets
            pallets_data = []
            for pallet in Pallet.query.all():
                # boxes_data = [makeDictBox(box) for box in pallet.containers]
                pallets_data.append(makeDictPallet(pallet))
            res["pallets"] = pallets_data

        res["data"] = sample
        return render_template("result.html", response=res)
        # except ZeroDivisionError:
        #     res["Reason"] = "ZeroDivisionError"
        #     return res
        # except Exception as e:
        #     res["Reason"] = "cal packing err " + str(e)
        #     return res


@app.route("/details")
def details():
    readme_file = open("README.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(),
        extensions=["fenced_code", "codehilite", "markdown.extensions.tables"],
    )

    return render_template("Sample.html", readme_html=md_template_string)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8000", debug=True)
