from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange,InputRequired

class BoxForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    whd = StringField('WHD (Width, Height, Depth)', validators=[DataRequired()])
    weight = IntegerField('Weight', validators=[DataRequired(), NumberRange(min=1)])
    openTop = StringField('Open Top', validators=[DataRequired()])
    coner = IntegerField('Coner', validators=[DataRequired()])
    submit = SubmitField('Add Box')

class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    whd = StringField('WHD (Width, Height, Depth)', validators=[DataRequired()])
    count = IntegerField('Count', validators=[DataRequired(), NumberRange(min=1)])
    updown = SelectField('Updown', choices=[(1, 'Yes'), (0, 'No')], coerce=int)
    type = SelectField('Type', choices=[(1, 'Type 1'), (2, 'Type 2')], coerce=int)
    level = IntegerField('Level', validators=[InputRequired()])
    loadbear = IntegerField('Loadbear', validators=[DataRequired(), NumberRange(min=1)])
    weight = IntegerField('Weight', validators=[DataRequired(), NumberRange(min=1)])
    color = SelectField('Color', choices=[(1, 'Red'), (2, 'Blue'), (3, 'Green'), (4, 'Yellow'), (5, 'Black'), (6, 'White'), (7, 'Brown')], coerce=int)
    submit = SubmitField('Add Item')
