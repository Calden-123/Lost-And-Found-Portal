from flask import Flask, render_template, redirect, url_for, flash, request, session
from .config import Config
from .db import db  # Correct relative import for db.py
from .models import User, Item, Claim, Admin  # Correct relative import for models.py
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm, LoginForm , ReportItemForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  # Initialize db with app

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view for Flask-Login

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# About route
@app.route('/about')
def about():
    return render_template('about.html')

# Contact route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get the form data (just for demonstration, we print it)
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Print the data to the console (or you could log it)
        print(f"Message from {name} ({email}): {message}")

        # You can add any confirmation or simple message here
        return render_template('contact.html', message_sent=True)
    return render_template('contact.html')

# Thank You route after form submission
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if request.method == 'POST':
        print("Form submitted")  # Debugging line
        print("Form errors:", form.errors)  # Show validation errors

    if form.validate_on_submit():
        print("Form validated successfully!")  # Debugging line

        name = form.name.data
        email = form.email.data
        password = form.password.data
        phone = form.phone.data

        # Check if the user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists!', 'danger')
            return redirect(url_for('register'))

        # Create a new user and hash the password
        new_user = User(name=name, email=email, phone=phone)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        # Find the user by email
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):  # Check if the password matches
            login_user(user)  # Log the user in
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard (or wherever you want)
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)

# Dashboard route (after login)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_item():
    form = ReportItemForm()

    if form.validate_on_submit():
        # Get the form data
        name = form.name.data
        description = form.description.data
        category = form.category.data
        status = form.status.data
        location = form.location.data

        # Create the new item and associate it with the current user
        new_item = Item(name=name, description=description, category=category,
                        status=status, location=location, user_id=current_user.id)

        # Add to the database
        db.session.add(new_item)
        db.session.commit()

        flash('Item reported successfully!', 'success')


        return redirect(url_for('dashboard'))

    return render_template('report.html', form=form)

#search
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query')  # Get search query from form
    results = []
    
    if query:
        results = Item.query.filter(Item.name.ilike(f"%{query}%")).all()
    
    return render_template('search.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
