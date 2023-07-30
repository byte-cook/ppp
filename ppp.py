#!/usr/bin/env python3

import argparse
import os
import utils
import subprocess
import time

"""
This program allows to rotate photos by Exif Orientation supported by many digital cameras.
The rotation is performed lossless if possible. Not all photos can be rotated lossless.
It depends on photos' block size which must be divisible by 8 or 16 (compare: jpegtran -perfect). 
If a lossless rotation is not possible ImageMagick will be used to perform the rotation. 
This approach guarantees that the "content" of the photo remains the same and no mirroring effect occurs.
See:
http://petapixel.com/2012/08/14/why-you-should-always-rotate-original-jpeg-photos-losslessly/
http://www.imagemagick.org/discourse-server/viewtopic.php?t=16784&p=62157
Alternatives:
jhead -autorot *.jpg
jpegtran -rotate 90 -perfect *.jpg
mogrify -auto-orient /home/path/to/my/picture.jpg
convert -auto-orient original_file.jpg new_file.jpg

Depends on: imagemagick, jpegtran, jpegexiforient (libjpeg-turbo-progs), jhead
History:
2013-11-19	initial version
2014-02-14  add rename option

"""

def _is_jpg_file(file):
    name,  ext = os.path.splitext(file)
    return ext.lower() in (".jpg",  ".jpeg")

def _rotate_file(file, degrees, args):
    """Rotates one single image."""
    if _is_jpg_file(file):
        if degrees == -90: degrees = 270
        if degrees == -180: degrees = 180
        if degrees == -270: degrees = 90
        if degrees in (90,  180,  270):
            # force to use only perfect rotation
            p = utils.execute_command(cmd=["jpegtran", "-copy",  "all",  "-rotate",  str(degrees), "-outfile",  file, "-perfect",  file], ignoreError=True, verbose=args.verbose, simulate=args.simulate)
            if p is None or p.poll() == 0:
                #  lossless rotation succeeded
                return
    # use lossy rotation
    if args.losslessOnly:
        print("{0}: {1}".format("Skipping file", file))
    else:
        if degrees == -180: degrees = 180
        if degrees == 270: degrees = -90
        if degrees in (90,  180,  -90):
            utils.execute_command(cmd=["mogrify", "-rotate", str(degrees), "-quality",  "100", file], verbose=args.verbose, simulate=args.simulate)

def rotate(files,  args):
    """Rotates images."""
    for file in files:
        print("{0}: {1}".format("Rotate " + str(args.degrees),  file))
        _rotate_file(file, args.degrees, args)
    
def auto_rotate(files,  args):
    """Rotates images by Exif orientation."""
    # see: http://jpegclub.org/exif_orientation.html
    for file in files:
        if not _is_jpg_file(file):
            # Auto rotate only work for JPG files
            if args.verbose: print("{0}: {1}".format("Skipping non JPG file", file))
            continue
        #p = utils.execute_command(cmd=["exiftool",  "-n",  "-S",  "-Orientation", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = utils.execute_command(cmd=["jpegexiforient",  "-n", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        orientation = p.communicate()[0]
        if orientation == "":
            if args.verbose: print("{0}: {1}".format("No Exif orientation set", file))
            continue
        degrees = 0
        if orientation == "1": degrees = 0
        elif orientation == "3": degrees = 180
        elif orientation == "6": degrees = 90
        elif orientation == "8": degrees = 270
        if degrees != 0:
            print("{0}: {1}".format("Rotate " + str(degrees),  file))
            _rotate_file(file, degrees, args)
            # remove exif rotation
            utils.execute_command(cmd=["jhead", "-q",  "-norot", file],  verbose=args.verbose, simulate=args.simulate)
#            utils.execute_command(cmd=["jpegexiforient", "-1", file],  verbose=args.verbose, simulate=args.simulate)
        elif args.verbose:
            print("{0}: {1}".format("No rotation necessary",  file))
    pass
    
def web(files,  args):
    """Prepare images for web."""
    for file in files:
        name,  ext = os.path.splitext(file)
        targetFile = name + "-web" + ext
        print("{0}: {1} -> {2}".format("Prepare for web", file, targetFile))
        if not os.path.exists(targetFile) or utils.prompt_yes_no(msg="Overwrite '" + targetFile + "'? (Y/N) ", noPrompt=args.noPrompt, simulate=args.simulate):
            utils.execute_command(cmd=["convert", file, "-strip",  "-quality",  str(args.quality), targetFile], verbose=args.verbose, simulate=args.simulate)

def resize(files,  args):
    """Resizes images."""
    for file in files:
        name,  ext = os.path.splitext(file)
        targetFile = name + "-" + args.size + ext
        print("{0}: {1} -> {2}".format("Resize", file, targetFile))
        if not os.path.exists(targetFile) or utils.prompt_yes_no(msg="Overwrite '" + targetFile + "'? (Y/N) ", noPrompt=args.noPrompt, simulate=args.simulate):
            utils.execute_command(cmd=["convert", file, "-resize", args.size, "-quality", "100", targetFile], verbose=args.verbose, simulate=args.simulate)

def remove_exif(files,  args):
    """Removes all Exif tags."""
    for file in files:
        print("{0}: {1}".format("Remove Exif", file))
        if _is_jpg_file(file):
            utils.execute_command(cmd=["jhead","-q", "-purejpg", file], verbose=args.verbose, simulate=args.simulate)
        else:
            utils.execute_command(cmd=["mogrify", "-strip", file], verbose=args.verbose, simulate=args.simulate)

def rename(files, args):
    """Rename images by Exif creation date."""
#   utils.execute_command(cmd=["jhead","-q", "-n%Y-%m-%d#%02i", file], verbose=args.verbose, simulate=args.simulate)
#   exiftool -P -'Filename<DateTimeOriginal' -d %Y-%m-%d_Handy.%%e ORDNERNAME/* 
    currentTime = None
    currentIndex = None
    # sort files by date
    files = sorted(files, key=lambda file: os.path.getmtime(file))
    for file in files:
        if _is_jpg_file(file):
            # set Exif creation date as file creation date
            utils.execute_command(cmd=["jhead","-q", "-ft", file], stdout=subprocess.PIPE, verbose=args.verbose, simulate=args.simulate)

        # get file creation time
        fileTime = os.path.getmtime(file)
        fileTime = time.strftime("%Y-%m-%d", time.gmtime(fileTime))
        # get current index
        if currentTime is None:
            currentTime = fileTime
            currentIndex = 1
        else:
            if currentTime == fileTime:
                currentIndex += 1
            else:
                currentTime = fileTime
                currentIndex = 1
        # rename file
        dir = os.path.dirname(file)
        name,  ext = os.path.splitext(file)
        targetFile = "{0}/{1}#{2:0>3}{3}".format(dir, fileTime, str(currentIndex), ext)
        print("{0}: {1} -> {2}".format("Rename", file, targetFile))
        if file == targetFile:
            print("Nothing to do")
        elif not os.path.exists(targetFile) or utils.prompt_yes_no(msg="Overwrite '" + targetFile + "'? (Y/N) ", noPrompt=args.noPrompt, simulate=args.simulate):
            utils.execute_command(cmd=["mv", file, targetFile], verbose=args.verbose, simulate=args.simulate)


CMD_ROTATE = "rotate"
CMD_AUTO_ROTATE = "auto-rotate"
CMD_WEB = "web"
CMD_RESIZE = "resize"
CMD_REMOVE_EXIF = "remove-exif"
CMD_RENAME = "rename"

if __name__ == "__main__":
    try:
        # parse arguments
        parser = argparse.ArgumentParser(description="Prepare Pictures and Photos", formatter_class=argparse.RawTextHelpFormatter)
        subparsers = parser.add_subparsers(title="Commands", dest="command", help="available commands",  description="Supported commands to prepare photos")
        # rotate
        rotateParser = subparsers.add_parser(CMD_ROTATE, help="rotates an image",  description="Rotates images lossless if possible, otherwise lossy rotation will be performed.")
        rotateParser.add_argument("-n", "--dry-run", action="store_true", dest="simulate", help="simulate installation process")
        rotateParser.add_argument("-v", "--verbose", action="store_true", help="print verbose output")
        rotateParser.add_argument("-l", "--lossless-only", action="store_true", dest="losslessOnly",  help="only perform lossless rotation")
        rotateParser.add_argument("-r", "--recursive", action="store_true", help="perform command recursively")
        rotateParser.add_argument("degrees",  type=int, choices=[90,  180,  270], help="degrees to rotate clockwise")
        rotateParser.add_argument("file", nargs="+", help="file or folder")
        # auto-rotate
        autoRotateParser = subparsers.add_parser(CMD_AUTO_ROTATE, help="rotates an image by Exif orientation",  description="Automatically rotates images by Exif rotation. Prefers a lossless rotation if possible, otherwise lossy rotation will be performed.")
        autoRotateParser.add_argument("-n", "--dry-run", action="store_true", dest="simulate", help="simulate installation process")
        autoRotateParser.add_argument("-v", "--verbose", action="store_true", help="print verbose output")
        autoRotateParser.add_argument("-l", "--lossless-only", action="store_true", dest="losslessOnly",  help="only perform lossless rotation")
        autoRotateParser.add_argument("-r", "--recursive", action="store_true", help="perform command recursively")
        autoRotateParser.add_argument("file", nargs="+", help="file or folder")
        # web
        webParser = subparsers.add_parser(CMD_WEB, help="prepares images for the WWW",  description="Prepares images for the WWW by reducing quality. All Exif tags will be removed.")
        webParser.add_argument("-n", "--dry-run", action="store_true", dest="simulate", help="simulate installation process")
        webParser.add_argument("-v", "--verbose", action="store_true", help="print verbose output")
        webParser.add_argument("-y", "--yes",  action="store_true",  dest="noPrompt",  help="answer all questions with yes")
        webParser.add_argument("-r", "--recursive", action="store_true", help="perform command recursively")
        webParser.add_argument("--quality", type=int,  help="compression level (default 50)",  default=50)
        webParser.add_argument("file", nargs="+", help="file or folder")
        # resize
        resizeParser = subparsers.add_parser(CMD_RESIZE, help="resizes images",  description="Resizes images.")
        resizeParser.add_argument("-n", "--dry-run", action="store_true", dest="simulate", help="simulate installation process")
        resizeParser.add_argument("-v", "--verbose", action="store_true", help="print verbose output")
        resizeParser.add_argument("-y", "--yes",  action="store_true",  dest="noPrompt",  help="answer all questions with yes")
        resizeParser.add_argument("-r", "--recursive", action="store_true", help="perform command recursively")
        resizeParser.add_argument("size", help="the new size in the format WIDTHxHEIGHT, e.g. 300, x200, 300x200, 300x200!, use ! to ignore original aspect ratio (see ImageMagick's geometry for more details)")
        resizeParser.add_argument("file", nargs="+", help="file or folder")
        # resize
        removeExifParser = subparsers.add_parser(CMD_REMOVE_EXIF, help="removes Exif tags",  description="Removes all Exif tags.")
        removeExifParser.add_argument("-n", "--dry-run", action="store_true", dest="simulate", help="simulate installation process")
        removeExifParser.add_argument("-v", "--verbose", action="store_true", help="print verbose output")
        removeExifParser.add_argument("-r", "--recursive", action="store_true", help="perform command recursively")
        removeExifParser.add_argument("file", nargs="+", help="file or folder")
        # rename
        renameParser = subparsers.add_parser(CMD_RENAME, help="rename images by Exif creation date",  description="Renames images by Exif creation date. File creation date will be used if Exif tag is missing.")
        renameParser.add_argument("-n", "--dry-run", action="store_true", dest="simulate", help="simulate installation process")
        renameParser.add_argument("-v", "--verbose", action="store_true", help="print verbose output")
        renameParser.add_argument("-y", "--yes",  action="store_true",  dest="noPrompt",  help="answer all questions with yes")
        renameParser.add_argument("-r", "--recursive", action="store_true", help="perform command recursively")
        renameParser.add_argument("file", nargs="+", help="file or folder")
        
        args = parser.parse_args()
        
        dirs,  files = utils.get_files(args.file, recursive=args.recursive)
#        files = [f for f in files if os.path.splitext(f)[1] == ".jpg"]
        files = sorted(files)
        if args.command in (CMD_ROTATE):
            rotate(files,  args)
        elif args.command in (CMD_AUTO_ROTATE):
            auto_rotate(files,  args)
        elif args.command in (CMD_WEB):
            web(files,  args)
        elif args.command in (CMD_RESIZE):
            resize(files,  args)
        elif args.command in (CMD_REMOVE_EXIF):
            remove_exif(files,  args)
        elif args.command in (CMD_RENAME):
            rename(files,  args)

    except Exception as e:
        print(e)
#        raise e
        exit(1)

