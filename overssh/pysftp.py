import contextlib
from pathlib import Path

import paramiko  # type: ignore
import pysftp  # type: ignore
from paramiko.config import SSH_PORT  # type: ignore
from paramiko.dsskey import DSSKey  # type: ignore
from paramiko.ecdsakey import ECDSAKey  # type: ignore
from paramiko.ed25519key import Ed25519Key  # type: ignore
from paramiko.hostkeys import HostKeyEntry, HostKeys  # type: ignore
from paramiko.pkey import PKey  # type: ignore
from paramiko.rsakey import RSAKey  # type: ignore
from pysftp.helpers import known_hosts  # type: ignore

from .aliases import PathLike
from .auth import LikeSSHAuth, SSHAuth
import io
from typing import BinaryIO


class PortHostKeys(HostKeys):
    """paramiko.hostkeys.HostKeys patch"""

    def __init__(self, filename: PathLike, port: int):
        self.port = port
        super().__init__(str(filename))

    def _hostname_matches(self, hostname: str, entry: HostKeyEntry) -> bool:
        if super()._hostname_matches(hostname, entry):
            return True
        if ":" not in hostname:
            hostname = f"[{hostname}]:{self.port}"
        return super()._hostname_matches(hostname, entry)


class Connection(pysftp.Connection):
    """SFTP Connection into the specified hostname"""

    def __init__(self, authinfo: LikeSSHAuth):
        authinfo = SSHAuth.cast(authinfo)
        opts = None
        if authinfo.hostport != SSH_PORT:
            opts = pysftp.CnOpts()
            opts.hostkeys = PortHostKeys(known_hosts(), authinfo.hostport)
        super().__init__(
            host=authinfo.hostaddr,
            port=authinfo.hostport,
            username=authinfo.username,
            password=authinfo.password,
            private_key=authinfo.identity,
            private_key_pass=authinfo.identity_password,
            cnopts=opts,
        )

    def _set_authentication(self, password, private_key, private_key_pass):
        if password is not None:
            return

        if private_key is None and Path("~/.ssh/id_ed25519").expanduser().exists():
            private_key = "~/.ssh/id_ed25519"

        if isinstance(private_key, (str, Path)):
            pkey_path = str(Path(private_key).expanduser())
            for cls in (RSAKey, DSSKey, ECDSAKey, Ed25519Key):
                with contextlib.suppress(paramiko.SSHException):
                    private_key = cls.from_private_key_file(pkey_path)
                    break

        if isinstance(private_key, PKey):
            self._tconnect["pkey"] = private_key
            return
        return super()._set_authentication(password, private_key, private_key_pass)


def _assert_pysftp_connection(client):
    if not isinstance(client, pysftp.Connection):
        raise TypeError("pysftp.Connection was expected")


@contextlib.contextmanager
def sftp_open(client: pysftp.Connection, remotepath: PathLike, mode="rb"):
    """Open the file via sftp connection and return the stream"""
    _assert_pysftp_connection(client)
    if mode != "rb":
        raise ValueError("only the rb open mode is supported")
    buffer = io.BytesIO()
    try:
        client.getfo(str(remotepath), buffer)
        buffer.seek(0)
        yield buffer
    finally:
        buffer.close()


def sftp_download(
    client: pysftp.Connection,
    remotepath: PathLike,
    localpath: PathLike,
) -> None:
    """Download file via sftp connection"""
    _assert_pysftp_connection(client)
    client.get(
        remotepath=str(remotepath),
        localpath=str(localpath),
        preserve_mtime=False,
    )


def sftp_download_bytes(
    client: pysftp.Connection,
    remotepath: PathLike,
) -> BinaryIO:
    _assert_pysftp_connection(client)
    buffer = io.BytesIO()
    client.getfo(str(remotepath), buffer)
    return io.BytesIO(buffer.getvalue())


def sftp_upload_bytes(
    client: pysftp.Connection,
    data: BinaryIO,
    remotepath: PathLike,
    mode: str = "0640",  # FIXME
) -> None:
    data.seek(0)
    client.putfo(data, str(remotepath), confirm=True)
    client.chmod(str(remotepath), int(mode))
