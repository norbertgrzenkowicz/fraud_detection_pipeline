pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://https://github.com/norbertgrzenkowicz/fraud_detection_pipeline.git'
            }
        }
        stage('Build') {
            steps {
                sh 'echo Building the project...'
                // Add your build commands here
            }
        }
        stage('Test') {
            steps {
                sh 'echo Running tests...'
                // Add your test commands here
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying the project...'
                // Add your deployment commands here
            }
        }
    }
}