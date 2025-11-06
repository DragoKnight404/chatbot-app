pipeline {
    agent any // Use any available Jenkins worker

    // =========================================================================
    // == ⬇️⬇️ (1) YOU MUST CHANGE THESE VALUES ⬇️⬇️ ==
    // =========================================================================
    environment {
        AWS_REGION          = "ap-south-1" // Your AWS Region
        ECR_REPO_URI        = "http://416521764601.dkr.ecr.ap-south-1.amazonaws.com/chatbot-backend" // Paste the ECR URI from Step 2
        EBS_APP_NAME        = "chatbot-app-backend" // The name of your EBS Application
        EBS_ENV_NAME        = "Chatbot-app-backend-env" // The name of your EBS Environment
        S3_BUCKET_NAME      = "chatbot-app-frontend" // Your S3 bucket for the frontend
    }

    stages {
        
        // =================================================================
        // == 📦 STAGE 1: BACKEND DEPLOYMENT 📦 ==
        // == This only runs if you change files in the 'backend' folder ==
        // =================================================================
        stage('Deploy Backend') {
            when { changeset "backend/**" } // Detects changes in the backend folder
            steps {
                echo "✅ Change detected in /backend. Starting Docker build and deploy..."
                
                // 1. Build the Docker Image
                // We'll tag it with the ECR URI and the build number
                script {
                    IMAGE_NAME = "${ECR_REPO_URI}:${env.BUILD_NUMBER}"
                }
                echo "Building image: ${IMAGE_NAME}"
                sh "docker build -t ${IMAGE_NAME} ./backend"
                
                // 2. Log in to ECR & Push the Image
                // 'ecr:ap-south-1' tells Jenkins to use the IAM Role from Step 1
                docker.withRegistry("https://${ECR_REPO_URI}", "ecr:${AWS_REGION}") {
                    echo "Logging into ECR and pushing image..."
                    sh "docker push ${IMAGE_NAME}"
                }
                
                // 3. Create the Dockerrun.aws.json file for EBS
                // This file tells EBS which image to pull
                echo "Creating Dockerrun.aws.json..."
                sh """
                echo '{ \\
                  "AWSEBDockerrunVersion": "1", \\
                  "Image": { \\
                    "Name": "${IMAGE_NAME}", \\
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
                // EBS only accepts a .zip file, even if it's just one file
                sh "zip -j deploy.zip Dockerrun.aws.json"
                
                // 5. Deploy to Elastic Beanstalk
                echo "Deploying new version to Elastic Beanstalk..."
                withAWS(region: "${AWS_REGION}") {
                    ebDeploy(
                        applicationName: "${EBS_APP_NAME}", 
                        environmentName: "${EBS_ENV_NAME}", 
                        versionLabel: "v-${env.BUILD_NUMBER}", // e.g., v-42
                        zipFile: "deploy.zip"
                    )
                }
            }
        }

        // =================================================================
        // == 🌐 STAGE 2: FRONTEND DEPLOYMENT 🌐 ==
        // == This only runs if you change files in the 'frontend' folder ==
        // =================================================================
        stage('Deploy Frontend') {
            when { changeset "frontend/**" } // Detects changes in the frontend folder
            steps {
                echo "✅ Change detected in /frontend. Syncing files to S3..."
                
                // 1. Use the 'withAWS' helper (from the plugin) to sync to S3
                withAWS(region: "${AWS_REGION}") {
                    s3Upload(
                        bucket: "${S3_BUCKET_NAME}", // The bucket to upload to
                        source: 'frontend',          // The local folder to upload
                        workingDir: '.'              // Where to find the 'frontend' folder
                    )
                }
            }
        }
    }
}