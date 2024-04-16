#Import functions for required functionality e.g. interacting with the OS, 
#running commands, inquiring with the user for prompts,
# and downloading files

import os
import platform
import subprocess
import inquirer
import requests
import gdown
from gdown.exceptions import FileURLRetrievalError
import time # will be used to record how long it takes to create vm's and compare the findings later to Fur or Spichkova.
import sys
import json
import hashlib

CONFIG_FILE = "vm_config.json" 

#USED TO FIND VBOXMANAGE WHICH IS USED TO MAKE VIRTUALBOX EXECUTE STUFF
def find_vboxmanage():
    """
    Attempts to find the VBoxManage command's path on the system to control VirtualBox.
    Returns the command or path if found, or None if VBoxManage is not found.
    """
    try:
        subprocess.run(["VBoxManage", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "VBoxManage"
    except FileNotFoundError:
        # list of common paths where VBoxManage can be located on various operating systems.
        possible_paths = [
            "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe",
            "/usr/bin/VBoxManage",
            "/usr/local/bin/VBoxManage",
            "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

def check_platform():
    """
    Determines the operating system platform.
    Returns the OS system.
    Not used for now, maybe in future versions
    """
    return sys.platform


# check if the required folder for the virtualmachines is made
def check_vmfolder_exists(): 
    """
    Checks if the folder for storing virtual machine downloads exists.
    Returns the folder path if it exists, False otherwise.
    """
    folder = os.path.join(os.path.expanduser('~'), 'VMDownloads')
    if os.path.exists(folder):
        return folder
    else:
        return False

#check if the path to the vm exists? this will be integrated into download vms place
def check_vm_exists(vmpath): 
    """
    Checks if a virtual machine already exists at the specified path.
    Returns True if it exists, False otherwise.
    """
    folder = os.path.join(os.path.expanduser('~'), 'VMDownloads')
    return os.path.exists(os.path.join(folder, vmpath))
    

# check if virtualbox is installed, if not prompt them to install it
def check_installation():
    """
    Checks if VirtualBox is installed by attempting to locate VBoxManage.
    Prompts the user to install VirtualBox if it's not found.
    """
    if find_vboxmanage() is not None:
        print("")
        #print("VirtualBox is installed.")
    else:
        answer = inquirer.prompt([
            inquirer.Confirm("install_prompt", message="VirtualBox is not installed, Do you want to install it?", default=False),
        ])
        if answer["install_prompt"]:
            install_vbox()
        else:
            print("Installation skipped. Exiting.")
            sys.exit()

def install_vbox():
    """
    Handles the installation of VirtualBox based on the operating system.
    Users are guided to manually install VirtualBox if automatic installation is not supported.
    """
    os_type = platform.system()
    if os_type == "Windows":
        print("Detected Windows OS.")
        success = windows_download()
        if not success:
            print("Failed to download VirtualBox. Please download and install manually and re-run the program.")
            sys.exit()
    elif os_type == "Linux":
        print("Detected Linux OS. please enter your password to proceed with the download\n")
        try:
            subprocess.run(["sudo", "apt-get", "install", "-y", "virtualbox"], check=True)
            print("VirtualBox installed successfully.")
            print("Exiting from the tool, please re-run it again to continue")
            sys.exit()
        except subprocess.CalledProcessError as e:
            print(f"Installation failed with error: {e}")
    elif os_type == "Darwin":
        print("Detected macOS, this platform is currently not supported by this tool")
    else:
        print("Automatic installation not supported on this operating system. Please install VirtualBox manually.")
    
def download_vms(vmname, link, name, hash):
    user_home_dir = os.path.expanduser("~")
    path_to_folder = os.path.join(user_home_dir, "VMDownloads")
    download_path = os.path.join(path_to_folder, name)

    if not os.path.exists(path_to_folder):
        os.makedirs(path_to_folder)

    if check_vm_exists(name):
        return True

    while True:
        print("In order to create this virtual machine you must first download it:")
        print(f"\nYou are about to download {vmname} from {link}""\n")
        questions = [
            inquirer.Confirm('download_question', message="Do you wish to proceed with the download?", default=True),
        ]

        answer = inquirer.prompt(questions)
 
        if answer['download_question']: #if the answer is Y, attempt to download
            try:
                gdown.download(link, download_path, quiet=False) #

                # hash Verification
                if verify_hash(download_path, hash):
                    print(f"\nDownloaded virtual machine {name} and saved at {download_path}")
                    print("The file has been verified! Continuening to next step \n")
                    return True
                else:
                    print(f"\nDownloaded file {name} has an incorrect hash.")
                    print("The file may be corrupt or tampered with. Deleting the file.")
                    os.remove(download_path)
                    print("Hash verification failed.")
            except FileURLRetrievalError as e: #stop the download in the event of an invalid URL or no internet
                print("\nFailed to retrieve the file URL. Please try again later.")
                print(f"\nError message: {e}")
            
            # provide them with a retry option, providing more accessibility and usability
            retry_questions = [
                inquirer.Confirm('retry_question', message="Do you want to retry the download?", default=False),
            ]
            retry_answer = inquirer.prompt(retry_questions)
            if not retry_answer['retry_question']: # if they decide not to retry the download, inform them
                print("Exiting download process. Please try again later or email me at: \nerayoismail@gmail.com")
                sys.exit()  # exits the tool
        else:
            print("\nDownload canceled.")
            sys.exit()  # exits the tool if the download is canceled by the user
            

def verify_hash(file_path, expected_hash):
    """
    Verifies the SHA256 hash of the downloaded file against the expected hash.
    Returns True if the hash matches, False otherwise.
    """
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    return sha256_hash.lower() == expected_hash.lower()



def windows_download(): 
    """
    Downloads the VirtualBox .exe installer for Windows from the official downloads page and saves it to the user's downloads folder.
    Exits the script if the download fails or after successfully saving the file.
    """
    url = "https://download.virtualbox.org/virtualbox/7.0.12/VirtualBox-7.0.12-159484-Win.exe"
    file_name = "VirtualBox-7.0.12-159484-Win.exe"
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    save_path = os.path.join(downloads_folder, file_name)

    print(f"Downloading VirtualBox installer to {save_path} ")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # this will raise an error if the download failed

        with open(save_path, "wb") as f:
            f.write(response.content)

        print("The VirtualBox installer has been successfully downloaded to your Downloads folder.")
    except requests.HTTPError as e:
        print(f"Download failed with HTTP error: {e}")
        sys.exit()
    except requests.RequestException as e:
        print(f"Download failed with error: {e}")
        sys.exit()


def attach_additional_iso():
    """
    Placeholder for future feature to attach an ISO with additional tools to a virtual machine.
    Intended for specialized VMs, such as those used for security testing (e.g., Kali Linux),
    to enhance their capabilities with extra tools and features.
    """
    print("Feature to be delivered in the future, intended to be an addition to Specialized machines such as Kali.\nHopefully, this would provide it with extra tools and features.")




def create_virtual_machine(vm_name, disk_path):
    """
    Creates and configures a new virtual machine using VBoxManage.

    - vm_name: Name of the virtual machine, provided from the user
    - disk_path: Path to the virtual disk file (.vmdk) to be attached to the VM

    Handles the vm creation, memory and cpu allocation, storage configuration, network setup and snapshoting of the tool
    """
    vbox_path = find_vboxmanage()
    try:
        # register the VM with VirtualBox
        subprocess.run([vbox_path, "createvm", "--name", vm_name, "--register"], check=True)
        
        # configure VM's CPU, memory, and video memory
        subprocess.run([vbox_path, "modifyvm", vm_name, "--memory", "2048", "--cpus", "2", "--vram", "128"], check=True)
        print("CPU cores: 2\nMemory: 2048MB\nVRAM: 128MB")
        
        # attach a SATA storage controller
        subprocess.run([vbox_path, "storagectl", vm_name, "--name", "SATA", "--add", "sata", "--controller", "IntelAHCI"], check=True)
        
        # attach the disk to the VM
        downloads_folder = os.path.join(os.path.expanduser("~"), "VMDownloads")
        save_path = os.path.join(downloads_folder, disk_path)
        subprocess.run([vbox_path, "storageattach", vm_name, "--storagectl", "SATA", "--port", "0", "--device", "0", "--type", "hdd", "--medium", save_path], check=True)
        
        # configure network adapter to use NAT
        subprocess.run([vbox_path, "modifyvm", vm_name, "--nic1", "nat"], check=True)
        print(f"Network adapter created and set to NAT for VM '{vm_name}'.")

        # take an initial snapshot of the VM
        subprocess.run([vbox_path, "snapshot", vm_name, "take", vm_name], check=True)
        print(f"Snapshot '{vm_name}' taken successfully.")

        print(f"Virtual Machine '{vm_name}' is registered, settings configured, SATA controller added, and disk attached successfully.")

        print(f"Virtual Machine {vm_name} successfuly created")

    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred: {e}")


def welcome_message():
    """
    Display virtualize@HOme logo
    """
    message = """
            *********************************************
            *                                           *
            *         Welcome to Virtualize@Home        *
            *                                           *
            *********************************************
            """
    print(message)


def CLI():
    """
    Command Line Interface function that handles the main interaction with the user.
    It allows the user to select a range of virtual machines from a predefined list (vm_list),
    It will attemp to download the vm if it does not exist in the local system, and then proceeds
    with the creation and configuration of the VM.
    """
    max_attempts = 2
    attempts = 0
    user_vm_name = None

    # ppredefined list of virtual machines with their download links and hashes
    vm_list = {
        "Linux Mint": {
            "download_link": "https://drive.google.com/uc?export=download&id=1P94IrsWHJmEOyIiiSHB3kf9DhnvmiSJO",
            "download_name": "Linux_mint.vmdk",
            "download_hash": "507a703efdd1958fb886e4efc6ccad9b630d755d1f6362ec0ef59310d298a6c0"
        },
        "Kali Linux": {
            "download_link": "https://drive.google.com/uc?export=download&id=1-W0qWcbmK4-czsqsQjhZQfhVlgcFGAzy",
            "download_name": "Kali_Linux.vmdk",
            "download_hash": "920338e65e21504ad1562aaecd5197b4f3539d58b9bcc41505f14a63df8fe3e1"
        },
        "Ubuntu_server": {
            "download_link": "https://drive.google.com/uc?export=download&id=1sqtTIKq_iHcugRoSJCqG0smnwLt3zaLN",
            "download_name": "ubuntu_server.vmdk",
            "download_hash": "104D559174F8D1325A29A9312F051F1750A78611F187422ED99B2DBA19138192"
        },
        "Exit Tool": { }
    }
    
    print("\nYou can choose options by moving arrows up and down, and pressing enter \n\n")

    # prompt user to select a VM from the list
    vm_questions = [
        inquirer.List("vm_choice", message="Select a Virtual Machine", choices=vm_list)
    ]
    answers = inquirer.prompt(vm_questions)
    selected_vm = answers["vm_choice"]

    if selected_vm == "Exit Tool":
        print("You have exited the out of the tool\n")
        sys.exit()
    else:
    
        # proceed with download and configuration based on user selection
        selected_vm_info = vm_list[selected_vm]
        download_vm_name = selected_vm
        download_link = selected_vm_info["download_link"]
        download_name = selected_vm_info["download_name"]
        download_hash = selected_vm_info["download_hash"]
        download_vms(download_vm_name, download_link, download_name, download_hash)

        # user name for the VM and validation loop
        while attempts < max_attempts:
            get_name_prompt = inquirer.Text("vm_name_pr", message="Enter a name for your VM")
            name_prompt_ans = inquirer.prompt([get_name_prompt])
            user_vm_name = name_prompt_ans["vm_name_pr"].strip() 

            if user_vm_name:
                break
            else:
                print("\nPlease enter a valid name.\n")
                attempts += 1

        if user_vm_name:
            print(f"\nYou have selected {selected_vm} and the name you have chosen is {user_vm_name}.\n")
        else:
            print("Maximum attempts reached. Exiting Virtualize@Home")
            sys.exit()

        # ask them if they want to proceed
        proceed_prompt = inquirer.Confirm("proceed", message="Do you wish to proceed?", )
        proceed_answer = inquirer.prompt([proceed_prompt])

        if proceed_answer["proceed"]:
            user_name = user_vm_name
            user_download_name = download_name
            create_virtual_machine(user_name, user_download_name)
        else:
            print("\nYou have chosen to not proceed, Exiting Virtualize@Home")
            sys.exit()


        # Optionally, open VirtualBox after the VM is set up
        print("\n") #empty space [inquirer does not handle \n well]
        open_vbox_prompt = inquirer.Confirm("open_vbox", message="Do you wish to open VirtualBox?")
        open_vbox_answer = inquirer.prompt([open_vbox_prompt])

        if open_vbox_answer["open_vbox"]:
            print("\nOpening VirtualBox\n")
            open_virtualbox()
        else:
            print("\nYou have chosen not to open VirtualBox, please open it manually through your system\n")


        warning_message = """
    ⚠️  WARNING: When deleting virtual machines from VirtualBox, ensure you select 'Remove Only' and proceed to manually delete the files.
    Selecting 'Delete All Files' may result in the deletion of the virtual machine disk,
    requiring you to repeat the download process. Exercise caution, this may or may not apply to your system!
                    """

        #WARNING MESSAGE
        print(warning_message)


    #new section not yet documented. 
def check_terms():
    """Checks if the user has agreed to the terms of use and manages the config file."""
    script_dir = os.path.dirname(__file__) 
    config_path = os.path.join(script_dir, CONFIG_FILE)

    if not os.path.exists(config_path):  
        try:
            display_terms()
            get_agreement(config_path)
        except OSError:
            print("Error creating config file. Please check permissions.")
            exit()
    else:
        with open(config_path, 'r') as f:  
            config = json.load(f)
        if not config.get("terms_agreed"):  
            display_terms()
            get_agreement(config_path)


def display_terms():
    terms_and_conditions_guidelines = "https://github.com/ErayOIsmail/FYP-Project/blob/main/guidelines_and_terms_of_condition"
    print("Please read our terms and conditions: you can click the link below if your terminal supports it, or copy and paste the URL into your web browser.\n")
    print(terms_and_conditions_guidelines)
    #print("\nIf you agree to these terms")
    print("\nAfter reading, please proceed with the agreement process.")


def get_agreement(config_path): 
    """Asks the user for agreement and writes the response to the config file."""
    questions = [
        inquirer.Confirm(
            "terms_agree",
            message="Do you agree to the terms of use?",
            default=False,
        )
    ]
    answer = inquirer.prompt(questions)

    if answer["terms_agree"]:
        config = {"terms_agreed": True}

        with open(config_path, 'w') as f:
            json.dump(config, f)

        print("Thanks for agreeing to the terms.")
    else:
        print("You must agree to the terms to use Virtualize@Home")
        exit()

def open_virtualbox():
    vbox_path = find_vboxmanage()
    if vbox_path:
        # get virtualbox directory
        vbox_install_dir = os.path.dirname(vbox_path)

        # check the likely paths of the virtualbox executable
        if platform.system() == "Windows":
            vbox_exe = os.path.join(vbox_install_dir, "VirtualBox.exe")
        elif platform.system() == "Darwin":  # apparently MacOS
            vbox_exe = os.path.join(vbox_install_dir, "VirtualBox.app", "Contents", "MacOS", "VirtualBox")
        elif platform.system() == "Linux":  # Assuming Linux 
            vbox_exe = os.path.join(vbox_install_dir, "VirtualBox")
        else:
            print("Application not found / System not supported")

        
        # try to launch VirtualBox
        try:
            subprocess.Popen([vbox_exe]) 
        except Exception as e:
            print(f"Error opening VirtualBox GUI: {e}")
    else:
        print("VirtualBox 'VBoxManage' not found.")


def main():
    record_findings = time.time()

    check_terms()
    welcome_message()
    check_installation()
    CLI()
    final_findings = time.time()

    total_time_taken = round(final_findings - record_findings, 2)
    
    print(f"Total amount of time taken to go through the virtual machine creation procedure is: {total_time_taken} seconds.")

if __name__ == "__main__":
    try:
        main() 
    except KeyboardInterrupt:
        print("\nProgram interrupted by the user. Exiting tool.")
    except Exception as e:
        print(f"An error occurred: {e}")
