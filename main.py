import markdown
import flask, os, random
from flask_cors import cross_origin
from py3dbp import Packer, Bin, Item  # , Painter
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from utils import makeDictBox, makeDictItem, getBoxAndItem, Stats
from pygments.formatters import HtmlFormatter

# from models import TBox, TItem
from forms import BoxForm, ItemForm

app = Flask(__name__, template_folder="template", static_folder="static")
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

db = SQLAlchemy()

db.app = app
db.init_app(app)


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
    # type = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    loadbear = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    color = db.Column(db.Integer, nullable=False)


@app.before_request
def create_tables():
    # The following line will remove this handler, making it
    # only run on the first request
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()


@app.route("/")
def index2():
    boxes = TBox.query.all()
    items = TItem.query.all()
    return render_template("index2.html", boxes=boxes, items=items)


@app.route("/add_box", methods=["GET", "POST"])
def add_box():
    form = BoxForm()
    if form.validate_on_submit():
        box = TBox(
            name=form.name.data,
            whd=form.whd.data,
            weight=form.weight.data,
            openTop=form.openTop.data,
            coner=form.corner.data,
        )
        db.session.add(box)
        db.session.commit()
        flash(f"Box {form.name.data} added!", "success")
        return redirect(url_for("index2"))
    return render_template("box_form.html", form=form)


@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = TItem(
            name=form.name.data,
            whd=form.whd.data,
            count=form.count.data,
            updown=form.updown.data,
            # type=form.type.data,
            level=form.level.data,
            loadbear=form.loadbear.data,
            weight=form.weight.data,
            color=form.color.data,
        )
        db.session.add(item)
        db.session.commit()
        flash(f"Item {form.name.data} added!", "success")
        return redirect(url_for("index2"))
    return render_template("item_form.html", form=form)


@app.route("/edit_box/<int:box_id>", methods=["GET", "POST"])
def edit_box(box_id):
    form = BoxForm()
    box = TBox.query.get_or_404(box_id)
    if request.method == "GET":
        form.name.data = box.name
        form.whd.data = box.whd
        form.weight.data = box.weight
        form.openTop.data = box.openTop
        form.corner.data = box.coner
    if form.validate_on_submit():
        box.name = form.name.data
        box.whd = form.whd.data
        box.weight = form.weight.data
        box.openTop = form.openTop.data
        box.coner = form.corner.data
        db.session.commit()
        flash(f"Box {form.name.data} updated!", "success")
        return redirect(url_for("index2"))
    return render_template("box_form.html", form=form, edit=True)


@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    form = ItemForm()
    item = TItem.query.get_or_404(item_id)
    if request.method == "GET":
        form.name.data = item.name
        form.whd.data = item.whd
        form.count.data = item.count
        form.updown.data = item.updown
        # form.type.data = item.type
        form.level.data = item.level
        form.loadbear.data = item.loadbear
        form.weight.data = item.weight
        form.color.data = item.color
    if form.validate_on_submit():
        item.name = form.name.data
        item.whd = form.whd.data
        item.count = form.count.data
        item.updown = form.updown.data
        # item.type = form.type.data
        item.level = form.level.data
        item.loadbear = form.loadbear.data
        item.weight = form.weight.data
        item.color = form.color.data
        db.session.commit()
        flash(f"Item {form.name.data} updated!", "success")
        return redirect(url_for("index2"))
    return render_template("item_form.html", form=form, edit=True)


@app.route("/delete_box/<int:box_id>", methods=["POST"])
def delete_box(box_id):
    box = TBox.query.get_or_404(box_id)
    db.session.delete(box)
    db.session.commit()
    flash("Box deleted!", "success")
    return redirect(url_for("index2"))


@app.route("/delete_item/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    item = TItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted!", "success")
    return redirect(url_for("index2"))


@app.route("/reset_data", methods=["GET", "POST"])
def reset_data():
    data = {
        "box": [
            {
                "name": "40ft High Cube Container",
                "WHD": [1300, 255, 275],
                "weight": 26280,
                "openTop": [1, 2],
                "corner": 15,
            }
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
            },
            {
                "name": "Superlux_RS921",
                "WHD": [60, 80, 200],
                "count": 15,
                "updown": 1,
                "level": 0,
                "loadbear": 200,
                "weight": 30,
                "color": 3,
            },
            {
                "name": "Dell_R740",
                "WHD": [70, 100, 30],
                "count": 30,
                "updown": 1,
                "level": 0,
                "loadbear": 200,
                "weight": 20,
                "color": 4,
            },
            {
                "name": "Wood_Table",
                "WHD": [152, 152, 75],
                "count": 2,
                "updown": 1,
                "level": 0,
                "loadbear": 200,
                "weight": 70,
                "color": 7,
            },
        ],
        "binding": ["Wood_Table", "50_Gal_Oil_Drum"],
    }

    try:
        # Clear the existing data
        db.session.query(TBox).delete()
        db.session.query(TItem).delete()
        db.session.commit()
        print(data["box"])
        # Insert new box data
        for box_data in data["box"]:
            print(box_data)
            # Check if the box data is compatible
            if (
                "name" not in box_data
                or "WHD" not in box_data
                or "weight" not in box_data
                or "openTop" not in box_data
                or "corner" not in box_data
            ):
                continue

            box = TBox(
                name=box_data["name"],
                whd=str(box_data["WHD"]),
                weight=box_data["weight"],
                openTop=str(box_data["openTop"]),
                coner=box_data["corner"],
            )
            db.session.add(box)

        # Insert new item data
        for item_data in data["item"]:
            item = TItem(
                name=item_data["name"],
                whd=str(item_data["WHD"]),
                count=item_data["count"],
                updown=item_data["updown"],
                # type=item_data["type"],
                level=item_data["level"],
                loadbear=item_data["loadbear"],
                weight=item_data["weight"],
                color=item_data["color"],
            )
            db.session.add(item)

        db.session.commit()
        # return {"Success": True, "Message": "Data reset and inserted successfully"}
        return redirect(url_for("index2"))
    except Exception as e:
        db.session.rollback()
        return {"Success": False, "Message": str(e)}


@app.route("/delete_data", methods=["GET"])
def delete_data():
    try:
        db.session.query(TBox).delete()
        db.session.query(TItem).delete()
        db.session.commit()
        # return {"Success": True, "Message": "Deleting Data successfully"}
        return redirect(url_for("index2"))
    except Exception as e:
        db.session.rollback()
        return {"Success": False, "Message": str(e)}


@app.route("/insert_data", methods=["GET", "POST"])
def insert_data():
    res = {"Success": False}
    if flask.request.method == "POST":
        q = flask.request.get_json()
        data = q
        try:
            # Clear the existing data
            db.session.query(TBox).delete()
            db.session.query(TItem).delete()
            db.session.commit()

            # Insert new box data
            for box_data in data["box"]:
                # Check if the box data is compatible
                print(box_data)
                box = TBox(
                    name=box_data["name"],
                    whd=str(box_data["WHD"]),
                    weight=box_data["weight"],
                    openTop=str(box_data["openTop"]),
                    coner=box_data["corner"],
                )
                db.session.add(box)

            # Insert new item data
            for item_data in data["item"]:
                item = TItem(
                    name=item_data["name"],
                    whd=str(item_data["WHD"]),
                    count=item_data.get("count", 1) if item_data else 1,
                    # count=item_data["count"] or 1,
                    updown=item_data["updown"],
                    # type=item_data["type"],
                    level=item_data["level"],
                    loadbear=item_data["loadbear"],
                    weight=item_data["weight"],
                    color=item_data["color"],
                )
                db.session.add(item)

            db.session.commit()
            return {"Success": True, "Message": "Data reset and inserted successfully"}
            # return redirect(url_for("index2"))
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "Message": str(e)}
    else:
        return render_template("insert_data.html")


@app.route("/calPacking", methods=["GET", "POST"])
@cross_origin()
def mkResultAPI():
    res = {"Success": False}
    if flask.request.method == "GET":

        return render_template(
            "packing.html", boxes=TBox.query.all(), items=TItem.query.all()
        )
    else:
        try:
            packer, box, binding = getBoxAndItem(TBox, TItem)
            bigger_first = bool(request.form.get("bigger_first"))
            distribute_items = bool(request.form.get("distribute_items"))
            fix_point = bool(request.form.get("fix_point"))
            check_stable = bool(request.form.get("check_stable"))
            gap_on = bool(request.form.get("gap_on"))
            gap = request.form.get("slider_Gap")

            # Handle support_surface_ratio with default value if not provided
            support_surface_ratio_str = request.form.get("slider")
            print(support_surface_ratio_str)
            if support_surface_ratio_str:
                try:
                    support_surface_ratio = float(support_surface_ratio_str)
                except ValueError:
                    support_surface_ratio = 0.5
            else:
                support_surface_ratio = 0.5

            # Handle binding with default empty list if not provided
            # binding = request.form.getlist('binding') or []

            # Convert number_of_decimals, use default if not provided or invalid
            number_of_decimals_str = request.form.get("number_of_decimals")
            try:
                number_of_decimals = (
                    int(number_of_decimals_str) if number_of_decimals_str else 0
                )
            except ValueError:
                number_of_decimals = 0

        except Exception as e:
            res["Reason"] = "input data err " + (str(e) if e else "no error")
            return res

        try:
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
                # box = packer.bins[0]

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
                plot_filename = f"plot_{box.partno}.html"
                plot_filepath = os.path.join(base_dir, "static", plot_filename)

                # Ensure static directory exists
                if not os.path.exists(os.path.join(base_dir, "static")):
                    os.makedirs(os.path.join(base_dir, "static"))

                # Save plot to HTML
                fig.write_html(plot_filepath)

                plot_url_name = f"plot_url_{idx}"
                # Make response
                res["Success"] = True
                boxname = f"box_{idx+1}"
                sample.append(
                    {
                        boxname: box_r,
                        "fitItem": fitItem,
                        "unfitItem": unfitItem,
                        "stats": Stats(box),
                        plot_url_name: plot_filename,
                    }
                )

            res["data"] = sample
            # print(type(sample))
            return render_template("result.html", response=res)
        except Exception as e:
            res["Reason"] = "cal packing err " + str(e)
            return res


@app.route("/details")
def details():
    readme_file = open("README.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(),
        extensions=["fenced_code", "codehilite", "markdown.extensions.tables"],
    )

    return render_template("Sample.html", readme_html=md_template_string)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8005", debug=True)
