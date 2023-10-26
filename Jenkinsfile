pipeline {
  agent any
  stages {
    stage('Lint') {
      when {
        anyOf {
          branch pattern:"feature-*"
          branch pattern: "fix-*"
        }
      }
      agent {
        docker {
          image 'python:3.11.3-buster'
          args '-u 0'
        }
      }
      steps {
        sh 'pip install poetry'
        sh 'poetry install --with dev'
        sh "poetry run -- black --check *.py"
      }
    }
    stage('Build') {
      when {
        anyOf {
          branch pattern: "master"
        }
      }
      
      steps {
        script {
          def image = docker.build "were3/dos14tla:${env.GIT_COMMIT}"
          docker.withRegistry('','were3/dos14tla') {
            image.push()
          }
        }
      }
    }
  }
}
