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


#make a script to find vboxmanage location
def find_vboxmanage():
  #try to check if VBoxManage is present by checking its version, if it is, return VBoxManage, if its not return None
  try:
      subprocess.run(["VBoxManage", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      return "VBoxManage"
  except FileNotFoundError:
    pass


  #additionally maybe add common paths aswell? incase the above fails

  common_paths = [
    #have like the paths in here idk how it works exactly, learn it later
  ]

  #have like a for loop to check each path, if it does exist then it works maybe? not sure
  for exists in common_paths:
    if os.path.exists(exists):
      return exists

  
  return None

#make a script to check if virtualbox is installed, if its not, prompt the user to download it.
#Maybe this should be with the find_vboxmanage script? idk better keep it seperated could be useful in the future
def check_installation():
  #okay maybe keep them seperated? seems better
  check_if_exist = find_vboxmanage()

  if check_if_exist is not None:
    print("VirtualBox is installed") #Idk if i really need to inform them? maybe for now for debuggign reasons
    return

  #maybe prompt the user if its not installed to downlaod it with a (yes) or (no)? them maybe proceed with the download, check if its possible to automatically download it for them, else prompt them to manually do it.
#maybe expirement with downloading files from some cloud provider? idk maybe aws

#figure out how to make VMs i guess, or maybe figure out how to import them? that seems more realistic

#user prompts
#create vm function?
#modify vm if needed
#attach any isos maybe? for additional applications if needed ? for specialized machines maybe
#main funciton
def main():

#have all the functions and prompts maybe in here? idk figure it out later


#runs the script
if __name__ == "__main__":
  main()
