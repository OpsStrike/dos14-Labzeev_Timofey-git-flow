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
          // Сохраняем код до проверки
          def originalCode = sh(script: 'cat *.py', returnStdout: true).trim()
          // Проверка форматирования с Black
          sh "poetry run -- black --check *.py"
          def blackExitCode = sh(script: 'echo $?', returnStatus: true)
          // Если Black обнаружил несоответствия, применяем изменения
          if (blackExitCode != 0) {
            sh "poetry run -- black *.py"
          } else {
            echo "Форматирование кода без изменений."
          }
        }
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

