# **Detailed Lecture Notes: Deploying a Dockerized Flask Application on AWS EC2 Using GitHub Actions (CI/CD)**

## **1. Introduction: What are we going to deploy?**

In the previous lecture, we successfully:

- Created a Docker image for our Flask application.
- Launched a Docker container using that image.
- Tested the application locally.
- Verified that the application was working correctly inside the container.

However, the application was only running on our local machine. To make it accessible to other users over the internet, we need to deploy it to a cloud server.

In this lecture, we will deploy the existing Dockerized Flask application using:

| Technology                | Purpose                                                        |
| ------------------------- | -------------------------------------------------------------- |
| AWS EC2                   | Provides a cloud-based virtual machine to host the application |
| AWS ECR                   | Stores Docker images in a private container registry           |
| GitHub Actions            | Automates the CI/CD pipeline                                   |
| GitHub Secrets            | Securely stores AWS credentials and configuration              |
| Self-hosted GitHub Runner | Executes deployment jobs on our EC2 instance                   |
| Docker                    | Runs the application inside a container                        |

### **Overall deployment architecture**

**Developer updates application code**

Changes are pushed to the GitHub main branch

**GitHub Actions**

Automatically triggers the CI/CD workflow

**Job 1: Continuous Integration (CI)**

- Authenticate with AWS
- Validate ECR configuration
- Build the Docker image
- Push the image to AWS ECR

**Job 2: Continuous Deployment (CD)**

Runs on the self-hosted runner installed on EC2

- Authenticate with AWS/ECR
- Pull or access the newly built image
- Run the Docker container

**Application deployed on AWS EC2**

Accessible using the EC2 public IP and port 8080

## **2. Understanding CI/CD in simple terms**

The instructor introduces Continuous Integration and Continuous Deployment (CI/CD).

### **A. Continuous Integration (CI)**

Continuous Integration means automatically integrating and validating code changes whenever developers push updates to a shared repository.

In this project, when we push code to the `main` branch:

1. GitHub detects the new commit.
2. GitHub Actions automatically triggers the workflow.
3. AWS credentials are retrieved securely from GitHub Secrets.
4. The Docker image is built.
5. The image is pushed to AWS Elastic Container Registry (ECR).

**In simple terms:** CI takes the latest application code and builds a Docker image, then stores that image in AWS ECR.

### **B. Continuous Deployment (CD)**

Continuous Deployment means automatically deploying the newly built application to the target server after the integration stage succeeds.

In this project:

1. The deployment job runs on a self-hosted GitHub runner installed on EC2.
2. It uses AWS credentials to access the ECR repository.
3. It obtains the Docker image.
4. It starts the application inside a Docker container.
5. The application becomes accessible through the EC2 instance's public IP address.

**In simple terms:** CD takes the latest Docker image and runs it on the EC2 server.

### **Complete CI/CD sequence**

| Stage | What happens?                                            |
| ----- | -------------------------------------------------------- |
| 1     | Developer modifies application code                      |
| 2     | Developer pushes changes to GitHub `main`                |
| 3     | GitHub Actions workflow is triggered                     |
| 4     | CI authenticates with AWS                                |
| 5     | CI builds Docker image                                   |
| 6     | CI pushes image to ECR                                   |
| 7     | CD runs on the EC2 self-hosted runner                    |
| 8     | CD retrieves the latest image and runs the container     |
| 9     | Application becomes accessible through the EC2 public IP |

**Important:** GitHub Actions is responsible for automating these operations. We do not need to manually rebuild and deploy the application every time we push a code change.

## **3. Creating the GitHub Actions workflow directory**

The instructor creates a specific folder structure inside the application repository.

At the root of the project, create:

```
project/
│
├── .github/
│   └── workflows/
│       └── main.yaml
│
├── app.py
├── Dockerfile
├── requirements.txt
└── ...
```

### **Steps**

1. Open the application project.
2. Create a folder named `.github`.
3. Inside `.github`, create another folder named `workflows`.
4. Inside `workflows`, create a YAML file named `main.yaml`.

**Why this folder structure?**

GitHub Actions automatically looks for workflow configuration files inside:

```
.github/workflows/
```

The `main.yaml` file defines the CI/CD pipeline, including its trigger conditions, jobs, authentication, Docker image creation, and deployment instructions.

## **4. Understanding the&#x20;**`main.yaml`**&#x20;workflow**

The instructor describes the workflow with the name:

```
name: Deploy Application Docker Image to EC2 Instance
```

The workflow contains two main jobs:

1. `integration` – Continuous Integration.
2. `deployment` – Continuous Deployment.

The exact YAML commands and complete configuration are not read aloud in the transcript, so the notes below explain the operations and configuration described rather than inventing an exact workflow file.

### **Job 1: Continuous Integration**

The integration job performs authentication and Docker image creation.

Its responsibilities are:

- Access AWS credentials stored in GitHub Secrets.
- Authenticate with AWS.
- Validate the ECR repository configuration.
- Build the Docker image using the project's Dockerfile.
- Push the image to the ECR repository.

The resulting image is stored in AWS ECR so that the deployment stage can use it.

### **Job 2: Continuous Deployment**

The deployment job executes using a **self-hosted GitHub Actions runner**.

Its responsibilities are:

- Run on the EC2 instance where the self-hosted runner has been configured.
- Retrieve AWS credentials from GitHub Secrets.
- Authenticate with ECR.
- Run the Docker deployment command.
- Make the application available through the EC2 server.

The instructor specifically explains that the deployment job uses a self-hosted runner rather than relying only on GitHub-hosted runners.

We will configure this runner in the upcoming steps.

## **5. Understanding GitHub Actions and GitHub Secrets**

### **Step 1: Open GitHub Actions**

1. Open your GitHub repository.
2. Click the **Actions** tab.
3. This is where you can view workflow executions, CI/CD jobs, and their results.

GitHub Actions is the platform that executes the automation instructions defined in `.github/workflows/main.yaml`.

### **Step 2: Open GitHub Secrets**

We need to configure AWS credentials so that GitHub Actions can authenticate with AWS.

Follow these steps:

1. Open the repository on GitHub.
2. Go to **Settings**.
3. Find **Secrets and variables** in the sidebar.
4. Expand the dropdown.
5. Select **Actions**.
6. Click the option to create a new repository secret.

The instructor explains that we need to add the AWS credentials obtained when creating an IAM user.

### **Step 3: Add AWS credentials**

Two important credentials are required:

| Secret name             | Value                            |
| ----------------------- | -------------------------------- |
| `AWS_ACCESS_KEY_ID`     | AWS IAM user's access key ID     |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM user's secret access key |

The configuration concept is:

```
Name: AWS_ACCESS_KEY_ID
Value: <AWS access key ID>
```

```
Name: AWS_SECRET_ACCESS_KEY
Value: <AWS secret access key>
```

**Important distinction:**

- The secret name is the identifier that the workflow uses.
- The secret value is the actual credential.
- The workflow retrieves these values using GitHub's `secrets` context.

For example:

```
${{ secrets.AWS_ACCESS_KEY_ID }}
${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

This prevents credentials from having to be written directly into the workflow file.

**Security recommendation**

Never commit AWS access keys or secret access keys directly into GitHub source code. Use narrowly scoped IAM permissions. Prefer short-lived AWS credentials through GitHub OIDC where practical; static access keys should be rotated and protected.

## **6. Creating an AWS ECR repository**

### **What is AWS ECR?**

AWS ECR stands for **Amazon Elastic Container Registry**.

It is a managed container registry service provided by AWS that allows us to store and manage Docker images.

In this project:

- Docker builds the application image.
- ECR stores that image.
- The EC2 deployment environment uses the image to run the application.

Think of ECR as a storage location for Docker images, similar in concept to Docker Hub, but integrated with AWS.

### **Step-by-step ECR repository creation**

1. Log in to the AWS Management Console.
2. Use the AWS search bar.
3. Search for `ECR`.
4. Open **Elastic Container Registry**.
5. Navigate to the Repositories section.
6. Click **Create repository**.
7. Enter the repository name.
8. Create the repository.

The instructor has already created a repository named:

```
segment
```

This is the repository name that will be used in the workflow configuration.

### **Step 2: Configure the ECR repository name in GitHub Secrets**

The instructor explains that the repository name must also be made available to GitHub Actions.

For example:

```
Name: ECR_REPO
Value: segment
```

The workflow can then retrieve it using:

```
${{ secrets.ECR_REPO }}
```

The repository name is not itself a password or secret, but storing it as a GitHub repository variable or secret is a convenient way to configure the workflow.

### **Credentials/configuration required so far**

| Name                    | Purpose                                   |
| ----------------------- | ----------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | AWS authentication                        |
| `AWS_SECRET_ACCESS_KEY` | AWS authentication                        |
| `ECR_REPO`              | Identifies the ECR repository (`segment`) |

The AWS region and AWS account ID may also be needed by the workflow to construct the ECR registry URL. These are not specified explicitly in the spoken transcript.

## **7. Creating a self-hosted GitHub Actions runner**

This is one of the most important parts of the lecture.

### **What is a self-hosted runner?**

A GitHub Actions runner is the machine that executes the commands defined in a workflow job.

There are two common types:

| Runner               | Description                                      |
| -------------------- | ------------------------------------------------ |
| GitHub-hosted runner | A virtual machine managed by GitHub              |
| Self-hosted runner   | A machine that we manage and configure ourselves |

In this project, the instructor uses the EC2 instance as the self-hosted runner.

This means the deployment job can execute directly on the EC2 machine.

### **Why use a self-hosted runner here?**

The instructor wants the deployment job to execute on the same EC2 instance where the application will run.

This makes it possible for the workflow to execute Docker commands on the target machine.

**GitHub-hosted runner**

Runs on infrastructure managed by GitHub.

**Self-hosted runner**

Runs on our own EC2 instance, which we configure and manage.

### **Step 1: Open runner settings**

1. Open your GitHub repository.
2. Click **Settings**.
3. Navigate to **Actions**.
4. Open **Runners**.
5. Click **New self-hosted runner**.

### **Step 2: Select the operating system**

GitHub displays operating system options such as:

- Linux
- Windows
- macOS

The instructor selects:

Linux

**Why Linux?**

The EC2 instance in this lecture is running Ubuntu, which is a Linux-based operating system.

Therefore, Linux is the appropriate runner configuration.

### **Step 3: Open the EC2 instance**

Now the instructor switches to the AWS Management Console.

1. Search for EC2.
2. Open the EC2 service.
3. Navigate to **Instances**.
4. Locate the running instance.
5. The instructor uses a `t2.medium` instance.
6. Select the instance.
7. Click **Connect**.
8. Click **Connect** again in the connection interface to open the EC2 terminal.

The instructor is now connected to the Ubuntu EC2 instance.

The t2.medium instance is the machine used in this particular lecture, not a mandatory instance type for every deployment.

## **8. Installing the self-hosted runner on EC2**

After selecting Linux, GitHub displays commands that must be executed on the EC2 instance.

The instructor follows the commands in the order shown by GitHub.

### **Step 1: Create the runner directory**

The first command creates a folder called:

```
mkdir actions-runner
```

This directory will contain the GitHub Actions runner files.

Move into the directory:

```
cd actions-runner
```

### **Step 2: Download the latest runner package**

GitHub provides a command to download the runner package.

The instructor copies the command shown on the GitHub runner setup page and pastes it into the EC2 terminal.

The downloaded package contains the files needed to install and configure the self-hosted runner.

**Important:** The exact download URL is generated by GitHub and may change with runner releases. Use the command displayed in your own repository's runner setup page rather than copying an old URL.

### **Step 3: Validate the download hash**

After downloading the package, GitHub provides a hash-validation command.

The instructor copies and executes this command.

The purpose of this step is to verify that the downloaded runner package matches the expected checksum.

The instructor emphasizes that the validation should return:

OK

If the result is not `OK`, the package should not be trusted. The instructor advises creating a new self-hosted runner configuration and restarting the setup process.

**Why is hash validation necessary?**

It helps detect:

- Corrupted downloads.
- Incomplete downloads.
- Files that do not match the expected package.

### **Step 4: Extract the runner package**

After successful hash validation, execute the extraction command provided by GitHub.

This extracts the runner package into the `actions-runner` directory.

At this point, the runner software is downloaded and extracted, but it has not yet been registered with GitHub.

### **Step 5: Configure the runner**

GitHub provides a configuration command to start the runner configuration process.

The instructor copies and executes it.

During configuration, GitHub asks several questions.

| Prompt                   | Instructor's action                                       |
| ------------------------ | --------------------------------------------------------- |
| Runner group             | Press Enter to use the default                            |
| Runner name              | Press Enter to accept the suggested name/IP-based default |
| Additional configuration | Follow the displayed prompts                              |

The instructor accepts the default runner group and runner name.

After completing the configuration, the terminal displays a successful registration message:

```
Runner successfully added
```

This means the EC2 machine has been registered as a self-hosted runner in the GitHub repository.

### **Step 6: Start the runner**

After configuration, GitHub provides another command to start the runner.

The instructor copies and executes it.

The terminal displays messages indicating:

```
Connected to GitHub
Listening for jobs
```

This is an important confirmation.

It means:

- The runner successfully connected to GitHub.
- It is registered.
- It is waiting for a GitHub Actions workflow job.

### **Step 7: Verify the runner in GitHub**

Return to:

```
Repository
   → Settings
      → Actions
         → Runners
```

Refresh the page.

The newly registered runner should appear in the list.

The instructor observes the runner using the EC2 private IP:

```
172.31.0.106
```

Its status is shown as:

```
Idle
```

**What does Idle mean?**

The runner is connected to GitHub and ready to execute a job, but no job is currently assigned to it.

### **Step 8: Stop the runner temporarily**

The instructor then terminates the runner process from the EC2 terminal.

After refreshing the GitHub runners page, the runner status changes to:

Offline

This demonstrates the relationship between the runner process and its GitHub status.

- Runner process running → Online/Idle or Busy.
- Runner process stopped → Offline.

**Important operational note**

Stopping the runner process does not unregister the runner. It simply makes the registered runner unavailable until the process is started again.

In production, the runner should be configured to run persistently as a service, rather than manually starting it for every deployment.

## **9. Installing Docker on the EC2 instance**

The instructor now checks whether Docker is already installed on the EC2 instance.

### **Step 1: Verify Docker installation**

Run:

```
docker --version
```

The instructor observes that Docker is not installed.

Therefore, Docker must be installed before the EC2 instance can run the application container.

### **Step 2: Update the Ubuntu package index**

The instructor copies the first installation command from the provided instructions and executes it.

```
sudo apt update
```

**Purpose:**

- Updates the local package index.
- Retrieves the latest package information from configured repositories.
- Helps Ubuntu identify the available package versions.

### **Step 3: Upgrade existing packages**

The next command is:

```
sudo apt upgrade
```

This upgrades installed packages for which updates are available.

The instructor executes the command and waits while Ubuntu downloads and installs the required packages.

The terminal displays download and installation progress, including the approximate percentage completed.

When the process asks for confirmation, the instructor enters:

```
Y
```

The installation continues.

### **Step 4: Handle the package configuration screen**

During the upgrade, Ubuntu displays an interactive configuration screen.

The instructor:

1. Presses Enter when prompted.
2. Uses the Tab key to move the cursor to the `OK` option.
3. Presses Enter again to confirm.

This allows the package upgrade process to continue.

### **Step 5: Download the Docker installation script**

The instructor then executes the next command from the installation instructions to download Docker's installation script.

The script is obtained from:

```
get.docker.com
```

This is Docker's convenience installation script.

### **Step 6: Execute the Docker installation script**

The instructor runs the downloaded script using:

```
sudo sh get-docker.sh
```

**What does this command do?**

- `sudo` executes the command with administrative privileges.
- `sh` runs the shell script.
- `get-docker.sh` is the downloaded Docker installation script.

The script installs Docker Engine and its associated components.

### **Step 7: Create the Docker group**

The instructor explains that a Docker group is created so that users can execute Docker commands without typing `sudo` every time.

The relevant command is:

```
sudo groupadd docker
```

This creates a Linux group named `docker`.

**Why is this useful?**

Without the appropriate permissions, a regular user may have to execute commands like:

```
sudo docker images
```

After being configured as a member of the Docker group, the user can execute:

```
docker images
```

without adding `sudo`.

### **Step 8: Add the current user to the Docker group**

The instructor copies the command provided in the installation instructions and executes it.

A typical command for an Ubuntu EC2 user is:

```
sudo usermod -aG docker $USER
```

Explanation:

| Part      | Meaning                                                                |
| --------- | ---------------------------------------------------------------------- |
| `usermod` | Modifies an existing user account                                      |
| `-a`      | Appends the new group rather than replacing existing group memberships |
| `-G`      | Specifies supplementary groups                                         |
| `docker`  | The group to which the user is added                                   |
| `$USER`   | The currently logged-in username                                       |

This allows the current user to run Docker commands without `sudo` after the new group membership takes effect.

**Important:** The transcript mentions creating a new group and adding a user. The commands above represent the standard Linux procedure; the exact commands should be checked against the instructor's displayed installation steps.

### **Step 9: Verify Docker installation**

Finally, execute:

```
docker --version
```

The instructor receives the Docker version output:

```
Docker version 23.0.01
```

The version string is reproduced as spoken in the lecture; verify the actual installed version using your terminal.

Docker installed successfully

The EC2 instance is now capable of running Docker containers.

## **10. Triggering the GitHub Actions CI/CD workflow**

Once the following components have been configured:

- GitHub Actions workflow.
- AWS credentials in GitHub Secrets.
- ECR repository.
- Self-hosted runner on EC2.
- Docker installation on EC2.

The instructor returns to GitHub and checks the Actions tab.

The workflow is triggered, and the instructor observes that both jobs have succeeded:

**Continuous Integration**

Succeeded

**Continuous Deployment**

Succeeded

### **What happened during execution?**

**CI stage:**

1. GitHub Actions started the integration job.
2. AWS authentication was performed using the configured credentials.
3. The ECR repository was accessed.
4. The Docker image was built.
5. The image was pushed to ECR.

**CD stage:**

1. GitHub Actions assigned the deployment job to the self-hosted runner.
2. The runner executed the deployment instructions on EC2.
3. AWS/ECR authentication was performed.
4. The Docker image was made available to the EC2 Docker Engine.
5. The application container was started.

The instructor verifies the successful deployment from the EC2 environment.

## **11. Configuring EC2 Security Groups and inbound rules**

Even after successfully deploying the application, users may not be able to access it from their browsers.

This can happen because AWS security groups control incoming and outgoing network traffic.

### **What is a security group?**

A security group acts as a virtual firewall for an EC2 instance.

It controls which network connections are allowed to reach the instance.

For example, if our Flask application is running inside a Docker container and we expose it through port `8080`, the EC2 security group must allow incoming traffic on port `8080`.

### **Step-by-step: Update inbound rules**

The instructor performs the following steps:

1. Open the AWS Management Console.
2. Navigate to **EC2**.
3. Click **Instances**.
4. Select the running EC2 instance.
5. Open the **Security** tab.
6. Click the associated **Security Group**.
7. Click **Edit inbound rules**.
8. Add the required port rules.

### **Step 1: Add port 8080**

The instructor adds:

| Setting    | Value      |
| ---------- | ---------- |
| Type       | Custom TCP |
| Port range | `8080`     |

Port `8080` is the host port through which external users will access the Dockerized application.

### **Step 2: Add port 5000**

The instructor also adds:

| Setting    | Value      |
| ---------- | ---------- |
| Type       | Custom TCP |
| Port range | `5000`     |

Port `5000` is the port on which the Flask application runs inside the container.

### **Step 3: Save the changes**

After adding both inbound rules:

1. Review the rules.
2. Click **Save rules**.

The security group is now updated.

**Port configuration used in the lecture**

**8080**

EC2 host port

**5000**

Container port / Flask

The Docker port mapping forwards traffic received on host port 8080 to port 5000 inside the container.

**Important technical clarification:** The security group only needs to allow the externally exposed host port `8080` for this particular access method. Port `5000` does not need to be publicly exposed if Flask is accessed exclusively through Docker's `8080:5000` mapping.

For a real deployment, restrict inbound access to trusted IP addresses where possible. Do not expose Flask's development server directly to the public internet; use a production WSGI server such as Gunicorn, preferably behind a reverse proxy and HTTPS.

## **12. Accessing the deployed application using the EC2 public IP**

After configuring the inbound rules, the instructor accesses the application through the EC2 instance's public IP address.

### **Step 1: Return to the EC2 Instances page**

1. Open the AWS EC2 console.
2. Navigate to **Instances**.
3. Select the running instance.

### **Step 2: Copy the public IP address**

The EC2 instance has a public IP address that can be used to access it over the internet, subject to its network and security configuration.

The instructor copies this IP address.

### **Step 3: Open the application in a browser**

Previously, when testing locally, the application was accessed through:

```
http://localhost:8080
```

However, `localhost` refers to the current machine.

Now that the application is deployed on EC2, we need to use the EC2 public IP address.

The URL format becomes:

```
http://<EC2_PUBLIC_IP>:8080
```

For example, if the EC2 public IP were `54.123.45.67`, the URL would be:

```
http://54.123.45.67:8080
```

The instructor enters the public IP and port `8080` into the browser.

Application accessible

The application interface loads successfully.

### **Why do we use the public IP instead of localhost?**

| Local deployment                       | EC2 deployment                                     |
| -------------------------------------- | -------------------------------------------------- |
| Application runs on our local computer | Application runs on an AWS virtual machine         |
| Access through `localhost`             | Access through the EC2 public IP                   |
| Local Docker port is exposed           | EC2 security group must allow the port             |
| Usually accessible locally             | Can be accessed remotely, subject to network rules |

**Remember:** The public IP is the address of the EC2 instance, not the Docker container itself.

## **13. Testing the deployed application**

After opening the application through the EC2 public IP, the instructor performs an actual functionality test.

The purpose is to verify that deployment has not affected the application's functionality.

### **Testing procedure**

1. Open the deployed Flask application in the browser.
2. Select an image file from the local system.
3. Upload the image through the application's interface.
4. Click the **Submit** button.
5. Wait for the application to process the image.
6. Observe the prediction generated by the application.

### **Expected result**

The application successfully:

- Accepts the uploaded image.
- Processes the image.
- Executes the image segmentation/prediction pipeline.
- Displays the prediction result.

The instructor confirms that the application works correctly after deployment, just as it did during local Docker testing.

**Final deployment verification**

Docker image successfully built

Docker image pushed to AWS ECR

Self-hosted runner configured on EC2

Docker installed on EC2

CI/CD jobs executed successfully

EC2 inbound rules updated

Application accessible through public IP

Image upload and prediction tested successfully

## **14. Complete deployment workflow: From code to application**

Let's connect all the steps into one end-to-end process.

## **End-to-end CI/CD pipeline**

1. **Develop the Flask application**

   Write the application code and Dockerfile.
2. **Push code to GitHub**

   Commit and push the latest changes to the `main` branch.
3. **GitHub Actions trigger**

   The workflow inside `.github/workflows/main.yaml` starts automatically.
4. **CI: AWS authentication**

   GitHub Secrets provide the configured AWS credentials.
5. **CI: Build Docker image**

   GitHub Actions builds the image using the Dockerfile.
6. **CI: Push to ECR**

   The newly created Docker image is stored in the AWS ECR repository named `segment`.
7. **CD: Execute on self-hosted runner**

   GitHub assigns the deployment job to the runner installed on EC2.
8. **CD: Deploy Docker container**

   The EC2 instance obtains the image and launches the application container.
9. **Configure network access**

   The EC2 security group allows the required inbound traffic.
10. **Access and test the application**

    Open `http://<EC2_PUBLIC_IP>:8080` and test image uploading and prediction.

## **15. Important technical concepts and clarifications**

The following are useful details to understand beyond the instructor's demonstration.

### **A. Difference between Docker Hub and AWS ECR**

Both services can store Docker images, but they are different services.

| Docker Hub                                  | AWS ECR                                  |
| ------------------------------------------- | ---------------------------------------- |
| General-purpose container registry          | AWS-managed container registry           |
| Can be used across cloud providers          | Integrated with AWS services             |
| Commonly used for public and private images | Supports private and public repositories |
| Docker's registry service                   | Amazon's registry service                |

In this lecture, AWS ECR is used to store the application image.

### **B. Difference between GitHub-hosted and self-hosted runners**

| GitHub-hosted                                               | Self-hosted                                                        |
| ----------------------------------------------------------- | ------------------------------------------------------------------ |
| Managed by GitHub                                           | Managed by the user                                                |
| Runs on GitHub infrastructure                               | Runs on our EC2 instance                                           |
| Environment is provisioned for the job                      | Environment must be configured by us                               |
| Does not automatically have access to our EC2 Docker Engine | Can execute Docker commands directly on the configured EC2 machine |

### **C. Why must Docker be installed on EC2?**

The EC2 instance is a virtual machine. It does not automatically have Docker installed.

Since our deployment process uses Docker commands to run the application, we must install Docker Engine on the EC2 instance first.

### **D. Why does the application need a public IP?**

The EC2 instance is hosted remotely in AWS.

The public IP provides an address through which external clients can connect to the instance, provided:

- The instance has a public IPv4 address or another public access route.
- Its networking configuration permits internet traffic.
- The security group allows the requested port.
- Docker is publishing the application port.
- Flask is listening on the appropriate container interface.

### **E. Why is port mapping necessary?**

The Flask application listens on port `5000` inside the container.

We expose the container through port `8080` on the EC2 host.

Conceptually:

```
docker run -d -p 8080:5000 <image>
```

The mapping follows this structure:

```
-p HOST_PORT:CONTAINER_PORT
```

Therefore:

```
8080:5000
```

means that requests received on host port `8080` are forwarded to port `5000` inside the container.

### **F. Why must Flask listen on&#x20;**`0.0.0.0`**?**

Inside a Docker container, Flask should listen on:

```
app.run(host="0.0.0.0", port=5000)
```

If Flask listens only on `127.0.0.1`, it may not accept connections forwarded from outside the container.

### **G. Important distinction: ECR authentication versus AWS credentials**

The workflow needs permission to access ECR.

The AWS credentials authenticate the workflow with AWS, while ECR authentication allows Docker to pull or push images to the registry.

These are related but distinct operations.

A typical ECR login command is:

```
aws ecr get-login-password --region <AWS_REGION> |
docker login --username AWS --password-stdin \
<AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com
```

The AWS CLI must be installed in whichever environment executes this command.

The exact authentication commands used in the instructor's workflow are not included in the spoken transcript.

### **H. Important distinction: Runner registration versus runner execution**

Registering the runner is not enough.

There are two separate operations:

1. **Configure/register:** Associates the EC2 machine with the GitHub repository.
2. **Start/listen:** Runs the runner process so that it can receive workflow jobs.

If the runner is registered but offline, GitHub cannot assign jobs to it.

### **I. Important distinction: CI/CD success versus application availability**

A successful CI/CD workflow means the workflow jobs completed without errors.

It does not automatically guarantee that:

- The application is reachable publicly.
- The correct ports are open.
- The application has no runtime errors.
- The container remains healthy.

That is why the instructor separately configures security groups and tests the application through the browser.

## **16. Production considerations and improvements**

The lecture demonstrates the deployment process successfully. However, there are several important considerations when using this approach in a real production environment.

### **1. Keep the self-hosted runner running**

In the lecture, the runner is started manually and then stopped to demonstrate its online/offline status.

For continuous deployment, the runner must remain available.

GitHub provides commands to configure the runner as a Linux service. This allows it to start automatically and run in the background.

### **2. Avoid running Docker as root unnecessarily**

The instructor adds the EC2 user to the Docker group to avoid using `sudo` for every command.

However, membership in the Docker group effectively grants root-level control over the host. Only trusted users should be members.

### **3. Use a production Flask server**

The development server built into Flask is not intended for production.

A more suitable setup would be:

```
Internet
   ↓
EC2 Security Group
   ↓
Nginx / Reverse Proxy
   ↓
Gunicorn
   ↓
Flask Application
```

HTTPS should also be configured for real users.

### **4. Avoid exposing unnecessary ports**

The lecture opens both ports `8080` and `5000`.

In a more secure setup:

- Allow public access to port `80` or `443`, depending on the reverse-proxy configuration.
- Keep Flask's internal port private.
- Avoid exposing port `5000` directly to the internet.

### **5. Use proper IAM permissions**

The IAM user or role should have only the permissions required for the workflow.

For example:

- Authenticate with ECR.
- Push images to the intended repository.
- Retrieve images from the intended repository.

Avoid granting unrestricted administrator permissions just to make the workflow work.

### **6. Be careful with the Docker image deployment command**

The instructor describes passing AWS credentials and the ECR repository details when running the container.

There are two separate concerns here:

- AWS credentials used by the deployment process to authenticate with ECR.
- Environment variables required by the Flask application while it runs.

AWS credentials should generally not be passed into the application container unless the application genuinely needs them. Prefer an EC2 IAM role and short-lived credentials where appropriate.

### **7. Handle existing containers during redeployment**

A deployment workflow must also handle an already-running container.

For example, a simple deployment sequence might be:

```
docker pull <ECR_IMAGE_URI>

docker stop segment-app || true

docker rm segment-app || true

docker run -d \
  --name segment-app \
  -p 8080:5000 \
  <ECR_IMAGE_URI>
```

This is an illustrative deployment sequence, not the exact command from the transcript.

Without stopping and replacing an existing container, repeated deployments may fail because the container name or host port is already in use.

### **8. EC2 public IP considerations**

An EC2 public IP may change when an instance is stopped and started, depending on its configuration.

For a stable application address, consider using an Elastic IP, DNS, or a load balancer.

### **9. Docker installation script considerations**

The lecture uses Docker's convenience installation script.

For a production environment, it is preferable to follow Docker's official Ubuntu installation instructions, verify the package source, and manage Docker updates deliberately.

## **17. Important commands from this lecture**

A consolidated reference for the commands discussed or demonstrated:

| Command                              | Purpose                            |
| ------------------------------------ | ---------------------------------- |
| `mkdir actions-runner`               | Create the runner directory        |
| `cd actions-runner`                  | Enter the runner directory         |
| `docker --version`                   | Check Docker installation          |
| `sudo apt update`                    | Update Ubuntu package indexes      |
| `sudo apt upgrade`                   | Upgrade installed packages         |
| `sudo sh get-docker.sh`              | Execute Docker installation script |
| `sudo groupadd docker`               | Create Docker group                |
| `sudo usermod -aG docker $USER`      | Add current user to Docker group   |
| `docker images`                      | List Docker images                 |
| `docker ps`                          | List running containers            |
| `docker logs <container_id>`         | View container logs                |
| `docker run -d -p 8080:5000 <image>` | Start container with port mapping  |
| `docker pull <ECR_IMAGE_URI>`        | Retrieve image from ECR            |
| `docker stop <container>`            | Stop a running container           |
| `docker rm <container>`              | Remove a stopped container         |

The runner download, checksum validation, extraction, configuration, and startup commands should be copied directly from GitHub's **New self-hosted runner** page because GitHub generates the appropriate commands for the runner version and operating system.

## **18. Important interview and revision questions**

**1. What is CI/CD?**

CI/CD stands for Continuous Integration and Continuous Delivery/Deployment. It automates the process of integrating code changes, building applications, testing them, and delivering or deploying them.

**2. What is GitHub Actions?**

GitHub Actions is an automation platform that executes workflows in response to events such as code pushes and pull requests.

**3. Where do we store GitHub Actions workflow files?**

Inside:

```
.github/workflows/
```

**4. What is AWS EC2?**

Amazon Elastic Compute Cloud provides virtual machines on AWS that can be used to host applications.

**5. What is AWS ECR?**

Amazon Elastic Container Registry is a managed service for storing and managing Docker container images.

**6. Why do we use ECR in this project?**

To store the Docker image built during the CI stage so that the deployment environment can retrieve it.

**7. What is a self-hosted runner?**

A machine that we manage ourselves and configure to execute GitHub Actions jobs.

**8. Why did we select Linux while creating the self-hosted runner?**

Because the EC2 instance used in the lecture runs Ubuntu, which is Linux-based.

**9. What does&#x20;**`Listening for jobs`**&#x20;mean?**

The self-hosted runner is connected to GitHub and waiting for a workflow job to execute.

**10. What does the Idle runner status mean?**

The runner is online and ready to execute jobs, but no job is currently assigned.

**11. Why did the runner become offline after terminating the terminal process?**

Because the runner process stopped communicating with GitHub.

**12. Why must Docker be installed on EC2?**

Because the EC2 machine needs Docker Engine to execute Docker commands and run the application container.

**13. What is the purpose of GitHub Secrets?**

To securely store sensitive configuration values, such as AWS access credentials, and make them available to GitHub Actions workflows.

**14. What is the purpose of the AWS access key ID and secret access key?**

They are credentials used to authenticate an IAM identity with AWS.

**15. Why do we need to configure security groups?**

To control which incoming network connections are allowed to reach an EC2 instance.

**16. Why did the instructor use port 8080?**

It is the host port exposed by Docker for accessing the Flask application.

**17. What does&#x20;**`-p 8080:5000`**&#x20;mean?**

It maps host port `8080` to container port `5000`.

**18. Why can't we use localhost to access the deployed application from another computer?**

Because localhost refers to the machine making the request, not the remote EC2 instance.

**19. What address do we use to access the deployed application?**

```
http://<EC2_PUBLIC_IP>:8080
```

**20. What happens when we push new code to the main branch?**

The configured GitHub Actions workflow is triggered and automatically executes the CI/CD pipeline.

**21. What is the difference between Docker image and Docker container?**

An image is the packaged application template; a container is a running instance of that image.

**22. What is the purpose of the Docker group?**

It allows authorized users to execute Docker commands without requiring `sudo` for every command.

**23. Does successfully building a Docker image mean the application has been deployed?**

No. The image must also be made available on the target machine, a container must be started, and network access must be configured.

**24. Why do we test the application after deployment?**

To verify that the application works correctly in the actual cloud environment, not just on the local machine.

**25. What is the difference between CI and CD in this project?**

- CI builds and pushes the Docker image to ECR.
- CD deploys the image by running the container on EC2.

## **19. Final summary: What we accomplished**

| Component          | Work completed                                   |
| ------------------ | ------------------------------------------------ |
| Flask application  | Existing application prepared for deployment     |
| Docker             | Installed on EC2 and used to run the application |
| GitHub Actions     | Configured to automate deployment                |
| GitHub Secrets     | AWS credentials and ECR configuration added      |
| AWS ECR            | Repository `segment` created                     |
| AWS EC2            | Ubuntu `t2.medium` instance used                 |
| Self-hosted runner | Installed and registered on EC2                  |
| CI                 | Docker image built and pushed to ECR             |
| CD                 | Docker container launched on EC2                 |
| Security groups    | Inbound rules configured                         |
| Public access      | Application accessed through EC2 public IP       |
| Testing            | Image upload and prediction verified             |

### **The most important takeaway**

The central concept of this lecture is automating Docker application deployment using GitHub Actions.

Previously, we manually created a Docker image and launched a container locally. Now, we have connected GitHub, AWS ECR, and AWS EC2 to automate the process.

**Whenever we update our application and push the changes to the configured GitHub branch, GitHub Actions can automatically build the latest Docker image, push it to ECR, and deploy it on EC2.**

This is the fundamental idea behind an automated CI/CD pipeline for a containerized application.