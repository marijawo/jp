from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField,  PasswordField, IntegerField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from wtforms.validators import DataRequired, InputRequired


# Add Student Form
class AddStudentForm(FlaskForm):
    studentCode = StringField('Student Code', validators=[DataRequired()])
    firstName = StringField('First Name', validators=[DataRequired()])
    middleName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('First Name', validators=[DataRequired()])
    gender = SelectField("Gender", choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    birthDate = DateField("Birth Date", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    course_id = StringField("Course", validators=[DataRequired()])
    # course_choice = QuerySele
    submit = SubmitField('Add Student')


# Course Form
class AddCourseForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    submit = SubmitField('Add Course')


# Paymens Form
class AddPaymentForm(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired()])
    reason = StringField('Paid for', validators=[DataRequired()])
    students = StringField('Student', validators=[DataRequired()])
    submit = SubmitField('Add Payment')




# Teacher Form
class AddTeacherForm(FlaskForm):
    teacherCode = StringField('Teacher Code', validators=[DataRequired])
    firstName = StringField('First Name', validators=[DataRequired])
    middleName = StringField('Middle Name', validators=[DataRequired])
    lastName = StringField('Last Name', validators=[DataRequired])
    gender = StringField('Gender', validators=[DataRequired])
    address = StringField('Address', validators=[DataRequired])
    phone = StringField('Phone', validators=[DataRequired])
    email = StringField('Email', validators=[DataRequired])
    course = StringField('Course', validators=[DataRequired])
    submit = SubmitField('Add Teacher')
