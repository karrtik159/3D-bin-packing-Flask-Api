from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange,InputRequired

class PalletForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField('Add Pallet')
class BoxForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    whd = StringField('WHD (Width, Height, Depth)', validators=[DataRequired()])
    weight = IntegerField('Weight', validators=[DataRequired(), NumberRange(min=1)])
    openTop = StringField("Open Top", validators=[DataRequired()])
    corner = IntegerField("Corner", validators=[InputRequired()])
    pallet_id = SelectField("Pallet", coerce=int)
    submit = SubmitField('Add Box')

class ItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    whd = StringField('WHD (Width, Height, Depth)', validators=[DataRequired()])
    count = IntegerField("Count", validators=[DataRequired()])
    updown = SelectField('Updown', choices=[(1, 'Yes'), (0, 'No')], coerce=int)
    level = IntegerField('Level', validators=[InputRequired()])
    loadbear = IntegerField('Loadbear', validators=[DataRequired(), NumberRange(min=1)])
    weight = IntegerField('Weight', validators=[DataRequired(), NumberRange(min=1)])
    # color = IntegerField("Color", validators=[DataRequired()])
    color = SelectField('Color', choices=[(1, 'Red'), (2, 'Blue'), (3, 'Green'), (4, 'Yellow'), (5, 'Black'), (6, 'White'), (7, 'Brown')], coerce=int)
    
    pallet_id = SelectField("Pallet", coerce=int)
    submit = SubmitField('Add Item')
