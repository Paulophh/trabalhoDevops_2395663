pipeline {
    agent any

    environment {
        REPOSITORY_URL = 'https://github.com/Paulophh/trabalhoDevops_2395663.git'
        BRANCH_NAME = 'main'
    }

    stages {
        stage('Baixar código do Git') {
            steps {
                // Clonar o repositório do Git
                git branch: "${BRANCH_NAME}", url: "${REPOSITORY_URL}"
            }
        }

        stage('Build e Deploy') {
            steps {
                script {
                    // Construir as imagens Docker para cada serviço
                    sh '''
                        docker-compose build
                    '''

                    // Subir os containers do Docker com Docker Compose
                    sh '''
                        docker-compose up -d
                    '''
                }
            }
        }

        stage('Rodar Testes') {
            steps {
                script {
                    // Rodar os testes dentro do contêiner de testes com Docker Compose
                    sh '''
                        docker exec pipeline_trabalhodevops_flask_1 python -m unittest test_app.py
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline executada com sucesso!'
        }
        failure {
            echo 'A pipeline falhou.'
        }
    }
}
