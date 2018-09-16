import random, string, re, os
import logging

# try:
from models.codius_vars import CodiusVariables
from settings.config import CODIUS_CONF

# except:
#     pass

logger = logging.getLogger(__name__)


def rnd_servname(n):
    return "server_" + rnd_string(n)


def rnd_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def get_codius_vars():
    used_vars = []
    try:
        with open(CODIUS_CONF, 'r') as myfile:
            data = myfile.read()

            for var in CodiusVariables:
                m = re.search(f'{var.name}=(.*)(?:\"|\'|\t|\ )', data)
                if m and not any(var.name == d['name'] for d in used_vars):
                    used_vars.append({'name': var.name, 'value': m.group(1)})

            return used_vars
    except Exception as e:
        logger.error(e)
        pass


def get_fee():
    try:
        with open(CODIUS_CONF, 'r') as myfile:
            data = myfile.read().replace('\n', '')

        regexList = ['CODIUS_COST_PER_MONTH=([0-9]+)', 'COST_PER_MONTH=([0-9]+)', 'CODIUS_XRP_PER_MONTH=([0-9]+)']
        gotMatch = False
        for regex in regexList:
            m = re.search(re.compile(regex), data)
            if m:
                gotMatch = True
                break

        if gotMatch:
            return int(m.group(1))
    except Exception as e:
        logger.error(e)
        pass


def set_fee_in_codiusconf(fee):
    try:
        with open(CODIUS_CONF) as f:
            newText = re.sub('CODIUS_XRP_PER_MONTH=[0-9]+', f'CODIUS_XRP_PER_MONTH={str(fee)}', f.read(), re.MULTILINE)
            newText = re.sub('CODIUS_COST_PER_MONTH=[0-9]+', f'CODIUS_COST_PER_MONTH={str(fee)}', newText, re.MULTILINE)
            newText = re.sub('COST_PER_MONTH=[0-9]+', f'COST_PER_MONTH={str(fee)}', newText, re.MULTILINE)

        with open(CODIUS_CONF, "w") as f:
            f.write(newText)

        return {'success': True, 'body': 'success'}
    except Exception as ex:
        logger.error(ex)
        return {'success': False, 'body': ex}


def set_variables_in_codiusconf(vars):
    try:
        with open(CODIUS_CONF) as f:
            data = f.read()

            for v in vars:
                if v['delete']:
                    lines = data.splitlines()
                    for l in lines:
                        if v['name'] in l:
                            lines.remove(l)
                    data = '\n'.join(lines)
                if len(v['name']) > 0 and not v['delete']:
                    p = f'{v["name"]}=(.*)(?:\"|\'|\t|\ )'
                    val = v["value"].strip('\"').strip('\'')
                    m = re.search(p, data, re.MULTILINE)
                    if m:
                        data = re.sub(p, f'{v["name"]}={val}\"', data, re.MULTILINE)
                    else:
                        lines = data.splitlines()
                        last_env_str = max(loc for loc, val in enumerate(lines) if "environment" in val.lower())
                        lines.insert(last_env_str+1, 'Environment=\"{}={}\"'.format(v["name"], val))
                        data = '\n'.join(lines)


        with open(CODIUS_CONF, "w") as f:
            f.write(data)

        return {'success': True, 'body': 'success'}
    except Exception as ex:
        logger.error(ex)
        return {'success': False, 'body': ex}


class Dict2Obj(object):
    """
    Turns a dictionary into a class
    """

    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])


if __name__ == "__main__":
    print(get_codius_vars())
