import random, string, re
import fileinput
import logging, traceback

# try:
from settings.config import CODIUS_CONF
# except:
#     pass

logger = logging.getLogger(__name__)


def rnd_servname(n):
    return "server_" + rnd_string(n)


def rnd_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def get_fee():
    try:
        with open(CODIUS_CONF, 'r') as myfile:
            data = myfile.read().replace('\n', '')

        p = re.compile('CODIUS_XRP_PER_MONTH=([0-9]+)')
        m = p.search(data)

        return int(m.group(1))
    except Exception as e:
        logger.error(e)
        pass


def set_fee_in_codiusconf(fee):
    try:
        with open(CODIUS_CONF) as f:
            newText = re.sub('CODIUS_XRP_PER_MONTH=[0-9]+', f'CODIUS_XRP_PER_MONTH={str(fee)}', f.read(), re.MULTILINE)

        with open(CODIUS_CONF, "w") as f:
            f.write(newText)
    except Exception as ex:
        traceback.print_exc(ex)

if __name__ == "__main__":
    print(set_fee_in_codiusconf(74))
