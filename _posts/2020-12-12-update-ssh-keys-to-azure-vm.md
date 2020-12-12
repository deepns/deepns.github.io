---
title: Update SSH keys to Azure VM
header:
    teaser: "/assets/images/teasers/update-ssh-keys-azure-vm-573x300.jpeg"
category:
    - Tech
tags:
    - programming
    - howto
    - azure
---

If you are creating a new VM in Azure, you can let Azure create a new SSH key pair or provide your own to be configured in the VM. At times, I just let Azure [create the keys](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/mac-create-ssh-keys) and I save the private key for logging into the VM from my local machine. All was well until I lost the key one day. I followed the below steps to update the keys with the existing user account on my Ubuntu VM running on Azure. Noting them down here for future reference.

- Login to Azure Portal and connect to Cloud Shell (alternatively you can use [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/get-started-with-azure-cli) if Azure CLI is installed on your local machine)
- Generate a new key pair (specify a name for the new key and the user name when running ssh-keygen. The option -f is optional here. When unspecified, it defaults to id_rsa). Use additional passphrase for added security.

```bash
$ ssh-keygen -m PEM -t rsa -b 4096 -f ~/.ssh/<new-key-name> -C <username>
```

- Update the user account with the new key. This will update the VM configuration and update authorized_keys with the provided public key. More details [here](https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/vmaccess). See the instance overview or description to find the resource-group-name of the VM.

```bash
$ az vm user update \
  --resource-group <resource-group-name> \
  --name <instance-name> \
  --username <username> \
  --ssh-key-value ~/.ssh/<new-key-name>.pub
```

- After this, you can ssh to the VM from Cloud Shell
- Download the private key from the Cloud Shell
- SSH to the VM from local machine using `ssh username@<public-ipaddr-or-fqdn-of-vm> -i <path-to-private-key-file>`