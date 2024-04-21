# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# zip file
import zipfile  
import subprocess, os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define Software model
class Software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    download_link = db.Column(db.String(255), nullable=False)

# Flask-Login user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('select_software'))
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Software selection route
@app.route('/select-software')
@login_required
def select_software():
    softwares = Software.query.all()
    return render_template('select_software.html', softwares=softwares)

# Batch script generation route
@app.route('/generate-script', methods=['POST'])
@login_required
def generate_script():
    selected_software = request.form.getlist('softwares')
    script_content = "# Batch script to install selected software\n"
    for software_id in selected_software:
        software = Software.query.get(int(software_id))
        script_content += f"winget install --id {software.name}\n"
    with open('static/software_installer.bat', 'w') as script_file:
        script_file.write(script_content)
    return redirect(url_for('download_script'))

# Download script route
@app.route('/download-script')
@login_required
def download_script():
    # create zip file and add script inside it
    with zipfile.ZipFile('static/software_installer.zip', 'w') as zip_file:
        print(os.listdir('static'))
        zip_file.write('static/software_installer.bat')
    return send_file('static/software_installer.zip', as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
