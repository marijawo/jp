# run.py
from flask import Flask, render_template, redirect, request, flash, url_for, make_response, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, Manager, MigrateCommand
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField
from wtforms.ext.sqlalchemy.orm import model_form, model_fields
from wtforms.validators import InputRequired, DataRequired

from config import BaseConfig
from forms import AddStudentForm, AddCourseForm, AddPaymentForm, AddTeacherForm

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(BaseConfig)

# Create Migration app instance
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

admin = Admin(app, name='application', template_mode='bootstrap3')


def choice_choice():
    return Student.query


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentCode = db.Column(db.String(10), unique=True, nullable=False)
    firstName = db.Column(db.String(20), nullable=False)
    middleName = db.Column(db.String(20), nullable=False)
    lastName = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthDate = db.Column(db.Date)
    address = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(12))
    email = db.Column(db.String(20))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    payments = db.relationship('Payment', backref=db.backref('students', lazy=True))

    def __init__(self, studentCode, firstName, middleName, lastName, gender, birthDate, address, phone, email,
                 course_id):
        self.studentCode = studentCode
        self.firstName = firstName
        self.middleName = middleName
        self.lastName = lastName
        self.gender = gender
        self.birthDate = birthDate
        self.address = address
        self.phone = phone
        self.email = email
        self.course_id = course_id

        def __repr__(self):
            # return self.studentCode
            return '<Student, %r>' % self.studentCode


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(50))
    students = db.relationship('Student', backref=db.backref('courses', lazy=True), uselist=False)
    teachers = db.relationship('Teacher', backref=db.backref('courses', lazy=True), uselist=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return self.description
        # return '<Course, %r>' % self.name


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacherCode = db.Column(db.String(20), unique=True, nullable=False)
    firstName = db.Column(db.String(20))
    middleName = db.Column(db.String(20), nullable=False)
    lastName = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(12))
    email = db.Column(db.String(20))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __init__(self, teacherCode, firstName, middleName, lastName, gender, address, phone, email, course_id):
        self.teacherCode = teacherCode
        self.firstName = firstName
        self.middleName = middleName
        self.lastName = lastName
        self.gender = gender
        self.address = address
        self.phone = phone
        self.email = email
        self.course_id = course_id

    def __repr__(self):
        return self.firstname, self.lastname
        # return '<Student, %r>' % self.studentCode


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, default=0)
    reason = db.Column(db.String(120))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    def __init__(self, amount, reason, student_id):
        self.amount = amount
        self.reason = reason
        self.student_id = student_id

    def __repr__(self):
        return self.amount, self.student_id
        # return '<Payment {}>'.format(self.student_id)


# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


##############################      Admin View      #############################
class CourseModelView(ModelView):
    column_searchable_list = ['name', 'description']
    column_editable_list = ['name', 'description']


class StudentModelView(ModelView):
    column_searchable_list = ['firstName', 'lastName', 'address', 'phone', 'email']
    column_editable_list = ['firstName', 'lastName', ]
    # create_modal = True
    # edit_modal = True


class PaymentModelView(ModelView):
    column_searchable_list = ['student_id']


class TeacherModelView(ModelView):
    column_searchable_list = ['firstName', 'lastName', 'phone', 'email', 'address']


admin.add_view(CourseModelView(Course, db.session))
admin.add_view(StudentModelView(Student, db.session))
admin.add_view(TeacherModelView(Teacher, db.session))
admin.add_view(ModelView(Payment, db.session))


##################   Admin URLS   ####################
@app.route('/')
def home():
    # return render_template('dashboard/index.html')
    # return "<h1> Home Page </h1>"
    return render_template('dashboard/index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


##################   Login URLS   ####################
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid Username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Password'
        else:
            session['logged_in'] = True
            flash("You were logged in")
            return redirect(url_for('home'))
    return render_template('users/login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('students'))


##################   Course URLS   ####################
@app.route('/courses')
def courses():
    return render_template('courses/list.html')


@app.route('/courses/list')
def list_courses():
    get_courses = Course.query.all()
    return render_template('courses/list.html', get_courses=get_courses)


@app.route('/courses/add', methods=['GET', 'POST'])
def course_add():
    error = None
    form = AddCourseForm(request.form)
    if request.method == 'POST' and form.validate():
        # name = form.name.data
        # description = form.description.data
        course = Course(form.name.data, form.description.data)
        db.session.add(course)
        db.session.commit()
        flash("You have successfully added ", course.name)
        return redirect(url_for('list_courses'))
    return render_template('courses/add.html', form=form, error=error)


@app.route('/courses/<int:id>/edit', methods=['GET', 'POST'])
def update_course(id):
    id = Course.query.get_or_404(id)
    course = Course.query.get_or_404(id)

    form = AddCourseForm(obj=course)
    if form.validate_on_submit():
        course.name = form.name.data
        course.description = form.description.data
        db.session.add(course)
        db.session.commit()
        flash('You have successfully Updated a course.')

        # redirect to the roles page
        return redirect(url_for('list_courses'))

    return render_template('courses/edit.html', course=course, form=form)


#
# @app.route('/course/add', methods=['GET', 'POST'])
# @login_required
# def add_course():
#     error = None
#     form = AddCourseForm()
#     if form.validate_on_submit():
#         course = Course(form.name.data, form.description.data)
#         db.session.add(course)
#         db.session.commit()
#         flash("Successfully added a new course")
#         return redirect('list-courses')
#     return render_template('courses/add.html', form=form, error=error)
#
#
# @app.route('/course/<int:id>/edit', methods=['GET', 'POST'])
# def course_edit(id):
#     """ Provide HTML form to edit a given course"""
#     course = db.session.query(Course).get(id)
#     if course is None:
#         abort(404)
#     form = AddCourseForm(request.form, course)
#     if request.method == 'POST' and form.validate():
#         form.populate_obj(course)
#         db.session.commit()
#         flash("Course Update Success")
#         return redirect(url_for('list_courses', id=course.id))
#     return render_template('courses/edit.html', form=form)


@app.route('/course/details')
def course_details():
    return render_template('courses/deteils.html')


#
# @app.route('/course/edit/<int:id>', methods=['GET', 'POST'])
# def edit_course(id):
#     # id = Course.query.get_or_404(id)
#     course = Course.query.filter_by(id=id).first()
#     form = AddCourseForm()
#     if form.__init_subclass__():
#         course.name = form.name.data
#         course.description = form.description.data
#         db.session.commit()
#         return redirect(url_for('list_courses'))
#     form.name.data = course.name
#     form.description.data = course.description
#     return render_template('courses/edit.html', form=form)
#

##################   Student URLS   ####################
@app.route('/students')
def students():
    return render_template('students/index.html')


@app.route('/list-students')
def list_students():
    all_students = Student.query.order_by(Student.studentCode).all()
    # all_male = Student.query.filter(Student.gender.match('male')).all()
    # all_female = Student.query.filter(Student.gender.match('female')).all()
    all_male = Student.query.filter(Student.gender.endswith('female')).count()
    return render_template('students/list.html', all_students=all_students, all_male=all_male)


@app.route('/add-student', methods=['GET', 'POST'])
@login_required
def add_student():
    error = None
    form = AddStudentForm()
    if form.validate_on_submit():
        student = Student(form.studentCode.data, form.firstName.data, form.middleName.data, form.lastName.data,
                          form.gender.data, form.birthDate.data, form.address.data, form.phone.data, form.email.data,
                          form.course_id.data)
        db.session.add(student)
        db.session.commit()
        flash("Successfully added a new course")
        return redirect('list-students')
    return render_template('students/add.html', form=form)


@app.route('/student-details')
def student_details():
    return render_template('students/details.html')


##########################     TEACHER PAGES      ##########################

@app.route('/teachers')
def teachers():
    return render_template('teachers/index.html')


@app.route('/teachers/list')
def list_teachers():
    teachers = Teacher.query.all()
    return render_template('teachers/list.html', teachers=teachers)


@app.route('/teacher/add', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = AddTeacherForm()
    return render_template('teachers/add.html', form=form)


##########################     PAYMENTS PAGES      ##########################
@app.route('/payments')
def payments():
    return render_template('payments/index.html')


@app.route('/payment/add', methods=['GET', 'POST'])
def add_payment():
    error = None
    form = AddPaymentForm()
    if form.validate_on_submit():
        payment = Payment(form.amount.data, form.reason.data, form.students.data)
        db.session.add(payment)
        db.session.commit()
        flash("Successfully added Payment")
        return redirect('list-payments')

    return render_template('payments/add.html', form=form)


def save_Changes(payment, form, new=False):
    """ Save the changes to the database """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object
    payment = Payment()
    payment.amount = form.amount.data
    payment.reason = form.reason.data
    payment.student_id = form.student.data

    if new:
        # Add the new album to the database
        db.session.add(payment)
    # Commit data to the database
    db.session.commit()


@app.route('/new_payment', methods=['GET', 'POST'])
def new_payment():
    """ Add a new payment to the database """
    form = AddPaymentForm(request.form)

    if request.method == 'POST' and form.validate():
        # Save the Payment
        payment = Payment()
        save_Changes(payment, form, new=True)
        flash("Payment added successfully")
        return redirect('/home')
    return render_template('payments/new_payment.html', form=form)


#
# @app.route('/payment/edit/<int:id>', methods=['GET', 'POST'])
# def editPayment(id):
#     edit = db.session.query(Payment).filter(Payment.id == id)
#     payment = edit.first()
#
#     if payment:
#         form = AddPaymentForm(formdata=request.form, obj=payment)
#         if request.method == 'POST' and form.validate():
#             # save edits
#             save_Changes(payment, form)
#             flash("Successfuly EDITED the form")
#             return redirect(url_for('list_payment'))
#         return render_template('payments/new_payment.html', form=form)
#     # else:
#     #     return 'Error loading ${id}'.format(id=id)
#

@app.route('/payment/edit/<int:id>', methods=['GET', 'POST'])
def edit_payment(id):
    # id = Payment.query.get(payment.id = 'id')
    add_payment = False
    # payment = Payment()
    payment = Payment.query.get_or_404(id)
    form = AddPaymentForm()
    if form.validate_on_submit():
        payment.amount = form.amount.data
        payment.reason = form.reason.data
        payment.students = form.students.data
        db.session.commit()
        flash('You have successfully edited the Payment')

        # return to the departments page
        return redirect(url_for('add_payment'))

    form.amount.data = payment.amount
    form.reason.data = payment.reason
    form.students.data = payment.students
    return render_template('payments/add.html', action="Edit", add_payment=add_payment, form=form)


@app.route('/payments/list')
def list_payment():
    all_payments = Payment.query.all()

    return render_template('payments/list.html', all_payments=all_payments)


##########################     SAMPLE PAGES      ##########################
@app.route('/register')
def register():
    return render_template('layouts/register.html')


@app.route('/blank')
def blank():
    return render_template('layouts/blank.html')


@app.route('/forgot-password')
def forgot_password():
    return render_template('layouts/forgot-password.html')


##########################     ERROR PAGES      ##########################


##########################     USERS URLS     ##########################
# Create a user to test with
# @app.before_first_request
# def create_user():
#     db.create_all()
#     user_datastore.create_user(email='ablie@ablie.com', password='password')
#     db.session.commit()


@app.route('/usrs')
def users():
    users = User.query.all()
    roles = Role.query.all()
    # if users.query.active==True:
    #     print("Active")
    return render_template('users/users.html', users=users, roles=roles)


@app.route('/roles')
def roles():
    return render_template('users/roles.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


if __name__ == '__main__':
    app.run()
