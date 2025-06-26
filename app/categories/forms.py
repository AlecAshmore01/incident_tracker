from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


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

    def validate_name(self, field):
        if '<' in field.data or '>' in field.data:
            raise ValidationError("Category name cannot contain '<' or '>' characters.")
