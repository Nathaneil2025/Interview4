pipeline {
    agent any
    
    environment {
        AWS_REGION = 'eu-central-1'
        ECR_REPO = 'interview4-app'
        APP_EC2_IP = '192.168.3.12'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                    credentialsId: 'github-creds', 
                    url: 'https://github.com/Nathaneil2025/Interview4.git'
            }
        }
        
        stage('Lint') {
            steps {
                sh '''
                    cd ${WORKSPACE}
                    python3 -m pip install --user flake8
                    python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                '''
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    cd ${WORKSPACE}
                    python3 -m pip install --user pytest httpx fastapi uvicorn
                    python3 -m pytest -v || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    def accountId = sh(script: 'aws sts get-caller-identity --query Account --output text', returnStdout: true).trim()
                    env.ECR_URL = "${accountId}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                }
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                    docker build -t ${ECR_REPO}:${IMAGE_TAG} .
                    docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}
                    docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URL}/${ECR_REPO}:latest
                '''
            }
        }
        
        stage('Push to ECR') {
            steps {
                sh '''
                    docker push ${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}
                    docker push ${ECR_URL}/${ECR_REPO}:latest
                '''
            }
        }
        
        stage('Deploy to App EC2') {
            steps {
                sshagent(['app-ec2-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ec2-user@${APP_EC2_IP} '
                            export AWS_REGION=${AWS_REGION}
                            export ECR_URL=${ECR_URL}
                            export ECR_REPO=${ECR_REPO}
                            
                            # Login to ECR
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                            
                            # Pull latest image
                            docker pull ${ECR_URL}/${ECR_REPO}:latest
                            
                            # Start GREEN container on port 8081
                            docker run -d --name interview4-app-green -p 8081:8000 ${ECR_URL}/${ECR_REPO}:latest
                            
                            # Health check GREEN
                            sleep 5
                            if curl -f http://localhost:8081/health; then
                                echo "GREEN is healthy, switching traffic..."
                                
                                # Stop BLUE (old container)
                                docker stop interview4-app || true
                                docker rm interview4-app || true
                                
                                # Stop GREEN and restart on production port
                                docker stop interview4-app-green
                                docker rm interview4-app-green
                                docker run -d --name interview4-app -p 8080:8000 ${ECR_URL}/${ECR_REPO}:latest
                                
                                echo "Deployment successful - switched to new version"
                            else
                                echo "GREEN health check failed, rolling back..."
                                docker stop interview4-app-green || true
                                docker rm interview4-app-green || true
                                exit 1
                            fi
                        '
                    """
                }
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    sleep 10
                    curl -f http://${APP_EC2_IP}:8080/health || exit 1
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}