#!groovy

pipeline {
    agent {
        label 'jenkins-python3'
    }
    environment {
        PROJECT_KEY = "status_pin_api"
        TAG_ID = "STATUS_PIN_API"
        ENV_NAME = "${env.BRANCH_NAME}"
        REGISTRY_HOST = "us.gcr.io"
        DOCKER_PROTOCOL = "https://"
        KUBE_REPO_TARGET_DIR = 'kubernetes'
        SONAR_HOST_URL = "http://sonarqube.fsvas.com"
        SRC_BRANCH_ID=""
        SRC_GIT_COMMIT=""

        GCPROJECT_PROD = "${fs_gcloud_project_producao}"
        CLUSTER_PROD = "${fs_env_producao_cluster_name}"
        KUBERNETES_CREDENTIALS_PROD = "fs-env-producao"
        LOGIN_PROD = "${fs_account_service_producao}"

        GCPROJECT_HOMOL = "${fs_gcloud_project_homologacao}"
        CLUSTER_HOMOL = "${fs_env_homologacao_cluster_name}"
        KUBERNETES_CREDENTIALS_HOMOL = "fs-env-homologacao-terraform"
        NAMESPACE_PROJECT = "status-pin-api"
        LOGIN_HOMOL = "${fs_account_service_homologacao}"

    }
    options {
        buildDiscarder(logRotator(daysToKeepStr: '365', numToKeepStr: '8'))
        disableConcurrentBuilds()
        timestamps()
    }
    stages {
        stage('Select Environment (default:QA)') {
            steps {
                script {
                    def environmentOptions = "QA\nPROD\n"
                    env.ENV_TO_BUILD = "QA"
                    try {
                        def sleepingMinutes = 1
                        if(isUpstreamTriggered()) {
                            sleepingMinutes = 0
                        }
                        timeout(time:sleepingMinutes, unit:'MINUTES') {
                            env.ENV_TO_BUILD = input message: 'Selecione um ambiente a ser construído?', ok: 'Select!',
                                parameters: [
                                    choice(
                                        name: 'ENV_TO_BUILD',
                                        choices: environmentOptions,
                                        description: 'Para qual ambiente você quer construir?'
                                    )
                                ]
                        }
                    } catch (err) {
                        println("timeout expired:" + err)
                    }
                    echo "${env.ENV_TO_BUILD}"
                }
            }
        }
        stage('Authorize') {
            steps {
                script {
                    if(! (env.ENV_TO_BUILD in getUserBranchPrivileges())) {
                        currentBuild.result = 'ABORTED'
                        error("Not Authorized:" + User.current() + ", branch:" + env.GIT_BRANCH )
                        throw new Exception("Not Authorized:" + User.current() + ", branch:" + env.GIT_BRANCH )
                    }
                }
            }
        }
        stage('QA: Install') {
            when {
                anyOf {
 	   	            expression { env.ENV_TO_BUILD == "QA" }
                }
            }
            steps {
                script{
                    try {
                        sh "make install"
                    } catch(err) {
                        echo "Tests failed: $err"
                    }
                }
            }
        }
        stage('QA: Tests') {
            when {
                anyOf {
 	   	            expression { env.ENV_TO_BUILD == "QA" }
                }
            }
            steps {
                script{
                    sh "make tests"
                }
            }
            post {
               always {
                    junit allowEmptyResults: true, testResults: "$WORKSPACE/unit.xml"
                    junit '**//unit.xml'
                    step([
                        $class: 'CloverPublisher',
                        cloverReportDir: "$WORKSPACE/",
                        cloverReportFileName: '**/coverage.xml'
                    ])
               }
            }
        }
        stage('QA: Sonnar') {
            when {
                anyOf {
 	   	            expression { env.ENV_TO_BUILD == "QA" }
                }
            }
            steps {
                script{
                    try {
                        withSonarQubeEnv('SonarQube FS') {
                            sh '/usr/bin/sonar-scanner -Dsonar.login=${SONAR_AUTH_TOKEN}'
                        }
                    } catch(err) {
                        echo "Tests failed: $err"
                    }
                }
            }
            post {
               always {
                   publishHTML (target: [
                       allowMissing: true,
                       alwaysLinkToLastBuild: false,
                       keepAll: true,
                       reportDir: "$WORKSPACE/tests/Reports/html",
                       reportFiles: 'index.html',
                       reportName: "Coverage Report"
                   ])
               }
           }
        }
        stage('QA: Build Docker Images') {
            when {
                anyOf {
 	   	            expression { env.ENV_TO_BUILD == "QA" }
                }
            }
            steps {
                script {
                    docker.withRegistry("${DOCKER_PROTOCOL}${REGISTRY_HOST}", "gcr:${KUBERNETES_CREDENTIALS_PROD}") {
                        sh "gcloud config set account $LOGIN_HOMOL"
                        sh "gcloud config set project $GCPROJECT_PROD"
                        sh "docker build -t ${REGISTRY_HOST}/${GCPROJECT_PROD}/${PROJECT_KEY}:${env.BUILD_ID} -f ${WORKSPACE}/Dockerfile ${WORKSPACE}/."
                        sh "docker push ${REGISTRY_HOST}/${GCPROJECT_PROD}/${PROJECT_KEY}:${env.BUILD_ID}"
                    }
                }
            }
        }
        stage('QA: Deploy to QA') {
            when {
                anyOf {
 	   	            expression { env.ENV_TO_BUILD == "QA" }
                }
            }
            steps {
                script {
                    echo 'Setting configmap / deployment / service'
                    sh "gcloud config set account $LOGIN_HOMOL"
                    sh "gcloud config set project $GCPROJECT_HOMOL"
                    sh "gcloud container clusters get-credentials $CLUSTER_HOMOL"

                    sh "kubectl get pods -n $NAMESPACE_PROJECT"

                    def folder = "$WORKSPACE/$KUBE_REPO_TARGET_DIR/homol"
                    sh "sed -i s/###BUILDNO###/${BUILD_NUMBER}/g $folder/deployment.yaml"
                    sh "cd $folder && kubectl apply -n $NAMESPACE_PROJECT -f ."

                    sh 'sleep 8'
                    sh "kubectl get pods -n $NAMESPACE_PROJECT"
                }
            }
        }
        stage("QA: Criando Tag") {
            when {
                anyOf {
                    expression { env.ENV_TO_BUILD == 'QA' }
                }
            }
            steps {
                script {
                    sh "cd $WORKSPACE/ && git config --global user.email 'jenkins@null.com'"
                    sh "cd $WORKSPACE/ && git config --global user.name 'jenkins.fs'"
                    sh "cd $WORKSPACE/ && git tag -a ${env.TAG_ID}-${env.ENV_TO_BUILD}-${env.BUILD_NUMBER} -m ${env.TAG_ID}-${env.ENV_TO_BUILD}-${env.BUILD_NUMBER}"
                    sh "cd $WORKSPACE/ && git push --tags"
                    println("currentBuild.result:" + currentBuild.result)
                }
            }
        }
        stage('Select Build Number (default: abort build') {
            when {
                anyOf {
			        expression { env.ENV_TO_BUILD == "PROD" }
                }
            }
            steps {
                script {
                    env.BUILDNO_TO_BUILD = ""
	                def upstreamBranch = "QA"
	                println("upstream branch:" + upstreamBranch)
	                def upstreamBuilds = getBuilds()
	                env.BUILDNO_TO_BUILD = upstreamBuilds[0]
	                def sleepingMinutes = 1
                    timeout(time:sleepingMinutes, unit:'MINUTES') {
                        env.BUILDNO_TO_BUILD = input message: 'Selecione um Build Number da Upstream Job', ok: 'Select!',
                            parameters: [choice(name: 'BUILDNO_TO_BUILD', choices: upstreamBuilds, description: 'What build number do you want to deploy?')]
                    }
                    println("BUILD # TO BUILD: ${env.BUILDNO_TO_BUILD}")
                }
            }
        }
        stage('PROD: Deploy to PROD') {
            when {
                anyOf {
                    expression { env.ENV_TO_BUILD == "PROD" }
                }
            }
            steps {
                script {
                    echo 'Setting configmap / deployment / service'
                    sh "gcloud config set account $LOGIN_PROD"
                    sh "gcloud config set project $GCPROJECT_PROD"
                    sh "gcloud container clusters get-credentials $CLUSTER_PROD"

                    sh "kubectl get pods -n $NAMESPACE_PROJECT"

                    def folder = "$WORKSPACE/$KUBE_REPO_TARGET_DIR/prod"

                    sh "sed -i s/###BUILDNO###/${env.BUILDNO_TO_BUILD}/g $folder/deployment.yaml"

                    sh "sleep 5"
                    sh "cd $folder && kubectl apply -f . -n $NAMESPACE_PROJECT"

                    sh "kubectl get pods -n $NAMESPACE_PROJECT"

                    sh "cd $WORKSPACE/ && git config --global user.email 'jenkins@null.com'"
                    sh "cd $WORKSPACE/ && git config --global user.name 'jenkins.fs'"
                    sh "cd $WORKSPACE/ && git tag -a ${env.TAG_ID}-${env.ENV_TO_BUILD}-${env.BUILD_NUMBER} -m ${env.TAG_ID}-${env.ENV_TO_BUILD}-${env.BUILD_NUMBER}"
                    sh "cd $WORKSPACE/ && git push --tags"
                    println("currentBuild.result:" + currentBuild.result)
                }
            }
        }
        stage('Finish') {
            steps {
                script {
                    env.JOB_DESCRIPTION = "Here we go"
                    emailext (
                        subject: "Build finished: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                        attachLog: true,
                        compressLog: true,
                        body: """<p>Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'</p>
                                            <p>Check report in: <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>""",
                        to: 'marcus.peixoto@fs.com.br'
                    )
                    println("currentBuild.result:" + currentBuild.result)
                    notifyBuild(currentBuild.result)
                }
            }
            post {
                success{
                    script {
                        postSuccessBadge()
                    }
                    addBadge(icon:"success.gif", text:"This has been built successfuly")
                }
                aborted {
                    script {
                        postAbortBadge()
                    }
                    addInfoBadge("Info Badge Text for Aborted")
                }
                failure {
                    script {
                        postErrorBadge()
                    }
                    addErrorBadge("Info Badge Text for Error")
                }
            }
        }
    }
}

@NonCPS
def isUpstreamTriggered() {
    def isUpstreamTriggered = (currentBuild.rawBuild.getCause(hudson.model.Cause$UpstreamCause) != null)
    print("isUpstreamTriggered?:" + isUpstreamTriggered)
    return isUpstreamTriggered
}

@NonCPS
def getBuilds() {
    def jenkinsInstance = Jenkins.getInstance()
    def jenkinsProject = "status_pin_api/master"
    def project = jenkinsInstance.getItemByFullName(jenkinsProject)
    def recentBuilds = project.getBuilds()
    def qaBuilds = []
    recentBuilds.each() { item ->
        def actions = item.getActions()
        actions.each() {action ->
            if(action instanceof org.jenkinsci.plugins.workflow.cps.EnvActionImpl) {
                if(action.getEnvironment()["ENV_TO_BUILD"] == "QA") {
                    qaBuilds.push(item.getId())
                }
            }
        }
    }
    return qaBuilds
}

@NonCPS
def getUserBranchPrivileges() {
    def allowedBranches = []
    def currentUser = getBuildUser()
    println("Checking authorization for user:" + currentUser + ", branch:" + env.GIT_BRANCH  )
//    println(currentUser.getAuthorities())
    if ("Deploy-Admin" in currentUser.getAuthorities() )  {
       allowedBranches.add("QA")
       allowedBranches.add("PROD")
    } else if("Deploy-Homol" in currentUser.getAuthorities() ) {
       allowedBranches.add("QA")
       allowedBranches.add("PROD")
    } else if("Desenvolvedores" in currentUser.getAuthorities() || "Dev Plataformas" in currentUser.getAuthorities() ) {
       allowedBranches.add("QA")
       allowedBranches.add("PROD")
    }
    println("User allowed branches:" + allowedBranches.toString())
    return allowedBranches
}

@NonCPS
def getBuildUser() {
    def isUpstreamTriggered = (currentBuild.rawBuild.getCause(hudson.model.Cause$UpstreamCause) != null)
    print("isUpstreamTriggered?:" + isUpstreamTriggered)
    def buildUserName = ""
    if(isUpstreamTriggered) {
        def upstreamCause = currentBuild.rawBuild.getCause(hudson.model.Cause$UpstreamCause)
        println("causes:" + upstreamCause.getUpstreamCauses())
        try {
            buildUserName = upstreamCause.getUpstreamCauses()[0].getUserId()
            println("buildUserName:" + buildUserName)
        } catch (err) {
            buildUserName = upstreamCause.getUpstreamCauses()[0].getShortDescription()
            buildUserName = buildUserName.replaceAll("Started by BitBucket push by ","")
            println("buildUserName:" + buildUserName)
        }
    } else {
        buildUserName = currentBuild.getRawBuild().getCauses()[0].getUserId()
    }
    return User.get(buildUserName)
}

//
def getCommiter(folder) {
    println("Gathering SCM changes")
    def commitUserEmail = sh(script: "cd $folder && git log -n 1 --pretty='%ae'", returnStdout: true, encoding: "UTF-8").trim()
    def commitUserName = commitUserEmail.split("@")[0]
    return(commitUserName)
}

def getGitShow(folder) {
    println("Gathering Git Show")
    def gitShow = sh(script: "cd $folder && git log -n 1", returnStdout: true, encoding: "UTF-8").trim()
    println("gitLog:" + gitShow)
    gitShow = gitShow.replaceAll("\n","<br>")
    return(gitShow)
}

def postSuccessBadge() {
    removeSummaries()
    removeBadges()
    def summary = createSummary(icon:"completed.gif")
    def commiter = getCommiter("$WORKSPACE")
    def gitShow = getGitShow("$WORKSPACE")
    summary.appendText("<p><b>Build Result</b></p><ul>",false,false,false,"#000000")
    summary.appendText("<li>Commiter:" + commiter + "</li>",false,false,false,"#000000")
    summary.appendText("<li>Info:" + gitShow + "</li>",false,false,false,"#000000")
    summary.appendText("</ul>",false,false,false,"#000000")
}

def postAbortBadge() {
    removeSummaries()
    removeBadges()
    def summary = createSummary(icon:"delete.gif")
    def commiter = getCommiter("$WORKSPACE")
    def gitShow = getGitShow("$WORKSPACE")
    summary.appendText("<p><b>Build Result</b></p><ul>",false,false,false,"#000000")
    summary.appendText("<li>Commiter:" + commiter + "</li>",false,false,false,"#000000")
    summary.appendText("<li>Info:" + gitShow + "</li>",false,false,false,"#000000")
    summary.appendText("</ul>",false,false,false,"#000000")
}

def postErrorBadge() {
    removeSummaries()
    removeBadges()
    def summary = createSummary(icon:"error.gif")
    def commiter = getCommiter("$WORKSPACE")
    def gitShow = getGitShow("$WORKSPACE")
    summary.appendText("<p><b>Build Result</b></p><ul>",false,false,false,"#000000")
    summary.appendText("<li>Commiter:" + commiter + "</li>",false,false,false,"#000000")
    summary.appendText("<li>Info:" + gitShow + "</li>",false,false,false,"#000000")
    summary.appendText("</ul>",false,false,false,"#000000")
}

def notifyBuild(String buildStatus = 'STARTED') {
    // build status of null means successful
    buildStatus =  buildStatus ?: 'SUCCESSFUL'

    // Default values
    def colorName = 'RED'
    def colorCode = '#FF0000'
    def subject = "${buildStatus}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
    def summary = "${subject} (${env.BUILD_URL})"

    // Override default values based on build status
    if (buildStatus == 'STARTED') {
      color = 'YELLOW'
      colorCode = '#FFFF00'
    } else if (buildStatus == 'SUCCESSFUL') {
      color = 'GREEN'
      colorCode = '#00FF00'
    } else {
      color = 'RED'
      colorCode = '#FF0000'
    }

    // Send notifications
    slackSend (color: colorCode, message: summary, channel: '#projeto-plataforma')
}
