#import the necessary libraries required
#figure out how to get a requirements file running idk 
import os
import subprocess
#importing inquirer to prompt the user
import inquirer


#import gdown (maybe for downloading?)
#import requests ( maybe for downaloding aswell idk)

#used in downloading, i found it to work better than "requests", but for now i am using Google drive
import gdown


vm_list = {
  #have a list of vms in here maybe? and each one will lead to its specified file locaiton either dynamically or statically idk yet
}


def find_vboxmanage():
    #try to check if VBoxManage is present by checking its version, if it is, return VBoxManage, if its not return None
    try:
        subprocess.run(["VBoxManage", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "VBoxManage"
    except FileNotFoundError:
        pass

    common_paths = [
        #Windows
        "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe", 
        "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage",
        #Linux
        "/usr/bin/VBoxManage",  
        "/usr/local/bin/VBoxManage",  
        #Mac - unsure if i will actually make it work on Mac, no idea how their inner structure works or how they work as a whole.
        "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    return None


def download_file(link, name, folder_name):
    #get to the users home directory
    user_home_dir = os.path.expanduser("~")

    folder_path = os.path.join(user_home_dir, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    download_save_path = os.path.join(folder_path, name)

    gdown.download(link, download_save_path, quiet=False)

    print(f"test message for file successful download {download_save_path}")










#make a script to check if virtualbox is installed, if its not, prompt the user to download it.
def check_installation():
    check_if_exist = find_vboxmanage()

    if check_if_exist is not None:
        print("VirtualBox is installed") #Idk if i really need to inform them? maybe for now for debuggign reasons
        return
  
    # VirtualBox is not found, so ask if the user wants to install it
    install_question = [
        inquirer.Confirm(
            "install_prompt",
            message="VirtualBox is not installed. Do you want to install it? (yes/no)",
            default=False,
        )
    ]

    install_answers = inquirer.prompt(install_question)
    install_virtualbox = install_answers["install_prompt"]
    #maybe prompt the user if its not installed to downlaod it with a (yes) or (no)? them maybe proceed with the download, check if its possible to automatically download it for them, else prompt them to manually do it.
    #maybe expirement with downloading files from some cloud provider? idk maybe aws
    if install_virtualbox == "yes":
        print("install proces should be here")
    else:
        print("install canceled")  # fix this up later

    exit()



#create vm function with iso? maybe a choice? idk how to make them be preconfigured if they come from an iso
def create_vm_from_iso(vm_name, iso_path, vm_size):
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
#user prompts



#Reference for Vboxmanage import format
""" VBoxManage import < ovfname | ovaname > [--dry-run] [--options= keepallmacs | keepnatmacs | importtovdi ] 
[--vsys=n] [--ostype=ostype] [--vmname=name] [--settingsfile=file] [--basefolder=folder] [--group=group] 
[--memory=MB] [--cpus=n] [--description=text] [--eula= show | accept ] [--unit=n] [--ignore] [--scsitype= BusLogic | LsiLogic ] 
[--disk=path] [--controller=index] [--port=n] """



#VM import function, currently takes ova path and the vm name (hardcoded for testing)
def create_vm_import(ova_path, vm_name):

    #Find path to VboxManage tool
    vbox_path = find_vboxmanage()

    #Check if VboxManage path is found
    if vbox_path is not None:

        #run the Vboxmanage 'list vms' cmd and capture the output in vm_exists
        vm_exists = subprocess.run([vbox_path, 'list', 'vms'], stdout=subprocess.PIPE, text=True).stdout

    #finish commenting the below part at a later stage when its in a better state.
        if f'"{vm_name}"' in vm_exists:
            print(f"The Virtual Machine {vm_name} already exists")
        else:
            try:
                subprocess.run([vbox_path, "import", ova_path, "--vsys", "0", "--vmname", vm_name], stdout=subprocess.PIPE, text=True)
                print(f"Virtual Machine {vm_name} has been created from {ova_path}.")
            #if the process failed (return code 0 not returned) print an error message to the user
            except subprocess.CalledProcessError as file:
                print(f"Error creating the Virtual Machine from the provided .ova file: {file}")



def modify_vm(vm_name, ram, vram):
    vbox_path = find_vboxmanage()

    if vbox_path is None:
        print("VBoxManage not found. Please make sure VirtualBox is installed.")
    #maybe redirect them to check_installation()?
        return   
    
    try:
        subprocess.run([vbox_path, 'modifyvm', vm_name, '--memory', str(ram), '--vram', str(vram)], stdout=subprocess.PIPE, text=True)
        print(f"VM '{vm_name}' modified.")
    except subprocess.CalledProcessError as file:
        print(f"Error modifying VM '{vm_name}': {file}")
#attach any isos maybe? for additional applications if needed ? for specialized machines maybe







def attach_additional_iso():
    #not sure yet, maybe a some tools in the .iso?
    print("test")










# start the vm function, kinda straight forward from the vboxmanage documentation
def start_vm(vm_name):
    vbox_path = find_vboxmanage()

    if vbox_path is None:
        print("VBoxManage not found. Please make sure VirtualBox is installed.")
        #maybe redirect them to check_installation()?
        return   
    
    subprocess.run([vbox_path, 'startvm', vm_name, '--type', 'headless'])








def resize_disk(disk_path): #works like 50% of the time not usable really? maybe in the future figure it out
    vbox_path = find_vboxmanage()
    #legit at this point maybe make this a standalone function?
    if vbox_path is None:
        print("VBoxManage not found. Please make sure VirtualBox is installed.")
        #maybe redirect them to check_installation()?
        return  
    
    subprocess.run([vbox_path, 'modifyhd', disk_path, '--resize', '10240'])





#main funciton
def main():
    print("test")


    #IMPORT TESTING

    # Use the specified file paths and VM name
    #The below will later on be turned into a more dynamic system, where the user picks the VM they want, and based on that it auto selects the .ova file
    #also add a Download prompt if the user does not have the ova downloaded.
    """ ova_file = os.path.join("D:", "ubuntutest", "buntuserver", "server_test.ova") """
    base_path = "C:/Users/eraic/Documents/testbuntu"
    file_name = "ubuntu_server.ova"








    # Use os.path.join to create the full file path
    ova_file = os.path.join(base_path, file_name)
    import_vm_name = "importtest321"

    #start_vm(import_vm_name)
    #create_vm_import(ova_file, import_vm_name)








    #DOWNLOAD SECTION TESTING
    #hardcoded values, this will later be changed to automatically do everything
    download_link = "https://drive.google.com/uc?export=download&id=1ZzrivfWtxn8k5p9pIqZ63eMqLn-MdCF8"
    download_name = "ubuntu_server.ova"
    folder_name = "VMDownloads"  
    download_file(download_link, download_name, folder_name)







    #hardcoded stuff for now to test
    harcoded_iso = os.path.join(os.path.expanduser('~'), 'Documents', 'ubuntu_ser.iso')
    vm_name = "banana"
    drive_size = 6000
    #disk_path = os.path.join(os.path.expanduser('~'), 'VirtualBox VMs', 'banana', 'banana.vdi')
    #create_vm_from_iso(vm_name, harcoded_iso, drive_size)]
    
    #start_vm(vm_name)
    #resize_disk(disk_path)
#have all the functions and prompts maybe in here? idk figure it out later


#runs the script
if __name__ == "__main__":
    main()
