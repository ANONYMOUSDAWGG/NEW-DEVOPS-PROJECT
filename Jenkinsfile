pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Cloning repository'
                git branch: 'main', url: 'https://github.com/<your-username>/devops-microservices-project.git'
            }
        }

        stage('Test - User Service') {
            steps {
                dir('user-service') {
                    bat 'pip install -r requirements.txt'
                    bat 'pytest'
                }
            }
        }

        stage('Test - Product Service') {
            steps {
                dir('product-service') {
                    bat 'pip install -r requirements.txt'
                    bat 'pytest'
                }
            }
        }

        stage('Test - Order Service') {
            steps {
                dir('order-service') {
                    bat 'pip install -r requirements.txt'
                    bat 'pytest'
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building versioned images for all 3 microservices'
                bat 'docker build -t user-service:%BUILD_NUMBER% ./user-service'
                bat 'docker build -t product-service:%BUILD_NUMBER% ./product-service'
                bat 'docker build -t order-service:%BUILD_NUMBER% ./order-service'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying the updated stack with docker-compose'
                bat 'docker compose down'
                bat 'docker compose up -d --build'
            }
        }
    }

    post {
        success {
            echo 'All 3 microservices were built, tested and deployed successfully!'
        }
        failure {
            echo 'Pipeline failed - check the stage logs above.'
        }
    }
}
