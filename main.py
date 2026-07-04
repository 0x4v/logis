import os,subprocess,shutil, re
from datetime import datetime

def run_command(cmd, require_sudo=False):
    if require_sudo:
        cmd = ["sudo"] + cmd
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Hata: {e}"

def command_exists(cmd):
    return shutil.which(cmd) is not None

def journal():
    if command_exists("journalctl"):
        return run_command(["journalctl", "-b", "--no-pager"])
    elif os.path.exists("/var/log/syslog"):
        with open("/var/log/syslog") as f:
            return f.read()
    elif os.path.exists("/var/log/messages"):
        with open("/var/log/messages") as f:
            return f.read()
    return "Journal and syslog not found."

def dmesg():
    return run_command(["dmesg", "--kernel"])

def pacman_log():
    path = "/var/log/pacman.log"
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return "Pacman logs not found."

def dpkg_log():
    path = "/var/log/dpkg.log"
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return "DPKG logs not found."

def xorg_log():
    path = "/var/log/Xorg.0.log"
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return "Xorg logs not found."

def lspci_info():
    if command_exists("lspci"):
        return run_command(["lspci", "-vnn"])
    return "lspci module not found"

def lsusb_info():
    if command_exists("lsusb"):
        return run_command(["lsusb"])
    return "lsusb module not found."

def inxi_info():
    if command_exists("inxi"):
        return run_command(["inxi", "-Fxxc0", "--za"])
    return "inxi module not found."

def hwinfo_info():
    if command_exists("hwinfo"):
        return run_command(["hwinfo", "--short"])
    return "hwinfo module not found."

def remove_personal_data(log_content):

    uid = str(os.getuid())
    user = os.getenv("USER") or "_user_"
    hostname = os.uname().nodename
    log_content = re.sub(rf"\b{re.escape(user)}\b", "_user_", log_content)
    log_content = re.sub(rf"\b{uid}\b", "_uid_", log_content)
    log_content = re.sub(rf"\b{re.escape(hostname)}\b", "_hostname_", log_content)
    log_content = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "_ip_", log_content)
    log_content = re.sub(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", "_mac_", log_content)
    return log_content


def save_logs(logs, filename=None):
    if not filename:
        filename = os.path.expanduser(f"~/{datetime.now().strftime('%H-%M-%S-%f')}_logis_logs.txt")
    with open(filename, "w") as f:
        for name, content in logs.items():
            f.write(f"\n===== {name} =====\n\n")
            f.write(content)
            f.write("\n")
    print(f"Saved Logs : {filename}")
    return filename


def main():
    log_mapping = {
        "Journal": journal,
        "Kernel (dmesg)": dmesg,
        "Pacman": pacman_log,
        "DPKG": dpkg_log,
        "Xorg": xorg_log,
        "PCI Devices": lspci_info,
        "USB Devices": lsusb_info,
        "Hardware (inxi)": inxi_info,
        "Hardware (hwinfo)": hwinfo_info,
    }

    logs = {}
    for name, func in log_mapping.items():
        logs[name] = remove_personal_data(func())


    save_logs(logs)

if __name__ == "__main__":
    main()