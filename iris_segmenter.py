"""
##############################################################################
# Title: Iris Matcher in Batch Mode based on VeriEye SDK
# Author:   Redwan Sony, 
#           PhD Student | iPRoBe Lab
#           Michigan State University
#           GitHub: www.github.com/redwankarimsony
#           Email: sonymd@msu.edu
# Version: 1.0
# Date: May 16, 2024
#
# Description: This script takes a csv file with the pair of iris images in each line and performs the iris matching and saves the match scores in a csv file.
#
# Usage: follow the README.md file
#
# Dependencies: opencv, pynsdk, pandas, numpy, tqdm
#
# Notes: pynsdk is a python wrapper for the Neurotechnology VeriEye SDK and owned by Neurotechnology.
#
# Please give credit to the author if you use or modify this script.
##############################################################################
"""






import argparse
import os.path as osp
import os
from glob import glob
import pandas as pd
from pynsdk.media import NImage, NPixelFormat
from pynsdk.core import NBuffer
from pynsdk.biometrics import NBiometricEngine, NBiometricOperations, NBiometricStatus, NIris, NSubject, NEImageType, BiometricAttributeId
from pynsdk.licensing import NLicense, NLicenseManager
import cv2
from tqdm import tqdm


def get_licences(licenses, is_trial_mode=False):

    NLicenseManager.set_trial_mode(is_trial_mode)
    print(f"Trial mode: {is_trial_mode}")

    failed = False
    for x in licenses:
        if not NLicense.obtain("/local", 5000, x):
            print(f"Failed to obtain license: {x}")
            failed = True
        else:
            print(f"License obtained successfully: {x}")
    return failed


def create_subject_with_iris(file_path):
    if osp.exists(file_path):
        nimage = NImage(file_path)
        iris = NIris()
        iris.image = nimage
        subject = NSubject()
        subject.id = file_path.split("/")[-1].split(".")[0]
        subject.irises.add(iris)
        return subject
    else:
        print(f"File does not exist: {file_path}")
        return None


def get_all_iris_images(input_file, dataset_dir):
    if not osp.exists(input_file):
        print(f"Input file does not exist: {input_file}")
        return []
    df = pd.read_csv(input_file)
    df.columns = ['iris1', 'iris2', 'label']

    iris1 = df['iris1'].tolist()
    iris2 = df['iris2'].tolist()

    all_iris_images = sorted(list(set(iris1 + iris2)))
    all_iris_paths = [osp.join(dataset_dir, x) for x in all_iris_images]

    return all_iris_paths, df


def load_templates(file_path):
    subs = {}
    if osp.exists(file_path):
        temps = glob(os.path.join(file_path, "*.dat"))
        for temp in tqdm(temps, total=len(temps)):
            # Get the subject ID
            subject_id = temp.split("/")[-1].split(".")[0]
            # Create the subject
            subject = NSubject()
            subject.id = subject_id
            # Load the template
            subject.template_buffer = NBuffer.from_file(temp)
            subs[subject_id] = subject
        print(f"Templates loaded: {len(subs)}")
        return subs
    else:
        print(f"File does not exist: {file_path}")
    return subs


def main(args):
    # Get the licenses
    license_status = get_licences(args.licences, is_trial_mode=True)
    # if not license_status:
    #     return

    # Creat and configure the biometric engine
    engine = NBiometricEngine()
    engine.irises_liveness_confidence_threshold = 0
    engine.matching_threshold = args.matching_threshold

    # Set matching speed
    # engine.irises_matching_speed = args.matching_speed

    # Get all the iris images
    all_iris_paths, df = get_all_iris_images(args.input_file, args.dataset_dir)

    # List all the preprocessed iris images
    all_subjects = []
    all_subjects = os.listdir(osp.join(args.dataset_dir, "templates"))

    sub = create_subject_with_iris(all_iris_paths[0])

    # Load the already crated templates
    all_subjects = load_templates(osp.join(args.dataset_dir, "templates"))

    for iris_path in tqdm(all_iris_paths):
        # Create the ID of the file
        file_id = iris_path.split("/")[-1].split(".")[0]
        if file_id in all_subjects.keys():
            continue
        else:
            subject = create_subject_with_iris(iris_path)
            if subject:
                status = engine.perform_operation(
                    subject, NBiometricOperations.CREATE_TEMPLATE)
                if status == NBiometricStatus.OK:
                    all_subjects[subject.id] = subject
                    # Save the template
                    subject.template_buffer.to_file(
                        osp.join(args.dataset_dir, "templates", f"{subject.id}.dat"))
                    
                else:
                    print(f"Failed to create template for {subject.id} from {iris_path}")
                    
    # Perform the matching
    results, all_keys = [], all_subjects.keys()
    for i in range(0, len(df)):
        iris1 = df.iloc[i]['iris1']
        iris2 = df.iloc[i]['iris2']
        label = df.iloc[i]['label']
        
        iris1_id = iris1.split("/")[-1].split(".")[0]
        iris2_id = iris2.split("/")[-1].split(".")[0]
        if iris1_id in all_keys and iris2_id in all_keys:
            probe_subject = all_subjects[iris1_id]
            gallery_subject = all_subjects[iris2_id]
            verification_result = engine.verify_offline(probe_subject, gallery_subject)
            matching_results = probe_subject.get_matching_results()
            score = matching_results[0].get_score()
            results.append(['Okay', iris1, iris2, label, score])
        else:
            print(f"Template not found for {iris1} or {iris2}")
            results.append(['Error', iris1, iris2, label, 0])
    results_df = pd.DataFrame(results, columns=['status', 'iris1', 'iris2', 'label', 'score'])
    
    # Save the results
    results_df.to_csv(args.output_file, index=False)
    print(f"Results saved to {args.output_file}")
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Iris Matching in Batch Mode')
    # parser.add_argument('file_name', help='File name')
    parser.add_argument("--input_file",
                        help="Input file with csv format of pair of iris Images",
                        default="casia_verification_input.csv")
    parser.add_argument("--dataset_dir", help="Dataset directory",
                        default="/home/iprobe/Desktop/CASIA_IRIS_V3")

    parser.add_argument("--licences", nargs="+",
                        help="Licences", default=["A"])
    parser.add_argument("--matching_threshold", type=int,
                        help="Matching threshold", default=48)
    parser.add_argument("--matching_speed", type=int, default=1)
    parser.add_argument("--output_file", help="Output file",
                        default="casia_verification_output.csv")
    
    args = parser.parse_args()

    args.licences = (["IrisClient", "IrisExtractor", "IrisMatcher"])

    main(args)
