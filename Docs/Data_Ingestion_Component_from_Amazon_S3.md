# **Detailed Notes: Data Ingestion Component Implementation**

These notes cover the complete implementation of the **Data Ingestion Component** in the Human Segmentation Using Augmentation project, including project structure, configuration, artifact management, AWS S3 integration, Python implementation, training pipeline integration, and step-by-step debugging.

# **1. Introduction to the Data Ingestion Component**

In this lecture, we start implementing the individual components of our machine learning project.

The first component we implement is the **Data Ingestion Component**.

### **What is the purpose of Data Ingestion?**

Data ingestion is the process of obtaining data from a source and making it available locally for further processing.

In this project:

1. The dataset is stored in an AWS S3 bucket.
2. We download the dataset folder from the S3 bucket.
3. The downloaded dataset is in ZIP format.
4. We extract the ZIP file.
5. We store the extracted dataset in our local project directory.
6. We return the path of the extracted data as an artifact.

This extracted data will be used by the subsequent components of the machine learning pipeline.

**Overall Data Ingestion Workflow**

**AWS S3 Bucket**

Dataset stored in ZIP format

AWS CLI – S3 Sync

**Local Download Directory**

data.zip

Python zipfile – Extract All

**Unzipped Data Directory**

Images, masks, CSV files, etc.

Data Ingestion Artifact

Path of the extracted data folder returned to the training pipeline

# **2. Step 1 – Updating Constants**

**File location:**

`src/constants/__init__.py`

The first step is to update all constants related to the Data Ingestion Component.

### **2.1 Why do we declare constants?**

Constants provide a central location where configuration-related values can be declared and accessed throughout the project.

Instead of hardcoding folder names, paths, and other configuration values in multiple files, we declare them once and import them wherever required.

**Advantages:**

- Centralized configuration management.
- Avoids repeatedly writing the same values.
- Makes modifications easier.
- Improves code organization and maintainability.

### **2.2 Constants required for Data Ingestion**

The constants define the folder names and paths required by the component.

The important constants include:

| Constant                       | Purpose                                       |
| ------------------------------ | --------------------------------------------- |
| `ARTIFACTS_DIR`                | Name of the main artifacts directory          |
| `DATA_INGESTION_ARTIFACTS_DIR` | Directory dedicated to data ingestion         |
| `DATA_INGESTION_DOWNLOAD_DIR`  | Directory where the ZIP dataset is downloaded |
| `DATA_INGESTION_UNZIP_DIR`     | Directory where the ZIP dataset is extracted  |
| `DATA_INGESTION_BUCKET_NAME`   | Name of the AWS S3 bucket                     |
| `DATA_INGESTION_S3_DATA_KEY`   | S3 dataset location/key                       |
| `DATA_INGESTION_S3_DATA_URI`   | S3 URI of the dataset                         |
| `DATA_INGESTION_RAW_DATA_DIR`  | Name/location of the raw data directory       |
| `DATA_INGESTION_RAW_DATA_ZIP`  | Name of the ZIP file                          |

*Note: The transcript explains the purpose of these constants but does not provide their exact declarations or values. Use the actual names from the project source code if they differ.*

# **3. Step 2 – Updating Configuration Entity**

**File location:**

`src/entity/config_entity.py`

After declaring constants, we define the configuration information for the Data Ingestion Component.

### **3.1 What is a Configuration Entity?**

A configuration entity is a data class structure used to organize and store configuration-related information required by a component.

In this project, the Data Ingestion Configuration Entity defines the paths where different files and folders will be created.

It uses the project root directory to construct paths.

### **3.2 Understanding&#x20;**`from_root`

The `from_root` functionality provides a path relative to the root directory of the project.

For example, suppose our project root is:

```
Human-Segmentation-Using-Augmentation/
```

We use this root directory to construct the artifacts path.

The directory structure will look like:

```
Human-Segmentation-Using-Augmentation/
│
└── artifacts/
    │
    └── data_ingestion/
        │
        ├── data/
        │   └── data.zip
        │
        └── unzip/
            └── data/
                ├── Training_Images/
                ├── Ground_Truth/
                └── CSV files
```

The exact extracted subfolder names depend on the dataset.

### **3.3 Important configuration paths**

The configuration entity creates and maintains the following paths:

| Configuration                 | Purpose                                     |
| ----------------------------- | ------------------------------------------- |
| `artifacts_dir`               | Main artifacts directory                    |
| `data_ingestion_artifact_dir` | Data ingestion-specific artifacts directory |
| `download_dir`                | Location where data is downloaded           |
| `unzip_dir`                   | Location where data is extracted            |
| `raw_data_dir`                | Raw data directory                          |
| `raw_data_zip`                | Complete path of the downloaded ZIP file    |

**Important distinction:**

- `download_dir` stores the downloaded ZIP file.
- `unzip_dir` stores the extracted contents.
- `raw_data_zip` points to the actual ZIP file.

The configuration entity ensures that all these paths are available to the component through a single configuration object.

# **4. Step 3 – Updating Artifacts Entity**

**File location:**

`src/entity/artifacts_entity.py`

Before implementing the component, we need to define what it will return.

### **4.1 What is an Artifact?**

An artifact is the output generated by a particular component.

For example:

- Data Ingestion Component → Extracted dataset path.
- Data Validation Component → Validation results.
- Data Transformation Component → Transformed dataset.
- Model Trainer Component → Trained model.

Artifacts are generally represented using structured data classes.

### **4.2 Data Ingestion Artifact**

The Data Ingestion Component returns a `DataIngestionArtifact`.

Its primary responsibility is to store the path of the extracted data folder.

Conceptually:

```
@dataclassclass DataIngestionArtifact:    data_path: str
```

The actual attribute name should match the project implementation.

**Why do we return the extracted data path?**

Because the next component in the pipeline needs to know where the dataset is stored.

Instead of searching for the dataset again, the next component can directly access the path from the artifact.

# **5. Step 4 – Creating the Data Ingestion Component**

**File location:**

`src/components/data_ingestion.py`

Now we create the basic skeleton of the Data Ingestion Component.

### **5.1 Importing required modules**

The component requires imports related to:

- Logging.
- Exception handling.
- Configuration entities.
- Artifact entities.
- AWS S3 synchronization.
- Python ZIP file handling.
- File and directory operations.

The exact imports depend on the implementation.

### **5.2 Creating the class**

We create a class named:

```
class DataIngestion:
```

Inside this class, we define a constructor and the main component execution function.

### **5.3 Constructor (**`__init__`**)**

The constructor initializes three important variables:

**1. Data Ingestion Configuration**

```
self.data_ingestion_config
```

This variable contains all the directory paths and configuration information required by the component.

It is initialized using the `DataIngestionConfig` entity.

**2. S3 Sync**

```
self.s3_sync
```

This object is responsible for synchronizing data between the local system and AWS S3.

We will implement it separately using AWS CLI commands.

**3. Data Ingestion Artifact**

```
self.data_ingestion_artifact
```

This variable represents the output of the component.

It contains the path of the extracted dataset.

### **5.4 Main function –&#x20;**`initiate_data_ingestion()`

This is the main execution function of the Data Ingestion Component.

Its responsibility is to execute the complete ingestion process.

The execution sequence is:

1. Log the beginning of data ingestion.
2. Create the required directories.
3. Download the dataset from AWS S3.
4. Extract the downloaded ZIP file.
5. Prepare the Data Ingestion Artifact.
6. Return the artifact.

Conceptually:

```
def initiate_data_ingestion(self) -> DataIngestionArtifact:    # Log information    # Create required directories    # Download data from cloud    # Unzip downloaded data    # Prepare Data Ingestion Artifact    return self.data_ingestion_artifact
```

The function explicitly specifies `DataIngestionArtifact` as its return type because it returns the artifact generated by this component.

### **5.5 Two important functions to implement**

Inside the Data Ingestion Component, we define two functions:

1. `get_data_from_cloud()`
2. `unzip_data()`

Their detailed implementations are explained below.

# **6. Step 5 – Integrating the Training Pipeline**

**File location:**

`src/pipeline/training_pipeline.py`

After preparing the Data Ingestion Component, we need to connect it to the main training pipeline.

The component should not execute independently. It should be triggered through the training pipeline.

### **6.1 Importing necessary modules**

The training pipeline imports:

- Logger.
- Exception handling.
- Constants.
- Configuration entities.
- Artifact entities.
- Data Ingestion Component.

The transcript uses wildcard imports (`*`) for some project modules to import their available definitions.

### **6.2 Creating the Training Pipeline class**

We create:

```
class TrainPipeline:
```

Inside its constructor, we initialize the Data Ingestion Configuration.

This makes the configuration information available to the pipeline.

### **6.3 Creating&#x20;**`start_data_ingestion()`

This function is responsible for initiating the Data Ingestion Component.

It:

1. Creates an object of the `DataIngestion` class.
2. Calls `initiate_data_ingestion()`.
3. Receives the Data Ingestion Artifact.
4. Returns that artifact.

Conceptually:

```
def start_data_ingestion(self) -> DataIngestionArtifact:    data_ingestion = DataIngestion(        data_ingestion_config=self.data_ingestion_config    )    return data_ingestion.initiate_data_ingestion()
```

The return type is `DataIngestionArtifact` because this function returns the output of the Data Ingestion Component.

### **6.4 Creating&#x20;**`run_pipeline()`

This is the main function responsible for executing the components of the training pipeline sequentially.

For now, we have only implemented the Data Ingestion Component.

Therefore, the function calls:

```
def run_pipeline(self) -> None:    data_ingestion_artifact = self.start_data_ingestion()
```

**Important concepts:**

- `start_data_ingestion()` triggers the Data Ingestion Component.
- `run_pipeline()` controls the execution of the overall pipeline.
- `data_ingestion_artifact` receives the output generated by the component.
- `None` is the return type of `run_pipeline()` because it does not explicitly return a value.

As we implement more components, they will be added to `run_pipeline()` and executed sequentially.

### **6.5 Overall connection between the pipeline and component**

**demo.py**

Creates TrainPipeline object

**run_pipeline()**

Controls pipeline execution

**start_data_ingestion()**

Triggers the ingestion component

**initiate_data_ingestion()**

Downloads, extracts and prepares data

**DataIngestionArtifact**

Returns extracted dataset path

# **7. Step 6 – Integrating AWS CLI for S3 Operations**

Now that the basic component structure and training pipeline are ready, we need to implement the two functions responsible for downloading and extracting data.

For downloading the dataset, the instructor uses **AWS CLI**.

### **7.1 Why AWS CLI?**

AWS CLI (Command Line Interface) allows us to interact with AWS services directly through terminal commands.

Using AWS CLI, we can perform operations such as:

- Creating an S3 bucket.
- Listing S3 buckets.
- Listing objects inside a bucket.
- Uploading files.
- Downloading files.
- Synchronizing local folders with S3.
- Deleting buckets and objects.

AWS also provides Boto3, which is its Python SDK.

However, the instructor chooses AWS CLI because it provides a relatively straightforward way to perform the required S3 operations.

### **7.2 AWS CLI documentation**

The instructor refers to the official AWS documentation:

[AWS CLI – S3 Commands Documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-services-s3.html?utm_source=chatgpt.com)

The project requires only two S3 synchronization operations.

### **7.3 Downloading a folder from S3**

The command used is:

```
aws s3 sync <S3_URI> <LOCAL_FOLDER_PATH>
```

For example:

```
aws s3 sync s3://human-segmentation/data ./data
```

**Explanation:**

| Part                           | Meaning                                 |
| ------------------------------ | --------------------------------------- |
| `aws`                          | Invokes AWS CLI                         |
| `s3`                           | Specifies Amazon S3                     |
| `sync`                         | Synchronizes the source and destination |
| `s3://human-segmentation/data` | Source folder in S3                     |
| `./data`                       | Local destination folder                |

This command downloads the contents of the specified S3 folder into the local directory.

**Important:** The source comes first and the destination comes second.

### **7.4 Uploading a folder to S3**

The command used for uploading is:

```
aws s3 sync <LOCAL_FOLDER_PATH> <S3_URI>
```

For example:

```
aws s3 sync ./data s3://human-segmentation/data
```

Here:

- Local folder is the source.
- S3 folder is the destination.
- The command synchronizes local files with the S3 location.

### **7.5 Difference between both operations**

| Operation        | Command structure               |
| ---------------- | ------------------------------- |
| Download from S3 | `aws s3 sync S3_URI LOCAL_PATH` |
| Upload to S3     | `aws s3 sync LOCAL_PATH S3_URI` |

The two commands have the same structure, but the source and destination are reversed.

### **7.6 How to obtain the S3 URI from AWS Console**

The instructor demonstrates how to obtain the S3 URI of the dataset.

Follow these steps:

1. Open your AWS account.
2. Navigate to the Amazon S3 service.
3. Open the bucket containing your dataset.
4. Locate the required folder.
5. Select the folder.
6. Click on **Copy S3 URI**.
7. Copy the URI.
8. Paste the copied URI into the appropriate project constant.

For this project:

- S3 bucket name: `human-segmentation`
- Dataset folder: `data`
- S3 URI: `s3://human-segmentation/data`

[LESSON 4 — Github, DVC and AWS S3 | by doductai | Medium](https://images.openai.com/static-rsc-4/cpvAdAO6Pb6Py9bFneThZ6ghVFDqRFYkcfmmTowaB6AFSqwDWp4gQtgFarFXi3LLzvoyLuazl7v2iTUUYwPFy3TKmhfZ1AQUvtxpQ_-5O8eB6of0JhZQk47nkL1yhHVHGnCTJsMLUeNqNBsBp9hemJ1eOmPbHm63-GcOKxDj2iI?purpose=inline)

[medium.com](https://medium.com/%40doductai8590/les-4-github-dvc-and-aws-cf6d0c69a755?utm_source=chatgpt.com)

This URI becomes the source location for the download operation.

### **7.7 Creating S3 synchronization functions**

**File location:**

`src/cloud_storage/aws_storage.py`

The instructor creates two functions inside the cloud storage module.

**Function 1:&#x20;**`sync_folder_from_s3()`

Its responsibility is to download a folder from an S3 bucket to local storage.

Conceptually:

```
def sync_folder_from_s3(self, folder, aws_bucket_url):    command = f"aws s3 sync {aws_bucket_url} {folder}"    os.system(command)
```

**Function 2:&#x20;**`sync_folder_to_s3()`

Its responsibility is to upload a local folder to an S3 bucket.

Conceptually:

```
def sync_folder_to_s3(self, folder, aws_bucket_url):    command = f"aws s3 sync {folder} {aws_bucket_url}"    os.system(command)
```

These are conceptual representations of the operations described in the lecture.

### **7.8 Understanding the parameters**

Both functions accept two parameters:

| Parameter        | Meaning              |
| ---------------- | -------------------- |
| `folder`         | Local folder path    |
| `aws_bucket_url` | S3 bucket/folder URI |

For downloading:

- `aws_bucket_url` is the source.
- `folder` is the destination.

For uploading:

- `folder` is the source.
- `aws_bucket_url` is the destination.

**Important:** The instructor creates both functions even though the current Data Ingestion Component only needs the download operation. The upload function can be reused elsewhere in the project.

### **7.9 AWS CLI prerequisites**

Before executing these operations, AWS CLI must be installed and configured on the local system.

The machine must have valid AWS credentials and permissions to access the required S3 bucket.

For example, the AWS CLI configuration can be initialized using:

```
aws configure
```

This normally requests:

- AWS Access Key ID.
- AWS Secret Access Key.
- Default region.
- Default output format.

The IAM identity must have the appropriate S3 permissions, such as `s3:ListBucket` and `s3:GetObject` for downloading, and `s3:PutObject` for uploading.

# **8. Step 7 – Implementing&#x20;**`get_data_from_cloud()`

**File location:**

`src/components/data_ingestion.py`

After implementing the S3 synchronization functions, we can now define the first major function inside the Data Ingestion Component.

### **8.1 Purpose**

The main responsibility of:

```
get_data_from_cloud()
```

is to download the dataset folder from the AWS S3 bucket to the local system.

The dataset is stored in the S3 bucket:

```
human-segmentation/data
```

The dataset folder contains a ZIP file.

### **8.2 Understanding the conditional logic**

The function contains two main blocks:

- `if` block.
- `else` block.

The purpose is to avoid downloading the dataset repeatedly when it is already available locally.

**IF block – Folder already exists**

First, the function checks whether the download directory already exists.

Conceptually:

```
if os.path.exists(self.data_ingestion_config.download_dir):    logger.info("Files already exist")
```

If the directory already exists, the function skips downloading the dataset again.

**Why?**

Because repeatedly downloading the same dataset wastes:

- Time.
- Network bandwidth.
- AWS data transfer resources.

**ELSE block – Folder does not exist**

If the download directory does not exist, the function performs the following operations:

1. Creates the download directory.
2. Calls the S3 synchronization function.
3. Passes the local download directory.
4. Passes the S3 dataset URI.
5. Downloads the dataset from S3.
6. Logs the download information.

Conceptually:

```
else:    os.makedirs(        self.data_ingestion_config.download_dir,        exist_ok=True    )    self.s3_sync.sync_folder_from_s3(        folder=self.data_ingestion_config.download_dir,        aws_bucket_url=self.data_ingestion_config.s3_data_uri    )
```

### **8.3 Understanding&#x20;**`os.makedirs()`

```
os.makedirs(path, exist_ok=True)
```

This function creates the specified directory, including any missing parent directories.

The parameter:

```
exist_ok=True
```

means that Python will not raise a `FileExistsError` if the directory already exists.

### **8.4 Understanding the actual download operation**

The most important statement is:

```
self.s3_sync.sync_folder_from_s3(...)
```

This calls the function we previously created in the AWS storage module.

The arguments are:

| Argument         | Value                    |
| ---------------- | ------------------------ |
| `folder`         | Local download directory |
| `aws_bucket_url` | S3 dataset URI           |

The download flow is:

**get_data_from_cloud()**

Check: Does download directory exist?

YES

Skip download

NO

Create directory

Run S3 sync

Download ZIP

**Result:** The downloaded ZIP file is stored inside the Data Ingestion download directory.

For this project, the resulting path is:

```
artifacts/
└── data_ingestion/
    └── data/
        └── data.zip
```

# **9. Step 8 – Implementing&#x20;**`unzip_data()`

**File location:**

`src/components/data_ingestion.py`

Once the dataset has been downloaded from AWS S3, our next task is to extract it.

The instructor implements this functionality using Python's built-in `zipfile` module.

### **9.1 Why do we need to unzip the data?**

The dataset stored in the S3 bucket is in ZIP format.

We cannot directly use the compressed dataset folder for the subsequent processing steps.

Therefore, we need to extract the ZIP file and make its contents available in a normal directory structure.

### **9.2 Importing the ZIP module**

```
from zipfile import ZipFile
```

`zipfile` is part of Python's standard library.

Therefore, there is no need to install an additional external package.

### **9.3 Getting the ZIP file path**

First, we obtain the path of the downloaded ZIP file from the Data Ingestion Configuration.

Conceptually:

```
raw_zip_path = self.data_ingestion_config.raw_data_zip
```

This path points to:

```
artifacts/data_ingestion/data/data.zip
```

### **9.4 Checking whether the extracted directory already exists**

Just like the download function, the unzip function also contains an `if-else` condition.

**IF block – Data already extracted**

The function checks whether the destination extraction directory already exists.

If it exists:

- The function skips extraction.
- A log message is generated.
- The message indicates that the unzip folder already exists and extraction is being skipped.

Conceptually:

```
if os.path.exists(self.data_ingestion_config.unzip_dir):    logger.info("Unzip folder already exists. Skipping unzipping.")
```

**ELSE block – Data not extracted**

If the extraction directory does not exist:

1. Create the destination directory.
2. Open the ZIP file.
3. Extract all its contents.
4. Store the extracted files in the configured destination.
5. Log successful extraction.

### **9.5 Creating the extraction directory**

```
os.makedirs(    self.data_ingestion_config.unzip_dir,    exist_ok=True)
```

This creates the destination directory where all extracted data will be stored.

### **9.6 Opening the ZIP file using&#x20;**`ZipFile`

The instructor uses:

```
with ZipFile(raw_zip_path, 'r') as f:
```

Let's understand this statement.

| Part           | Explanation                                                                    |
| -------------- | ------------------------------------------------------------------------------ |
| `ZipFile`      | Python class used to work with ZIP files                                       |
| `raw_zip_path` | Path of the ZIP file to open                                                   |
| `'r'`          | Opens the ZIP file in read mode                                                |
| `as f`         | Stores the opened ZIP file object in variable `f`                              |
| `with`         | Context manager that automatically closes the ZIP file when the block finishes |

### **9.7 Extracting all files**

Inside the `with` block, the instructor uses:

```
f.extractall(    self.data_ingestion_config.unzip_dir)
```

The `extractall()` method extracts all files and folders contained in the ZIP archive into the specified destination directory.

**Parameters:**

- ZIP source: `raw_zip_path`.
- Extraction destination: `unzip_dir`.

Conceptually, the complete extraction operation is:

```
with ZipFile(raw_zip_path, 'r') as f:    f.extractall(        self.data_ingestion_config.unzip_dir    )
```

### **9.8 Logging successful extraction**

After extraction, a log message is generated to indicate that the unzipping operation has completed successfully.

It also mentions the location where the dataset has been extracted.

### **9.9 Understanding the complete unzip flow**

**unzip_data()**

Get raw ZIP file path

Check whether extraction directory exists

YES

Skip extraction

NO

Create directory

Open ZIP file

Extract all files

Log completion

### **9.10 Expected extracted directory structure**

After successful extraction, the project directory looks approximately like this:

```
Human-Segmentation-Using-Augmentation/
│
└── artifacts/
    │
    └── data_ingestion/
        │
        ├── data/
        │   └── data.zip
        │
        └── unzip/
            │
            └── data/
                │
                ├── Ground_Truth/
                │
                ├── Training_Images/
                │
                └── CSV files
```

The dataset contains:

- **Training Images:** Images containing human subjects.
- **Ground Truth:** Corresponding segmentation masks.
- **CSV files:** Dataset-related information.

The Ground Truth masks represent the human regions in the corresponding training images.

# **10. Step 9 – Completing&#x20;**`initiate_data_ingestion()`

Now both helper functions have been implemented:

1. `get_data_from_cloud()`
2. `unzip_data()`

We can complete the main execution function.

### **Execution sequence**

The `initiate_data_ingestion()` function performs the following operations:

**Step 1:** Generate a log message indicating that data ingestion has started.

**Step 2:** Create the required directories using the directory creation logic.

**Step 3:** Call:

```
self.get_data_from_cloud()
```

This downloads the ZIP file from AWS S3 if it is not already available locally.

**Step 4:** Call:

```
self.unzip_data()
```

This extracts the ZIP file if the dataset has not already been extracted.

**Step 5:** Create the Data Ingestion Artifact.

The artifact stores the path of the extracted data directory.

Conceptually:

```
self.data_ingestion_artifact = DataIngestionArtifact(    data_path=self.data_ingestion_config.unzip_dir)
```

The actual constructor argument must match the attribute defined in `artifacts_entity.py`.

**Step 6:** Log that the Data Ingestion Artifact has been prepared successfully.

**Step 7:** Return the artifact.

```
return self.data_ingestion_artifact
```

### **Why is the artifact returned?**

The extracted dataset is required by subsequent pipeline components.

Returning the artifact allows the next component to access the dataset location without having to repeat the downloading and extraction operations.

# **11. Step 10 – Debugging the Data Ingestion Component**

After completing the implementation, the instructor demonstrates how to debug the component using VS Code.

Debugging helps us understand how the different functions are executed and how the directory paths are generated.

### **11.1 Creating&#x20;**`demo.py`

First, create a new file:

```
demo.py
```

This file is used to execute and debug the training pipeline independently.

### **11.2 Importing the Training Pipeline**

Inside `demo.py`, import the training pipeline class.

```
from src.pipeline.training_pipeline import TrainPipeline
```

### **11.3 Creating the pipeline object**

Create an object of the `TrainPipeline` class.

```
obj = TrainPipeline()
```

### **11.4 Calling&#x20;**`run_pipeline()`

Now use the pipeline object to call the main execution function.

```
obj.run_pipeline()
```

The complete conceptual structure of `demo.py` is:

```
from src.pipeline.training_pipeline import TrainPipelineobj = TrainPipeline()obj.run_pipeline()
```

This triggers the execution of the Data Ingestion Component through the training pipeline.

### **11.5 Setting breakpoints**

Before starting debugging, the instructor sets two breakpoints.

**Breakpoint 1: Inside the Data Ingestion Component**

Set a breakpoint around the creation or preparation of the Data Ingestion Artifact.

This allows us to inspect the component's output and understand the extracted data path.

**Breakpoint 2: Inside&#x20;**`demo.py`

Set another breakpoint at:

```
obj.run_pipeline()
```

This allows us to begin debugging from the pipeline execution.

### **11.6 Starting the debugger**

In VS Code:

1. Open the `demo.py` file.
2. Set the breakpoints.
3. Navigate to the Run menu.
4. Select Start Debugging.

Alternatively, press:

```
F5
```

This starts the debugging session.

# **12. Understanding Step Into and Step Over**

During debugging, the instructor uses two important operations.

These are essential for understanding how functions execute in Python.

### **12.1 Step Into – F11**

**Shortcut: F11**

Step Into allows us to enter a function and execute its statements line by line.

For example:

```
obj.run_pipeline()
```

When the debugger reaches this statement, pressing F11 takes us inside the `run_pipeline()` function.

If we press F11 again on:

```
self.start_data_ingestion()
```

the debugger enters the `start_data_ingestion()` function.

Similarly, we can enter:

- `initiate_data_ingestion()`
- `get_data_from_cloud()`
- `unzip_data()`

This helps us understand the internal execution of each function.

### **12.2 Step Over – F10**

**Shortcut: F10**

Step Over executes the current line without entering the function being called.

For example:

```
self.get_data_from_cloud()
```

If we press F10, the debugger executes the entire function and moves to the next statement in the current function.

**Difference between Step Into and Step Over:**

| Feature                 | Step Into (F11)                       | Step Over (F10)                                               |
| ----------------------- | ------------------------------------- | ------------------------------------------------------------- |
| Function execution      | Enters the function                   | Executes without entering                                     |
| Line-by-line inspection | Yes, inside the function              | No, inside the called function                                |
| Best use                | Understanding internal implementation | Skipping functions whose implementation is already understood |

# **13. Step 11 – Debugging Configuration Paths**

The instructor first enters the Data Ingestion initialization process using F11.

During debugging, we can observe the `DataIngestionConfig` object.

This is where the folder paths are generated.

### **13.1 Understanding the project root directory**

The root directory is:

```
Human-Segmentation-Using-Augmentation/
```

All artifact directories are created relative to this project root.

### **13.2 Understanding the artifacts directory**

The first directory created is:

```
artifacts/
```

This is the main directory used to store the outputs generated by different components.

### **13.3 Understanding the Data Ingestion directory**

Inside artifacts, we have:

```
artifacts/
└── data_ingestion/
```

This directory stores the outputs related specifically to the Data Ingestion Component.

### **13.4 Understanding the download directory**

Inside the Data Ingestion directory:

```
artifacts/
└── data_ingestion/
    └── data/
```

This is where the dataset is downloaded from the AWS S3 bucket.

Since the dataset is stored in ZIP format, the downloaded file is:

```
artifacts/data_ingestion/data/data.zip
```

### **13.5 Understanding the unzip directory**

The extracted dataset is stored separately:

```
artifacts/
└── data_ingestion/
    └── unzip/
        └── data/
```

The instructor uses this directory to store the extracted contents of the ZIP file.

### **13.6 Understanding the raw ZIP path**

The raw ZIP path points to:

```
artifacts/data_ingestion/data/data.zip
```

This is the source file used by Python's `ZipFile` class.

### **13.7 Complete path structure**

The instructor demonstrates how all the configured paths are generated.

```
Human-Segmentation-Using-Augmentation/
│
└── artifacts/
    │
    └── data_ingestion/
        │
        ├── data/
        │   └── data.zip
        │
        └── unzip/
            └── data/
                ├── Ground_Truth/
                ├── Training_Images/
                └── CSV files
```

**Important debugging observation:**

The configuration entity does not download or extract anything itself.

Its responsibility is to prepare and provide the required paths.

The actual downloading and extraction happen inside the Data Ingestion Component.

# **14. Step 12 – Debugging&#x20;**`get_data_from_cloud()`

After understanding the configuration paths, the instructor enters:

```
get_data_from_cloud()
```

using F11.

### **Execution process**

**Step 1: Check whether the download directory exists.**

The function checks whether the configured download directory is already available.

During the first execution, the directory does not exist.

Therefore, the condition evaluates to `False`.

**Step 2: Enter the ELSE block.**

Since the directory does not exist, the function enters the `else` block.

**Step 3: Create the directory.**

The download directory is created.

```
artifacts/data_ingestion/data/
```

**Step 4: Execute the AWS CLI synchronization command.**

The function calls:

```
self.s3_sync.sync_folder_from_s3(...)
```

This triggers the AWS CLI operation:

```
aws s3 sync s3://human-segmentation/data <LOCAL_DOWNLOAD_PATH>
```

**Step 5: Download the ZIP file.**

The dataset is downloaded from the S3 bucket.

During debugging, the instructor observes that the download operation is successfully executing.

The resulting file is:

```
artifacts/
└── data_ingestion/
    └── data/
        └── data.zip
```

**Step 6: Log the information.**

After the download operation, the component logs the relevant information.

At this point, the first major task of data ingestion is complete.

Download completed

# **15. Step 13 – Debugging&#x20;**`unzip_data()`

After downloading the ZIP file, the instructor moves to the next function:

```
unzip_data()
```

### **Execution process**

**Step 1: Obtain the raw ZIP path.**

The function accesses:

```
artifacts/data_ingestion/data/data.zip
```

This is the ZIP file downloaded from AWS S3.

**Step 2: Check whether the extraction directory exists.**

The function checks the existence of the configured unzip directory.

During the first execution, the directory does not exist.

Therefore, the function enters the `else` block.

**Step 3: Create the extraction directory.**

The destination directory is created.

```
artifacts/data_ingestion/unzip/
```

**Step 4: Open the ZIP file.**

The Python `ZipFile` class opens the downloaded ZIP file in read mode.

**Step 5: Extract all contents.**

The function executes:

```
f.extractall(    self.data_ingestion_config.unzip_dir)
```

All files and folders contained inside the ZIP archive are extracted.

**Step 6: Log successful extraction.**

A log message indicates that the unzipping process has completed and specifies the extraction location.

Extraction completed

# **16. Step 14 – Preparing the Data Ingestion Artifact**

After both operations have completed successfully, the instructor reaches the artifact preparation section.

At this stage:

- Dataset has been downloaded.
- ZIP file is available locally.
- Dataset has been extracted.
- Extracted data is available in the configured directory.

Now the component creates its output artifact.

### **What does the artifact contain?**

The Data Ingestion Artifact contains the path of the extracted dataset directory.

Conceptually:

```
DataIngestionArtifact(    data_path="artifacts/data_ingestion/unzip")
```

The actual path and attribute name depend on the project configuration.

The artifact is returned by:

```
return self.data_ingestion_artifact
```

The instructor observes that the Data Ingestion Artifact has been prepared successfully.

The artifact is then passed back through:

```
initiate_data_ingestion()
        ↓
start_data_ingestion()
        ↓
run_pipeline()
```

This completes the execution of the first component.

# **17. Step 15 – Verifying the Artifacts Directory**

After debugging, the instructor stops the debugger and manually inspects the generated artifacts.

The purpose is to verify whether the expected directory structure has been created correctly.

### **17.1 Verifying the downloaded ZIP file**

Navigate to:

```
artifacts/data_ingestion/data/
```

Check whether:

```
data.zip
```

is present.

This confirms that the dataset has been downloaded successfully.

### **17.2 Verifying the extracted data**

Next, navigate to:

```
artifacts/data_ingestion/unzip/
```

Check whether the extracted dataset directory exists.

The instructor verifies the following contents:

| Folder/File       | Description                               |
| ----------------- | ----------------------------------------- |
| `Training_Images` | Contains images of human subjects         |
| `Ground_Truth`    | Contains corresponding segmentation masks |
| CSV files         | Contains dataset-related information      |

### **17.3 Understanding Training Images and Ground Truth**

This is particularly important because the project is about human image segmentation.

**Training Images:**

These are the original images containing humans.

**Ground Truth:**

These are the corresponding segmentation masks that identify the human regions in the images.

The segmentation model will eventually learn the relationship between the original images and their corresponding masks.

[people-segmentation · PyPI](https://images.openai.com/static-rsc-4/2OiFTCoU3RQ_QhoqxzrQxXh1HG-nsFOl7PNIfTgCtrtqa-H8wGB0A4_9f60uVo72Y7Vh3TEc3sbZ7OA6N9ySOwu38rRPbF7KYxGmIlHWpeN3lsh-xf_9MSmp7XrWUZb4lk3peKIM8XbUePmgvZSNtlfNsdMkDZ-YiF1wkL7t62g?purpose=inline)

[Go Selfies — How to do photo background removal using deep learning(segmentation + codes) | by Yunan Wu | Medium](https://images.openai.com/static-rsc-4/-crso-Tuq5bpz89apeLIA8a4Dguq4raLxw_l71aCJGCfMfGlyHNfp6ZvbjftYQ3fXgGXQebpddVgSaECiT_9BikzZRbzIobulgLoTHB9uROhaNxXXWoSwOmgcDcIVKXBU80b_SHoTDu0x0PeKSKsdxqEslqF_MT47UGJo1VMXLY?purpose=inline)

[GitHub - David-Estevez/u2net: Implementation of "U^2-Net: Going Deeper with Nested U-Structure for Salient Object Detection" packaged for easy use. (Original repo: https://github.com/xuebinqin/U-2-Net) · GitHub](https://images.openai.com/static-rsc-4/g8wLTN72KohGZDMcrvfsMJayle1XfSSkAHBPFqdA8DcJAuHiCNtSai9RohSHi5MtwueMJvsPZdSlEJz8auOYpPGmov7W2lcH5tzT__mc5r_Ya1qNSGH-egGTfYyJ3RJ0cxinMn3ICm549W196tOcQ5hDGjkOWy2ica0EFdPLTPQ?purpose=inline)

7

After verifying the ZIP file and extracted folders, the instructor confirms that everything has been created successfully.

The Data Ingestion Component is now complete.

# **18. Complete Data Ingestion Component – Execution Summary**

Let's consolidate the entire implementation into one sequence.

## **Data Ingestion: Complete Workflow**

1. **Update Constants**

   `src/constants/__init__.py`

   Define folder names, artifact paths and S3-related constants.
2. **Update Configuration Entity**

   `src/entity/config_entity.py`

   Define all paths required by the Data Ingestion Component.
3. **Update Artifacts Entity**

   `src/entity/artifacts_entity.py`

   Define `DataIngestionArtifact` to store the extracted dataset path.
4. **Create Data Ingestion Component**

   `src/components/data_ingestion.py`

   Prepare the class, constructor and main execution function.
5. **Create AWS S3 Operations**

   `src/cloud_storage/aws_storage.py`

   Implement folder download and upload using AWS CLI.
6. **Implement Cloud Download**

   `get_data_from_cloud()`

   Download the ZIP file from AWS S3 if it is not already downloaded.
7. **Implement ZIP Extraction**

   `unzip_data()`

   Extract the ZIP file into the configured directory.
8. **Prepare Artifact**

   `initiate_data_ingestion()`

   Store and return the extracted dataset path.
9. **Integrate with Training Pipeline**

   `src/pipeline/training_pipeline.py`

   Create `start_data_ingestion()` and call it from `run_pipeline()`.
10. **Debug and Verify**

    `demo.py`

    Execute the pipeline, inspect the paths and verify the downloaded and extracted data.

# **19. Important Concepts to Remember**

These are the key concepts introduced in this lecture.

| Concept                 | Explanation                                            |
| ----------------------- | ------------------------------------------------------ |
| Constants               | Centralized storage of configuration values            |
| Configuration Entity    | Maintains paths and configuration information          |
| Artifacts               | Outputs generated by individual components             |
| Data Ingestion          | Obtaining and preparing data for subsequent processing |
| AWS S3                  | Cloud object storage service                           |
| AWS CLI                 | Command-line interface for interacting with AWS        |
| `aws s3 sync`           | Synchronizes files between local storage and S3        |
| `os.path.exists()`      | Checks whether a file or directory exists              |
| `os.makedirs()`         | Creates directories                                    |
| `exist_ok=True`         | Avoids errors if a directory already exists            |
| `ZipFile`               | Python class for working with ZIP archives             |
| `extractall()`          | Extracts all contents of a ZIP archive                 |
| `with`                  | Context manager that handles resource cleanup          |
| `DataIngestionArtifact` | Stores the output of data ingestion                    |
| `run_pipeline()`        | Controls sequential execution of pipeline components   |
| Step Into (F11)         | Enters a function during debugging                     |
| Step Over (F10)         | Executes a function without entering it                |

# **20. Important Practical Observations**

A few implementation details are worth understanding beyond the lecture.

**1. AWS CLI and Boto3 are different approaches.**

- AWS CLI allows AWS operations through terminal commands.
- Boto3 allows AWS operations directly through Python code.

The instructor chooses AWS CLI for simplicity.

**2. Downloading and extracting are separate operations.**

Downloading only obtains the ZIP file. Extraction makes its contents available as normal files and folders.

**3. Configuration Entity and Artifact Entity have different responsibilities.**

- Configuration Entity tells the component where to perform operations.
- Artifact Entity tells other components where the output is available.

**4. The component avoids repeated operations.**

The existence checks prevent repeated downloads and extraction when the corresponding directories already exist.

However, these checks only verify directory existence. They do not verify whether the directory contains complete, valid, or up-to-date data. A partially downloaded or outdated directory could therefore be skipped.

**5. AWS S3 synchronization is not the same as downloading a single file.**

`aws s3 sync` synchronizes the contents of a folder/prefix. It can download multiple objects while preserving the directory structure.

**6. Artifact passing makes the pipeline modular.**

The next component does not need to know how the data was downloaded or extracted. It only needs the artifact containing the data path.

**7. A production implementation should handle errors.**

The conceptual AWS CLI examples in these notes use `os.system()` to illustrate execution. A more robust implementation should check command exit status, handle exceptions, validate ZIP integrity, and avoid extracting untrusted ZIP paths without validation.

# **21. Quick Revision – Questions and Answers**

**Q1. What is the main purpose of the Data Ingestion Component?**

To download the dataset from AWS S3, extract it locally and make it available for subsequent pipeline components.

**Q2. Why do we use constants?**

To maintain configuration-related values centrally and access them throughout the project.

**Q3. What is the purpose of&#x20;**`config_entity.py`**?**

It defines and manages the directory paths required by different components.

**Q4. What is an artifact?**

An artifact is the output generated by a component.

**Q5. What does&#x20;**`DataIngestionArtifact`**&#x20;contain?**

The path of the extracted dataset.

**Q6. Why do we use AWS CLI?**

To interact with AWS services and perform S3 operations through terminal commands.

**Q7. What is the command to download data from S3?**

```
aws s3 sync <S3_URI> <LOCAL_PATH>
```

**Q8. What is the command to upload data to S3?**

```
aws s3 sync <LOCAL_PATH> <S3_URI>
```

**Q9. Why do we use&#x20;**`os.path.exists()`**?**

To check whether the download or extraction directory already exists.

**Q10. Why do we use&#x20;**`os.makedirs()`**?**

To create the required directory structure.

**Q11. Why do we use Python's&#x20;**`zipfile`**&#x20;module?**

To extract the downloaded ZIP archive.

**Q12. What does&#x20;**`extractall()`**&#x20;do?**

It extracts all files and folders from the ZIP archive into the specified destination.

**Q13. Why do we use&#x20;**`with ZipFile()`**?**

To open and work with the ZIP file using a context manager that automatically closes it afterward.

**Q14. What is the purpose of&#x20;**`start_data_ingestion()`**?**

To initialize and execute the Data Ingestion Component and return its artifact.

**Q15. What is the purpose of&#x20;**`run_pipeline()`**?**

To control the execution of all components in the training pipeline sequentially.

**Q16. What is the difference between F11 and F10?**

F11 enters a function, whereas F10 executes the function without entering it.

**Q17. Why do we create&#x20;**`demo.py`**?**

To independently execute and debug the training pipeline.

**Q18. What is the difference between Training Images and Ground Truth?**

Training Images contain the original human images, whereas Ground Truth contains the corresponding segmentation masks.

## **Final takeaway**

The most important concept of this lecture is understanding how an individual ML pipeline component is structured and connected to the overall training pipeline.

The Data Ingestion Component follows this flow:

```
AWS S3
  ↓
Download ZIP using AWS CLI
  ↓
Store ZIP locally
  ↓
Extract ZIP using Python zipfile
  ↓
Prepare DataIngestionArtifact
  ↓
Return extracted data path
  ↓
Training Pipeline
```

**Outcome:** The dataset is successfully downloaded from AWS S3, extracted into the local artifacts directory, and made available to the next component through `DataIngestionArtifact`.

This completes the first component of the Human Segmentation Using Augmentation project.