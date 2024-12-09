import re
import cryptography.x509 as x509

member_id_argument = re.compile("-override-member-id[\s=]([0-9]+)")
tls_path_argument = re.compile("-tls-path[\s=]([a-zA-Z\/]+)")
cn_re = re.compile("([0-9]+):oriond")


def resolve_user_id(config):
    if "overrideMemberId" in config:
        return config["overrideMemberId"]

    fs = open("/etc/default/oriond", "r")
    file = fs.read()
    matches = re.findall(member_id_argument, file)
    if len(matches) > 1:
        raise Exception("multiple number id overrides found")
    elif len(matches) == 0:

        tls_matches = re.findall(tls_path_argument, file)
        if len(tls_matches) > 1:
            raise Exception("multiple tls paths found")
        elif len(tls_matches) == 0:
            tls_path = "/etc/oriond/identity.pem"
        else:
            tls_path = str(matches[0])

        tls_fs = open(tls_path)
        tls_file = tls_fs.read()
        cert = x509.load_pem_x509_certificate(str.encode(tls_file))
        commonName = cert.subject.get_attributes_for_oid(x509.OID_COMMON_NAME)
        if len(commonName) > 1 or len(commonName) < 1:
            raise Exception("couldn't extract the certificate commonName")
        cn = str(commonName[0].value)
        cn_matches = re.match(cn_re, cn)
        return int(cn_matches[1])

    else:
        return int(matches[0])
