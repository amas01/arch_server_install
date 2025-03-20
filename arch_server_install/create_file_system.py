import sh
from box import Box

from arch_server_install.config import CONFIG
from arch_server_install.config.config_objects import Disk, LogicalVolume


def setup_disks(vol_group: Box) -> str | None:
    lvm_disks = []
    boot_disk = None
    for disk in vol_group.disk:
        assert isinstance(disk, Disk)

        # clean partition table on disk
        sh.wipefs("--all", "-f", disk.disk)

        if disk.boot is True:
            # create boot disk and lvm partition
            sh.sfdisk(
                disk.disk, _in=sh.echo("-e", "size=2G, type=83\n size=+, type=8e\n")
            )
            boot_disk = f"{disk.disk}1"  # /dev/sdb1
            lvm_disk = f"{disk.disk}2"  # /dev/sdb2

            # add ext2 partition to boot
            sh.mkfs("--type=ext2", "-F", boot_disk)

        else:
            # create only lvm partition
            sh.sfdisk(disk.disk, _in=sh.echo("-e", "size=+, type=8e\n"))
            lvm_disk = f"{disk.disk}1"  # /dev/sdb1

        # create physical volume
        sh.pvcreate("-y", lvm_disk)
        lvm_disks.append(lvm_disk)
    sh.vgcreate("-y", vol_group.name, " ".join(lvm_disks))

    for lv in vol_group.partitions:
        assert isinstance(lv, LogicalVolume)

        if lv.size:
            # create a fixed size lv
            sh.lvcreate("-y", "-L", lv.size, vol_group.name, "-n", lv.label)

        else:
            # create a lv using a percentage
            sh.lvcreate("-y", "-l", lv.size, vol_group.name, "-n", lv.label)

            # ensure final lv has "256M left after it to allow using e2scrub"
            sh.lvreduce("-y", "-L", "-256M", f"/dev/{vol_group.name}/{lv.label}")

        sh.mkfs("--type=ext4", "-F", f"/dev/{vol_group.name}/{lv.label}")

    return boot_disk


def mount_partitions(
    mount_path: str,
    lvs: list[LogicalVolume],
    vol_group_name: str,
    boot_partition: str | None,
):
    for lv in lvs:
        # create directory
        sh.mkdir("-p", f"{mount_path}/{lv.mount}")

        # mount lv
        sh.mount(f"/dev/{vol_group_name}/{lv.label}", f"{mount_path}/{lv.mount}")

    if boot_partition:
        # mount boot partition
        sh.mkdir("-p", f"{mount_path}/boot")
        sh.mount(boot_partition, f"{mount_path}/boot")


def install_base_os(mount_path: str, packages: list[str]):
    sh.pacstrap(
        "-K",
        mount_path,
        " ".join(packages),
    )


if __name__ == "__main__":
    with sh.contrib.sudo:
        for vol_group in CONFIG.volume_groups:
            boot_disk = setup_disks(vol_group)
            mount_partitions(
                mount_path=CONFIG.mount_path,
                lvs=vol_group.partitions,
                vol_group_name=vol_group.name,
                boot_partition=boot_disk,
            )
        install_base_os(
            mount_path=CONFIG.mount_path, packages=CONFIG.packages.list_of_packages
        )
