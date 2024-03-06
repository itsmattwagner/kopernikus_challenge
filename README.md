
# Kopernikus Coding Task

Solution for the interview challenge by Kopernikus to remove duplicate images from a dataset. 

# Task

- find and remove all similar-looking images in a folder
- The input of the program should be a path to a folder with images
- the result program should remove all non-essential images for data collection 

# Questions
* What did you learn after looking on our dataset?
  - There are four different cameras.
  - There are eight different image dimensions.
  - There are two date formats UNIX timestamp and Year_Month_Day__Hours_Minutes_Seconds, every single digit leads with a 0
  - All images are of filetype PNG
  - There are 1080 images in total
  - One images dimensions are too small -> probably an error and has to be removed
  - One image cannot be read by OpenCV, I expect a fault in the encoding.

* How does you program work?
      
      1. The program reads in all the filenames of the images
      2. Images are grouped by camera id
      3. Images are sorted ascending by their timestamp (regardless if UNIX or %Y_%m_%d__%H_%M_%S)
      4. For each camera id images are preprocessed and then compared as pairs.
      5. Images are either deleted or copied in a seperat output folder.

- What values did you decide to use for input parameters and how did you find these values?
  - I decided on (5,11,21) as radii for the gaussian blur list. I tried to smooth out small details and inconsistencies with the first radius, then slightly larger details with the second and with the last I tried to cover larger details.
  - As the minimum contour area I chose a value of 500. I ran the program with a few different values and looked at the images that were left untouched. For a value like 1000 people were often disregarded.   
  - I set the score threshold low to 100, so that similar images with a low score are sorted out.
- What you would suggest to implement to improve data collection of unique cases in future?
  - a higher refresh rate of images per second
  - an advanced masking solution
  - a lightweight machine learning component
- Any other comments about your solution?
  - The file c21_2021_03_27__12_53_37.png has been removed from the dataset for its small dimension size.
  - OpenCV was not able to read c21_2021_03_27__10_36_36.png, it has been removed as well.



## Run Locally

### Go to the project directory

```bash
  cd kopernikus-challenge
```

### Install dependencies

```bash
  conda env create -f environment.yml
```

If you run into any problems installing the envs, the following are the libraries I installed

```bash
conda create --name <env_name> python=3.8
conda install anaconda::pytest
conda install anaconda::ipykernel
conda install anaconda::pandas
conda install -c conda-forge opencv

pip install matplotlib
pip install imutils
pip install pytest-mock
```

#### Run the python file
```bash
  python -m src.remove_duplicates --data_path "./data/dataset/" --gaussian_blur_radius_list 5 11 21 --min_contour_area 500 --score_threshold 100
```

### Input parameter
There are seven input parameter options.

The only one required is the path to your dataset.

- -v, --verbose | Increase the output verbosity for logging
- --data_path | The absolute path to the dataset or relative to the root dir.
- --gaussian_blur_radius_list | A list with radii for gaussian blur to be applied onto the images
- --min_contour_area | The min area for contours to change to be considered dissimilar images
- --score_threshold | The threshold for the score for two images to be considered similar
- --output_path | The path to the folder to save the unique images, if --delete is not set
- --delete | Determines if the images that are not unique should be deleted. If set, the images will be deleted. If not set, the images will be copied to the output_path.

