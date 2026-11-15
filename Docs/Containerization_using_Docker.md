# **Detailed Notes: Dockerizing a Flask Application**

This lecture covers how to **Dockerize an existing Flask application, build a Docker image, create and run a Docker container, test the application inside the container, and push the Docker-related changes to GitHub.**

The next lecture will cover deploying this Dockerized application on an AWS EC2 instance.

The complete workflow covered here is:

## **Dockerization Workflow**

**Existing Flask Application**

Previously tested locally on port 5000

**Create&#x20;**`.dockerignore`**&#x20;and&#x20;**`Dockerfile`

**Build Docker Image**

docker build

**Create Docker Container**

docker run

**Test Flask Application**

localhost:8080

**Push Changes to GitHub**

Ready for AWS EC2 Deployment

# **1. Introduction: Why Dockerize the Flask Application?**

In the previous lecture, we developed a Flask application and verified that it was running successfully in our local development environment.

However, if we want other people to access our application, we need to deploy it on a server.

In this lecture, the instructor prepares the application for deployment using Docker.

### **1.1 What is Dockerization?**

Dockerization is the process of packaging an application along with its required dependencies and environment into a Docker image.

This image can then be used to create Docker containers.

A Docker container provides an isolated environment in which the application runs.

### **1.2 Why do we need Docker?**

Consider a situation where an application works perfectly on your local Windows machine but fails when deployed on a Linux server.

This can happen because of differences in:

- Operating systems.
- Python versions.
- Installed libraries.
- System dependencies.
- Environment configurations.

Docker helps address these differences by packaging the application and its dependencies into a standardized environment.

**Main advantages:**

1. Portability across different environments.
2. Consistent application execution.
3. Dependency isolation.
4. Easier deployment.
5. Better reproducibility.
6. Simplified application distribution.

The instructor's objective is to make the Flask application run inside a Docker container before deploying it to AWS EC2.

# **2. Step 1 – Creating the&#x20;**`.dockerignore`**&#x20;File**

Just as Git uses a `.gitignore` file, Docker uses a `.dockerignore` file.

### **2.1 What is&#x20;**`.dockerignore`**?**

The `.dockerignore` file specifies which files and directories should be excluded from the Docker build context.

In simple words, it tells Docker which files are unnecessary when building the Docker image.

**Why is it important?**

Suppose your project contains:

- Source code.
- Jupyter notebooks.
- Training datasets.
- Model artifacts.
- Logs.
- Temporary files.
- Local environment folders.

Not all these files are required inside the Docker image.

Including unnecessary files can:

- Increase Docker image size.
- Increase build time.
- Consume additional storage.
- Transfer unnecessary data to the Docker build process.

Therefore, we create a `.dockerignore` file.

### **2.2 Creating the file**

At the root of the project, create:

```
.dockerignore
```

The instructor mentions excluding the following items:

```
notebooks
artifacts
logs
data
env
demo.py
template.py
static/predict
static/upload
```

The lecture also mentions excluding `.git` information and other irrelevant project files.

The exact patterns should match the actual project structure.

### **2.3 Understanding the excluded files**

| File/Directory    | Reason for excluding                                                              |
| ----------------- | --------------------------------------------------------------------------------- |
| `notebooks/`      | Development and experimentation notebooks are not required to run the application |
| `artifacts/`      | Local generated artifacts are not needed in this particular image build           |
| `logs/`           | Existing local logs are unnecessary                                               |
| `data/`           | Local datasets are not required in the image                                      |
| `env/`            | Local Python environment should not be copied                                     |
| `demo.py`         | Development/testing script                                                        |
| `template.py`     | Development or temporary file, as identified in the lecture                       |
| `static/predict/` | Generated prediction files                                                        |
| `static/upload/`  | Uploaded files from the local application                                         |
| `.git/`           | Git repository metadata                                                           |

**Important:** `.dockerignore` does not delete these files from your computer. It only excludes matching files from the Docker build context.

Also, if the application needs a particular dataset or model artifact at runtime, it must obtain that resource through another mechanism, such as downloading it or mounting a volume.

# **3. Step 2 – Creating the Dockerfile**

After creating `.dockerignore`, the instructor creates the Dockerfile.

### **3.1 What is a Dockerfile?**

A Dockerfile is a text file containing instructions that Docker uses to build a Docker image.

It describes:

- The base operating system/environment.
- Required system packages.
- Python dependencies.
- Application working directory.
- Files to copy.
- Application startup command.

Think of the Dockerfile as a set of instructions for preparing the environment in which your application will run.

### **3.2 Creating the Dockerfile**

At the root of the project, create a file named:

```
Dockerfile
```

The instructor emphasizes using an uppercase `D` in `Dockerfile`.

The standard filename is `Dockerfile`, without an extension.

### **3.3 Understanding the Dockerfile instructions**

The instructor's Dockerfile contains several important instructions.

Let's understand them individually.

## **3.3.1&#x20;**`FROM`**&#x20;– Selecting the base image**

The first instruction is:

```
FROM python:3.8
```

The actual Python tag should match the version used in the project.

**What does&#x20;**`FROM`**&#x20;do?**

It specifies the base image on which our Docker image will be built.

Here:

- `python` refers to the official Python Docker image.
- `3.8` specifies the Python version.

Instead of installing Python manually inside a fresh operating system, we use an existing Python image.

This base image already contains the Python environment required to execute Python applications.

**Important:** The instructor's exact Python tag should be retained if reproducing the lecture. A production project should use a version compatible with its dependencies.

## **3.3.2&#x20;**`RUN`**&#x20;– Updating operating system packages**

The next instruction uses:

```
RUN apt-get update
```

**What does it do?**

It updates the package lists maintained by the operating system's package manager.

The base Python image uses a Debian-based environment in this example, so the instructor uses `apt-get`.

Updating the package list ensures that the package manager has current information about available packages and their versions.

Next:

```
RUN apt-get upgrade -y
```

This upgrades installed operating system packages to newer available versions.

### **Understanding the&#x20;**`-y`**&#x20;flag**

The `-y` flag automatically answers yes to confirmation prompts.

For example, without `-y`, the installation process may ask:

```
Do you want to continue? [Y/n]
```

When we use:

```
apt-get upgrade -y
```

the command automatically confirms the prompt.

This is particularly useful during Docker builds because they should execute without manual interaction.

## **3.3.3&#x20;**`RUN`**&#x20;– Installing/upgrading AWS CLI**

The instructor uses:

```
RUN pip3 install --upgrade awscli
```

**Why do we need AWS CLI?**

In the previous Data Ingestion lecture, we used AWS CLI to interact with the S3 bucket.

The application/project requires AWS CLI to perform the necessary cloud storage operations.

This instruction:

1. Uses `pip3` to install the AWS CLI Python package.
2. Uses `--upgrade` to install a newer version if an older version is present.

The AWS CLI allows us to interact with AWS services through command-line commands.

## **3.3.4&#x20;**`RUN`**&#x20;– Installing PyTorch CPU versions**

The instructor next installs:

- PyTorch.
- TorchVision.
- TorchAudio.

The installation command uses the official PyTorch CPU package index:

```
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Why this installation command?**

The application uses PyTorch-related dependencies.

However, the instructor chooses CPU versions rather than GPU versions.

### **Why CPU versions?**

A GPU-enabled PyTorch installation requires compatible GPU hardware and supporting CUDA dependencies.

For this deployment, the instructor chooses CPU-based packages to avoid requiring a GPU environment.

The `--index-url` argument specifies the package repository from which pip downloads the packages.

Official reference:

[PyTorch – Official Installation Guide](https://pytorch.org/get-started/locally/?utm_source=chatgpt.com)

## **3.3.5&#x20;**`WORKDIR`**&#x20;– Setting the working directory**

The next instruction is:

```
WORKDIR /app
```

This sets the working directory inside the Docker image/container.

Here:

```
/app
```

becomes the working directory.

**What happens when we use&#x20;**`WORKDIR`**?**

- If the directory does not exist, Docker creates it.
- Subsequent relative commands are executed with this directory as their working directory.
- Relative paths used by later instructions are interpreted from this location.

For example, when we install requirements or execute the application, the working directory will be `/app`.

## **3.3.6&#x20;**`COPY`**&#x20;– Copying project files into the image**

The next instruction is:

```
COPY . .
```

This is one of the most important Dockerfile instructions.

Let's understand both dots.

```
COPY <source> <destination>
```

In:

```
COPY . .
```

- First `.` represents the current build context on the host machine.
- Second `.` represents the current working directory inside the Docker image.

Since we previously defined:

```
WORKDIR /app
```

the files are copied into:

```
/app
```

**What gets copied?**

The project files that are part of the Docker build context and are not excluded by `.dockerignore`.

For example:

```
Project/
│
├── src/
├── static/
├── templates/
├── app.py
├── requirements.txt
└── Dockerfile
```

These relevant project files are copied into `/app`.

## **3.3.7&#x20;**`RUN`**&#x20;– Installing project requirements**

After copying the project files, the instructor installs the dependencies.

```
RUN pip3 install -r requirements.txt
```

### **Understanding the command**

| Part               | Meaning                                     |
| ------------------ | ------------------------------------------- |
| `RUN`              | Executes a command during image building    |
| `pip3`             | Python package installer                    |
| `install`          | Installs packages                           |
| `-r`               | Reads dependencies from a requirements file |
| `requirements.txt` | File containing project dependencies        |

The requirements file may contain packages such as:

- Flask.
- OpenCV.
- Albumentations.
- PyTorch-related dependencies.
- Image processing libraries.
- Other application dependencies.

Docker installs these dependencies inside the image.

This ensures that the application has the libraries it requires to run.

## **3.3.8&#x20;**`CMD`**&#x20;– Defining the application startup command**

The final instruction is:

```
CMD ["python3", "app.py"]
```

This tells Docker what command to execute when a container is started from the image.

Here:

- `python3` is the Python interpreter.
- `app.py` is the application script.

When the container starts, Docker executes:

```
python3 app.py
```

This launches the Flask application inside the container.

### **Important: Difference between&#x20;**`RUN`**&#x20;and&#x20;**`CMD`

This is one of the most important concepts in the lecture.

| `RUN`                                                     | `CMD`                                            |
| --------------------------------------------------------- | ------------------------------------------------ |
| Executes during image building                            | Executes when the container starts               |
| Used to prepare the image                                 | Used to define the default container process     |
| Can execute multiple times across Dockerfile instructions | Normally one effective CMD instruction per image |
| Example: installing requirements                          | Example: starting Flask                          |

**Example:**

```
RUN pip3 install -r requirements.txt
```

This installs dependencies while building the image.

```
CMD ["python3", "app.py"]
```

This starts the application when the container runs.

# **4. Step 3 – Additional Dockerfile Modifications**

During the second Docker build demonstration, the instructor mentions an additional modification.

He observed some warnings related to image-processing dependencies while building the Docker image.

To address these warnings, he researched the issue and added commands for installing the required JPEG and PNG system libraries.

These are related to image-processing support.

Typical Debian package names for these libraries include:

```
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libpng-dev
```

**Note:** These are representative package names, not a verbatim copy of the instructor's exact Dockerfile commands. The transcript does not provide the complete commands.

### **Why are these libraries needed?**

Image-processing libraries such as OpenCV and other image-handling packages may depend on underlying operating-system libraries.

Installing the required system libraries helps provide the necessary support for processing JPEG and PNG images.

Since this is a human segmentation application, image-processing dependencies are particularly important.

# **5. Complete Dockerfile – Conceptual Structure**

Combining the instructions discussed in the lecture, the Dockerfile follows this structure:

```
# Base image
FROM python:3.8

# Update operating system packages
RUN apt-get update

# Upgrade installed packages
RUN apt-get upgrade -y

# Install system libraries required for image processing
RUN apt-get install -y libjpeg-dev libpng-dev

# Upgrade AWS CLI
RUN pip3 install --upgrade awscli

# Install CPU versions of PyTorch packages
RUN pip3 install torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install project dependencies
RUN pip3 install -r requirements.txt

# Start Flask application
CMD ["python3", "app.py"]
```

This is a consolidated illustrative version of the Dockerfile explained in the lecture. It is not guaranteed to reproduce every original line or instruction exactly.

# **6. Step 4 – Building the Docker Image**

Once the Dockerfile and `.dockerignore` files are ready, the next step is to build the Docker image.

### **6.1 What is a Docker Image?**

A Docker image is a packaged, read-only template containing everything required to create and run a container.

It contains:

- Base image.
- Operating system dependencies.
- Python environment.
- Installed libraries.
- Application source code.
- Startup instructions.

A Docker image is used to create Docker containers.

### **6.2 Checking existing Docker images**

Before creating a new image, the instructor checks the images already available on the local system.

Command:

```
docker images
```

This displays the locally available Docker images.

Initially, the instructor observes that there are no images available.

### **6.3 Creating the Docker image**

The instructor uses:

```
docker build -t test .
```

Later, for the actual project, he uses a more meaningful image name:

```
docker build -t human .
```

Let's understand this command.

| Part     | Explanation                                          |
| -------- | ---------------------------------------------------- |
| `docker` | Invokes Docker                                       |
| `build`  | Builds a Docker image                                |
| `-t`     | Assigns a name/tag to the image                      |
| `human`  | Name of the Docker image                             |
| `.`      | Specifies the current directory as the build context |

### **Why do we use&#x20;**`.`**?**

The dot represents the current directory.

Docker uses this directory as the build context.

It looks for the Dockerfile in the current directory by default and makes the non-ignored files available to the build process.

### **6.4 What happens during Docker image creation?**

When we execute:

```
docker build -t human .
```

Docker reads the Dockerfile and executes its instructions.

The process involves:

1. Downloading or using the specified Python base image.
2. Updating operating system packages.
3. Installing the required system libraries.
4. Installing/upgrading AWS CLI.
5. Installing PyTorch CPU packages.
6. Setting `/app` as the working directory.
7. Copying project files into the image.
8. Installing dependencies from `requirements.txt`.
9. Configuring the default startup command.

The instructor observes the installation process in the terminal.

Some of the packages shown during installation include:

- `opencv-python-headless`
- `albumentations`
- `imageio`
- `contourpy`
- `torchvision`
- Other dependencies from `requirements.txt`.

### **6.5 Why do we use&#x20;**`opencv-python-headless`**?**

The instructor specifically observes that OpenCV's headless version is installed.

The headless version is designed for environments that do not require OpenCV's GUI functionality.

It is commonly useful in Docker containers and server-side applications where graphical desktop windows are unnecessary.

### **6.6 Why does TorchVision get installed?**

The instructor notices that TorchVision is installed even though it was not separately installed through the requirements installation command at that point.

The reason is that dependencies can install other packages automatically.

For example:

- One package may require another package.
- Pip resolves dependencies.
- Required packages are downloaded and installed automatically.

Thus, TorchVision may already be available through the installation of other declared packages or dependency relationships.

### **6.7 Checking the created image**

Once the build completes, execute:

```
docker images
```

The instructor observes that the image has been created successfully.

**Docker Image Build – Lecture Observation**

# **71 sec**

Initial build duration

# **1.98 GB**

Observed image size

These are the values observed in the lecture, not guaranteed values for every build.

The Docker image is now ready, but we still need a container to execute it.

# **7. Step 5 – Understanding Docker Containers**

Before creating the container, let's understand the difference between a Docker image and a Docker container.

### **7.1 What is a Docker Container?**

A Docker container is a running or stopped instance of a Docker image.

The image provides the packaged environment, whereas the container is the actual instance in which the application executes.

### **7.2 Image vs Container**

| Docker Image                          | Docker Container                         |
| ------------------------------------- | ---------------------------------------- |
| Template used to create containers    | Instance created from an image           |
| Contains application and dependencies | Executes the application                 |
| Relatively static                     | Has a runtime state                      |
| Can create multiple containers        | Each container is an individual instance |
| Created using `docker build`          | Created using `docker run`               |

**Simple analogy:**

- Docker Image = Recipe.
- Docker Container = Prepared dish using that recipe.

One image can be used to create multiple containers.

# **8. Step 6 – Creating and Running the Docker Container**

Now that the Docker image is ready, the instructor creates a container using the image.

### **8.1 Understanding the application port**

Before running the container, we need to understand the port configuration.

The Flask application is running on:

```
5000
```

However, the instructor wants to access it through Docker using:

```
8080
```

Therefore, we need to establish port mapping between the host and the container.

### **8.2 What is Port Mapping?**

Port mapping connects a port on the host machine to a port inside the Docker container.

This allows users to access an application running inside a container through a port on their local machine.

The instructor uses:

```
Host Port: 8080
Container Port: 5000
```

The mapping is:

**Docker Port Mapping**

# **8080**

**Host Port**

Browser accesses this port

# **5000**

**Container Port**

Flask application listens here

8080 → 5000

Host traffic on port 8080 is forwarded to container port 5000.

### **8.3 Docker run command**

The instructor executes:

```
docker run -d -p 8080:5000 human
```

Let's understand each part.

| Command      | Explanation                                |
| ------------ | ------------------------------------------ |
| `docker run` | Creates and starts a container             |
| `-d`         | Runs the container in detached mode        |
| `-p`         | Specifies port mapping                     |
| `8080:5000`  | Maps host port 8080 to container port 5000 |
| `human`      | Name of the Docker image                   |

### **8.4 Understanding detached mode (**`-d`**)**

The `-d` flag stands for detached mode.

It allows the container to run in the background without occupying the terminal.

This means:

- The container continues running in the background.
- We can use the terminal for other commands.
- We can inspect the container separately.
- We can view logs whenever required.

Without detached mode, the container runs in the foreground and its output is displayed in the terminal.

### **8.5 Understanding&#x20;**`-p 8080:5000`

The format is:

```
-p HOST_PORT:CONTAINER_PORT
```

Therefore:

```
-p 8080:5000
```

means:

- Host machine port = 8080.
- Container port = 5000.

The Flask application continues to use its internal port 5000.

We access it externally through port 8080.

### **8.6 Container creation result**

Once the command executes successfully, Docker creates and starts the container.

The terminal returns a container ID.

This indicates that the container has been created.

Container started

# **9. Step 7 – Understanding Docker Desktop**

The instructor also uses Docker Desktop to visually inspect the Docker image and container.

### **9.1 What is Docker Desktop?**

Docker Desktop is a graphical application that helps us manage Docker resources.

It provides a visual interface for:

- Images.
- Containers.
- Container status.
- Logs.
- Port mappings.
- Resource utilization.

Official reference:

[Docker Desktop](https://www.docker.com/products/docker-desktop/?utm_source=chatgpt.com)

### **9.2 Checking the Docker image**

Open Docker Desktop.

Navigate to the Images section.

Here, we can observe the image created earlier.

For example:

```
human
```

The image appears with its creation time and size.

### **9.3 Checking the container**

Navigate to the Containers section.

We can observe the container created using:

```
docker run -d -p 8080:5000 human
```

The instructor verifies that the container is running.

### **9.4 Opening the application through Docker Desktop**

Docker Desktop provides a port link for the running container.

The instructor clicks on the HTTP port link.

This opens the application in the browser.

The browser URL is:

```
http://localhost:8080
```

The Flask application is now accessible through the Docker container.

**Important observation:**

Earlier, we accessed the application using port 5000.

Now we access it through port 8080 because of Docker port mapping.

# **10. Step 8 – Verifying the Container Using Terminal Commands**

Apart from Docker Desktop, we can also manage and inspect Docker containers using terminal commands.

The instructor demonstrates two important commands.

### **10.1 Checking running containers –&#x20;**`docker ps`

Command:

```
docker ps
```

This displays the currently running Docker containers.

The output contains information such as:

| Column       | Meaning                               |
| ------------ | ------------------------------------- |
| CONTAINER ID | Unique identifier of the container    |
| IMAGE        | Image used to create the container    |
| COMMAND      | Command executed inside the container |
| CREATED      | Time since container creation         |
| STATUS       | Current container status              |
| PORTS        | Published and mapped ports            |
| NAMES        | Container name                        |

The instructor observes that the newly created container is listed.

Its status indicates that it is running.

### **10.2 Understanding the container name**

In the lecture, Docker automatically generates a name for the container.

The instructor observes a randomly generated name similar to:

```
hardcore_sky
```

This happens because the `docker run` command does not specify a custom container name.

Docker automatically assigns a name when `--name` is omitted.

We can provide our own name using:

```
docker run -d -p 8080:5000 --name human-container human
```

This would create a container named `human-container`.

*This custom naming command is an additional example; the instructor uses the automatically generated name.*

### **10.3 Checking container logs –&#x20;**`docker logs`

The instructor next demonstrates how to view application logs.

Command:

```
docker logs <CONTAINER_ID>
```

For example:

```
docker logs abc123def456
```

Here, replace the example ID with the actual container ID returned by Docker.

The command displays the logs generated by the application inside the container.

### **What does the instructor observe?**

The logs indicate that the Flask application is being served.

For example, the output may contain:

```
Serving Flask app
```

This helps us verify that the application has started inside the container.

**Why are logs important?**

They help us:

- Check whether the application started successfully.
- Identify errors.
- Inspect requests.
- Understand application execution.
- Troubleshoot container-related issues.

# **11. Step 9 – Testing the Flask Application Inside Docker**

After verifying that the container is running, the instructor tests the actual application.

### **11.1 Opening the application**

Open your browser and enter:

```
http://localhost:8080
```

The Flask application should appear.

Remember:

- Port 5000 is the Flask application's internal port.
- Port 8080 is the host port exposed through Docker.

### **11.2 Uploading an image**

The instructor now tests the application's actual functionality.

Follow these steps:

1. Open the application using `localhost:8080`.
2. Select an image using the upload option.
3. Click the Submit button.
4. Wait for the application to process the image.
5. Observe the prediction result.

The application takes some time to process the uploaded image.

### **11.3 Understanding what happens during prediction**

The application uses the EfficientNet architecture.

When the image is submitted, the application loads the required model resources.

During the demonstration, the instructor observes that the application downloads the EfficientNet architecture's weights and associated resources.

These weights are required for the model to perform prediction.

The instructor also checks the Docker Desktop logs to observe the execution.

### **11.4 Verifying the prediction**

After processing is complete, the prediction result appears successfully.

The instructor compares the result with the result obtained previously when running the Flask application locally.

Both results are consistent.

Application tested successfully

### **11.5 Why is this testing important?**

This confirms that the Dockerized application is not merely starting successfully, but is also performing its actual functionality.

There are two separate things to verify:

1. **Container verification:** Is the container running?
2. **Application verification:** Is the Flask application functioning correctly inside the container?

Both are necessary.

# **12. Step 10 – Why Docker Helps with Deployment**

After successfully testing the application, the instructor explains an important advantage of Docker.

The application is now running inside an isolated Docker container.

This helps reduce problems caused by differences between development and deployment environments.

### **Example**

Suppose the application was developed on Windows.

Later, we want to deploy it on a Linux-based AWS EC2 instance.

Without proper environment management, there might be issues involving:

- Python versions.
- Dependency versions.
- System libraries.
- Package compatibility.
- Environment configuration.

With Docker, the application and its dependencies are packaged into an image.

The same image can be used to create containers on different supported environments.

### **Important understanding**

Docker does not mean that an application will automatically run on every operating system without any compatibility requirements.

Rather, Docker provides a consistent container environment, reducing differences between development and deployment.

For example:

```
Development Machine
       |
       v
   Docker Image
       |
       v
  Docker Container
       |
       v
 Flask Application
```

The same image can be deployed to an appropriate Linux-based server without manually recreating the entire Python environment.

This is particularly useful for cloud deployment.

# **13. Step 11 – Pushing Docker-Related Changes to GitHub**

After testing the Dockerized application, the instructor pushes the changes to GitHub.

This is necessary because the next lecture will involve deployment.

The Dockerfile and `.dockerignore` file need to be available in the GitHub repository.

### **13.1 Checking the changes**

The instructor has added:

```
Dockerfile
.dockerignore
```

These files contain the Docker configuration required to build the application image.

### **13.2 Adding files to Git**

Command:

```
git add .
```

**Explanation:**

- `git add` stages changes.
- `.` means all applicable changes in the current repository.

This stages the Docker-related files and other modified or untracked files that are not excluded by Git.

### **13.3 Committing the changes**

Command:

```
git commit -m "add docker file"
```

**Explanation:**

| Part                | Meaning                      |
| ------------------- | ---------------------------- |
| `git commit`        | Creates a commit             |
| `-m`                | Specifies the commit message |
| `"add docker file"` | Description of the changes   |

The commit records the changes in the local Git repository.

### **13.4 Pushing changes to GitHub**

Command:

```
git push origin main
```

**Explanation:**

| Part       | Meaning                                      |
| ---------- | -------------------------------------------- |
| `git push` | Uploads local commits to a remote repository |
| `origin`   | Name of the remote repository                |
| `main`     | Target branch                                |

The instructor executes the command and observes that the changes are successfully pushed.

GitHub push successful

### **13.5 What happens after pushing?**

The GitHub repository now contains the Docker-related configuration.

The next deployment stage can use this repository to obtain the application source code and build or retrieve the Docker image.

**Important:** Pushing the code to GitHub does not automatically deploy the application to AWS EC2. That deployment is covered in the next lecture.

# **14. Complete Command Reference**

This section consolidates all the important commands used in the lecture.

| Purpose                        | Command                            |
| ------------------------------ | ---------------------------------- |
| Check available images         | `docker images`                    |
| Build Docker image             | `docker build -t human .`          |
| Run container in detached mode | `docker run -d -p 8080:5000 human` |
| Check running containers       | `docker ps`                        |
| View container logs            | `docker logs <CONTAINER_ID>`       |
| Access application             | `http://localhost:8080`            |
| Stage Git changes              | `git add .`                        |
| Commit changes                 | `git commit -m "add docker file"`  |
| Push changes                   | `git push origin main`             |

### **Docker commands worth knowing additionally**

These commands were not demonstrated in detail in the lecture, but are useful when working with Docker.

| Purpose                                     | Command                         |
| ------------------------------------------- | ------------------------------- |
| List all containers, including stopped ones | `docker ps -a`                  |
| Stop a running container                    | `docker stop <CONTAINER_ID>`    |
| Start a stopped container                   | `docker start <CONTAINER_ID>`   |
| Remove a stopped container                  | `docker rm <CONTAINER_ID>`      |
| Remove an image                             | `docker rmi <IMAGE_NAME>`       |
| Follow logs continuously                    | `docker logs -f <CONTAINER_ID>` |
| Inspect container details                   | `docker inspect <CONTAINER_ID>` |

# **15. Important Docker Concepts – Quick Comparison**

These are the concepts from this lecture that you should be able to explain confidently.

### **15.1&#x20;**`.gitignore`**&#x20;vs&#x20;**`.dockerignore`

| `.gitignore`                                                 | `.dockerignore`                                                       |
| ------------------------------------------------------------ | --------------------------------------------------------------------- |
| Used by Git                                                  | Used by Docker                                                        |
| Specifies files Git should ignore for untracked-file staging | Specifies files excluded from the Docker build context                |
| Prevents matching untracked files from being added by Git    | Prevents matching files from being sent into the Docker build context |
| Does not automatically remove previously tracked files       | Does not remove files from the host machine                           |

### **15.2 Dockerfile vs Docker Image vs Docker Container**

| Dockerfile                  | Docker Image                              | Docker Container             |
| --------------------------- | ----------------------------------------- | ---------------------------- |
| Contains build instructions | Contains packaged application environment | Runs an instance of an image |
| Used to build an image      | Used to create containers                 | Executes the application     |
| Created manually            | Created using `docker build`              | Created using `docker run`   |

### **15.3&#x20;**`RUN`**&#x20;vs&#x20;**`CMD`

| RUN                            | CMD                                |
| ------------------------------ | ---------------------------------- |
| Executes during image building | Executes when the container starts |
| Prepares the environment       | Starts the application by default  |
| Installs dependencies          | Executes `python3 app.py`          |

### **15.4&#x20;**`docker build`**&#x20;vs&#x20;**`docker run`

| `docker build`                     | `docker run`                                |
| ---------------------------------- | ------------------------------------------- |
| Builds a Docker image              | Creates and starts a container              |
| Uses Dockerfile                    | Uses an existing image                      |
| Executes build instructions        | Executes the container's startup command    |
| Example: `docker build -t human .` | Example: `docker run -d -p 8080:5000 human` |

### **15.5 Host Port vs Container Port**

| Host Port                                 | Container Port                                    |
| ----------------------------------------- | ------------------------------------------------- |
| Port exposed on the host machine          | Port used by the application inside the container |
| Used to access the application externally | Used for internal application communication       |
| 8080 in this lecture                      | 5000 in this lecture                              |

# **16. Important Practical Points and Corrections**

These are a few additional technical details that are important when implementing the same workflow yourself.

### **16.1 Flask must listen on&#x20;**`0.0.0.0`

This is particularly important for Docker.

If your Flask application uses:

```
app.run(host="127.0.0.1", port=5000)
```

it may only accept connections from inside its own container.

For Docker port mapping to work correctly, configure Flask to listen on:

```
app.run(host="0.0.0.0", port=5000)
```

This allows connections through the container's network interface.

The application port must match the container port specified in:

```
docker run -d -p 8080:5000 human
```

### **16.2 Port mapping does not change the Flask application port**

This is a common misunderstanding.

When we execute:

```
docker run -d -p 8080:5000 human
```

we are not changing Flask's port from 5000 to 8080.

We are forwarding traffic from host port 8080 to container port 5000.

### **16.3 Docker image size can be optimized**

The instructor observes an image size of approximately 1.98 GB.

This is relatively large.

Possible optimization techniques include:

- Using a smaller compatible base image.
- Avoiding unnecessary system packages.
- Excluding unnecessary files using `.dockerignore`.
- Removing package-manager caches.
- Using multi-stage builds.
- Avoiding unnecessary duplicate dependencies.

However, image optimization should not break application dependencies.

### **16.4&#x20;**`apt-get update`**&#x20;and&#x20;**`apt-get upgrade`**&#x20;are different**

- `apt-get update`: Refreshes package lists.
- `apt-get upgrade`: Upgrades installed packages using the available package lists.

The first updates information about available packages; the second installs newer versions of installed packages.

### **16.5&#x20;**`docker ps`**&#x20;does not show every container**

By default:

```
docker ps
```

shows only running containers.

To see stopped containers as well:

```
docker ps -a
```

### **16.6 Docker image creation and application deployment are different**

Building an image does not automatically start the application.

The sequence is:

```
Dockerfile
    ↓
docker build
    ↓
Docker Image
    ↓
docker run
    ↓
Docker Container
    ↓
Running Flask Application
```

### **16.7 Docker Desktop is not the same as Docker Engine**

Docker Desktop provides a graphical interface and manages the Docker environment on supported desktop systems.

Docker Engine is the underlying technology responsible for building and running containers.

A Linux EC2 server can run Docker Engine without requiring Docker Desktop.

# **17. Quick Revision – Interview and Conceptual Questions**

**Q1. What is Dockerization?**

Packaging an application and its dependencies into a Docker image so that it can run consistently in different environments.

**Q2. What is a Dockerfile?**

A text file containing instructions to build a Docker image.

**Q3. What is&#x20;**`.dockerignore`**?**

A file that specifies which files and directories should be excluded from the Docker build context.

**Q4. Why do we use&#x20;**`FROM`**?**

To specify the base image used for building our Docker image.

**Q5. What is the purpose of&#x20;**`WORKDIR`**?**

It sets the working directory inside the Docker image.

**Q6. What does&#x20;**`COPY . .`**&#x20;do?**

Copies files from the current build context on the host into the current working directory inside the image, excluding files matched by `.dockerignore`.

**Q7. What is the difference between&#x20;**`RUN`**&#x20;and&#x20;**`CMD`**?**

`RUN` executes commands during image building, whereas `CMD` specifies the default command executed when a container starts.

**Q8. Why do we use&#x20;**`-y`**&#x20;with apt-get?**

To automatically confirm installation or upgrade prompts without requiring manual interaction.

**Q9. Why are we installing AWS CLI inside the Docker image?**

To enable AWS CLI operations from the container when required by the application.

**Q10. Why are we installing CPU versions of PyTorch?**

To run the application without requiring GPU-specific CUDA dependencies.

**Q11. What is a Docker image?**

A packaged, read-only template used to create Docker containers.

**Q12. What is a Docker container?**

An isolated runtime instance created from a Docker image.

**Q13. What does&#x20;**`docker build -t human .`**&#x20;do?**

Builds a Docker image named `human` using the Dockerfile in the current directory.

**Q14. What does&#x20;**`-t`**&#x20;represent?**

It specifies the image name and optionally its tag.

**Q15. What does the dot (**`.`**) represent in the Docker build command?**

It specifies the current directory as the Docker build context.

**Q16. What does&#x20;**`docker run`**&#x20;do?**

Creates and starts a container from a Docker image.

**Q17. What is detached mode?**

It allows a Docker container to run in the background.

**Q18. What does&#x20;**`-p 8080:5000`**&#x20;mean?**

It maps host port 8080 to container port 5000.

**Q19. Why are we using port 8080?**

To access the Flask application through the host machine using Docker port mapping.

**Q20. What does&#x20;**`docker images`**&#x20;display?**

All locally available Docker images.

**Q21. What does&#x20;**`docker ps`**&#x20;display?**

Currently running Docker containers.

**Q22. What does&#x20;**`docker logs`**&#x20;do?**

Displays the logs generated by a particular container.

**Q23. Why do we use Docker Desktop?**

To visually manage Docker images, containers, logs and port mappings.

**Q24. Does pushing Dockerfile to GitHub automatically deploy the application?**

No. It only uploads the repository changes. Deployment requires additional steps.

**Q25. Why is Docker useful for cloud deployment?**

It provides a consistent runtime environment and reduces dependency and configuration differences between development and deployment environments.

# **18. Final Lecture Summary**

The instructor completes the Dockerization of the previously developed Flask application.

The complete sequence is:

| Step | Task                        | Result                             |
| ---- | --------------------------- | ---------------------------------- |
| 1    | Create `.dockerignore`      | Exclude unnecessary files          |
| 2    | Create `Dockerfile`         | Define image-building instructions |
| 3    | Select Python base image    | Establish Python environment       |
| 4    | Install system dependencies | Prepare operating system           |
| 5    | Install AWS CLI and PyTorch | Prepare required packages          |
| 6    | Set `WORKDIR /app`          | Configure working directory        |
| 7    | Execute `COPY . .`          | Copy application files             |
| 8    | Install requirements        | Install Python dependencies        |
| 9    | Configure `CMD`             | Define application startup         |
| 10   | Execute `docker build`      | Create Docker image                |
| 11   | Execute `docker run`        | Create and start container         |
| 12   | Map ports 8080 and 5000     | Expose Flask application           |
| 13   | Execute `docker ps`         | Verify running container           |
| 14   | Execute `docker logs`       | Inspect application logs           |
| 15   | Test image prediction       | Verify application functionality   |
| 16   | Push changes to GitHub      | Prepare repository for deployment  |

## **What was achieved in this lecture?**

**Docker image created successfully**

**Docker container running successfully**

**Flask application accessible through port 8080**

**Image upload and prediction tested successfully**

**Docker-related changes pushed to GitHub**

**Next lecture:** Deployment of the Dockerized Flask application on an AWS EC2 instance.

The key takeaway is that we have moved from running our Flask application directly in the local Python environment to running it inside a Docker container. This prepares the application for deployment on a cloud server such as AWS EC2.