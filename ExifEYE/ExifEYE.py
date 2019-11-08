from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
from tqdm import tqdm
import os
import reverse_geocoder as rg
import pprint


def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def parse_exif(exif):
    exifData = {}
    if exif:
        for (tag, value) in exif.items():
            if value:
                decoded_tag = TAGS.get(tag, tag)
                if decoded_tag != 'GPSInfo':
                    exifData[decoded_tag] = value
                else:
                    for (key, val) in GPSTAGS.items():
                        if key in exif[tag]:
                            exifData[val] = exif[tag][key]
                            # Note: GPS Latitude and Longitude are represented in true rational64u format
    if 'GPSLatitude' in exifData.keys() and 'GPSLongitude' in exifData.keys():
        parse_coordinates(exifData)
        parse_location(exifData)
    return exifData

def parse_location(exifData):
    # Reverse Geocoding
    location = (str(exifData['GPSLatitude']), str(exifData['GPSLongitude']))
    # rg.search(location)
    location_info = rg.search(location, mode=1)
    exifData['rg_ISO3166-1_alpha2(country_code)'] = location_info[0]['cc']
    exifData['rg_Latitude'] = location_info[0]['lat']
    exifData['rg_Longitude'] = location_info[0]['lon']
    exifData['rg_Location_Name'] = location_info[0]['name']
    exifData['rg_Administrative_Region_1'] = location_info[0]['admin1']
    exifData['rg_Administrative_Region_2'] = location_info[0]['admin2']
    return exifData


def convert_dms_to_dd(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 15)


def parse_coordinates(exifData):
    try:
        dms_lat = exifData['GPSLatitude']
        dms_lat_r = exifData['GPSLatitudeRef']
        dms_long = exifData['GPSLongitude']
        dms_long_r = exifData['GPSLongitudeRef']

        lat = convert_dms_to_dd(exifData['GPSLatitude'], exifData['GPSLatitudeRef'])

        long = convert_dms_to_dd(exifData['GPSLongitude'], exifData['GPSLongitudeRef'])
        '''
        
        print("[#] GPS Coordinates converted from DMS -> DD")
        print("\t[+] Latitude  | DMS: {:<=18} {:<=18} => DD: {}".format(dms_lat, dms_lat_r, lat))
        print("\t[+] Longitude | DMS: {:<=18} {:<=18} => DD: {}".format(dms_long, dms_long_r, long))
        '''
        exifData['GPSLatitude'] = lat
        exifData['GPSLongitude'] = long
        exifData['GPSCoordinatesDD'] = (lat, long)
        return exifData
    except Exception as e:
        print("[-] Error = " + str(e))


def print_exif(exifData):
    try:
        print('-' * 99)
        for key in exifData:
            print("\t[+] {:<28} | {}".format(key, exifData[key]))
        print('-' * 99 + '\n')
    except Exception as e:
        print("[-] Error = " + str(e))

def parse_indv_exif(exif_data,jpg):
    summary = ''
    if 'GPSCoordinatesDD' in exif_data.keys():
        header = "[+] {:<25} | Coordinates(DD) | {:<18}, {:<18}".format(jpg, exif_data['GPSLatitude'], exif_data['GPSLongitude'])
        location = [
            exif_data['rg_ISO3166-1_alpha2(country_code)'],
            exif_data['rg_Latitude'],
            exif_data['rg_Longitude'],
            exif_data['rg_Location_Name'],
            exif_data['rg_Administrative_Region_1'],
            exif_data['rg_Administrative_Region_2']]
        location_string = ' '+str(location[3])+', '+str(location[4])+', '+str(location[5])+', '+str(location[0])
        return header + ' | LOCATION : ' + str(location_string) + '\n' + '='*155
    else:
        summary = "[-] {:<25} \t\t\t\t\t\t\t\t\t\t!!!Does not contain GPSCoordinates :( !!!".format(jpg) + '\n' + '='*155
    return summary


def iterate_folder(folder_name):
    directory = os.fsencode(folder_name)
    img_list = []
    parse_list = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            img_list.append(filename)
    print(img_list)

    for jpg in tqdm(img_list):
        print("[*] Starting ExifEYE on {}\{}".format(folder_name, jpg))
        exif = get_exif(folder_name + '\\' + jpg)
        exif_data = parse_exif(exif)
        indv_sum = parse_indv_exif(exif_data, jpg)
        if '[-]' in indv_sum:
            parse_list.insert(0,indv_sum)
        elif '[+]' in indv_sum:
            parse_list.append(indv_sum)
    print('[-] End of Iteration...\n')
    print('#'*160)
    print('\t\t\t\t\t\t ----------------------------')
    print('\t\t\t\t\t\t| ExifEYE GeoLocator Summary |')
    print('\t\t\t\t\t\t ----------------------------')
    print('='*155)
    print(*parse_list, sep = "\n")
    return parse_list




'''
exif = get_exif('images\IMG_1003.jpg')
exif_data = parse_exif(exif)
#gps_exif = parse_coordinates(exif_data)
#print_exif(exif_data)
print_exif(exif_data)

'''

iterate_folder('images')
