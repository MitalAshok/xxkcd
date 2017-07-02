SECURE_PROTOCOL = 'https:'
INSECURE_PROTOCOL = 'http:'

class xkcd(object):
    base = SECURE_PROTOCOL + '//xkcd.com'
    latest = base
    for_comic = (base + '/{number}').format
    class json(object):
        base = SECURE_PROTOCOL + '//xkcd.com'
        _suffix = '/info.0.json'
        latest = base + _suffix
        for_comic = (base + '/{number}' + _suffix).format
    # Or, alternatively, `http://c.xkcd.com/api-0/jsonp/comic/{number}`
    class c(object):
        base = SECURE_PROTOCOL + '//c.xkcd.com'
        class whatif:
            base = SECURE_PROTOCOL + '//c.xkcd.com/whatif'
            news = base + '/news'
    class mobile(object):
        base = SECURE_PROTOCOL + '//m.xkcd.com'
        latest = base
        for_comic = (base + '/{number}').format

class Explainxkcd(object):
    base = INSECURE_PROTOCOL + '//www.explainxkcd.com'
    latest = base
    for_comic = (base + '/{number}').format

class WhatIf(object):
    base = SECURE_PROTOCOL + '//what-if.xkcd.com'
    archive = base + '/archive/'
    latest = base
    for_article = (base + '/{number}/').format
