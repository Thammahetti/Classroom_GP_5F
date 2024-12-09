from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Classroom, Post

# Configurazione dell'app Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classroom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Creazione delle tabelle nel database
with app.app_context():
    db.create_all()

# Rotte principali
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['POST'])
def register():
    nome = request.form['nome']
    email = request.form['email']
    password = request.form['password']
    tipo = request.form['tipo']

    # Verifica se l'email è già registrata
    if User.query.filter_by(email=email).first():
        return "Email già registrata!"

    # Creazione del nuovo utente
    new_user = User(nome=nome, email=email, password=password, tipo=tipo)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return redirect(url_for('dashboard', user_id=user.id))
    return "Credenziali errate!"

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    user = User.query.get_or_404(user_id)
    classrooms = Classroom.query.filter_by(id_professore=user.id).all() if user.tipo == 'professore' else Classroom.query.all()
    return render_template('dashboard.html', user=user, classrooms=classrooms)

@app.route('/classroom/create/<int:professor_id>', methods=['POST'])
def create_classroom(professor_id):
    nome = request.form['nome']
    descrizione = request.form['descrizione']

    # Controlla che il professore non abbia già una classroom
    if Classroom.query.filter_by(id_professore=professor_id).first():
        return "Hai già creato una classroom."

    new_classroom = Classroom(nome=nome, descrizione=descrizione, id_professore=professor_id)
    db.session.add(new_classroom)
    db.session.commit()
    return redirect(url_for('dashboard', user_id=professor_id))

@app.route('/classroom/<int:classroom_id>')
def classroom_details(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    posts = Post.query.filter_by(id_classroom=classroom.id).all()
    return render_template('classroom_details.html', classroom=classroom, posts=posts)

@app.route('/classroom/<int:classroom_id>/post', methods=['POST'])
def add_post(classroom_id):
    title = request.form['title']
    description = request.form['description']
    new_post = Post(title=title, description=description, id_classroom=classroom_id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('classroom_details', classroom_id=classroom_id))

if __name__ == '__main__':
    app.run(debug=True)
