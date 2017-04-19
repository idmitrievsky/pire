#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import subprocess as sp
from tempfile import mkstemp


def skip(g, *ks):
    for k, x in enumerate(g):
        if k not in ks:
            yield x


if __name__ == '__main__':
    tmp_req_f, tmp_req_path = mkstemp()
    os.close(tmp_req_f)

    sp.check_call(['pip-compile', '--output-file', 'dev-requirements.txt', 'dev-requirements.in'])
    sp.check_call(['pip-compile', '--output-file', tmp_req_path, 'requirements.in'])

    with open(tmp_req_path) as tmp_req_f:
        with open('requirements.txt', 'w') as req_f:
            for line in skip(tmp_req_f, 6):
                print(line.rstrip(), file=req_f)

    os.remove(tmp_req_path)

    sp.check_call(['pip-sync', 'dev-requirements.txt', 'requirements.txt'])
