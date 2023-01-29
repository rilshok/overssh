from pathlib import Path
from typing import AnyStr, Mapping, NamedTuple, Optional, Union

import paramiko  # type: ignore
from paramiko.config import SSH_PORT

LikeSSHAuth = Union["SSHAuth", AnyStr, Mapping]
PathLike = Union[str, Path]


class SSHAuth(NamedTuple):
    hostaddr: str
    hostport: int = SSH_PORT
    hostname: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    identity: Optional[str] = None
    identity_password: Optional[str] = None

    @property
    def socket(self):
        return (
            f"{self.hostaddr}:{self.hostport}"
            if self.hostport != SSH_PORT
            else self.hostaddr
        )

    @property
    def destination(self):
        return f"{self.username}@{self.socket}" if self.username else self.socket

    def __str__(self) -> str:
        return self.hostname or self.hostaddr

    def __repr__(self) -> str:
        return f"SSHAuth[{str(self)}]"

    def enter_password(self, password: str) -> "SSHAuth":
        return self._replace(password=password)

    def enter_identity_password(self, password: str) -> "SSHAuth":
        return self._replace(identity_password=password)

    @staticmethod
    def from_file(hostname: str, path: Optional[PathLike] = None) -> "SSHAuth":
        config_path = Path(path or "~/.ssh/config").expanduser()
        sshconfig = paramiko.SSHConfig.from_path(str(config_path))
        if hostname not in sshconfig.get_hostnames():
            msg = f"{hostname} not found in {str(config_path)}"
            raise FileNotFoundError(msg)
        info = sshconfig.lookup(hostname)

        identityfile = info.get("identityfile")
        identity = str(Path(identityfile[0]).expanduser()) if identityfile else None

        return SSHAuth(
            hostname=hostname,
            hostaddr=info["hostname"],
            hostport=int(info.get("port") or SSH_PORT),
            username=info.get("user"),
            identity=identity,
        )

    @staticmethod
    def cast(auth: LikeSSHAuth) -> "SSHAuth":
        if isinstance(auth, SSHAuth):
            return auth
        if isinstance(auth, str):
            return SSHAuth.from_file(auth)
        if isinstance(auth, dict):
            return SSHAuth(**auth)
        raise NotImplementedError
