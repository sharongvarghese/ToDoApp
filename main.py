from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Todo, Card
from forms import TodoForm, SignupForm, LoginForm, CardForm
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Fix for psycopg3 + Render PostgreSQL
db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and default "Today" cards
with app.app_context():
    db.create_all()
    for user in User.query.all():
        if not Card.query.filter_by(user_id=user.id, name="Today").first():
            db.session.add(Card(name="Today", user_id=user.id))
    db.session.commit()

# -------------------- HOME --------------------
@app.route('/')
def home():
    if current_user.is_authenticated:
        today_card = Card.query.filter_by(user_id=current_user.id, name="Today").first()
        today_tasks = today_card.tasks if today_card else []
        user_cards = Card.query.filter(Card.user_id == current_user.id, Card.name != "Today").all()
        return render_template('index.html', today_tasks=today_tasks, user_cards=user_cards)
    return render_template('index.html', card_form=CardForm())

# -------------------- ADD TASK --------------------
@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TodoForm()
    form.choices.choices = [(card.id, card.name) for card in Card.query.filter_by(user_id=current_user.id)]
    if form.validate_on_submit():
        new_task = Todo(task=form.task.data, card_id=form.choices.data, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully!", "success")
        return redirect(url_for('home'))
    return render_template('add_task.html', form=form)

# -------------------- TOGGLE TASK --------------------
@app.route('/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Todo.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return {"error": "Unauthorized"}, 403
    task.completed = not task.completed
    db.session.commit()
    return {"success": True, "completed": task.completed}

# -------------------- EDIT TASK --------------------
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Todo.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You are not authorized to edit this task!", "danger")
        return redirect(url_for('home'))

    form = TodoForm()

    # Populate dropdown with user's cards
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.choices.choices = [(card.id, card.name) for card in cards]

    if request.method == "GET":
        form.task.data = task.task
        form.choices.data = task.card_id

    if form.validate_on_submit():
        task.task = form.task.data
        task.card_id = form.choices.data
        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for('home'))

    return render_template('edit.html', form=form, task=task)


# -------------------- DELETE TASK --------------------
@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Todo.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You are not authorized to delete this task!", "danger")
        return redirect(url_for('home'))
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!", "success")
    return redirect(url_for('home'))

# -------------------- CREATE CARD --------------------
@app.route('/create_card', methods=['GET', 'POST'])
@login_required
def create_card():
    form = CardForm()
    if form.validate_on_submit():
        if Card.query.filter_by(user_id=current_user.id, name=form.name.data).first():
            flash("Card with this name already exists!", "warning")
        else:
            db.session.add(Card(name=form.name.data, user_id=current_user.id))
            db.session.commit()
            flash("Card created successfully!", "success")
            return redirect(url_for('home'))
    return render_template('create_card.html', form=form)
    

# -------------------- DELETE CARD --------------------
@app.route('/delete_card/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id != current_user.id:
        flash("You are not authorized to delete this card!", "danger")
        return redirect(url_for('home'))
    if card.name == "Today":
        flash("Cannot delete the default 'Today' card!", "danger")
        return redirect(url_for('home'))

    for task in card.tasks:
        db.session.delete(task)
    db.session.delete(card)
    db.session.commit()
    flash("Card deleted successfully!", "success")
    return redirect(url_for('home'))

# -------------------- SIGNUP --------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append("Username already exists.")
        elif form.password.data != form.confirm_password.data:
            form.confirm_password.errors.append("Passwords must match.")
        else:
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            db.session.add(Card(name="Today", user_id=new_user.id))
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("signup.html", form=form)

# -------------------- LOGIN --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            form.username.errors.append("User not found.")
        elif not check_password_hash(user.password, form.password.data):
            form.password.errors.append("Incorrect password.")
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form)

# -------------------- LOGOUT --------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists("todo.db"):
            db.create_all()
    app.run(debug=True)
