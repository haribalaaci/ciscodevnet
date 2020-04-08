#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using SSH via paramiko to configure network devices.
"""
import time
from netmiko import Netmiko
from yaml import safe_load
from jinja2 import Environment, FileSystemLoader


def send_cmd(conn, command):
    """
    Given an open connection and a command, issue the command and wait
    1 second for the command to be processed. Sometimes this has to be
    increased, can be very tricky!
    """
    output = conn.send(command + "\n")
    time.sleep(1.0)
    return output


def get_output(conn):
    """
    Given an open connection, read all the data from the buffer and
    decode the byte string as UTF-8.
    """
    return conn.recv(65535).decode("utf-8")


def main():
    """
    Execution starts here.
    """

    # Read the hosts file into structured data, may raise YAMLError
    with open("hosts.yml", "r") as handle:
        host_root = safe_load(handle)

# Netmiko uses "cisco_ios" instead of "ios" and
    # "cisco_xr" instead of "iosxr", so use a mapping dict to convert
    platform_map = {"ios": "cisco_ios"}

    # Iterate over the list of hosts (list of dictionaries)
    for host in host_root["host_list"]:

        # Use the map to get the proper Netmiko platform
        platform = platform_map[host["platform"]]

        # Load the host-specific VRF declarative state
    with open(f"/home/cisco/python_sripts/{host['name']}_vrbls.yml", "r") as handle:
            intfs = safe_load(handle)
   
        # Setup the jinja2 templating environment and render the template
    j2_env = Environment(
            loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
     )
    template = j2_env.get_template(f"/templates/netmiko/{host['platform']}_template.j2")
    new_intf_config = template.render(data=intfs)
           
# Create netmiko SSH connection handler to access the device
    conn = Netmiko(
            host=host["name"],
            username="cisco",
            password="cisco",
            device_type=platform,
   )  
    print(f"Logged into {conn.find_prompt()} successfully")

        # Send the configuration string to the device. Netmiko
        # takes a list of strings, not a giant \n-delimited string,
        # so use the .split() function
    result = conn.send_config_set(new_intf_config.split("\n"))

        # Netmiko automatically collects the results; you can ignore them
        # or process them further
    print(result)

    conn.disconnect()


if __name__ == "__main__":
    main()

