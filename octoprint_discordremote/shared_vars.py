#Used for accessing variables across classes when imports are not viable


base_url = ""
prefix = ""


def init_baseurl(bu):
    global base_url
    base_url = bu


def init_prefix(p):
    global prefix
    prefix = p
