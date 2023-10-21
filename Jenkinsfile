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
          docker.withRegistry('https://hub.docker.com/r/were3/pythonapp', 'were3/pythonapp') {
            def image = docker.build "were3/pythonapp/tla/dos14bank:${env.GIT_COMMIT}"
            image.push()
          } 

        }
      }
    }
  }
}
