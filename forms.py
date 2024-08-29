from flask_wtf import FlaskForm
import matplotlib.colors as mcolors
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

    # Get a list of color names from matplotlib
    color_names = list(mcolors.CSS4_COLORS.keys())

    color_choices = [(color, color.capitalize()) for color in color_names]

    color = SelectField(
        "Color",
        choices=color_choices,
        coerce=str,
        validators=[InputRequired(message="Color selection is required.")],
    )
    pallet_id = SelectField(
        "Pallet",
        coerce=int,
        validators=[InputRequired(message="Pallet ID is required.")],
    )
    submit = SubmitField("Add Item")
