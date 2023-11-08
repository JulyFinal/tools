import os, re
import aria2p


# aria2 option
aria2_url = os.getenv("aria2_url")
aria2_rpc_port = os.getenv("aria2_rpc_port")


# download runner
def aria2_download(uri=""):
    aria2 = aria2p.API(aria2p.Client(host=aria2_url, port=aria2_rpc_port))

    if re.match(r"http", uri):
        aria2.add(uri=uri)
    elif re.match(r"magnet", uri):
        aria2.add_magnet(uri)
    else:
        return {"status": "cant donload type"}

    return {"status": "successful"}
