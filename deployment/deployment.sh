PROJECT_NAME="the-spymaster"
STAGE="dev"
DOCKER_TAG="$PROJECT_NAME-$STAGE-layer"
AWS_ACCOUNT_ID="096386908883"
CONTAINER_REPO_NAME="$DOCKER_TAG-image-repo"
ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"
CONTAINER_REPO_URL="$ECR_URL/$CONTAINER_REPO_NAME:latest"

sudo docker build -t "$DOCKER_TAG" .
sudo docker run -p 9000:8080 "$DOCKER_TAG"
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin "$ECR_URL"
aws ecr create-repository --repository-name "$CONTAINER_REPO_NAME" --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

sudo docker tag "$DOCKER_TAG:latest" "$CONTAINER_REPO_URL"
sudo docker push "$CONTAINER_REPO_URL"
