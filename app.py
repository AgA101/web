from flask import Flask, render_template, abort, request
from markupsafe import escape
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


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
    lessons = db.relationship('Lesson', backref='course')


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


@app.route('/')
def homepage():  # put application's code here
    return render_template('index.html', courses=courses)


@app.route('/search')
def search():
    text = escape(request.args['text'])
    selected_courses = [course for course in courses if text in course['name'] or text in course['desc']]
    return render_template('search.html', text=text, courses=selected_courses)


@app.route('/about')
def about():
    return 'All about me!'


@app.route('/courses')
def get_courses():
    return 'All my courses'


@app.route('/courses/<int:course_id>')
def get_course(course_id):
    found_courses = [course for course in courses if course['id'] == course_id]
    if not found_courses:
        abort(404)

    return render_template('course.html', course=found_courses[0])


@app.errorhandler(404)
def handle_404(error):
    return render_template('404.html'), 404


@app.template_filter('datetime')
def datetime_format(value, format="%c"):
    return value.strftime(format)


@app.template_test('new_course')
def is_new(course):
    if 'is_new' not in course:
        return False
    return course['is_new']


if __name__ == '__main__':
    app.run()