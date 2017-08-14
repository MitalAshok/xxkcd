__all__ = ('xkcd', 'explain_xkcd', 'what_if')

SECURE_PROTOCOL = 'https:'
INSECURE_PROTOCOL = 'http:'


class Constantsxkcd(object):
    base = SECURE_PROTOCOL + '//xkcd.com'
    with_subdomain = (SECURE_PROTOCOL + '//{subdomain}.xkcd.com').format
    latest = base
    for_comic = (base + '/{number}/').format


class ConstantsxkcdJSON(object):
    base = Constantsxkcd.base
    suffix = '/info.0.json'
    latest = base + suffix
    for_comic = (base + '/{number}' + suffix).format
    # Or, alternatively, `http://c.xkcd.com/api-0/jsonp/comic/{number}`


class ConstantsxkcdC(object):
    base = Constantsxkcd.with_subdomain(subdomain='c')


class ConstantsxkcdCWhatIf(object):
    base = ConstantsxkcdC.base + '/whatif'
    news = base + '/news'


class ConstantsxkcdMobile(object):
    base = Constantsxkcd.with_subdomain(subdomain='m')
    latest = base
    for_comic = (base + '/{number}/').format


class ConstantsxkcdImages(object):
    base = Constantsxkcd.with_subdomain(subdomain='imgs') + '/comics'
    for_image = (base + '/{image}').format
    blank = base + '/'


class ConstantsExplainxkcd(object):
    base = INSECURE_PROTOCOL + '//www.explainxkcd.com'
    latest = base
    for_comic = (base + '/{number}').format


class ConstantsWhatIf(object):
    base = Constantsxkcd.with_subdomain(subdomain='what-if')
    archive = base + '/archive/'
    latest = base
    for_article = (base + '/{number}/').format


xkcd = Constantsxkcd()
xkcd.json = ConstantsxkcdJSON()
xkcd.c = ConstantsxkcdC()
xkcd.c.what_if = ConstantsxkcdCWhatIf()
xkcd.mobile = ConstantsxkcdMobile()
xkcd.images = ConstantsxkcdImages()

explain_xkcd = ConstantsExplainxkcd()

what_if = ConstantsWhatIf()
