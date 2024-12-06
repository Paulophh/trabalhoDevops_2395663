import pytest
from flask.testing import FlaskClient
from app import app  # Importa o aplicativo principal

@pytest.fixture
def client() -> FlaskClient:
    """
    Configuração do cliente de teste para a aplicação Flask.
    """
    with app.test_client() as client:
        with app.app_context():
            # Se necessário, configure o banco de dados para os testes
            yield client

def test_listar_alunos(client: FlaskClient):
    """
    Testa a rota GET /alunos para verificar:
    - Código de status correto.
    - Resposta no formato esperado (lista).
    """
    response = client.get('/alunos')
    assert response.status_code == 200, "GET /alunos deve retornar 200 OK."
    assert isinstance(response.json, list), "Resposta de /alunos deve ser uma lista."

def test_adicionar_aluno(client: FlaskClient):
    """
    Testa a rota POST /alunos para verificar:
    - Código de status correto.
    - Mensagem de sucesso ao adicionar um novo aluno.
    - Persistência do aluno na lista de alunos.
    """
    new_aluno = {
        "nome": "Lal",
        "sobrenome": "de Lal",
        "turma": "2º período",
        "disciplinas": "Alemão",
        "ra": "2007"
    }
    # Enviar a requisição POST
    response = client.post('/alunos', json=new_aluno)
    assert response.status_code == 201, "POST /alunos deve retornar 201 Created."
    assert response.json['message'] == 'Aluno adicionado com sucesso!', \
        "Mensagem de sucesso esperada ao adicionar um aluno."

    # Verificar se o aluno foi adicionado com sucesso
    response_list = client.get('/alunos')
    assert response_list.status_code == 200, "GET /alunos deve retornar 200 OK."
    alunos = response_list.json
    assert any(aluno['ra'] == new_aluno['ra'] for aluno in alunos), \
        "O aluno adicionado deve estar presente na lista."

def test_adicionar_aluno_invalido(client: FlaskClient):
    """
    Testa a rota POST /alunos com dados inválidos para verificar:
    - Código de status de erro.
    - Mensagem de erro apropriada.
    """
    invalid_aluno = {
        "nome": "",  # Nome vazio (inválido)
        "sobrenome": "SemNome",
        "turma": "3º período",
        "disciplinas": "Matemática",
        "ra": "3007"
    }
    response = client.post('/alunos', json=invalid_aluno)
    assert response.status_code == 400, "POST com dados inválidos deve retornar 400 Bad Request."
    assert 'Erro ao adicionar aluno' in response.json['message'], \
        "Mensagem de erro esperada ao tentar adicionar um aluno inválido."
