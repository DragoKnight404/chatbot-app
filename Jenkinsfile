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
        EBS_S3_BUCKET       = "elasticbeanstalk-ap-south-1-416521764601" // EBS's private S3 bucket
    }

    stages {
        
        // =D===============================================================
        // == 📦 STAGE 1: BACKEND DEPLOYMENT (FIXED) 📦 ==
        // =================================================================
        stage('Deploy Backend') {
            when { changeset "backend/**" } 
            steps {
                script {
                    // Define variable for all steps
                    env.IMAGE_NAME = "${ECR_REPO_URI}:${env.BUILD_NUMBER}"
                }
                
                echo "✅ Change detected in /backend. Starting Docker build and deploy..."
                
                // 1. Build the Docker Image
                echo "Building image: ${env.IMAGE_NAME}"
                sh "docker build -t ${env.IMAGE_NAME} ./backend"
                
                // 2. Log in to ECR & Push the Image
                withAWS(region: "${AWS_REGION}") {
                    echo "Logging into ECR..."
                    sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URI}"
                    
                    echo "Pushing image to ECR..."
                    sh "docker push ${env.IMAGE_NAME}"
                }
                
                // 3. Create the Dockerrun.aws.json file
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
                
                // --- 🚀 NEW AWS CLI DEPLOYMENT (REPLACES ebDeploy) 🚀 ---
                
                // 5. Deploy to Elastic Beanstalk using AWS CLI
                echo "Deploying new version to Elastic Beanstalk..."
                withAWS(region: "${AWS_REGION}") {
                    
                    def versionLabel = "v-${env.BUILD_NUMBER}"
                    def s3Key = "deploy/${versionLabel}.zip" // The path in the S3 bucket

                    // 5a. Upload zip to the EBS S3 bucket
                    echo "Uploading deploy.zip to EBS S3 bucket..."
                    sh "aws s3 cp deploy.zip s3://${EBS_S3_BUCKET}/${s3Key}"

                    // 5b. Create new application version
                    echo "Creating new application version: ${versionLabel}..."
                    sh """
                        aws elasticbeanstalk create-application-version \
                          --application-name "${EBS_APP_NAME}" \
                          --version-label "${versionLabel}" \
                          --source-bundle S3Bucket="${EBS_S3_BUCKET}",S3Key="${s3Key}"
                    """

                    // 5c. Update the environment to the new version
                    echo "Updating environment ${EBS_ENV_NAME}..."
                    sh """
                        aws elasticbeanstalk update-environment \
                          --environment-name "${EBS_ENV_NAME}" \
                          --version-label "${versionLabel}"
                    """
                }
                // --- END OF NEW DEPLOYMENT STEPS ---
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