from arch_server_install.config.config_objects import (
    Config,
    Disk,
    LogicalVolume,
    Packages,
    VolumeGroup,
)


CONFIG = Config(
    volume_groups=[
        VolumeGroup(
            name="OsVolGroup",
            disks=[Disk(disk="/dev/sdb", boot=True)],
            partitions=[  # this is the order they will be created in and mounted!
                LogicalVolume(
                    label="root", mount="/", size="50G"
                ),  # root partition must be specified
                LogicalVolume(label="home", mount="/home", size="50G"),
                LogicalVolume(label="tmp", mount="/tmp", size="5G"),
                LogicalVolume(label="var", mount="/var", size="5G"),
                LogicalVolume(label="var-tmp", mount="/var/tmp", size="5G"),
                LogicalVolume(label="var-log", mount="/var/log", size="5G"),
                LogicalVolume(
                    label="var-lib", mount="/var/lib", remaining_percentage="100%Free"
                ),
            ],
        ),
    ],
    mount_path="/mnt/chroot",
    packages=Packages(
        linux_kernel="linux-lts",  # linux, linux-hardened, linux-lts, linux-rt, linux-rt-lts, linux-zen
        microcode="intel-ucode",  # intel-ucode, amd-ucode
        base_packages=["base", "linux_firmware", "lvm2", "openssh", "sudo", "grub"],
        text_editor="nvim",
        additional_packages=[
            "e2fsprogs",
            "docker",
            "docker-compose",
            "ufw",
            "git",
            "zsh",
            "grml-zsh-config",
            "wget",
            "python",
        ],
    ),
    hostname="itachi",
)
