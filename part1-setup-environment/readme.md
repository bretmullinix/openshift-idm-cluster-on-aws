# Installation of OpenShit Cluster and IDM on AWS

Last updated: 06.21.2020

## Purpose

The purpose of the document is to teach the reader how to set up their
environment for the exercise.

## Installation

### Install Python 3 on Fedora
1. Open up a terminal
1. sudo dnf install python3.8
1. Type `python3.8 --version`
1. The output should show you are running Python 3.8.0


### Install Docker on Fedora

1. Open up a terminal
1. sudo dnf install -y grubby
1. sudo grubby --update-kernel=ALL --args="systemd.unified_cgroup_hierarchy=0"
1. sudo reboot
1. sudo dnf config-manager --add-repo=https://download.docker.com/linux/fedora/docker-ce.repo
1. sudo dnf install docker-ce
1. sudo systemctl enable --now docker
1. systemctl enable --now docker
1. The output show that you have **docker** running on your machine.

To enable a regular user to run **docker**, perform the following steps:

1. sudo groupadd docker
1. sudo usermod -aG docker USERNAME

### Install Ansible and Ansible Molecule

1. Open up a terminal
1. Navigate to a directory where you plan on putting your
python virtual environments.

    :warning: You must always work out of a virtual environment.
    Virtual environments prevent you from corrupting
    your default system virtual environment and allow users to install different
    software for each virtual environment.

1. Run `python3.8 -m venv venv_openshift_idm_ansible`
1. To activate your virtual environment on **Fedora**, you run
`source ./venv_openshift_idm_ansible/bin/activate`
1. Run `python --version`.  This is the version of Python running in your
virtual environment.
1. Run `pip install --upgrade pip`
1. Run `pip list`.  This should list the modules currently installed in your
environment.  Notice how ansible is not present.
1. Run `pip install ansible==2.9`.  The command installs **ansible 2.9** in the
virtual environment.
1. Run `pip list` to confirm **ansible 2.9** is installed.
1. Run `pip install molecule==3.0.4`
1. Run `pip list` to confirm **molecule 3.0.4** is installed.
1.  Run `pip install molecule[docker]`

    The **molecule[docker]** provides the code to spin up
    docker containers for molecule tests.
