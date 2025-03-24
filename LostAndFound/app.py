from flask import Flask, render_template, redirect, url_for, flash, request, session, send_from_directory
from .config import Config
from .db import db  # Correct relative import for db.py
from .models import User, Item,Claim  # Correct relative import for models.py
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm, LoginForm , ReportItemForm, AdminLoginForm
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)


app.config.from_object(Config)

# Predefined admin credentials
ADMIN_EMAIL = "nextgeninnovators@dut4life.ac.za"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123") 



db.init_app(app)  # Initialize db with app

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view for Flask-Login

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def match_lost_and_found_items(new_item):
    if new_item.status == 'Lost':
        # Look for a matching found item
        found_items = Item.query.filter_by(status='Found', name=new_item.name, location=new_item.location).all()
        for found_item in found_items:
            # Create a new claim
            new_claim = Claim(
                item_id=found_item.id,  # Use the found item's ID
                user_id=new_item.user_id,  # Use the lost item's user ID
                status="Pending"
            )
            db.session.add(new_claim)

            # Optionally, mark the items as resolved
            new_item.status = 'Resolved'
            found_item.status = 'Resolved'

     

            db.session.commit()
            print(f"Match found: Lost Item ID {new_item.id} and Found Item ID {found_item.id}")

    elif new_item.status == 'Found':
        # Look for a matching lost item
        lost_items = Item.query.filter_by(status='Lost', name=new_item.name, location=new_item.location).all()
        for lost_item in lost_items:
            # Create a new claim
            new_claim = Claim(
                item_id=new_item.id,  # Use the found item's ID
                user_id=lost_item.user_id,  # Use the lost item's user ID
                status="Pending"
            )
            db.session.add(new_claim)

            # Optionally, mark the items as resolved
            lost_item.status = 'Resolved'
            new_item.status = 'Resolved'


            db.session.commit()
            print(f"Match found: Lost Item ID {lost_item.id} and Found Item ID {new_item.id}")

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# About route
@app.route('/about')
def about():
    return render_template('about.html')

# Contact route
@app.route('/contact')
def contact():
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
    session.pop('item_reported', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()  # Use AdminLoginForm for the admin login
    
    if form.validate_on_submit():
        # Check if the email and password match the hardcoded admin credentials
        if form.email.data == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD_HASH, form.password.data):
            session['is_admin'] = True  # Mark the session as admin
            flash('Admin Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
        
        flash('Invalid email or password', 'danger')

    return render_template('admin_login.html', form=form)

#Admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    print("Admin Dashboard Route Accessed")  # Debugging step

    if not session.get('is_admin'):  # Check if the user is logged in as admin
        flash('Access denied!', 'danger')
        return redirect(url_for('admin_login'))  # Redirect to admin login if not an admin

    users = User.query.all()
    report_items = Item.query.all()  # Fetch all items, resolved or not
    claims = Claim.query.all()  # Fetch all claims

    print("Users:", users)  # Debugging
    print("Active Items:", report_items)
    print("Claims:", claims)

    return render_template('admin_dashboard.html', users=users, reported_items=report_items, claims=claims) 



# Add these new routes after your existing admin_dashboard route
@app.route('/admin/users/add', methods=['GET', 'POST'])
def admin_add_user():
    if not session.get('is_admin'):
        flash('Access denied!', 'danger')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            phone = request.form.get('phone', '')
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already exists!', 'danger')
                return redirect(url_for('admin_add_user'))

            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password),
                phone=phone
            )
            db.session.add(new_user)
            db.session.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding user: {str(e)}', 'danger')

    return render_template('admin_add_user.html')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    if not session.get('is_admin'):
        flash('Access denied!', 'danger')
        return redirect(url_for('admin_login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        try:
            user.name = request.form['name']
            user.email = request.form['email']
            user.phone = request.form.get('phone', '')
            
            if request.form.get('password'):
                user.password = generate_password_hash(request.form['password'])
            
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')

    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if not session.get('is_admin'):
        flash('Access denied!', 'danger')
        return redirect(url_for('admin_login'))

    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

# ... (keep all your remaining existing routes) )
# Edit item
@app.route('/item/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    print("Admin session set:", session.get('is_admin'))

    if not session.get('is_admin'):
        flash('Access denied!', 'danger')
        return redirect(url_for('admin_login'))

    item = Item.query.get_or_404(item_id)

    if request.method == 'POST':
        print("Form submitted with data:", request.form)

        item.name = request.form['name']
        item.description = request.form['description']
        item.category = request.form['category']
        item.status = request.form['status']
        item.location = request.form['location']

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    print("Rendering edit_item.html template")
    return render_template('edit_item.html', item=item)


# Delete item
@app.route('/item/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if not session.get('is_admin'):
        flash('Access denied!', 'danger')
        return redirect(url_for('admin_login'))

    item = Item.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.commit()

    flash('Item deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)  # Remove the admin session
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))  # Redirect to admin login page




def allowed_file(filename):
    print("Checking file:", filename)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

        image_path = None
        image_url = None
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Ensure the upload folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                print("Creating upload folder")
                os.makedirs(app.config['UPLOAD_FOLDER'])

            
            file.save(image_path)

            image_url = os.path.join('uploads', filename).replace("\\", "/") # Relative path for the front-end

        # Create the new item and associate it with the current user
        new_item = Item(name=name, description=description, category=category,
                        status=status, location=location, user_id=current_user.id,
                        image_url=image_url)

        # Add to the database
        db.session.add(new_item)
        db.session.commit()

        # Automatically check for matches
        match_lost_and_found_items(new_item)


        flash('Item reported successfully!', 'success')

        session['item_reported'] = True


        return redirect(url_for('dashboard'))

    return render_template('report.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query')  # Get search query from form
    results = []

    if query:
        # Search only for found items
        results = Item.query.filter(Item.name.ilike(f"%{query}%"), Item.status == "Found").all()
    
    return render_template('search.html', results=results, query=query)




if __name__ == '__main__':
    app.run(debug=True)
