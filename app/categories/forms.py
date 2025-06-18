from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=100)]
    )
    description = TextAreaField(
        'Description',
        validators=[Length(max=255)]
    )
    submit = SubmitField('Save')
