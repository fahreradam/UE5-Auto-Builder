## What Does This Do
This auto builder has three aspects of it, it has perforce integration, Discord integration, and project auto-building once a new perforce push is made. Unless modified all aspects need to be filled out in order for the builder to work properly.

### Perforce Integration

In order to get it to work there are 5 variables that need to be filled in within the AutoBuilder.py file.

    PerforceLogin = {"Username":"", "Password":""}
    
A perforce account that has access to the desired repo so it can pull the most latest revision.

    Port = ""

The server address of the perforce server (the first item when signing into p4v normally).

    Workspace = ""

The Workspace of the account being used. This has to be a workspace that includes the desired repo.

    PullDelay = -1

How many seconds to wait before the next pull attempt is made

    NumberOfSavedBuilds = -1

How many builds should be stored before they start to be obliterated. In order for this to work, the perforce account needs to be an admin of the repo so they have the ability to call the obliterate command. A delete command does not work as perforce is designed to save old revisions on the server without being visible to the client. This can potentially result in using all the storage space of the server and locking everything up.

Make sure you are using a different workspace for the builder as it will obliterate all revisions that were made using that workspace until it is within the NumberOfSavedBuilds threshold starting with the oldest revisions of that workspace.

### Discord Integration

Discord integration is fairly straightforward. There are three variables that need to be filled out.

    userlist = {}

This userlist is a dictionary that should contain a perforce username and their discord ID. An example of this would be

    userlist = {"Adam": 02010606604050545} (Number was made up)

This user list is used to ping the person who submitted the last revision if the build failed to package.

    BuildManagerRoleID = 0

This is a role ID that was made within the server the webhook bot is made in. Whoever has that role will be pinged if the build fails, for my team it was set to the project anger role.

    WebhookAddress = ''

A webhook should be made in a desired server as well as creating a channel for the webhook bot to send messages to. The webhook address should be the address of the webhook bot.

### Auto Builder
The build script is the PackageGame.bat file, this code was referenced heavily by a user botman99 and their GitHub version can be viewed [here](https://github.com/botman99/ue4-unreal-automation-tool/blob/main/Build.bat). I modified his code to allow for more versatility when it came to file pathing as well as storing the log with each build. In order for the build to work properly, 6 variables need to be set.

For all paths ensure that there is are in front of the quotation marks otherwise you will more than likely get a unicode error when attempting to run the program.

    ProjectPath = r""

This is the path to the unreal project folder. It should be the directory with the project folder, not the directory inside the project folder.

    ProjectName = ""

This is the name of the project, it should be the same name as the project folder

    UnrealVersion Path = r""

This is the path to the version of Unreal you are using for the project. An example would be

    C:\Program Files\Epic Games\UE_5.2 

The path should be wherever your Epic Games folder is located and then the folder of the version you are using. Note that the example is for version 5.2. The builder should theoretically work with any unreal version but it has only been tested with UE5 versions so older versions are not guaranteed to work.

    BuildCommand = r""

This should be the path to PackageGame.bat

    BuildsFolder = r""

This is the path to the folder that the build should be stored in. This path must be within the repo file structure otherwise the marking for adding and pushing will not work. 

    Maps = ""

These are all the maps that will be built in the project. The format of this is

    Maps = "Level1+Levl2"

This is saying level1 and level2 need to be built, it is also important to note that there are no spaces.