---
title: Using GCP VM with VSCode Remote Development
category:
    - Tech
tags:
    - vscode
    - gcp
    - azure
---

I recently started using cloud VMs for some personal projects. Though the cloud shells ([azure](https://docs.microsoft.com/en-us/azure/cloud-shell/overview), [gcp](https://cloud.google.com/shell)) are great, VS code makes it much easier to develop with VS Code. Noting the steps here for future references.

1. Generate the ssh keys

```bash
ssh-keygen -t rsa -f $HOME/.ssh/<key-file> -C <gcp-user-name>
```

2. Create a GCP VM, add ssh public key
3. Update SSH config file locally

```config
Host gcp-nsd
    HostName <GCP-V-IP>
    User <GCP-user-name>
    IdentityFile <path-to-key-file>
```

4. Connect to VM from vscode

## References

- [VS Code Remote ssh](https://code.visualstudio.com/docs/remote/ssh)
- [Add instance level public SSH keys](https://cloud.google.com/compute/docs/instances/adding-removing-ssh-keys#instance-only)