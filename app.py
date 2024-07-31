from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bcrypt import hashpw, gensalt
from werkzeug.security import check_password_hash

# Generate a salt for password hashing
salt = gensalt()
db = SQLAlchemy()
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///faq.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'your_secret_key' 
# initialize the app with the extension
db.init_app(app)


class Faq(db.Model):
    sno=db.Column(db.Integer ,primary_key=True)
    question=db.Column(db.String(200) ,nullable=False)
    answer=db.Column(db.String(500) ,nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    status = db.Column(db.Boolean,default=True)
  # Add status column

    def __repr__(self) -> str:
        return f"{self.sno}-{self.question}"
    
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120)) 

    
def add_initial_admin():
    
    admin = Admin(username='admin', password='password123')  # Replace with desired credentials
    db.session.add(admin)
    db.session.commit()

# # database for users
class User(db.Model):
    sno=db.Column(db.Integer ,primary_key=True)
    username=db.Column(db.String(200) ,nullable=False)
    email=db.Column(db.String(500) ,nullable=False)
    password=db.Column(db.String(500) ,nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    def __init__(self,email,password,username):
        self.username = username
        self.email = email
        self.password =password
    def check_password(self, password):
        return check_password_hash(self.password, password)
with app.app_context():
    def __repr__(self) -> str:
        return f"{self.sno}-{self.username}"
    
# # database for publications
    
class Publication(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)

    abstract = db.Column(db.Text, nullable=False)
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.sno'))  # Another foreign key
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    file_path = db.Column(db.String(255))  # Store the file path
    user = db.relationship('User', foreign_keys=[created_by])
    published = db.Column(db.Boolean, default=False)
    def __repr__(self) -> str:
        return f"{self.sno}-{self.title}"


    
with app.app_context():
    db.create_all()

@app.route('/')
def home(): 
    if 'email' not in session:
       email=''
    else:

       email=session['email']
    return render_template('home.html',email=email)
    # return 'Hello, World!'


# Admin's Faq page
@app.route('/admin/faq')
def admin_faq(): 

    
    allFaq= Faq.query.all()   
    return render_template('admin/faq.html', faqs=allFaq)
    # return 'Hello, World!'

# admin faq session
@app.route('/delete/<int:sno>')
def delete(sno): 
    
    faq= Faq.query.filter_by(sno=sno).first()  
    db.session.delete(faq)
    db.session.commit()
    return redirect(url_for('admin_faq'))
   

@app.route('/add_faq', methods=['POST'])
def add():
    allFaq = Faq.query.all()   
    question = request.form.get('question')
    answer= request.form.get('answer')
    
    # Create a new FAQ object
    faq = Faq(question=question, answer=answer)
   
    db.session.add(faq)
    db.session.commit()
    #  # Create a new FAQ object
    # admin = Admin(username='admin', password='password123')  # Replace with desired credentials
    # db.session.add(admin)
    # db.session.commit()
   
    return redirect(url_for('admin_faq'))

@app.route('/update_faq/<int:sno>')
def update_faq(sno):
    faq= Faq.query.filter_by(sno=sno).first()  
    # return redirect(url_for('admin_faq'))
    return render_template('admin/update_faq.html', faq=faq)
@app.route("/faqs")
def faqs():
    
    all_faqs = Faq.query.filter_by(status=1)
    return render_template("faq_user.html", faqs=all_faqs)


@app.route('/user_registration')
def register():
    return render_template('register.html')

@app.route('/adduser', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Create a new user object
    user = User(username=username, email=email, password=password)

    db.session.add(user)
    db.session.commit()
    flash('User registered successfully!')
    return redirect(url_for('login'))

    


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        count = User.query.filter_by(email=email,password=password).count()
        
        
        if count==1:
            user = User.query.filter_by(email=email,password=password).first()
            session['email'] = user.email
            session['user_id'] = user.sno
            return redirect('/')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin/listuser')
def view_users():
    # Fetch all users (customize query if needed)
    users = User.query.all()

    return render_template('admin/listuser.html', users=users)
@app.route('/deleteuser/<int:sno>')
def deleteuser(sno): 
    
    user= User.query.filter_by(sno=sno).first()  
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('view_users'))

@app.route('/add_publication')
def add_publications():
    return render_template('publications.html')


@app.route('/upload_publication' , methods=['POST'])
def upload_publication():
    title = request.form.get('title')
    author = request.form.get('author')
    abstract = request.form.get('abstract')
    file_path = request.form.get('file_path')
    
    # user_id = session.get('user_id')  # Retrieve user ID from session
    created_by= session.get('user_id')
    if not created_by:
        flash('Please log in to upload publications')
        return redirect(url_for('login'))  # Redirect to login page
    
    publication = Publication(
        title=title,
        author=author,
        abstract=abstract,
        file_path=file_path,
        created_by=created_by
    )
    # ... rest of the function
    db.session.add(publication)
    db.session.commit()

    flash('Publication uploaded successfully')
    return redirect(url_for('home')) 

@app.route('/admin/publications')
def admin_publications():
    publications = Publication.query.all()
    return render_template('admin/admin_publication.html', publications=publications)

def publish_publication(publication_id):
    publication = Publication.query.get_or_404(publication_id)
    publication.published = True  # Assuming published status is a boolean field
    db.session.commit()
    flash('Publication published successfully')
    return redirect(url_for('admin.publications'))


@app.route('/list_of_publications')
def user_publications():
    publications = Publication.query.filter_by(published=True).all()
    return render_template('user_publications.html', publications=publications)


if __name__=="__main__":
    app.run(debug=True ,port=8000)
