import time
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import AppBuilder, SQLA, ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy.exc import OperationalError
from prometheus_flask_exporter import PrometheusMetrics

# Configuração e inicialização do aplicativo
app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configurações de segurança e banco de dados
app.config['SECRET_KEY'] = 'minha_chave_secreta_super_secreta'  # Substitua por uma chave segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root_password@mariadb/school_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados e do AppBuilder
db = SQLAlchemy(app)
appbuilder = AppBuilder(app, db.session)

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo de Aluno
class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    disciplinas = db.Column(db.String(200), nullable=False)
    ra = db.Column(db.String(200), nullable=False)

# Configuração do banco de dados
def configurar_banco_de_dados():
    tentativas = 5
    for tentativa in range(tentativas):
        try:
            with app.app_context():
                db.create_all()  # Cria as tabelas no banco de dados
                # Criar usuário administrador padrão, se necessário
                if not appbuilder.sm.find_user(username='admin'):
                    appbuilder.sm.add_user(
                        username='admin',
                        first_name='Admin',
                        last_name='User',
                        email='admin@admin.com',
                        role=appbuilder.sm.find_role(appbuilder.sm.auth_role_admin),
                        password='admin'
                    )
            logger.info("Banco de dados inicializado com sucesso.")
            break
        except OperationalError as e:
            if tentativa < tentativas - 1:
                logger.warning(f"Tentativa {tentativa + 1} de conexão com o banco falhou. Tentando novamente em 5 segundos...")
                time.sleep(5)
            else:
                logger.error("Falha ao conectar ao banco de dados após várias tentativas.")
                raise e

configurar_banco_de_dados()

# Visão do modelo Aluno para o painel administrativo
class AlunoModelView(ModelView):
    datamodel = SQLAInterface(Aluno)
    list_columns = ['id', 'nome', 'sobrenome', 'turma', 'disciplinas', 'ra']

# Registrar a visão no AppBuilder
appbuilder.add_view(
    AlunoModelView,
    "Lista de Alunos",
    icon="fa-folder-open-o",
    category="Alunos",
)

# Rotas
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    alunos = Aluno.query.all()
    output = [
        {
            'id': aluno.id,
            'nome': aluno.nome,
            'sobrenome': aluno.sobrenome,
            'turma': aluno.turma,
            'disciplinas': aluno.disciplinas,
            'ra': aluno.ra
        }
        for aluno in alunos
    ]
    return jsonify(output), 200

@app.route('/alunos', methods=['POST'])
def adicionar_aluno():
    data = request.get_json()
    try:
        novo_aluno = Aluno(
            nome=data['nome'],
            sobrenome=data['sobrenome'],
            turma=data['turma'],
            disciplinas=data['disciplinas'],
            ra=data['ra']
        )
        db.session.add(novo_aluno)
        db.session.commit()
        logger.info(f"Aluno {data['nome']} {data['sobrenome']} adicionado com sucesso.")
        return jsonify({'message': 'Aluno adicionado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao adicionar aluno: {str(e)}")
        return jsonify({'message': 'Erro ao adicionar aluno.'}), 400

# Inicialização do servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
