pipeline {
  agent any
  stages {
    stage('Lint') {
      when {
        anyOf {
          branch pattern: "feature-*"
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
        script {
          def diff = sh(script: 'poetry run -- black --diff *.py', returnStdout: true).trim()
          
          if (diff) {
            echo "Изменения форматирования:"
            echo diff
            // Применяем изменения к исходным файлам
            script {
              sh "echo \"$diff\" | poetry run -- black -"
            }
          } else {
            echo "Форматирование кода без изменений."
          }
        }
      }
    }
  }
}

