#import the necessary libraries required
#figure out how to get a requirements file running idk 
import os
import subprocess
#importing inquirer to prompt the user
import inquirer
#import gdown (maybe for downloading?)
#import requests ( maybe for downaloding aswell idk)
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



#figure out how to make VMs i guess, or maybe figure out how to import them? that seems more realistic
def create_vm_import():
    vbox_path = find_vboxmanage()

    if vbox_path is None:
        print("VBoxManage not found. Please make sure VirtualBox is installed.")
        #maybe redirect them to check_installation()?
        return    
    



def modify_vm():
    vbox_path = find_vboxmanage()

    if vbox_path is None:
        print("VBoxManage not found. Please make sure VirtualBox is installed.")
    #maybe redirect them to check_installation()?
        return   
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


   
    #hardcoded stuff for now to test
    harcoded_iso = os.path.join(os.path.expanduser('~'), 'Documents', 'ubuntu_ser.iso')
    vm_name = "banana"
    drive_size = 6000
    #disk_path = os.path.join(os.path.expanduser('~'), 'VirtualBox VMs', 'banana', 'banana.vdi')
    create_vm_from_iso(vm_name, harcoded_iso, drive_size)
    start_vm(vm_name)
    #resize_disk(disk_path)
#have all the functions and prompts maybe in here? idk figure it out later


#runs the script
if __name__ == "__main__":
    main()