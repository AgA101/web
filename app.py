from flask import Flask, render_template, abort, request,  redirect
from markupsafe import escape
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, URLField, BooleanField, DateTimeLocalField, EmailField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bcrypt import generate_password_hash, check_password_hash
from os import getenv

app = Flask(__name__)

db = SQLAlchemy(app)
db.create_all()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config["SECRET_KEY"] = "dgihghthfi"
csrf = CSRFProtect(app)
login_manager = LoginManager(app)

courses = [
    {
        'id': 1,
        'name': 'Хорроры',
        'desc': 'жанр фантастики, который предназначен устрашить, напугать, шокировать или вызвать отвращение у своих читателей или зрителей, вызвав у них чувства ужаса и шока.',
        'img': 'https://true-gamer.com/wp-content/uploads/2020/04/horror-810x400.jpg',
        'is_new': False,
        'start': datetime.fromisoformat('2022-09-23T12:00:00'),
        'end': datetime.fromisoformat('2022-12-23T12:00:00'),
        'movies': [
            {'name': 'Рассвет мертвецов',
             'img': 'https://3dnews.ru/assets/external/illustrations/2015/08/12/918560/LayersofFear_screen.jpg'},
            {'name': 'Рассвет'},
        ]
    },
    {
        'id': 2,
        'name': 'Боевики',
        'desc': ' жанр кинематографа, в котором основное внимание уделяется перестрелкам, дракам, погоням и т. д. Боевики часто обладают высоким бюджетом, изобилуют каскадёрскими трюками и спецэффектами. Большинство боевиков иллюстрируют известный тезис «добро должно быть с кулаками».',
        'img': 'https://artifex.ru/wp-content/uploads/2019/09/%D1%84%D0%BE%D1%82%D0%BE-1-2.jpg',
        'is_new': True,
        'start': datetime.now(),
        'end': datetime.now(),
    },
    {
        'id': 3,
        'name': 'Комедии',
        'desc': ' жанр художественного произведения, характеризующийся юмористическим или сатирическим подходами, и также вид драмы, в котором специфически разрешается момент действенного конфликта или борьбы. Является противоположным жанром трагедии.',
        'img': 'https://wl-adme.cf.tsp.li/resize/728x/png/675/25b/8325645233aef27e685dc270f4.png',
        'is_new': True,
        'start': datetime.now(),
        'end': datetime.now(),
    },
    {
        'id': 4,
        'name': 'Детективы',
        'desc': 'преимущественно литературный и кинематографический жанр, произведения которого описывают процесс исследования загадочного происшествия с целью выяснения его обстоятельств и раскрытия загадки.',
        'img': 'https://school-of-inspiration.ru/wp-content/uploads/2020/11/5ae1ce7200f5c794801760.jpg',
        'start': datetime.now(),
        'end': datetime.now(),
    }
]


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.TEXT, nullable=False)
    cover = db.Column(db.TEXT)
    is_new = db.Column(db.Boolean, default=False)
    date_start = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)
    #owner_id = db.Column(db.Integer, db.ForeignKey)
    lessons = db.relationship('Lesson', backref='course')


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60))
    nickname = db.Column(db.String(32), unique=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class CreateCoursesForm(FlaskForm):
    name = StringField(label="Название курса", validators=[DataRequired()])
    description = TextAreaField(label="Описание", validators=[DataRequired()])
    cover = URLField(label="Ссылка на курс", validators=[DataRequired(), URL()])
    is_new = BooleanField(label="Новый курс")
    date_start = DateTimeLocalField(label="Дата начала")
    date_end = DateTimeLocalField(label="Дата окончания")


class LoginForm(FlaskForm):
    email = EmailField(label="Электронная почта", validators=[DataRequired()])
    password = PasswordField(label="Пароль", validators=[DataRequired()])
    remember_me = BooleanField(label='Запомнить меня')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def homepage():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') is not None
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            return redirect('/')
    return render_template('login.html', form=login_form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/search')
def search():
    text = escape(request.args['text'])
    selected_courses = [course for course in courses if text in course['name'] or text in course['desc']]
    return render_template('search.html', text=text, courses=selected_courses)


@app.route('/courses')
def get_courses():
    return 'All my courses'


@app.route('/courses/create', methods=["GET", "POST"])
@login_required
def c_course():
    create_course_form = CreateCoursesForm()
    if create_course_form.validate_on_submit():
        new_course = Course()
        new_course.name = request.form.get("name")
        new_course.description = request.form.get("description")
        new_course.cover = request.form.get("cover")
        new_course.is_new = request.form.get("is_new") is not None
        new_course.date_start = datetime.fromisoformat(request.form.get('date_start'))
        new_course.date_end = datetime.fromisoformat(request.form.get('date_end'))
        db.session.add(new_course)
        db.session.commit()
        return redirect('/')
    return render_template('create_course.html', form=create_course_form)


@app.route('/courses/<int:course_id>')
def get_course(course_id):
    #found_courses = [course for course in courses if course['id'] == course_id]
    #if not found_courses:
    #    abort(404)
    courses = Course.query.all()
    return render_template('course.html', course=courses)


@app.errorhandler(404)
def handle_404(error):
    return render_template('404.html'), 404


@app.template_filter('datetime')
def datetime_format(value, format="%c"):
    return value.strftime(format)

'''
@app.template_test('new_course')
def is_new(course):
    if 'is_new' not in course:
        return False
    return course['is_new']
'''

if __name__ == '__main__':

    app.run()