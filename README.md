# PPP.py (Prepare pictures and photos)

PPP.py allows to batch processing images:
- Automatically rotate images to the correct orientation with less loss
- Rotate images by given degree with less loss
- Optimize images for the web

PPP.py attaches great importance to performing the rotation with as little loss as possible. To achieve this, PPP.py relies on external programs that must be installed separately.

Supported file formats are: JPEG, JPG

## Install

1. Install Python3 as follows in Ubuntu/Debian Linux:
```
sudo apt install python3.6
```

2. Install external applications:
```
sudo apt install imagemagick jpegtran libjpeg-turbo-progs jhead
```

3. Downlaod PPP.py and set execute permissions:
```
curl -LJO https://github.com/byte-cook/ppp/blob/main/ppp.py
curl -LJO https://github.com/byte-cook/ppp/blob/main/osutil.py
chmod +x ppp.py
```

## Example usage

Automatically rotate all images in the current directory:
```
ppp.py auto-rotate .
```

Rotate an image by 90 degrees clockwise:
```
ppp.py rotate 90 <photo.jpg>
```

Optimize a photo for the web:
```
ppp.py web <photo.jpg>
```
The new file is created in the same directory with postfix "-web", e.g. photo.jpg -> photo-web.jpg.


