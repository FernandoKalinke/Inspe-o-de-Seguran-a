import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import db
from models import Inspection, Question, Answer, Photo
import os

def create_app():
    """Cria e configura uma instância da aplicação Flask."""
    app = Flask(__name__)

    # Obtém o caminho absoluto para o diretório do projeto
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Configurações da aplicação
    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')

    # Garante que o diretório de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicializa o banco de dados com a aplicação
    db.init_app(app)

    @app.route('/')
    def index():
        return redirect(url_for('list_inspections'))

    @app.route('/questions', methods=['GET', 'POST'])
    def list_questions():
        if request.method == 'POST':
            text = request.form['text']
            weight = float(request.form['weight'])
            new_question = Question(text=text, weight=weight)
            db.session.add(new_question)
            db.session.commit()
            flash('Pergunta adicionada com sucesso!', 'success')
            return redirect(url_for('list_questions'))

        questions = Question.query.all()
        return render_template('questions.html', questions=questions)

    @app.route('/questions/delete/<int:question_id>')
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        flash('Pergunta removida com sucesso!', 'success')
        return redirect(url_for('list_questions'))

    @app.route('/inspections')
    def list_inspections():
        inspections = Inspection.query.order_by(Inspection.timestamp.desc()).all()
        return render_template('inspections.html', inspections=inspections)

    @app.route('/inspections/new', methods=['GET', 'POST'])
    def new_inspection():
        if request.method == 'POST':
            title = request.form['title']
            if not title:
                flash('O título é obrigatório!', 'danger')
                return redirect(url_for('new_inspection'))

            inspection = Inspection(title=title)
            db.session.add(inspection)
            db.session.commit()

            return redirect(url_for('start_inspection', inspection_id=inspection.id))

        return render_template('new_inspection.html')

    @app.route('/inspections/<int:inspection_id>')
    def start_inspection(inspection_id):
        inspection = Inspection.query.get_or_404(inspection_id)
        questions = Question.query.all()
        return render_template('inspection.html', inspection=inspection, questions=questions)

    @app.route('/inspections/<int:inspection_id>/submit', methods=['POST'])
    def submit_inspection(inspection_id):
        inspection = Inspection.query.get_or_404(inspection_id)

        for i in range(len(Question.query.all())):
            question_id = request.form.get(f'question_id_{i}')
            response_text = request.form.get(f'response_{i}')

            if question_id and response_text:
                question = Question.query.get(question_id)
                answer = Answer(response=response_text, inspection_id=inspection.id, question_id=question.id)
                db.session.add(answer)
                db.session.commit() # Commit to get answer.id for photo relationship

                photos = request.files.getlist(f'photos_{i}')
                for photo_file in photos:
                    if photo_file:
                        from werkzeug.utils import secure_filename
                        filename = secure_filename(photo_file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        photo_file.save(filepath)

                        photo = Photo(filename=filename, answer_id=answer.id)
                        db.session.add(photo)

        db.session.commit()
        flash('Inspeção finalizada com sucesso!', 'success')
        return redirect(url_for('show_report', inspection_id=inspection.id))

    @app.route('/inspections/<int:inspection_id>/report')
    def show_report(inspection_id):
        inspection = Inspection.query.get_or_404(inspection_id)

        total_weight = 0
        conforming_weight = 0

        for answer in inspection.answers:
            if answer.response != 'N/A':
                total_weight += answer.question.weight
                if answer.response == 'Conforme':
                    conforming_weight += answer.question.weight

        compliance_score = (conforming_weight / total_weight) * 100 if total_weight > 0 else 100

        return render_template('report.html', inspection=inspection, compliance_score=compliance_score)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/create_db')
    def create_db_command():
        """Cria as tabelas do banco de dados."""
        with app.app_context():
            db.create_all()
        return 'Banco de dados criado com sucesso!'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)