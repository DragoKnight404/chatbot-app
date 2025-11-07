pipeline {
    agent any // Use any available Jenkins worker

    // =========================================================================
    // == ⬇️⬇️ (1) YOU MUST CHANGE THESE VALUES ⬇️⬇️ ==
    // =========================================================================
    environment {
        AWS_REGION          = "ap-south-1" // Your AWS Region
        ECR_REPO_URI        = "416521764601.dkr.ecr.ap-south-1.amazonaws.com/chatbot-backend" // Paste the ECR URI
        EBS_APP_NAME        = "chatbot-app-backend" // The name of your EBS Application
        EBS_ENV_NAME        = "Chatbot-app-backend-env" // The name of your EBS Environment
        S3_BUCKET_NAME      = "chatbot-app-frontend" // Your S3 bucket for the frontend
    }

    stages {
        
        // =================================================================
        // == 📦 STAGE 1: BACKEND DEPLOYMENT (FIXED) 📦 ==
        // =================================================================
        stage('Deploy Backend') {
            when { changeset "backend/**" } 
            steps {
                // --- FIX 2: Define IMAGE_NAME using 'env' for proper scope ---
                script {
                    // This makes the variable available to all steps in this stage
                    env.IMAGE_NAME = "${ECR_REPO_URI}:${env.BUILD_NUMBER}"
                }
                
                echo "✅ Change detected in /backend. Starting Docker build and deploy..."
                
                // 1. Build the Docker Image
                echo "Building image: ${env.IMAGE_NAME}"
                sh "docker build -t ${env.IMAGE_NAME} ./backend"
                
                // --- FIX 1: Replaced 'docker.withRegistry' with explicit AWS CLI login ---
                // This is much more reliable and uses the IAM role from the withAWS plugin.
                withAWS(region: "${AWS_REGION}") {
                    echo "Logging into ECR..."
                    // This command gets a password from ECR and pipes it to 'docker login'
                    sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URI}"
                    
                    echo "Pushing image to ECR..."
                    sh "docker push ${env.IMAGE_NAME}"
                }
                // --- END OF FIX 1 ---
                
                // 3. Create the Dockerrun.aws.json file for EBS
                echo "Creating Dockerrun.aws.json..."
                sh """
                echo '{ \\
                  "AWSEBDockerrunVersion": "1", \\
                  "Image": { \\
                    "Name": "${env.IMAGE_NAME}", \\
                    "Update": "true" \\
                  }, \\
                  "Ports": [ \\
                    { \\
                      "ContainerPort": 5000 \\
                    } \\
                  ] \\
                }' > Dockerrun.aws.json
                """
                
                // 4. Zip the deployment file
                sh "zip -j deploy.zip Dockerrun.aws.json"
                
                // 5. Deploy to Elastic Beanstalk
                echo "Deploying new version to Elastic Beanstalk..."
                withAWS(region: "${AWS_REGION}") {
                    ebDeploy(
                        applicationName: "${EBS_APP_NAME}", 
                        environmentName: "${EBS_ENV_NAME}", 
                        versionLabel: "v-${env.BUILD_NUMBER}", 
                        zipFile: "deploy.zip"
                    )
                }
            }
        }

        // =================================================================
        // == 🌐 STAGE 2: FRONTEND DEPLOYMENT 🌐 ==
        // =================================================================
        stage('Deploy Frontend') {
            when { changeset "frontend/**" } 
            steps {
                echo "✅ Change detected in /frontend. Syncing files to S3..."
                
                withAWS(region: "${AWS_REGION}") {
                    // --- 🚀 FIX 2: Added '--acl public-read' ---
                    // This flag automatically makes all uploaded files public
                    sh "aws s3 sync ./frontend s3://${S3_BUCKET_NAME} --delete --acl public-read"
                }
            }
        }
    }
}