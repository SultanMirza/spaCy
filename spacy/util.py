import os
import io
import json
import re
import os.path
import pathlib

import six
import sputnik
from sputnik.dir_package import DirPackage
from sputnik.package_list import (PackageNotFoundException,
                                  CompatiblePackageNotFoundException)
import pathlib

from . import about
from .attrs import TAG, HEAD, DEP, ENT_IOB, ENT_TYPE


LANGUAGES = {}


def set_lang_class(name, cls):
    global LANGUAGES
    LANGUAGES[name] = cls


def get_lang_class(name):
    lang = re.split('[^a-zA-Z0-9_]', name, 1)[0]
    if lang not in LANGUAGES:
        raise RuntimeError('Language not supported: %s' % lang)
    return LANGUAGES[lang]


def get_package(data_dir):
    return data_dir
    #if not isinstance(data_dir, six.string_types):
    #    raise RuntimeError('data_dir must be a string')
    #return DirPackage(data_dir)


def get_package_by_name(name=None, via=None):
    lang = get_lang_class(name)
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    data_dir = pathlib.Path(data_dir)
    return data_dir / lang.lang
    #try:
    #    return sputnik.package(about.__title__, about.__version__,
    #        name, data_path=via)
    #except PackageNotFoundException as e:
    #    raise RuntimeError("Model '%s' not installed. Please run 'python -m "
    #                       "%s.download' to install latest compatible "
    #                       "model." % (name, lang.__module__))
    #except CompatiblePackageNotFoundException as e:
    #    raise RuntimeError("Installed model is not compatible with spaCy "
    #                       "version. Please run 'python -m %s.download "
    #                       "--force' to install latest compatible model." %
    #                       (lang.__module__))


def normalize_slice(length, start, stop, step=None):
    if not (step is None or step == 1):
        raise ValueError("Stepped slices not supported in Span objects."
                         "Try: list(tokens)[start:stop:step] instead.")
    if start is None:
       start = 0
    elif start < 0:
       start += length
    start = min(length, max(0, start))

    if stop is None:
       stop = length
    elif stop < 0:
       stop += length
    stop = min(length, max(start, stop))

    assert 0 <= start <= stop <= length
    return start, stop


def utf8open(loc, mode='r'):
    return io.open(loc, mode, encoding='utf8')


def align_tokens(ref, indices): # Deprecated, surely?
    start = 0
    queue = list(indices)
    for token in ref:
        end = start + len(token)
        emit = []
        while queue and queue[0][1] <= end:
            emit.append(queue.pop(0))
        yield token, emit
        start = end
    assert not queue


def detokenize(token_rules, words): # Deprecated?
    """To align with treebanks, return a list of "chunks", where a chunk is a
    sequence of tokens that are separated by whitespace in actual strings. Each
    chunk should be a tuple of token indices, e.g.

    >>> detokenize(["ca<SEP>n't", '<SEP>!'], ["I", "ca", "n't", "!"])
    [(0,), (1, 2, 3)]
    """
    string = ' '.join(words)
    for subtoks in token_rules:
        # Algorithmically this is dumb, but writing a little list-based match
        # machine? Ain't nobody got time for that.
        string = string.replace(subtoks.replace('<SEP>', ' '), subtoks)
    positions = []
    i = 0
    for chunk in string.split():
        subtoks = chunk.split('<SEP>')
        positions.append(tuple(range(i, i+len(subtoks))))
        i += len(subtoks)
    return positions
