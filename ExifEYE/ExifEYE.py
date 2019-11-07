from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
from tqdm import tqdm


def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def parse_exif(exif):
    exifData = {}
    try:
        if exif:
            for (tag, value) in tqdm(exif.items()):
                if value:
                    decoded_tag = TAGS.get(tag, tag)
                    if decoded_tag != 'GPSInfo':
                        exifData[decoded_tag] = value
                    else:
                        for (key, val) in GPSTAGS.items():
                            if key in exif[tag]:
                                exifData[val] = exif[tag][key]
                                # Note: GPS Latitude and Longitude are represented in true rational64u format
        return exifData
    except:
        print('Failed')


def convert_dms_to_dd(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 10)


def parse_coordinates(exifData):
    dms_lat = exifData['GPSLatitude']
    dms_lat_r = exifData['GPSLatitudeRef']
    dms_long = exifData['GPSLongitude']
    dms_long_r = exifData['GPSLongitudeRef']

    lat = convert_dms_to_dd(exifData['GPSLatitude'], exifData['GPSLatitudeRef'])

    long = convert_dms_to_dd(exifData['GPSLongitude'], exifData['GPSLongitudeRef'])
    print("[#] GPS Coordinates converted from DMS -> DD")
    print("\t[+] Latitude  | DMS: {} {} => DD: {}".format(dms_lat, dms_lat_r, lat))
    print("\t[+] Longitude | DMS: {} {} => DD: {}".format(dms_long, dms_long_r, long))

    exifData['GPSLatitude'] = lat
    exifData['GPSLongitude'] = long

    return exifData


def print_exif(exifData):
    print('-' * 99)
    for key in exifData:
        print('-' * 85)
        if 'GPS' in key:
            print("[+] {:<28} | {}".format(key, exifData[key]))
        else:
            print("{:<28} | {}".format(key, exifData[key]))


exif = get_exif('geo_jpg\DSCN0012.jpg')
exif_data = parse_exif(exif)
gps_exif = parse_coordinates(exif_data)
print_exif(exif_data)
