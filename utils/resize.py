
from PIL import Image
import glob
import os
from tqdm import tqdm

keyword = input('작품 : ')
# keyword = 'ponyo'
S = 512
size = (S, S)

# get all the files in a folder, make sure all are image files
files = glob.glob(f'./data/crawled_data/{keyword}/*')

save_path = f'./data/resized_data/{keyword}_{S}'
os.makedirs(save_path, exist_ok=True)

for file in tqdm(files):
    # implement file type checking here if required
    
    # get the basename, e.g. "dragon.jpg" -> ("dragon", ".jpg")
    basename = os.path.splitext(os.path.basename(file))[0]

    with Image.open(file) as img:
        # resize the image to 512 x 512
        img = img.resize(size)
        
        # rotate the image if required
        # img = img.rotate(90)
        
        # save the resized image, modify the resample method if required, modify the output directory as well
        img.save(f"{save_path}/{basename}.png", format="PNG", resample=Image.Resampling.NEAREST)