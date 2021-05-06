---
title: Using GCP VM with Visual Studio code for remote development
header:
    teaser: /assets/images/teasers/gcp-vm-with-vscode-500x300.jpeg
category:
    - Tech
tags:
    - vscode
    - gcp
    - azure
    - programming
---

I recently started using cloud VMs for some personal projects. Initially I accessed the VMs through the cloud shells ([azure](https://docs.microsoft.com/en-us/azure/cloud-shell/overview), [gcp](https://cloud.google.com/shell)) for quicker access. It works great and has tonnes of features too, but I miss the familiarity of local development which I used to get with VS Code.

VS Code's [remote ssh extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) makes it much easier to develop with remote servers, making the remote development very much like native development. The steps I used to set up my remote development environment with a Linux VM on GCP and work with VS Code on macOS.

- Generate the ssh keys on the local machine

```bash
# This will generate private and public key file at the given path.
# Replace <key-file> with the name of the key and <gcp-user-name> with your GCP user name
$ ssh-keygen -t rsa -f $HOME/.ssh/<key-file> -C <gcp-user-name>
```

- [Create a VM](https://cloud.google.com/compute/docs/instances/create-start-instance), and [add instance level public keys](https://cloud.google.com/compute/docs/instances/adding-removing-ssh-keys#instance-only). The contents of the public key generated in the above step will have to pasted in the SSH keys section
- VM can then be accessed using the external IP assigned to it. (e.g. `ssh user@35.229.100.113 -i $HOME/.ssh/my-gcp-key`)
- Update SSH config file on the local machine for easy access.

```config
Host my-gcp-vm
    HostName <VM-External-IP>
    User <GCP-user-name>
    IdentityFile <path-to-key-file>
```

- Use Remote-SSH extension to [connect to the VM](https://code.visualstudio.com/docs/remote/ssh).

## Moving from GCP to Azure VM

The external IP assigned to GCP VM is ephemeral, so we get a new external IP upon restarting the VM. The SSH config file will then have to be updated every time the external IP is changed. I tried to get a [FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name) for the GCP VM, but later realized that it is not supported out of the box. This [article](https://cloud.google.com/compute/docs/instances/custom-hostname-vm) setting up a custom host name for GCP VM.

Interestingly, Azure [supports](https://docs.microsoft.com/en-us/azure/virtual-machines/create-fqdn#create-a-fqdn) FQDN out of the box without having to set up our own DNS record. The fqdn subdomain may vary depending on the location. My VM was deployed in the US East Zone, so I had something like this `<vm-name>.eastus.cloudapp.azure.com`.

With [Azure Virtual Machines extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurevirtualmachines) and FQDN assigned to the Azure VM, I could control start/stop of the VM and access the VM through SSH all within VS Code without stepping out. That makes the workflow with Azure VMs much easier than GCP VMs.
