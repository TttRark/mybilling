from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class TransactionForm(FlaskForm):
    amount = FloatField('金额', validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('描述', validators=[Length(max=256)])
    category = StringField('分类', validators=[Length(max=64)])
    transaction_type = SelectField('类型', choices=[('income', '收入'), ('expense', '支出')], validators=[DataRequired()])
    date = DateField('日期', validators=[DataRequired()])
    submit = SubmitField('保存') 