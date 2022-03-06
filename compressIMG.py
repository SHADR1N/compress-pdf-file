# To run this file type in cmd: python compression.py 

# importing required libraries
import json 
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import piexif



def compressing_img():
    # Opening compression_parameters.json for reading input parameters
    try :
        json_filename = 'compression_parameters.json'
        fh = open(json_filename,"r")
    except :
        print("ERROR: Opening compression_parameters.json file failed. Ensure it is located in the current working directory- {}".format(Path.cwd()))
        exit()

    # Reading input parameters from JSON file 
    try :
        params = json.load(fh)
    except :
        print("ERROR: Unable to parse json in compression_parameters.json. Check for correctness of JSON format")
        exit()
    #print(params)

    # Performing basic error checking on input parameters read from the json file 
    in_folder_path = Path(params["input_folder"])
    if not in_folder_path.is_dir():
        print("ERROR: Input folder {} not found".format(params["input_folder"]))
        exit()

    out_folder_path = Path(params["output_folder"])
    if not out_folder_path.is_dir():
        print("ERROR: Output folder {} not found".format(params["output_folder"]))
        exit()

    quality = int(params["quality"])
    if (quality <= 0 or quality > 95) :
        print("ERROR: quality value must be within (0-95] range")
        exit()

    num_splits = params["num_splits"]
    if  (not isinstance(num_splits, int)) or num_splits < 1 :
        print("ERROR: num_splits {} is not an integer or is less than 1".format(num_splits))
        exit()

    left_crop_px = int(params["left_crop_px"])
    top_crop_px = int(params["top_crop_px"])
    right_crop_px = int(params["right_crop_px"])
    bottom_crop_px = int(params["bottom_crop_px"])
    left_crop_px = max(0, left_crop_px)
    top_crop_px = max(0, top_crop_px)
    right_crop_px = max(0, right_crop_px)
    bottom_crop_px = max(0, bottom_crop_px)

    # Processing input images (with .jpg extension) to generate cropped, split and compressed output images
    in_filepaths = in_folder_path.glob('*.jpg')
    #print("Found {} .jpg input images".format(len(list(in_filepaths))))  

    # Defining exif/metadata for including in the image 
    exif_dict_0th = { 282: (300, 1), 283: (300, 1), 296: 2, 305: b'Enhira Scan Reg Utility'}
    exif_dict = {"0th": exif_dict_0th}
    exif_bytes = piexif.dump(exif_dict)

    for in_filepath in in_filepaths :
        img = Image.open(in_filepath)
        img_w, img_h = img.size 
        img_cropped = img.crop((left_crop_px, top_crop_px, img_w - right_crop_px, img_h - bottom_crop_px))
        img_cropped_w , img_cropped_h = img_cropped.size
        
        # saving cropped image 
        img_name_wo_suffix   = in_filepath.stem # example : test  
        img_name_with_suffix = in_filepath.name # example : test.jpg                    
        out_filepath = out_folder_path / img_name_with_suffix
        img_cropped.save(out_filepath, "JPEG", optimize=True, quality=quality, exif=exif_bytes) 

        # skip processing next image if num_splits is equal to 1 (i.e no splitting required)
        if num_splits == 1 :
            continue

        # splitting and saving compressed copy of the images
        w_split_px = img_cropped_w // num_splits # integer division
        for i in range(num_splits) :
            crop_indices = ( i*w_split_px , 0 , (i+1)*w_split_px , img_cropped_h )
            img_split = img_cropped.crop(crop_indices)
            out_filepath = out_folder_path / "{}_{}.jpg".format(img_name_wo_suffix, i+1)
            img_split.save(out_filepath, "JPEG", optimize=True, quality=quality, exif=exif_bytes) 