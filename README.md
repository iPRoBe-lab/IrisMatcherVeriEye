# IrisMatcherVeriEye
Iris Matcher (Python Version on Linux) based on the VeriEye SDK by  Neurotechnology


# System Requirements
- Ubuntu Linux OS (Tested on v22.04)
- Anaconda Python Environment Manager

# License Activation (for Python SDK)
1. To run VeriEye in Python, you must run the license server. Otherwise, most of the features are unusable.
2. Get your IrisClient, IrisExtractor, and IrisMatcher internet license files obtained from Neurotechnology and run the license server.
3. To activate the licenses, update all the license paths in the `Neurotec_Biometric_13_1_SDK/Bin/Linux_x86_64/Activation/pgd.conf` file. Do not include licenses for other platforms here; they will fail the activation process. Use the absolute path for the license file here.
4. To use the fully activated VeriEye, modify the `pgd.conf` file as follows
  - `mode = single`
  - `trial = false`
  - update the paths of the LicenseFile. If you have multiple licenses, add multiple lines in the `pgd.conf` file accordingly.
4. Run the command `sudo run_pgd.sh start` to start the license server. You can use commands like `stop`, `restart` to restart the license server. If you have copied the license files from an active machine for your project, ensure you have stopped the license server in the previous machine. Otherwise, your's will not be activated. For swapping machines for the licenses, there is a 30-minute delay. If you are installing licenses to a new machine, wait at least 30 minutes before running the activation server.


 # Create Virtual Environment
 1. Create a virtual environment in Anaconda and activate it using the following.
```bash
  conda create --name VeriEye python=3.10
  conda activate VeriEye
```
2. Download the VeriEye-SDK-Python from the [Official VeriEye Download Page](https://download.neurotechnology.com/Neurotec_Biometric_13_1_Python_Linux_2024-02-13.zip)
 3. Unzip the `Neurotec_Biometric_13_1_Python_Linux_2024-02-13.zip` folder and install the precompiled wheel file `pynsdk-13.1.0-py3-none-any.whl` using the command
  ```bash
    pip install pynsdk-13.1.0-py3-none-any.whl
```
in your VeriEye environment.
 4. assuming the license server is running, you should be all set.
 

# How to Use
- **Step 1:** Create a CSV file with three columns. The first two are for the image pairs, and the third one is whether a match or non-match by {0,1}. with column names `iris1`, `iris2`, and `label.`
- **Step 2:** Run the script with the following command.
```bash
python iris_matcher.py --input_file iris_matching_task_dataframe.csv \
    --dataset_dir sample_iris_database \
    --output_file iris_matching_task_output.csv
```


- **Note:** The script is written in such a way that, for each iris, a subject's template is created, and then it is stored. If that subject's template comes in a new test pair, the old one is retrieved. Also, all the extracted templates are stored by default.
- 

