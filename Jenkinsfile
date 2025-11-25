pipeline {
    agent any

    environment {
        AWS_REGION          = "ap-south-0" 
        ECR_REPO_URI        = "416521764601.dkr.ecr.ap-south-1.amazonaws.com/chatbot-backend" 
        EBS_APP_NAME        = "chatbot-app-backend" 
        EBS_ENV_NAME        = "Chatbot-app-backend-env" 
        S3_BUCKET_NAME      = "my-s3-bucket-001-demo"
        EBS_S3_BUCKET       = "elasticbeanstalk-ap-south-1-416521764601"
    }

    stages {
        stage('Deploy Backend') {
            when { changeset "backend/**" } 
            steps {
                script {
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
                
                // Create the Dockerrun.aws.json file 
                echo "Creating Dockerrun.aws.json..."
                writeFile file: 'Dockerrun.aws.json', text: """
                {
                  "AWSEBDockerrunVersion": "1",
                  "Image": {
                    "Name": "${env.IMAGE_NAME}",
                    "Update": "true"
                  },
                  "Ports": [
                    {
                      "ContainerPort": 5000
                    }
                  ]
                }
                """
                
                // 4. Zip the deployment file
                sh "zip -j deploy.zip Dockerrun.aws.json"
                
                // 5. Deploy to Elastic Beanstalk using AWS CLI
                echo "Deploying new version to Elastic Beanstalk..."
                
                script {
                    withAWS(region: "${AWS_REGION}") {
                    
                        def versionLabel = "v-${env.BUILD_NUMBER}"
                        def s3Key = "deploy/${versionLabel}.zip" 

                        // 5a. Upload zip to the EBS S3 bucket
                        echo "Uploading deploy.zip to EBS S3 bucket..."
                        sh "aws s3 cp deploy.zip s3://${EBS_S3_BUCKET}/${s3Key} --region ${AWS_REGION}"

                        // 5b. Create new application version
                        echo "Creating new application version: ${versionLabel}..."
                        sh """
                            aws elasticbeanstalk create-application-version \
                              --region "${AWS_REGION}" \
                              --application-name "${EBS_APP_NAME}" \
                              --version-label "${versionLabel}" \
                              --source-bundle S3Bucket="${EBS_S3_BUCKET}",S3Key="${s3Key}"
                        """

                        // 5c. Update the environment to the new version
                        echo "Updating environment ${EBS_ENV_NAME}..."
                        sh """
                            aws elasticbeanstalk update-environment \
                              --region "${AWS_REGION}" \
                              --environment-name "${EBS_ENV_NAME}" \
                              --version-label "${versionLabel}"
                        """

                        // 5d. Wait for deployment to finish
                        echo "Waiting for environment update to complete..."
                        sh """
                            aws elasticbeanstalk wait environment-updated \
                              --region "${AWS_REGION}" \
                              --environment-name "${EBS_ENV_NAME}"
                        """
                        echo "✅ Backend deployment completed successfully!"
                    }
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
                    // This command syncs and makes files public
                    sh "aws s3 sync ./frontend s3://${S3_BUCKET_NAME} --delete --acl public-read --region ${AWS_REGION}"
                }
            }
        }
    }
}

// pipeline {
//     agent any // Use any available Jenkins worker

//     // =========================================================================
//     // == ⬇️⬇️ (1) YOU MUST CHANGE THESE VALUES ⬇️⬇️ ==
//     // =========================================================================
//     environment {
//         AWS_REGION          = "ap-south-1" 
//         ECR_REPO_URI        = "416521764601.dkr.ecr.ap-south-1.amazonaws.com/chatbot-backend" 
//         EBS_APP_NAME        = "chatbot-app-backend" 
//         EBS_ENV_NAME        = "Chatbot-app-backend-env" 
//         S3_BUCKET_NAME      = "chatbot-app-frontend"
//         EBS_S3_BUCKET       = "elasticbeanstalk-ap-south-1-416521764601"
//     }

//     stages {
        
//         // =================================================================
//         // == 📦 STAGE 1: BACKEND DEPLOYMENT (FINAL VERSION) 📦 ==
//         // =================================================================
//         stage('Deploy Backend') {
//             when { changeset "backend/**" } 
//             steps {
//                 script {
//                     env.IMAGE_NAME = "${ECR_REPO_URI}:${env.BUILD_NUMBER}"
//                 }
                
//                 echo "✅ Change detected in /backend. Starting Docker build and deploy..."
                
//                 // 1. Build the Docker Image
//                 echo "Building image: ${env.IMAGE_NAME}"
//                 sh "docker build -t ${env.IMAGE_NAME} ./backend"
                
//                 // 2. Log in to ECR & Push the Image
//                 withAWS(region: "${AWS_REGION}") {
//                     echo "Logging into ECR..."
//                     sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URI}"
                    
//                     echo "Pushing image to ECR..."
//                     sh "docker push ${env.IMAGE_NAME}"
//                 }
                
//                 // 3. Create the Dockerrun.aws.json file
//                 echo "Creating Dockerrun.aws.json..."
//                 sh """
//                 echo '{ \\
//                   "AWSEBDockerrunVersion": "1", \\
//                   "Image": { \\
//                     "Name": "${env.IMAGE_NAME}", \\
//                     "Update": "true" \\
//                   }, \\
//                   "Ports": [ \\
//                     { \\
//                       "ContainerPort": 5000 \\
//                     } \\
//                   ] \\
//                 }' > Dockerrun.aws.json
//                 """
                
//                 // 4. Zip the deployment file
//                 sh "zip -j deploy.zip Dockerrun.aws.json"
                
//                 // 5. Deploy to Elastic Beanstalk using AWS CLI
//                 echo "Deploying new version to Elastic Beanstalk..."
                
//                 script {
//                     withAWS(region: "${AWS_REGION}") {

//                         def versionLabel = "v-${env.BUILD_NUMBER}"
//                         def s3Key = "deploy/${versionLabel}.zip" 

//                         // 5a. Upload zip to the EBS S3 bucket
//                         echo "Uploading deploy.zip to EBS S3 bucket..."
//                         sh "aws s3 cp deploy.zip s3://${EBS_S3_BUCKET}/${s3Key} --region ${AWS_REGION}"

//                         // 5b. Create new application version
//                         echo "Creating new application version: ${versionLabel}..."
//                         sh """
//                             aws elasticbeanstalk create-application-version \
//                                 --region "${AWS_REGION}" \
//                                 --application-name "${EBS_APP_NAME}" \
//                                 --version-label "${versionLabel}" \
//                                 --source-bundle S3Bucket="${EBS_S3_BUCKET}",S3Key="${s3Key}"
//                         """

//                         // 5c. Update the environment to the new version
//                         echo "Updating environment ${EBS_ENV_NAME}..."
//                         sh """
//                             aws elasticbeanstalk update-environment \
//                                 --region "${AWS_REGION}" \
//                                 --environment-name "${EBS_ENV_NAME}" \
//                                 --version-label "${versionLabel}"
//                         """

//                         // 5d. Wait for deployment to finish
//                         echo "Waiting for environment update to complete..."
//                         sh """
//                             aws elasticbeanstalk wait environment-updated \
//                                 --region "${AWS_REGION}" \
//                                 --environment-name "${EBS_ENV_NAME}"
//                         """
//                         echo "✅ Backend deployment completed successfully!"
//                     }
//                 }
//             }
//         }

//         // =================================================================
//         // == 🌐 STAGE 2: FRONTEND DEPLOYMENT 🌐 ==
//         // =================================================================
//         stage('Deploy Frontend') {
//             when { changeset "frontend/**" } 
//             steps {
//                 echo "✅ Change detected in /frontend. Syncing files to S3..."
                
//                 withAWS(region: "${AWS_REGION}") {
//                     // This command syncs and makes files public
//                     sh "aws s3 sync ./frontend s3://${S3_BUCKET_NAME} --delete --acl public-read --region ${AWS_REGION}"
//                 }
//             }
//         }
//     }
// }