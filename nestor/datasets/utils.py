import requests
from pathlib import Path
from .. import get_nestor_cache_dir


def download_datafile(url: str, filename: str, overwrite: bool = False) -> Path:
    """If needed, send a request to a url to download data (e.g. csv)

    This does not check if the data url matches the past, only whether the given
    filename already exists or not.
    (See: [DVC.org](dvc.org) for a more sophisticated implementation, which *may* be utilized in the future)

    If `overwrite` is true, a fresh copy of the data will always be downloaded to overwrite an existing file.

    returns: location on-disk of the cached data file.
    """

    datapath: Path = get_nestor_cache_dir() / "data" / filename

    if (not datapath.is_file()) or overwrite:
        response = requests.get(url)
        datapath.parent.mkdir(exist_ok=True, parents=True)
        datapath.write_bytes(response.content)

    return datapath
