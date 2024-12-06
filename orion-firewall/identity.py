import re
import cryptography.x509 as x509

member_id_argument = re.compile("-override-member-id[\s=]([0-9]+)")
tls_path_argument = re.compile("-tls-path[\s=]([a-zA-Z\/]+)")
cn_re = re.compile("([0-9]+):oriond")

def resolve_user_id(config):
    if config["overrideMemberId"] != None:
        return config["overrideMemberId"]

    file = open("/etc/default/oriond", "r")
    # regex for override-member-id
    #
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

        tls_file = open(tls_path)
        certificates = x509.load_pem_x509_certificates(tls_file)
        for cert in certificates:
            commonName = cert.subject.get_attributes_for_oid(x509.NameOID)
            if len(commonName) > 1 and len(commonName) < 1:
                raise Exception("couldn't extract the certificate commonName")
            cn = commonName[0]
            cn_matches = re.match(cn_re, cn)
            if len(cn_matches) == 1:
                return int(cn_matches[0])
            else:
                raise Exception("unable to get certificate")

    else:
        return int(matches[0])
