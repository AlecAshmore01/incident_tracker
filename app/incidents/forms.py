from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from app.utils.validators import SafeText


class IncidentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=140), SafeText()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10), SafeText()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    status = SelectField(
        'Status',
        choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Closed', 'Closed')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit')
