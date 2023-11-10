from P4 import P4, P4Exception
import subprocess
import os
from discord import Webhook
import aiohttp
import asyncio
import time


############################################ Start of Variable Section ################################################################

#### Discord Variables ####

# List of the discord users and their Discord ID's for pinging purpouses 
# Params : ("PerforceUsername" : DiscrodUserID)
userlist = {}

# A discrod role ID that is in charge of managing succefull builds
# Will be pinged along with the person responsible for the failed build
BuildManagerRoleID = 0

# A discord webhook in charage of sending build messages within a server
WebhookAddress = ''

#### Perforce Varaibles ####

# Perforce login inforamtion to be able to pull the most recent build
PerforceLogin = {"Username":"", 
                 "Password":""}

# Port of The Perforce Server
Port = ""

# The workspace of the perforce user
Workspace = ""

# How many seconds to wait till another pull attempt can be made
PullDelay = 1

# How many builds should be saved before they are obliterated in perforce
# Note oblioteration will only work if the user is an admin
NumberOfSavedBuilds = -1


#### Project Path Variables ####
# Note: All paths shoud have a r infront of their quotes to prevent errors
# Ex. Path = r"_FilePath_"

# The Path to the folder the .uproject is located in
# If the project's .uproject file was in C:\User\MyProject
# ProjectPath would be C:\User
ProjectPath = r""

# The project name
ProjectName = ""

# The Path to the UE5 Version
# Ex. C:\Program Files\Epic Games\UE_5.2 Note that this is for version 5.2
UnrealVersionPath = r""

# The location of Packagegame.bat
BuildCommand = r""

# The folder that will contain all the build folders
BuildsFolder = r""

# All Maps that are intended to be built
# Ex. Level1+Level2 Note that there are no spaces between levels
Maps = ""

############################################ End of Variable Section ##################################################################

# Confirming Variables are set
RunProgram = True
if(len(userlist) == 0):
    print("At least one user has not been set in the user list")
    RunProgram = False
if(type(BuildManagerRoleID) != int):
    print("Build Manager Role ID is supposed to be an int")
    RunProgram = False
if(len(str(BuildManagerRoleID)) <= 1):
    print("Build Manager Role ID has not been set")
    RunProgram = False
if(type(WebhookAddress) != str):
    print("Webhook Address should be a string")
    RunProgram = False
if(len(WebhookAddress) == 0):
    print("Webhook Address has not been set")
    RunProgram = False
if(type(PerforceLogin["Username"]) != str):
    print("Username should be a string")
    RunProgram = False
if(len(PerforceLogin["Username"]) == 0):
    print("Username has not been set")
    RunProgram = False
if(type(PerforceLogin["Password"]) != str):
    print("Password should be a string")
    RunProgram = False
if(len(PerforceLogin["Password"]) == 0):
    print("Password has not been set")
    RunProgram = False
if(type(Port) != str):
    print("Port should be a string")
    RunProgram = False
if(len(Port) == 0):
    print("Port has not been set")
    RunProgram = False
if(type(Workspace) != str):
    print("Workspace should be a string")
    RunProgram = False
if(len(Workspace) == 0):
    print("Workspace has not been set")
    RunProgram = False
if(type(PullDelay) != float and type(PullDelay) != int):
    print("Pull Delay should be either int or float")
    RunProgram = False
if(PullDelay < 0):
    print("Pull Delay should be a positive number")
    RunProgram = False
if(type(NumberOfSavedBuilds) != int):
    print("Number of saved builds should be an int")
    RunProgram = False
if(NumberOfSavedBuilds < 1):
    print("Number of saved builds should be at least 1 or greater")
    RunProgram = False
if(type(ProjectPath) != str):
    print("ProjectPath should be a string")
    RunProgram = False
if(len(ProjectPath) == 0):
    print("ProjectPath has not been set")
    RunProgram = False
if(type(ProjectName) != str):
    print("ProjectName should be a string")
    RunProgram = False
if(len(ProjectName) == 0):
    print("ProjectName has not been set")
    RunProgram = False
if(type(UnrealVersionPath) != str):
    print("UnrealVersionPath should be a string")
    RunProgram = False
if(len(UnrealVersionPath) == 0):
    print("UnrealVersionPath has not been set")
    RunProgram = False
if(type(BuildCommand) != str):
    print("BuildCommand should be a string")
    RunProgram = False
if(len(BuildCommand) == 0):
    print("BuildCommand has not been set")
    RunProgram = False
if(type(BuildsFolder) != str):
    print("BuildsFolder should be a string")
    RunProgram = False
if(len(BuildsFolder) == 0):
    print("BuildsFolder has not been set")
    RunProgram = False
if(type(Maps) != str):
    print("Maps should be a string")
    RunProgram = False
if(len(Maps) == 0):
    print("Maps has not been set")
    RunProgram = False

if(RunProgram == False):
    print("One or more variables have not been set")
    exit()


#################### Past This Point Should Not Need To Be Altered Unless Adding Or Removing Functionality ############################

async def RunBuild():
    # Login into perforce
    os.system('cmd /c "echo {}|p4 -u {} login"'.format(PerforceLogin["Password"], PerforceLogin["Username"]))
    p4 = P4()
    p4.port = Port
    p4.user = PerforceLogin["Username"]
    p4.client = Workspace
    p4.connect()

    # Ensures Builder is always active
    while(True):
        time.sleep(PullDelay)
        current_changelist = p4.run('changelists')[0]
        BuildLocation = r"{}\Revision{}_Build".format(BuildsFolder, current_changelist["change"])

        if(os.path.exists(BuildLocation) == False and current_changelist["client"] != p4.client and current_changelist['status'] == 'submitted'): 
            # Preforming a regular pull otherwise preform a force pull if there were problem
            # Force pull is usually needed if soemthing is modified on the autobuilder
            # Note: Force pull will vary in time greatly depending on network speed
            try:
                if (current_changelist['path'].split('/')[2] == ProjectPath.split('\\')[-1]):
                    p4.run_sync()
            except P4Exception:
                if 'File(s) up-to-date.' not in p4.warnings:
                    p4.run_sync('-f')
                else:
                    continue


            # Creating a folder for the project build
            os.system('cmd /c "mkdir {}"'.format(BuildLocation))

            # Command to start the project build
            # Params : 
            # Build Command - Path of PackageGame.bat
            # Project Name - Name of the unreal project
            # ProjectPath - Path to the project folder
            # Build Location - Path to place the build of the folder
            # UnrealVersionPath - UE5 version path of the project to use the proper build file
            # Maps - The maps that are desired to be built
            # BuildLocation - This second one is to direct where the log file should be placed

            subprocess.run([BuildCommand, ProjectName, ProjectPath, BuildLocation, UnrealVersionPath, Maps, BuildLocation])

            if(os.path.isfile("{}\PackageBuildLog.txt".format(BuildLocation))):
                Logfile = open("{}\PackageBuildLog.txt".format(BuildLocation), "r")
                os.remove("{}\GameBuildLog.txt".format(BuildLocation))
                os.remove("{}\EditorBuildLog.txt".format(BuildLocation))

            elif(os.path.isfile("{}\GameBuildLog.txt".format(BuildLocation))):
                Logfile = open("{}\GameBuildLog.txt".format(BuildLocation), "r")
                os.remove("{}\EditorBuildLog.txt".format(BuildLocation))            
            
            elif(os.path.isfile("{}\EditorBuildLog.txt".format(BuildLocation))):
                Logfile = open("{}\EditorBuildLog.txt".format(BuildLocation), "r")
                
            LogLines = Logfile.readlines()


            ErrorLog = open("{}/ErrorLog.txt".format(BuildLocation), "w")
            for line in LogLines:
                if(line.find("error") != -1 or line.find("Error") != -1):
                    ErrorLog.write(line)

            WarningLog = open("{}/WarningLog.txt".format(BuildLocation), "w")

            for line in LogLines:
                if(line.find("Warning:") != -1):
                    WarningLog.write(line)
                    
            ErrorLog.close()
            WarningLog.close()
            Logfile.close()


            # Make all files in directory for add
            dir = os.walk(BuildLocation)
            for (dir_path, dir_names, file_name) in dir:
                for name in file_name:
                    p4.run("add", r"{}\{}".format(dir_path, name))

            # Submit files to perforce and send a message to the discord webhook whether build was successful or not
            BuildFiles = p4.fetch_change()
            if(LogLines[len(LogLines) - 1].find("Success") != -1):
                BuildFiles._description = "Auto Builder\nSubmitting successful build for revision number "+current_changelist["change"]
                p4.run_submit(BuildFiles)
                await SendMessage("Build Successful For Revision **{}**, Submitted By **{}**".format(current_changelist["change"], current_changelist["user"]))
            else:
                BuildFiles._description = "Auto Builder\nSubmitting failed build logs for revision {} by {}, for more information check ErrorLog.txt and WarningLog.txt".format(current_changelist["change"], current_changelist["user"])
                p4.run_submit(BuildFiles)
                await SendMessage("<@&{}> Build Failed On Revision **{}** Submitted By <@{}>. Check WarningLog.txt and ErrorLog.txt located at {} for more information".format(BuildManagerRoleID, current_changelist["change"], userlist[current_changelist['user'].lower()], r"senprj_23\Builds\Revision{}_Build".format(current_changelist["change"])))

            print("Files sent")

            
            BuildSubmissions = []

            # Collect all pushed from the auto builder workspace
            for i in p4.run('changelists'):
                if(i['client'] == Workspace):
                    try:
                        if(i['path'].split('/')[2] == ProjectPath.split('\\')[-1]):
                            BuildSubmissions.append(i)     
                    except:
                        pass

            # Obliterate builds a past a given number
            # Clean up empty revisions caused by the obliterate
            while(len(BuildSubmissions) > NumberOfSavedBuilds):
                p4.run('obliterate', '-y', '//...@={}'.format(BuildSubmissions[-1]['change']))
                p4.run('change', '-d', '-f', BuildSubmissions[-1]['change'])
                BuildSubmissions.pop(-1)
                
    p4.disconnect()

# Funtion that sends messages to the webhook
async def SendMessage(message):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(WebhookAddress, session=session)
        message = await webhook.send(message)

asyncio.run(RunBuild())