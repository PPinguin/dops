import math
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditRiddleForm, SearchForm
from app.models import User, Riddle, Solution
from werkzeug.urls import url_parse

home_stack = []
explore_stack = []

def pager(current, count):
    max_page = int(math.ceil(count/app.config['RIDDLES_PER_PAGE']))
    max_page += int(max_page==0)
    if current>max_page: current = max_page
    return { 'start':(current - 3)*int(current>3) + int(current<=3),
        'end':(current + 3)*int(current<max_page-3) + max_page*int(current>=max_page-3) }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():    
    global home_stack
    if len(home_stack) == 0:
        home_stack = current_user.followed_riddles()
    page = request.args.get('page', 1, type=int)
    limit = pager(page, home_stack.count())
    return render_template(
        'home.html', riddles = home_stack.paginate(
            page, app.config['RIDDLES_PER_PAGE'], False).items, page = page, start = limit['start'], end = limit['end'])

@app.route('/explore', methods=['GET', 'POST'])
def explore():    
    global explore_stack
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('explore', filter = form.body.data))
    filter = request.args.get('filter', type=int)
    if not filter is None:
        riddles = Riddle.query.filter_by(id = filter)
        form.body.data = filter
    elif len(explore_stack) == 0:
        explore_stack = Riddle.query.order_by(Riddle.timestamp.desc())
        riddles = explore_stack
    else: 
        riddles = explore_stack
    page = request.args.get('page', 1, type=int)
    limit = pager(page, riddles.count())
    return render_template(
        'explore.html', form = form, riddles = riddles.paginate(
            page, app.config['RIDDLES_PER_PAGE'], False).items, page = page, start = limit['start'], end = limit['end'])

@app.route('/rate')
def rate():
    users = User.query.order_by(User.points.desc()).limit(30)
    return render_template('rate.html', title='Rate', users = users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, points=0)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration is successful')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form)

@app.route('/user/<id>')
def user(id):
    user = User.query.get(int(id))
    riddles = Riddle.query.filter_by(user_id=user.id).order_by(Riddle.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    limit = pager(page, riddles.count())
    return render_template(
        'user.html', loc = 'user', user = user, riddles = riddles.paginate(
            page, app.config['RIDDLES_PER_PAGE'], False).items, page = page, start = limit['start'], end = limit['end'])

@app.route('/follow/<id>')
@login_required
def follow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        return redirect(url_for('home'))
    if user == current_user:
        return redirect(url_for('home'))
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for('user', id=id))

@app.route('/unfollow/<id>')
@login_required
def unfollow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        return redirect(url_for('home'))
    if user == current_user:
        return redirect(url_for('home'))
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for('user', id=id))

@app.route('/new_riddle', methods=['GET', 'POST'])
@login_required
def new_riddle():
    form = EditRiddleForm()
    if form.validate_on_submit():
        riddle = Riddle(body=form.body.data, answer=form.answer.data, author=current_user, theme = form.theme.data.hex_l)
        db.session.add(riddle)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit_riddle.html', title='New riddle', form=form)

@app.route('/edit_riddle/<id>', methods=['GET', 'POST'])
@login_required
def edit_riddle(id):
    form = EditRiddleForm()
    riddle = Riddle.query.filter_by(id = id).first()
    all = Solution.query.filter_by(riddle_id = id).count()
    correct = Solution.query.filter_by(riddle_id = id, answer = riddle.answer).count()
    if form.validate_on_submit():
        riddle.body = form.body.data
        riddle.answer = form.answer.data
        riddle.theme = form.theme.data.hex_l
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    else:
        form.body.data = riddle.body
        form.answer.data = riddle.answer
        form.theme.data = riddle.theme
    return render_template('edit_riddle.html', title='Edit riddle', form=form, proportion = int(correct/all*100))

@app.route('/answer', methods=['POST'])
@login_required
def answer():
    id = int(request.form['id'])
    answer = request.form['answer']
    riddle = Riddle.query.filter_by(id = id).first()
    if not riddle.is_answered(current_user):
        solution = Solution(riddle_id = id, user_id = current_user.id, answer = answer)
        resp = (answer == riddle.answer)
        if resp: current_user.add_point()
        db.session.add(solution)
        db.session.commit()
        return jsonify({'response': resp, 'answer':riddle.answer})

@app.route('/info', methods=['POST'])
@login_required
def info():
    id = int(request.form['id'])
    riddle = Riddle.query.filter_by(id = id).first()
    if riddle.is_answered(current_user):
        solution = Solution.query.filter_by(riddle_id = id, user_id = current_user.id).first()
        return jsonify({'correct': riddle.answer, 'custom': solution.answer})