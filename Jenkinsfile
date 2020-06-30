pipeline {
    agent any
    options {
        // Running builds concurrently could cause a race condition with
        // building the Docker image.
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    environment {
        // Some branches have a "/" in their name (e.g. feature/new-and-cool)
        // Some commands, such as those tha deal with directories, don't
        // play nice with this naming convention.  Define an alias for the
        // branch name that can be used in these scenarios.
        BRANCH_ALIAS = sh(
            script: 'echo $BRANCH_NAME | sed -e "s#/#-#g"',
            returnStdout: true
        ).trim()
        DOCKER_BUILDKIT=1
        //spawns GITHUB_USR and GITHUB_PSW environment variables
        GITHUB_API=credentials('38b2e4a6-167a-40b2-be6f-d69be42c8190')
        GITHUB_CLIENT_ID=credentials('380f58b1-8a33-4a9d-a67b-354a9b0e792e')
        GITHUB_CLIENT_SECRET=credentials('71626c21-de59-4450-bfad-5034fd596fb2')
        GOOGLE_STT_KEY=credentials('287949f8-2ada-4450-8806-1fe2dd8e4c4d')
        WOLFRAM_ALPHA_KEY=credentials('f718e0a1-c19c-4c7f-af88-0689738ccaa1')
    }
    stages {
        stage('Lint & Format') {
            // Run PyLint and Black to check code quality.
            when {
                changeRequest target: 'dev'
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                     docker build \
                        --build-arg github_api_key=$GITHUB_API_PSW \
                        --file test/Dockerfile \
                        --target code-checker \
                        -t selene-linter:${BRANCH_ALIAS} .
                """
                labelledShell label: 'Running linter and formatter', script: 'docker run selene-linter:${BRANCH_ALIAS}'
            }
        }
        stage('Bootstrap DB') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                }
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                    docker build \
                        --target db-bootstrap \
                        --build-arg github_api_key=$GITHUB_API_PSW \
                        -t selene-db:${BRANCH_ALIAS} .
                """
                timeout(time: 5, unit: 'MINUTES')
                {
                    labelledShell label: 'Run database bootstrap script', script: """
                        docker run --net selene-net selene-db:${BRANCH_ALIAS}
                    """
                }
            }
        }
        stage('Account API Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                }
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                    docker build --target account-api-test -t selene-account:${BRANCH_ALIAS} .
                """
                timeout(time: 5, unit: 'MINUTES')
                {
                    labelledShell label: 'Running behave tests', script: """
                        docker run \
                            --net selene-net \
                            -v '$HOME/allure/selene/:/root/allure' \
                            selene-account:${BRANCH_ALIAS}
                    """
                }
            }
        }
        stage('Single Sign On API Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                }
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                    docker build \
                        --build-arg github_client_id=${GITHUB_CLIENT_ID} \
                        --build-arg github_client_secret=${GITHUB_CLIENT_SECRET} \
                        --target sso-api-test \
                        -t selene-sso:${BRANCH_ALIAS} .
                """
                timeout(time: 2, unit: 'MINUTES')
                {
                    labelledShell label: 'Running behave tests', script: """
                        docker run \
                            --net selene-net \
                            -v '$HOME/allure/selene/:/root/allure' \
                            selene-sso:${BRANCH_ALIAS}
                    """
                }
            }
        }
        stage('Public Device API Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                }
            }
            steps {
                labelledShell label: 'Building Docker image', script: """
                    docker build \
                        --build-arg google_stt_key=${GOOGLE_STT_KEY} \
                        --build-arg wolfram_alpha_key=${WOLFRAM_ALPHA_KEY} \
                        --target public-api-test \
                        -t selene-public:${BRANCH_ALIAS} .
                """
                timeout(time: 2, unit: 'MINUTES')
                {
                    labelledShell label: 'Running behave tests', script: """
                        docker run \
                            --net selene-net \
                            -v '$HOME/allure/selene/:/root/allure' \
                            selene-public:${BRANCH_ALIAS}
                    """
                }
            }
        }
    }
}
