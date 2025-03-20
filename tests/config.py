import pytest

from arch_server_install.config.config import CONFIG
from arch_server_install.config.config_objects import Config, Disk, VolumeGroup


def test_validate_disks():
    assert CONFIG.volume_groups[0].disks == [Disk(disk="/dev/sdb", boot=True)]
    with pytest.raises(AssertionError):
        disks = [Disk(disk="/dev/sdb", boot=False)]
        Config(
            volume_groups=[VolumeGroup(name="test", disks=disks, partitions=None)],
            mount_path="/mnt",
            packages=None,
            hostname="host",
        )
