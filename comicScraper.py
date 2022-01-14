#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import os.path
import requests
import time
import random
import sys
import argparse
import platform
import shutil
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import re

# selenium TODO's
# TODO: Download uBlock Origin crx and use as the adblocker extension instead of Adblock Plus
# TODO: Add Firefox support (if we care)

# general TODO's:
# TODO: give the user an option to set a custom directory to download images and/or final CBZ to
# TODO: add the option to download a range of issues
# TODO: add a subdirectory for each issue so we don't clutter up the script directory

# geneneral TODO's pulled from aus's script:
# TODO: ensure all image types are grabbed (jpg, png, gif, etc.) from the blogspot links (needed?)
# TODO: add a function to just download images, and one to just convert named images to CBZ's
# TODO: add an option to just pass the search term and download all the series in the results (hit the search API)
# TODO: add logging over print statements and a -v / --verbose flag

prefix = "https://readcomiconline.li"
readType = "&readType=1" # Suffix for issue URLs that makes it show all images on one page
script_dir = os.getcwd() # lets the user add the script to their PATH var and have it populate in current working directory
COUNTER = 0 # Image Numbers

# Unsure if these headers have any effect that we care about
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

# Not used with Selenium
def checkForCaptcha(line):
    if "AreYouHuman" in line:
        print("Captcha Detected")
        return True
    return False

# Not used with Selenium
def solveCaptcha(url, tries=0):
    driverChoice = input("Do you prefer firefox 'f' or chrome 'c'? ") or "c"
    if tries > 2:
        print("Too many tries, selecting chrome")
        driverChoice = "c"
    if driverChoice == "f":
        print("Downloading geckodriver so that you can solve the captcha \n")
        s=Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
    elif driverChoice == "c":
        print("Downloading chromedriver so that you can solve the captcha \n")
        s=Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=s, options=options)
    else:
        print("You didn't select a valid option. Please enter c or f")
        return solveCaptcha(url, tries+1)

    driver.maximize_window()
    driver.get(url)
    input("Press Enter to continue once you have solved the captcha and closed the browser window")

# function to prepad zeros to issue numbers and move all CBZs in the current directory to title/CBZ_Files folder
def fileCBZrenamer(issuePath, currentPath=""):
    # get the current location of the cbz files
    if not currentPath:
        currentPath = get_script_path()
    if platform.system() == "Windows":
        folderLocation = issuePath + "\\CBZ_Files"
    else:
        folderLocation = issuePath + "/CBZ_Files"
    if not os.path.isdir(folderLocation):
        os.mkdir(folderLocation)
    # filter out all the comics with a number and .cbz at the end
    numberedComics = [comic for comic in os.listdir(currentPath) if comic.endswith(".cbz") and re.search(".*[0-9].cbz", comic)]
    if not numberedComics:
        return
    # pad the comic with the correct number
    for comicFile in numberedComics:
        # strip the .cbz and number
        strippedCBZ = str(comicFile).split(".")[0]
        strippedNumber = strippedCBZ.split("-")[-1]
        splitComic = strippedCBZ.split("-")[0:-1]
        # pad the number
        prepadLength = len(str(len(numberedComics)))
        paddedNumber = strippedNumber.rjust(prepadLength, "0")
        # rebuild the comic name with the padded number
        comic = '-'.join(map(str, splitComic)) + "-" + paddedNumber + ".cbz"
        # rename and move the numbered comics to the CBZ_Files folder
        if platform.system() == "Windows":
            shutil.move(comicFile, folderLocation + "\\" + comic)
        else:
            shutil.move(comicFile, folderLocation + "/" + comic)
    # move the remaning cbz files
    leftOverComics = [comic for comic in os.listdir(currentPath) if comic.endswith(".cbz")]
    for leftOver in leftOverComics:
        if platform.system() == "Windows":
            shutil.move(leftOver, folderLocation + "\\" + leftOver)
        else:
            shutil.move(leftOver, folderLocation + "/" + leftOver)
    print(f"Comics have been moved to {folderLocation}")


def folderCBZPacker(comicTitle, issuename="Complete"):
    # NOTE: this wont work for mixed media as it zips all images AND subfolders
    if issuename == "Complete":
        shutil.make_archive(comicTitle + "-" + issuename, 'zip', comicTitle)
    else:
        if platform.system() == "Windows":
            shutil.make_archive(comicTitle + issuename, 'zip', comicTitle + "\\" + issuename)
        else:
            shutil.make_archive(comicTitle + "-" + issuename, 'zip', comicTitle + "/" + issuename)
    if issuename:
        if platform.system() == "Windows":
            os.rename(comicTitle + issuename + ".zip", comicTitle + issuename + ".cbz")
        else:
            os.rename(comicTitle + "-" + issuename + ".zip", comicTitle + "-" + issuename + ".cbz")
    else:
        # removes trailing "-" in the filename
        os.rename(comicTitle + "-" + issuename + ".zip", comicTitle + ".cbz")

# checks if the number of issues matches up with the number of downloads
def compareCBZtoIssueList(issues, path="."):
    # grab all the cbz files in the current directory
    allCBZFiles = [comic.split(".")[0] for comic in os.listdir(path) if comic.endswith(".cbz")]
    named = []
    for issue in issues:
        if platform.system() == "Windows":
            named.append(getIssueName(issue, "\\Comic\\", "-"))
        else:
            named.append(getIssueName(issue, "/Comic/", "-"))
    missing = [comic for comic in named if comic not in allCBZFiles]
    if len(missing) > 0:
        print(f"\nThere was an error downloading {missing}")
        for missed in missing:
            named.remove(missed)
    return named

def getIssueName(issueLink, startURL, replaceChar=""):
    # first get the issue name/number.
    # remove the start url, trim the leading /, and everything after the ?
    issueName = issueLink.replace(startURL, "", 1)[0:].split("?",1)[0]
    if platform.system() == "Windows":
        issueName = issueName.replace("\\", replaceChar)
    else:
        issueName = issueName.replace("/", replaceChar)
    return issueName

def getComicTitle(url, issue=False):
    startURL = prefix + "/Comic/"
    title = url.replace(startURL, "", 1)

    if issue:
        # Add the issue number to the title
        titlePieces =   title.split("/")
        issueTitle = titlePieces[1].split("?")[0]
        title = titlePieces[0] + "-" + issueTitle

    return title

def getLinksFromStartPage(url):
    req = requests.get(url, headers)
    soup = bs(req.content, 'html.parser')

    links = soup.find_all('a')
    linkArrayRaw = []
    for link in links:
        if link.get('href') != None:
            linkArrayRaw.append(link.get('href'))

    linkArray = []
    for link in linkArrayRaw:
        if link.startswith('/Comic/'):
            linkArray.append(link)

    linkArray.reverse()

    return linkArray

def scrapeImageLinksFromIssue(url, lowres):
    req = requests.get(url, headers)
    soup = bs(req.content, 'html.parser')
    soup = soup.prettify()
    lines = soup.split("\n")
    imageLinks = []

    for line in lines:
        if "https://2.bp.blogspot.com" in line:
            imageUrl = extractImageUrlFromText(line, lowres)
            imageLinks.append(imageUrl)

        if checkForCaptcha(line):
            solveCaptcha(url)
            return scrapeImageLinksFromIssue(url, lowres)

    return imageLinks

def extractImageUrlFromText(text, lowres):
    urlEnd = text.find("s1600")
    urlStart = text.find("https")
    output = text[urlStart:urlEnd+5]
    print("extractImageUrlFromText output ", output)
    if not lowres:
        output = output.replace("s1600","s0")
        print("extractImageUrlFromText output ", output)
    return output

def displayDownloadInfo(path):
    list_of_files = list(filter( lambda x: os.path.isfile(os.path.join(path, x)), os.listdir(path)))
    files_with_size = [ (file_name, os.stat(os.path.join(path, file_name)).st_size) for file_name in list_of_files  ]

    print(f"Downloaded {len(list_of_files)} files to {path}")
    smallFiles = []
    totalSize = 0
    for file_name, size in files_with_size:
        totalSize += size
        if size < 10000:
            smallFiles.append(file_name)

    sizeDisplay = round((totalSize/1000000),3)

    if sizeDisplay > 1:
        sizeType = "mb"
    else:
        sizeType = "kb"
        sizeDisplay = round((totalSize/1000),3)

    print(f"Total size of files: {sizeDisplay}{sizeType}")

    sizeDisplay = round(((totalSize/1000000)/len(list_of_files)),3)

    if sizeDisplay > 1:
        sizeType = "mb"
    else:
        sizeDisplay = round(((totalSize/1000)/len(list_of_files)),3)
        sizeType = "kb"

    print(f"Average file size: {sizeDisplay}{sizeType}")

    if len(smallFiles) > 0:
        print(f"The following {len(smallFiles)} files are smaller than 10kb")
        print(smallFiles)
    else:
        print("All files are larger than 10kb - good to go!")

def saveImagesFromImageLinks(imageLinks, numberOfImages, issueName=""):
    global COUNTER
    initial = COUNTER
    print("Downloading images...")
    for imageLink in imageLinks:
        path = saveImageFromUrl(imageLink, numberOfImages, issueName)
    # path should be the same for all images per folder
    displayDownloadInfo(path)
    return path

def saveImageFromUrl(url, numberOfImages, issueName=""):
    global COUNTER
    digits=len(str(numberOfImages))

    if os.name == 'nt':
        if issueName != "":
            path = script_dir + "\\" + comicTitle + "\\" + issueName + "\\"
        else:
            path = script_dir + "\\" + comicTitle + "\\"
    elif issueName != "":
        path = script_dir + "/" + comicTitle + "/" + issueName + "/"
    else:
        path = script_dir + "/" + comicTitle + "/"

    if not os.path.exists(path):
        os.makedirs(path)

    filename = path + str(COUNTER).rjust(digits,"0") + ".jpg"
    with open(filename, "wb") as f:
        f.write(requests.get(url).content)
        COUNTER += 1

    # pass the path back for usage with zip
    return path

def runWait():
    # This counter could probably be tweaked for faster performance
    counter=random.randint(10,20)
    print(f"Sleeping for {counter} seconds")
    time.sleep(counter)

def addAdblocker(options):
    try:
        if os.name == 'nt':
            print("Looking for adblocker here:")
            print(get_script_path() + '\\AdblockPlusModified.crx')
            options.add_extension(get_script_path() + '\\AdblockPlusModified.crx')
        else:
            options.add_extension(get_script_path() + '/AdblockPlusModified.crx')
    except:
        print("Adblocker not added")

def downloadIssueWithSelenium(fullComicDownload, driver, service, issue, imageLinks, issueImageDict, startURL, title, singleIssueDownload, disableWait, seleniumDisplay):
    issueName = getIssueName(issue, startURL)
    # I *think* that driver.get causes it to wait until the entire page finish loading
    # It *appears* to load all the images into the browser before continuing
    print(f"Selenium accessing {issue}")
    print("Please wait...")
    driver.get(issue)
    source = driver.page_source
    if "AreYouHuman" in source:
        print("\n\nCaptcha detected, solving...")
        print("Starting new Selenium session for captcha...")
        options = webdriver.ChromeOptions()
        addAdblocker(options)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        captchaDriver = webdriver.Chrome(service=service, options=options)
        captchaDriver.maximize_window()
        print("Attempting to add Adblocker extension... Please wait for page to refresh")
        captchaDriver.get("https://www.google.com")
        captchaDriver.get(issue)
        input("Press Enter to continue once you have solved the captcha and closed the browser window")
        return downloadIssueWithSelenium(fullComicDownload, driver, service, issue, imageLinks, issueImageDict, startURL, title, singleIssueDownload, disableWait)

    print("Issue loaded in Selenium")
    images = driver.find_elements(By.TAG_NAME, "img")
    issueImageLinks = []
    for img in images:
        source = img.get_attribute('src')
        if 'blogspot' in source:
            issueImageLinks.append(source)

    imageLinks.append(issueImageLinks)

    print(f"Number of images to download {len(issueImageLinks)} \n")

    if singleIssueDownload:
        # title contains the issue name in this case
        issueImageDict[title] = issueImageLinks
    else:
        print(f"Issue name: {issueName}")
        issueImageDict[issueName] = issueImageLinks

    if not fullComicDownload:
        print(f"Downloading Issue: {comicTitle} : {issueName}")
        global COUNTER
        COUNTER = 1
        path = saveImagesFromImageLinks(issueImageDict[issueName], len(issueImageDict[issueName]), issueName)
        if singleIssueDownload:
            folderCBZPacker(comicTitle, "")
        else:
            folderCBZPacker(comicTitle, issueName)

    if not disableWait:
        runWait()

def downloadAllWithSelenium(fullComicDownload, startURL, issueLinks, title, singleIssueDownload, disableWait, seleniumDisplay):
    print("\n Starting Selenium...")
    s=Service(ChromeDriverManager().install())
    print()
    options = webdriver.ChromeOptions()
    # verbose (turned off)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if seleniumDisplay:
        # I modified the function detectFirstRun in the file background.js to prevent it from opening the 'introduction' tab on every run
        addAdblocker(options)
        driver = webdriver.Chrome(service=s, options=options)
        print("Attempting to add Adblocker extension... Please wait for page to refresh")
        driver.get("https://www.google.com")
    else:
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=s, options=options)

    issueImageDict = {}
    imageLinks = []

    for issue in issueLinks:
        downloadIssueWithSelenium(fullComicDownload, driver, s, issue, imageLinks, issueImageDict, startURL, title, singleIssueDownload, disableWait, seleniumDisplay)

    return (imageLinks, issueImageDict)

def downloadAllWithRequests(fullComicDownload, startURL, issueLinks, title, singleIssueDownload, disableWait):
    issueImageDict = {}
    imageLinks = []

    for issueLink in issueLinks:
        issueName = getIssueName(issueLink, startURL)
        issueImageLinks = scrapeImageLinksFromIssue(issueLink, lowres)
        imageLinks.append(issueImageLinks)

        if singleIssueDownload:
            # title contains the issue name in this case
            issueImageDict[title] = issueImageLinks
        else:
            issueImageDict[issueName] = issueImageLinks

        if not fullComicDownload:
            print(f"Downloading Issue {issueName}")
            global COUNTER
            COUNTER = 1
            path = saveImagesFromImageLinks(issueImageDict[issueName], len(issueImageDict[issueName]), issueName)
            if singleIssueDownload:
                folderCBZPacker(comicTitle, "")
            else:
                folderCBZPacker(comicTitle, issueName)

        if not disableWait:
            runWait()

    return (imageLinks, issueImageDict)

def main(fullComicDownload, singleIssueDownload, title, lowres, disableWait, startURL, useSelenium, seleniumDisplay, issueStart):
    comicLength = 0

    if singleIssueDownload:
        issues = [startURL.replace(prefix, "")]
    else:
        issues = getLinksFromStartPage(startURL)
        issues = issues[int(issueStart):]

    # verbose
    # print(f"Issues: {issues}\n")

    highquality = ""
    if useSelenium and not lowres:
        highquality = "&quality=hq"

    issueLinks = []
    for issue in issues:
        issueLink = prefix + issue + readType + highquality
        issueLinks.append(issueLink)
    print(f"Number of Issues to download {len(issueLinks)}\n")
    issueTitles = [getIssueName(issueLink, startURL, replaceChar="") for issueLink in issueLinks]
    print(f"Issues to download: \n{issueTitles}")

    # verbose
    # print(f"Issue Links {issueLinks}")

    if useSelenium:
        imageLinks, issueImageDict = downloadAllWithSelenium(fullComicDownload, startURL, issueLinks, title, singleIssueDownload, disableWait, seleniumDisplay)
    else:
        imageLinks, issueImageDict = downloadAllWithRequests(fullComicDownload, startURL, issueLinks, title, singleIssueDownload, disableWait)

    print(f"Image links: {' '.join(map(str, imageLinks))}")
    print(f"Number of issues to download {len(imageLinks)} \n")
    totalImages = 0
    for issue in imageLinks:
        totalImages += len(issue)
    print(f"Number of images to download: \n{totalImages}")
    print(f"Issue image dict {issueImageDict}")

    # Determine length of full comic (how many zeroes to pad)
    if fullComicDownload:
        for key in issueImageDict:
            comicLength += len(issueImageDict[key])

        # uses the list object to package all the images into a single CBZ
        for issue in imageLinks:
            saveImagesFromImageLinks(issue, comicLength)
        folderCBZPacker(title)

    downloadedBooks = compareCBZtoIssueList(issues)
    print(f"\nDownloaded:")
    for book in downloadedBooks:
        print(f"{book}")
    fileCBZrenamer(title)


if __name__ == "__main__":
    # set versioning, follows https://semver.org/
    VERSION = "0.1.14"
    print(f"\nComicScraper v{VERSION} \n")

    # build the parser
    parser = argparse.ArgumentParser(description=f'Script for downloading CBZ files from readcomiconline.li, version {VERSION}',
    epilog='Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer')
    parser.add_argument('URL', help='The url of the comic to download')
    parser.add_argument('-f', '--folder', help='The folder to save the comic in')
    parser.add_argument('-v', '--version', help='Display the current version of the script', action='version', version=VERSION)
    parser.add_argument('-c', '--complete', help='Download the entire comic into one folder. Omit this argument to download each issue into its own folder', action='store_true')
    parser.add_argument('-l', '--lowres', help='Download low resolution images. Omit this argument to download the max quality images', action='store_true')
    parser.add_argument('-d', '--disable-wait', help='Disable the wait between requests (captcha guard)', action='store_true')
    parser.add_argument('-s', '--selenium', help='Scrape image links using Selenium and a headless browser', action='store_true')
    parser.add_argument('-sd', '--selenium-display', help='Use Selenium in display mode', action='store_true')
    parser.add_argument('-i', '--issue', help='Select an issue to start downloading with, Experimental', action='store_true')

    # ensure that no args is a help call
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    arguments = parser.parse_args()

    if arguments.selenium == True and arguments.selenium_display == True:
        print("Please provide only -s or -sd, not both")
        print("Quitting")
        quit()

    # set variables from arguments
    startURL = arguments.URL
    singleIssue = False
    if "?id=" in startURL:
        singleIssue = True
        print("You have provided the link for a single issue.")
        print("When providing the URL for the info page, this script will download all issues in the series.")

    if arguments.folder != None:
        print(f"Title detected, using {arguments.folder} as title")
        comicTitle = arguments.folder
    else:
        print("No title specified. Reading title from Url...")
        comicTitle = getComicTitle(startURL, singleIssue)
        print(f"Using title: {comicTitle}")

    downloadFull = False
    if arguments.complete == True and singleIssue == False:
        print("Argument -c detected and comic info URL supplied. Downloading entire comic into one folder")
        downloadFull = True

    lowres = False
    if arguments.lowres == True:
        print("Argument -l detected. Downloading low resolution images")
        lowres = True
    else:
        print("Downloading max quality images")

    useSelenium = False
    if arguments.selenium == True:
        print("Argument -s detected. Using Selenium to scrape the page(s)")
        useSelenium = True

    seleniumDisplay = False
    if arguments.selenium_display == True:
        print("Argument -sd detected. Using Selenium in display mode")
        useSelenium = True
        seleniumDisplay = True

    disableWait = False
    if arguments.disable_wait == True:
        print("Argument -d detected. Disabling wait between requests")
        print("This may cause CAPTCHAs to appear more often.")
        disableWait = True

    issueStart = 0
    if arguments.issue == True:
        print("Argument -i detected.")
        print("This is an experimental feature. Use at your own risk. Meant to be used when the script has crashed partway through a series.")
        issueStart = input("What issue would you like to start with? enter an integer: ")

    print(f"Starting to scrape {comicTitle} from {startURL}")

    main(downloadFull, singleIssue, comicTitle, lowres, disableWait, startURL, useSelenium, seleniumDisplay, issueStart)
    print("\nComic Downloaded")
