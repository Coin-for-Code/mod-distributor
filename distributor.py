import os
from os import scandir

import toml.decoder
from toml import load
import zipfile

# Step 1: find distribution-config.toml -> initialize all config values
# Step 2: find mod_warehouse -> look at mods if there are any
# Step 3: archive mods into mod_warehouse/archives/ directory (Ask if this is a major or minor update or just a patch)
# Step 4: connect with FTP server and upload changes to it
# Step 5: upload new archives to Google Drive


class Project:

    def __init__(self):
        if Project.verify_project() is False:
            print("Project didn't exist or wasn't in good shape and now needs configuration."
                  " Please follow steps above to prepare project.")
        else:
            print("Everything is OK. Ready to work.")

    def configure(self, config):
        pass

    @staticmethod
    def verify_project() -> bool:
        hasConfig = False
        hasWarehouse = False
        isFine = True
        with scandir() as entries:
            for entire in entries:

                # We don't want to have second config
                if entire.name == "distribution-config.toml" and hasConfig is False:
                    hasConfig = True
                    print("Found a config. Proceed to verify...")
                    # Here we check for config's validity, I don't know how does toml work,
                    # so I assume here that we check toml image of the config and repair file itself.
                    with open("distribution-config.toml", "r") as config:
                        if not Project.verify_config_file(config):
                            print("Config is damaged, proceed to repair...")
                            isFine = False
                            Project.repair_config_file(config)

                if entire.name == "mod_warehouse" and hasWarehouse is False:
                    hasWarehouse = True
                    print("Found a mod warehouse. Proceed to verify...")
                    if not Project.verify_warehouse():
                        print("Warehouse is damaged, proceed to repair...")
                        isFine = False
                        Project.repair_warehouse()

            if hasConfig is False:
                isFine = False
                print("Did not find a config file. Proceed to create one...")
                Project.create_config()
                print("Please configure `distribution-config.toml` before running.")

            if hasWarehouse is False:
                isFine = False
                print("Did not find a mod warehouse. Proceed to create one...")
                Project.create_warehouse()
                print("Please add mods to mod_warehouse/mods/server or mod_warehouse/mods/client.")

        return isFine

    @staticmethod
    def create_warehouse():
        """
        Makes the mod_warehouse structure. The error shall never be raised as it contradicts with the logic.
        :return: Nothing
        """
        print("Creating a mod warehouse...")
        try:
            os.mkdir("./mod_warehouse")
            os.makedirs("./mod_warehouse/mods/server")
            os.makedirs("./mod_warehouse/mods/client")
            os.makedirs("./mod_warehouse/archives/essentials")
            os.makedirs("./mod_warehouse/archives/client")

        except FileExistsError as error:
            print("Distributor tried to create 'mod_warehouse', but it already exits. This error shall never occur,"
                  "if it does, that means that your program is corrupted and won't work properly.\n Please download "
                  "a newer stable version. If this is a 'new' and 'stable' version, please contact the developer.")
            exit(1)
        print("Created the mod warehouse.")

    # Disgusting mess. A proposition: use an Object ProjectStructure, and compare them both
    @staticmethod
    def verify_warehouse() -> bool:
        hasModsServer = False
        hasModsClient = False
        hasArchivesEssentials = False
        hasArchivesClients = False

        with scandir("./mod_warehouse") as entries:
            for entry in entries:
                # Checking `mods` folder
                if entry.name == "mods":
                    print("Found 'mods' folder! Checking its validity...")
                    with scandir("./mod_warehouse/mods") as inside_mods:
                        for item in inside_mods:
                            if item.name == "server":
                                print("Found mods/server folder!")
                                hasModsServer = True
                            elif item.name == "client":
                                print("Found mods/client folder!")
                                hasModsClient = True
                            else:
                                print(f"Found unexpected item {item.name}. It will not interrupt the program, but"
                                      f"it is suggested that 'mods' folder has no other folders"
                                      f" than 'server' and 'client'.")

                # Checking `archives` folder
                elif entry.name == "archives":
                    print("Found 'archives' folder! Checking its validity")
                    with scandir("./mod_warehouse/archives") as inside_mods:
                        for item in inside_mods:
                            if item.name == "essentials":
                                print("Found archives/essentials folder!")
                                hasArchivesEssentials = True
                            elif item.name == "client":
                                print("Found archives/client folder!")
                                hasArchivesClients = True
                            else:
                                print(f"Found unexpected item {item.name}. It will not interrupt the program, but"
                                      f"it is suggested that 'archives' folder has no other folders"
                                      f" than 'essentials' and 'client'.")

        # Warn user about the lost folders
        if hasModsServer is False:
            print("Haven't found 'mods/server'")
        if hasModsClient is False:
            print("Haven't found 'mods/client'")
        if hasArchivesEssentials is False:
            print("Haven't found 'archives/essentials'")
        if hasArchivesClients is False:
            print("Haven't found 'archives/client'")

        return hasModsServer and hasModsClient and hasArchivesEssentials and hasArchivesClients

    # Disgusting mess. A proposition: use an Object ProjectStructure, and repair one using the other
    @staticmethod
    def repair_warehouse():
        foundFolders = []

        with scandir("./mod_warehouse") as entries:
            for entry in entries:
                # Checking `mods` folder
                if entry.name == "mods":
                    print("Repair has found 'mods' folder. No actions needed.")
                    foundFolders.append("mods")
                    with scandir("./mod_warehouse/mods") as inside_mods:
                        for item in inside_mods:
                            if item.name == "server":
                                print("Repair has found mods/server folder. No actions needed.")
                                foundFolders.append("mods/server")
                            elif item.name == "client":
                                print("Repair has found mods/client folder. No actions needed.")
                                foundFolders.append("mods/client")

                # Checking `archives` folder
                elif entry.name == "archives":
                    print("Repair has found 'archives' folder. No actions needed.")
                    foundFolders.append("archives")
                    with scandir("./mod_warehouse/archives") as inside_mods:
                        for item in inside_mods:
                            if item.name == "essentials":
                                print("Repair has found archives/essentials folder. No actions needed.")
                                foundFolders.append("archives/essentials")
                            elif item.name == "client":
                                print("Repair has found archives/client folder. No actions needed.")
                                foundFolders.append("archives/client")

        if "mods" not in foundFolders:
            os.mkdir("./mod_warehouse/mods")
            print("Repair has not found the `mods folder`, creating one.")
        if "archives" not in foundFolders:
            os.mkdir("./mod_warehouse/archives")
            print("Repair has not found the `archives` folder`, creating one.")
        if "mods/server" not in foundFolders:
            os.mkdir("./mod_warehouse/mods/server")
            print("Repair has not found the `mods/server` folder`, creating one.")
        if "mods/client" not in foundFolders:
            os.mkdir("./mod_warehouse/mods/client")
            print("Repair has not found the `mods/client` folder`, creating one.")
        if "archives/essentials" not in foundFolders:
            os.mkdir("./mod_warehouse/archives/essentials")
            print("Repair has not found the `archives/essentials` folder`, creating one.")
        if "archives/client" not in foundFolders:
            os.mkdir("./mod_warehouse/archives/client")
            print("Repair has not found the `archives/client` folder`, creating one.")

    @staticmethod
    def verify_config_file(config) -> bool:
        print("Verifying the config...")
        isFine = True
        try:
            configuration = load(config)
            if "server-mods-version" not in configuration.keys():
                isFine = False
                print("Didn't find `server-mods-config` property in the config. Please check your configuration file.")
            if "client-mods-version" not in configuration.keys():
                isFine = False
                print("Didn't find `client-mods-version` property in the config. Please check your configuration file.")
        except toml.decoder.TomlDecodeError as decode_error:
            isFine = False
            print("Failed to load configuration. Please verify the configuration file.")
        return isFine

    @staticmethod
    def repair_config_file(config_file):
        print("Repairing the config file...")
        Project.create_config()
        print("Repaired the config.")

    @staticmethod
    def create_config():
        print("Creating the config file...")
        with open("distribution-config.toml", "w") as config:
            config.write("server-mods-version=\n"
                         "client-mods-version=\n")
        print("Created the config.")


if __name__ == '__main__':
    a = Project()

