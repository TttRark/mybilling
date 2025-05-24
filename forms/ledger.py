from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class LedgerForm(FlaskForm):
    name = StringField('账本名称', validators=[DataRequired(), Length(min=1, max=64)])
    description = TextAreaField('描述', validators=[Length(max=500)])
    submit = SubmitField('保存') 