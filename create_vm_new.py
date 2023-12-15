#Import functions for required functionality e.g. interacting with the OS, 
#running commands, inquiring with the user for prompts,
# and downloading files

import os
import platform
import subprocess
import inquirer
import requests
import gdown
import time
import sys


#CHECK SECTION

#USED TO FIND VBOXMANAGE WHICH IS USED TO MAKE VIRTUALBOX EXECUTE STUFF

def find_vboxmanage():
    #try to check if vboxmange exists in the current system by checking version, return if its here
    try: 
        subprocess.run(["VBoxManage", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "VBoxManage"
    except FileNotFoundError: #idk if its this tbh maybe subprocess.CalledProcessError?
        pass

    #the following paths are from https://www.virtualbox.org/manual/ch08.html#vboxmanage-common section 8.4
    possible_paths = [
        #Windows
        "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe", 
        "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage",
        #Linux
        "/usr/bin/VBoxManage",  
        "/usr/local/bin/VBoxManage",  
        #Mac - unsure if i will actually make it work on Mac, no idea how their inner structure works or how they work as a whole.
        "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
    ]

    #go through the list, if the path exists return the path to be used.
    for path in possible_paths:
        if os.path.exists(path):
            return path
    #if the path does not exist, return none
    return None

# Check for what platform is currently being run

def check_platform():
    #not sure
    return sys.platform


# check if the required folder for the virtualmachines is made

def check_vmfolder_exists(): 
    folder = os.path.join(os.path.expanduser('~'), 'VMDownloads')
    if os.path.exists(folder):
        return folder
    else:
        return False

#check if the path to the vm exists? this will be integrated into download vms place

def check_vm_exists(vmpath): 
    folder = os.path.join(os.path.expanduser('~'), 'VMDownloads')
    return os.path.exists(os.path.join(folder, vmpath))
    

# check if virtualbox is installed, if not prompt them to install it
def check_installation():
    check_vbox = find_vboxmanage()

    if check_vbox is not None:
        print("PLACEHOLDE WILL REMOVE | VirtualBox is installed")
        return
    
    install_question = [
        inquirer.Confirm(
            "install_prompt",
            message="VirtualBox is not installed, Do you want to install it?",
            default=False,
            )
        ]
    
    answer = inquirer.prompt(install_question)

    if answer["install_prompt"]:
        install_vbox()
    else:
        ("Installation will be skipped temp message")

#DOWNLOADS SECTION

#new version of check_installation?
def install_vbox():
    platform = check_platform()

    if platform == "win32":
        print("Please manually install windows through the provided file")
        windows_download()
    elif platform == "linux":
        try:
            subprocess.run(["sudo", "apt-get", "install", "virtualbox"])
            print("palceholder for installed")
        except subprocess.CalledProcessError as test: #if the process came in as an error
            print(f"Error : {test}")
    else:
        print(f"this is a test message if platform not support for debugging {platform}")
    
def download_vms(vmname,link, name):
    user_home_dir = os.path.expanduser("~")

    path_to_folder = os.path.join(user_home_dir, "VMDownloads")

    if not os.path.exists(path_to_folder):
        os.makedirs(path_to_folder)

    download_path = os.path.join(path_to_folder, name)

    if check_vm_exists(name):
        return


    print(f"You are about to download {vmname} from {link}")
    proceed = input("\nDo you wish to proceed with the download? (y/n): ").lower() #covnert it to lower anyways

    if proceed == "y":
        gdown.download(link, download_path, quiet=False)
        print(f"\nDownloaded VM {name} and saved at {download_path}")
    else:
        print("\nDownload canceled.")


def windows_download():
    url = "https://download.virtualbox.org/virtualbox/7.0.12/VirtualBox-7.0.12-159484-Win.exe"
    response = requests.get(url)

    # get the path to download folder
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

    # specify filename, no idea why i have to do this but doesnt work withotu
    file_name = "VirtualBox-7.0.12-159484-Win.exe"
    save_path = os.path.join(downloads_folder, file_name)

    # if it returns code 200(Nothing went wrong), proceed
    if response.status_code == 200:
        
        with open(save_path, "wb") as f:
            f.write(response.content)
            print("The VirtualBox installer has been successfuly installed in your Downloads Folder")
    else: #else return the status code and error message
        print(f"Failed to retrieve the file. Status code: {response.status_code}")

    exit()


#IDK SECITOn
#commented it out as no purpose for now, could play a purpose later on
#te subprocess comands related to vboxmanage are from vboxmanage site
""" VBoxManage import < ovfname | ovaname > [--dry-run] [--options= keepallmacs | keepnatmacs | importtovdi ] 
[--vsys=n] [--ostype=ostype] [--vmname=name] [--settingsfile=file] [--basefolder=folder] [--group=group] 
[--memory=MB] [--cpus=n] [--description=text] [--eula= show | accept ] [--unit=n] [--ignore] [--scsitype= BusLogic | LsiLogic ] 
[--disk=path] [--controller=index] [--port=n] """

""" def create_vm_from_iso(vm_name, iso_path, vm_size):
    vbox_path = find_vboxmanage()

    if vbox_path is None:
        print("VBoxManage not found. Please make sure VirtualBox is installed.")
        #maybe redirect them to check_installation()?
        return   

    #run the creatvm process with the supplied vm name and register it
    subprocess.run([vbox_path, 'createvm', '--name', vm_name, '--ostype', 'Ubuntu_64', '--register' ]) # the ostype thing should prob be automatically detected based on vm ?

    #create the storage path
    storage_path = os.path.join(os.path.expanduser('~'), 'VirtualBox VMs', vm_name, vm_name + '.vdi')
    subprocess.run([vbox_path, 'createhd', '--filename', storage_path, '--size', str(vm_size)])

    #attach the virtual disk to the vm
    subprocess.run([vbox_path, 'storagectl', vm_name, '--name', 'SATA Controller', '--add', 'sata', '--controller', 'IntelAHCI'])
    subprocess.run([vbox_path, 'storageattach', vm_name, '--storagectl', 'SATA Controller', '--port', '0', '--device', '0', '--type', 'hdd', '--medium', storage_path])

    subprocess.run([vbox_path, 'storagectl', vm_name, '--name', 'IDE Controller', '--add', 'ide'])
    subprocess.run([vbox_path, 'storageattach', vm_name, '--storagectl', 'IDE Controller', '--port', '0', '--device', '0', '--type', 'dvddrive', '--medium', iso_path])
 """


#pochni pak da gledash sled vbox import < ovfname lline 139
def import_vm(path, name):
    vbox_path = find_vboxmanage()

    downloads_folder = os.path.join(os.path.expanduser("~"), "VMDownloads")

    # specify filename, no idea why i have to do this but doesnt work withotu
    save_path = os.path.join(downloads_folder, path)

    if vbox_path is not None:

        vm_exists = subprocess.run([vbox_path, 'list', 'vms'], stdout=subprocess.PIPE, text=True).stdout

        if f'"{name}"' in vm_exists:
            print(f"The Virtual Machine {name} already exists")
        else:
            try:
                subprocess.run([vbox_path, "import", save_path, "--vsys", "0", "--vmname", name], stdout=subprocess.PIPE, text=True)
                print(f"{name} Successfully created")


            except subprocess.CalledProcessError as file:
                print(f"Error creating Virtual Machine from the provided .ova file: {file}")

def modify_vm(name, ram ,vram):
    vbox_path = find_vboxmanage()


    if vbox_path is None:
        print("VBoxManage not found. Please make sure VirtualBox is installed.")
        return
    
    try:
        subprocess.run([vbox_path, 'modifyvm', name, '--memory', str(ram), '--vram', str(vram)], stdout=subprocess.PIPE, text=True)
        print(f"VM 'f{name}' modified.")
    except subprocess.CalledProcessError as file:
        print(f"Error modifying VM '{vm_name}': {file}")


def ovftest2():
    print("ovftest")

    vbox_path = find_vboxmanage()

    if vbox_path is None:
        print("VBoxManage not found. Please make sure VirtualBox is installed.")
        return

    vm_name = "ovftest"

    if vbox_path is not None:
        try:
            base_path = r"C:\\Users\\eraic\\Documents\\ovf"

            # Placeholder names and stuff hardcoded pretty much
            ovf_filename = "lelqti.ovf"
            vmdk_filename = "lelqti-disk001.vmdk"

            ovf_path = os.path.join(base_path, ovf_filename)
            vmdk_path = os.path.join(base_path, vmdk_filename)

            # register the VM (if it is not already done so)
            subprocess.run([vbox_path, "createvm", "--name", vm_name, "--register"], check=True)

            # set VM settings (if needed)
            subprocess.run([vbox_path, "modifyvm", vm_name, "--memory", "1024", "--cpus", "2", "--vram", "128"])

            # attach the disk file
            subprocess.run([vbox_path, "storageattach", vm_name, "--storagectl", "SATA", "--port", "0", "--device", "0", "--type", "hdd", "--medium", vmdk_path], check=True)

            print("Disk attached successfully")

        except Exception as e:
            print(f"An error occurred: {e}")




#attach an iso with tools if needed? potentially useful for specialised vms
def attach_additional_iso():
    #not sure yet, maybe a some tools in the .iso?
    print("test")


#potental function for configuring ?
def configure_vm():
    print("TEST")

def start_vm():
    print("make this")

def register_and_attachtest(vm_name, disk_path, snapshot_name="test"):
    vbox_path = find_vboxmanage()
    try:
        # register the vm
        subprocess.run([vbox_path, "createvm", "--name", vm_name, "--register"], check=True)

        # set any settings like cpu cores and memory ( will cehckwhat else i can do, definately do internet tho )
        subprocess.run([vbox_path, "modifyvm", vm_name, "--memory", "1024", "--cpus", "2", "--vram", "128"], check=True)
        print("CPU cores: 2")
        print("Memory: 1024MB")
        # attach the sata controller
        subprocess.run([vbox_path, "storagectl", vm_name, "--name", "SATA", "--add", "sata", "--controller", "IntelAHCI"], check=True)

        # attach the disk to the SATA controller on the vm
        subprocess.run([vbox_path, "storageattach", vm_name, "--storagectl", "SATA", "--port", "0", "--device", "0", "--type", "hdd", "--medium", disk_path], check=True)

        subprocess.run([vbox_path, "snapshot", vm_name, "take", snapshot_name], check=True)
        print(f"Snapshot '{snapshot_name}' taken successfully.")

        print(f"VM '{vm_name}' is registered, settings configured, SATA controller added, and disk attached successfully.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")



#for the above, figure out how to set network settings, cpu, memory, OS TYPE, macaddress, attach any tools?

#make snapshots aswell



#VM RELATED FUNCTIONS .e.g. Modified, importing, creating, configuring, starting etc
def main():
    check_installation()


    #add a check if virtualbox is not installed, and the user clicks no, to not proceed with the stuff below.

    #exit()
    #ovftest()

    vm_list = {
        "Kali": {
            "download_link": "https://download.virtualbox.org/virtualbox/7.0.12/VirtualBox-7.0.12-159484-Win.exe",
            "download_name": "kali.ova"
        },
        "Ubuntu_server": {
            "download_link": "https://drive.google.com/uc?export=download&id=1ZzrivfWtxn8k5p9pIqZ63eMqLn-MdCF8",
            "download_name": "ubuntu_server.ova"
        },
        "Ubuntu_client": {
            "download_link": "https://drive.google.com/uc?export=download&id=...",
            "download_name": "ubuntu_client.ova"
        }
    }

    vm_questions = [
        inquirer.List(
            "vm_choice",
            message="Select a VM",
            choices=vm_list,
        )
    ]

    answers = inquirer.prompt(vm_questions)
    selected_vm = answers["vm_choice"]


    # this section deals with the download process if the vm does not exist already.
    selected_vm_info = vm_list[selected_vm]
    download_link = selected_vm_info["download_link"]
    download_name = selected_vm_info["download_name"]
    download_vm_name = selected_vm
    download_vms(download_vm_name, download_link, download_name)

    # ask the user for the name they want 
    get_name_prompt = inquirer.Text("vm_name_pr", message="Enter a name for your VM:")
    name_prompt_ans = inquirer.prompt([get_name_prompt])
    user_vm_name = name_prompt_ans["vm_name_pr"]

    print(f"\nYou have selected {selected_vm} and the name you have chosen is {user_vm_name}.\n")

    # ask them if they want to proceed
    proceed_prompt = inquirer.Confirm("proceed", message="Do you wish to proceed?")
    proceed_answer = inquirer.prompt([proceed_prompt])

    if proceed_answer["proceed"]:
        print("Proceeding with the selected VM and name.")
        import_vm(download_name, user_vm_name)
        print("\n")
        attachtest1 = inquirer.Confirm("attach_test", message="Test out attach method?")
        attachtest2 = inquirer.prompt([attachtest1])

        if attachtest2["attach_test"]:
            #hardcoded data due to still being a new found method for me and being in the testing process.
            uno = "notsure123111"
            dos = r"C:\\Users\\eraic\\Documents\\ovf\\a\\demotest.vmdk"
            register_and_attachtest(uno, dos)
        else:
            exit()
    else:
        print("\nClosing down Script")
        exit()

    print("\n\nWARNING! WHEN DELETING VIRTUAL MACHINES FROM VIRTUALBOX PLEASE CLICK ON 'REMOVE ONLY', CLICKING ON DELETE ALL FILES WILL REQUIRE YOU TO GO THROUGH THE DOWNLOAD PROCESS AGAIN")
    #alot of testing stuff have been removed just because it confused me more and more
if __name__ == "__main__":
    main()
