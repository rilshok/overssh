"""Credentials for connecting to hosts"""

__all__ = (
    "SSHAuth",
)

from pathlib import Path
from typing import AnyStr, Mapping, NamedTuple, Optional, Union

import paramiko  # type: ignore
from paramiko.config import SSH_PORT  # type: ignore

from .aliases import PathLike

LikeSSHAuth = Union["SSHAuth", AnyStr, Mapping]


class SSHAuth(NamedTuple):
    """SSH connection credentials"""

    hostaddr: str
    hostport: int = SSH_PORT
    hostname: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    identity: Optional[str] = None
    identity_password: Optional[str] = None

    @property
    def socket(self):
        """hostaddr[:port]"""
        return (
            f"{self.hostaddr}:{self.hostport}"
            if self.hostport != SSH_PORT
            else self.hostaddr
        )

    @property
    def destination(self):
        """[username@]hostaddr[:port]"""
        return f"{self.username}@{self.socket}" if self.username else self.socket

    def __str__(self) -> str:
        return self.hostname or self.socket

    def __repr__(self) -> str:
        return f"SSHAuth[{str(self)}]"

    def enter_password(self, password: str) -> "SSHAuth":
        """Remember the user password used when connecting to the server"""
        return self._replace(password=password)

    def enter_identity_password(self, password: str) -> "SSHAuth":
        """Remember the password to use the identity file"""
        return self._replace(identity_password=password)

    @staticmethod
    def from_file(hostname: str, path: Optional[PathLike] = None) -> "SSHAuth":
        """Using the host specified in the SSH Config File ("~/.ssh/config)"""
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
        """Trying to use anything as a host configuration"""
        if isinstance(auth, SSHAuth):
            return auth
        if isinstance(auth, str):
            return SSHAuth.from_file(auth)
        if isinstance(auth, dict):
            return SSHAuth(**auth)
        raise NotImplementedError
