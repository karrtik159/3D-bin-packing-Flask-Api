from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired


class PalletForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Add Pallet")


class BoxForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message="Name is required.")])
    whd = StringField(
        "WHD (Width, Height, Depth)",
        validators=[DataRequired(message="WHD (Width, Height, Depth) is required.")],
    )
    weight = IntegerField(
        "Weight",
        validators=[
            DataRequired(message="Weight is required."),
            NumberRange(min=1, message="Weight must be at least 1."),
        ],
    )
    openTop = StringField(
        "Open Top",
        validators=[DataRequired(message="Open Top information is required.")],
    )
    corner = IntegerField(
        "Corner", validators=[InputRequired(message="Corner value is required.")]
    )
    pallet_id = SelectField(
        "Pallet",
        coerce=int,
        validators=[InputRequired(message="Pallet selection is required.")],
    )
    submit = SubmitField("Add Box")


class ItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message="Name is required.")])
    whd = StringField(
        "WHD (Width, Height, Depth)",
        validators=[DataRequired(message="WHD is required.")],
    )
    count = IntegerField(
        "Count", validators=[DataRequired(message="Count is required.")]
    )
    updown = SelectField(
        "Updown",
        choices=[(1, "Yes"), (0, "No")],
        coerce=int,
        validators=[InputRequired(message="Updown selection is required.")],
    )
    level = IntegerField(
        "Level", validators=[InputRequired(message="Level is required.")]
    )
    loadbear = IntegerField(
        "Loadbear",
        validators=[
            DataRequired(message="Loadbear is required."),
            NumberRange(min=1, message="Loadbear must be at least 1."),
        ],
    )
    weight = IntegerField(
        "Weight",
        validators=[
            DataRequired(message="Weight is required."),
            NumberRange(min=1, message="Weight must be at least 1."),
        ],
    )
    color = SelectField(
        "Color",
        choices=[
            (1, "Red"),
            (2, "Blue"),
            (3, "Green"),
            (4, "Yellow"),
            (5, "Black"),
            (6, "White"),
            (7, "Brown"),
        ],
        coerce=int,
        validators=[InputRequired(message="Color selection is required.")],
    )
    pallet_id = SelectField(
        "Pallet",
        coerce=int,
        validators=[InputRequired(message="Pallet ID is required.")],
    )
    submit = SubmitField("Add Item")
