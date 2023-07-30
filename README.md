# PPP.py (Prepare pictures and photos)

PPP.py allows to batch processing images:
- Automatically rotate images to the correct orientation with less loss
- Rotate images by given degree with less loss
- Optimize images for the web

PPP.py attaches great importance to performing the rotation with as little loss as possible. To achieve this, PPP.py relies on external programs that must be installed separately.

Supported file formats are: JPG

## Install

1. Install external applications:
```bash
sudo apt install imagemagick jpegtran libjpeg-turbo-progs jhead
```

2. Install Python3 and pip as follows in Ubuntu/Debian Linux:
```bash
sudo apt install python3.6 python3-pip
```

??? utils.py

## Example usage

Automatically rotate all images in the current directory:
```
ppp.py auto-rotate .
```

Rotate an images by 90 degrees clockwise:
```
ppp.py rotate 90 <photo.jpg>
```

Optimize a photo for the web:
```
ppp.py web <photo.jpg>
```
The new file is created in the same directory with postfix "-web", e.g. photo.jpg -> photo-web.jpg.


