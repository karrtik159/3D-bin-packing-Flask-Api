from flask import Flask, request, jsonify,render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="template", static_folder="static")
app.config["SECRET_KEY"] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'  # Change to your preferred database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.app = app
db.init_app(app)

class Pallet(db.Model):
    __tablename__ = 'pallet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    containers = db.relationship('TBox', backref='pallet', lazy=True)
    items = db.relationship('TItem', backref='pallet', lazy=True)

class TBox(db.Model):
    __tablename__ = 't_box'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whd = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    openTop = db.Column(db.String(100), nullable=False)
    corner = db.Column(db.Integer, nullable=False)
    pallet_id = db.Column(db.Integer, db.ForeignKey('pallet.id'), nullable=False)

class TItem(db.Model):
    __tablename__ = 't_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whd = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    updown = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    loadbear = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    color = db.Column(db.Integer, nullable=False)
    pallet_id = db.Column(db.Integer, db.ForeignKey('pallet.id'), nullable=False)

# Function to create tables
@app.before_request
def create_tables():
    db.create_all()

@app.route('/add_sample_data', methods=['GET'])
def add_sample_data():
    pallet1 = Pallet(name="Pallet 1")
    pallet2 = Pallet(name="Pallet 2")
    db.session.add(pallet1)
    db.session.add(pallet2)
    db.session.commit()

    tbox1 = TBox(name="Box 1", whd="10x10x10", weight=100, openTop="No", corner=4, pallet_id=pallet1.id)
    tbox2 = TBox(name="Box 2", whd="20x20x20", weight=200, openTop="Yes", corner=4, pallet_id=pallet1.id)
    tbox3 = TBox(name="Box 3", whd="15x15x15", weight=150, openTop="No", corner=8, pallet_id=pallet2.id)
    db.session.add(tbox1)
    db.session.add(tbox2)
    db.session.add(tbox3)
    db.session.commit()

    titem1 = TItem(name="Item 1", whd="5x5x5", count=10, updown=1, level=2, loadbear=50, weight=10, color=1, pallet_id=pallet1.id)
    titem2 = TItem(name="Item 2", whd="3x3x3", count=20, updown=2, level=1, loadbear=30, weight=5, color=2, pallet_id=pallet1.id)
    titem3 = TItem(name="Item 3", whd="8x8x8", count=15, updown=1, level=3, loadbear=40, weight=8, color=3, pallet_id=pallet2.id)
    db.session.add(titem1)
    db.session.add(titem2)
    db.session.add(titem3)
    db.session.commit()

    return jsonify({'message': 'Sample data added successfully!'}), 201

  
@app.route('/get_pallets', methods=['GET'])
def get_pallets():
    pallets = Pallet.query.all()
    return jsonify([{'id': t.id, 'name': t.name} for t in pallets])

@app.route('/pallet/<int:id>', methods=['GET'])
def get_pallet(id):
    pallet = Pallet.query.get_or_404(id)
    return jsonify({'id': pallet.id, 'name': pallet.name})

@app.route('/pallet', methods=['POST'])
def create_pallet():
    data = request.json
    new_pallet = Pallet(name=data['name'])
    db.session.add(new_pallet)
    db.session.commit()
    return jsonify({'id': new_pallet.id, 'name': new_pallet.name}), 201

@app.route('/update_pallet', methods=['POST'])
def update_pallet_from_form():
    pallet_id = request.form['updatePalletId']
    name = request.form['updatePalletName']
    
    pallet = Pallet.query.get_or_404(pallet_id)
    pallet.name = name
    db.session.commit()
    return redirect(url_for('manage_pallets'))

@app.route('/delete_pallet/<int:id>', methods=['POST'])
def delete_pallet_from_form(id):
    pallet = Pallet.query.get_or_404(id)
    
    # Delete all associated boxes and items
    TBox.query.filter_by(pallet_id=id).delete()
    TItem.query.filter_by(pallet_id=id).delete()
    
    db.session.delete(pallet)
    db.session.commit()
    return redirect(url_for('manage_pallets'))


@app.route('/tboxes', methods=['GET'])
def get_tboxes():
    pallet_id = request.args.get('pallet_id')
    if pallet_id:
        tboxes = TBox.query.filter_by(pallet_id=pallet_id).all()
    else:
        tboxes = TBox.query.all()  # Optional: if you want to handle cases with no pallet_id
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'whd': t.whd,
        'weight': t.weight,
        'openTop': t.openTop,
        'corner': t.corner,
        'pallet_id': t.pallet_id
    } for t in tboxes])


@app.route('/titems', methods=['GET'])
def get_titems():
    pallet_id = request.args.get('pallet_id')
    if pallet_id:
        titems = TItem.query.filter_by(pallet_id=pallet_id).all()
    else:
        titems = TItem.query.all()  # Optional: if you want to handle cases with no pallet_id
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'whd': t.whd,
        'count': t.count,
        'updown': t.updown,
        'level': t.level,
        'loadbear': t.loadbear,
        'weight': t.weight,
        'color': t.color,
        'pallet_id': t.pallet_id
    } for t in titems])

@app.route('/create_box', methods=['POST'])
def create_box_from_form():
    name = request.form['boxName']
    whd = request.form['boxWhd']
    weight = request.form['boxWeight']
    openTop = request.form['boxOpenTop']
    corner = request.form['boxCorner']
    pallet_id = request.form['palletSelect']
    
    new_box = TBox(name=name, whd=whd, weight=weight, openTop=openTop, corner=corner, pallet_id=pallet_id)
    db.session.add(new_box)
    db.session.commit()
    return redirect(url_for('manage_pallets'))

@app.route('/update_box', methods=['POST'])
def update_box_from_form():
    box_id = request.form['updateBoxId']
    name = request.form['updateBoxName']
    whd = request.form['updateBoxWhd']
    weight = request.form['updateBoxWeight']
    openTop = request.form['updateBoxOpenTop']
    corner = request.form['updateBoxCorner']
    
    box = TBox.query.get_or_404(box_id)
    box.name = name
    box.whd = whd
    box.weight = weight
    box.openTop = openTop
    box.corner = corner
    db.session.commit()
    return redirect(url_for('manage_pallets'))

@app.route('/delete_box/<int:id>', methods=['POST'])
def delete_box_from_form(id):
    box = TBox.query.get_or_404(id)
    db.session.delete(box)
    db.session.commit()
    return redirect(url_for('manage_pallets'))

@app.route('/create_item', methods=['POST'])
def create_item_from_form():
    name = request.form['itemName']
    whd = request.form['itemWhd']
    weight = request.form['itemWeight']
    count = request.form['itemStacking']
    pallet_id = request.form['palletSelect']
    
    new_item = TItem(name=name, whd=whd, weight=weight, count=count, pallet_id=pallet_id)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('manage_pallets'))

@app.route('/update_item', methods=['POST'])
def update_item_from_form():
    item_id = request.form['updateItemId']
    name = request.form['updateItemName']
    whd = request.form['updateItemWhd']
    weight = request.form['updateItemWeight']
    count = request.form['updateItemStacking']
    
    item = TItem.query.get_or_404(item_id)
    item.name = name
    item.whd = whd
    item.weight = weight
    item.count = count
    db.session.commit()
    return redirect(url_for('manage_pallets'))

@app.route('/delete_item/<int:id>', methods=['POST'])
def delete_item_from_form(id):
    item = TItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('manage_pallets'))

@app.route('/fetch_pallet_data/<int:id>', methods=['GET'])
def fetch_pallet_data(id):
    pallet = Pallet.query.get_or_404(id)
    boxes = TBox.query.filter_by(pallet_id=id).all()
    items = TItem.query.filter_by(pallet_id=id).all()

    return jsonify({
        'pallet': {'id': pallet.id, 'name': pallet.name},
        'boxes': [{'id': box.id, 'name': box.name} for box in boxes],
        'items': [{'id': item.id, 'name': item.name} for item in items]
    })


@app.route('/')
def index():
    pallets = Pallet.query.all()
    return render_template("index2.html", pallets=pallets)

# Route to render the Pallet Manager template
@app.route('/manage_pallets')
def manage_pallets():
    pallets = Pallet.query.all()
    return render_template("manage_pallets.html", pallets=pallets)

if __name__ == '__main__':
    
    app.run(debug=True)
    