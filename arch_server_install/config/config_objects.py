from dataclasses import dataclass

LINUX_KERNEL = [
    "linux",
    "linux-hardened",
    "linux-lts",
    "linux-rt",
    "linux-rt-lts",
    "linux-zen",
]
MICROCODE = ["intel-ucode", "amd-ucode"]


@dataclass
class Disk:
    disk: str
    boot: bool = False


@dataclass
class LogicalVolume:
    label: str
    mount: str
    size: str | None = None
    remaining_percentage: str | None = None

    def __post_init__(self):
        assert not (self.size and self.remaining_percentage)
        assert self.size or self.remaining_percentage


@dataclass
class VolumeGroup:
    name: str
    disks: list[Disk]
    partitions: list[LogicalVolume]


@dataclass
class Packages:
    linux_kernel: str
    microcode: str
    base_packages: list[str]
    text_editor: str
    additional_packages: list[str]

    def __post_init__(self):
        assert self.linux_kernel in LINUX_KERNEL
        assert self.microcode in MICROCODE

    def list_of_packages(self) -> list[str]:
        return (
            [self.linux_kernel]
            + [self.microcode]
            + self.base_packages
            + [self.text_editor]
            + self.additional_packages
        )


@dataclass
class Config:
    volume_groups: list[VolumeGroup]
    mount_path: str
    packages: Packages
    hostname: str

    def __post_init__(self):
        disks = [v.disks for v in self.volume_groups]
        assert [d for d_list in disks for d in d_list if d.boot is True]
