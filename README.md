# raw2reflectance.py
* Convert *"Raw .TIF Images"* to *"Reflectance .TIF Images (scale:0-65536)"*
```
python raw2reflectance.py {raw_images_path} {reflectance_images_path}
```

* Example:
```
python ~/python/p4m/Raw2Reflectance/raw2reflectance.py ~/gdsl-depot/Cruz_ACRE/2020/raw_data/200902_p4m_acre/101MEDIA ~/reflectance_path
```
This command will create a path *"\~\/reflectance_path"* with *"reflectance images(.TIF)"* by converting raw images(.TIF) in *"\~\/gdsl-depot/Cruz_ACRE/2020/raw_data/200902_p4m_acre/101MEDIA"*


# Setup
1. ssh login
2. module load anaconda/5.3.1-py37
3. source .bashrc
4. conda create -n P4M
5. conda activate P4M
6. conda install pip
7. conda install -c conda-forge exiftool tifffile matplotlib pysolar
8. pip install PyExifTool opencv-python
9. conda install -c anaconda pytz scikit-image


## Comment
please contact Hunsoo if you have any question </br>
please refer https://github.com/micasense/imageprocessing for MicaSense

Adding a new line.
