from collections import defaultdict

from django.contrib.sitemaps import Sitemap
from django.db.models import Q

from cms.models import PageContent, PageUrl
from cms.utils import get_current_site
from cms.utils.i18n import get_public_languages


def from_iterable(iterables):
    """
    Backport of itertools.chain.from_iterable
    """
    for it in iterables:
        for element in it:
            yield element


class CMSSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        #
        # It is counter-productive to provide entries for:
        #   > Pages which redirect:
        #       - If the page redirects to another page on this site, the
        #         destination page will already be in the sitemap, and
        #       - If the page redirects externally, then it shouldn't be
        #         part of our sitemap anyway.
        #   > Pages which cannot be accessed by anonymous users (like
        #     search engines are).
        #
        # It is noted here: http://www.sitemaps.org/protocol.html that
        # "locations" that differ from the place where the sitemap is found,
        # are considered invalid. E.g., if your sitemap is located here:
        #
        #     http://example.com/sub/sitemap.xml
        #
        # valid locations *must* be rooted at http://example.com/sub/...
        #
        # This rules any redirected locations out.
        #
        # If, for some reason, you require redirecting pages (PageContent) to be
        # included, simply create a new class inheriting from this one, and
        # supply a new items() method which doesn't filter out the redirects.
        site = get_current_site()
        languages = get_public_languages(site_id=site.pk)
        all_urls = (
            PageUrl
            .objects
            .get_for_site(site)
            .select_related('page')
            .filter(language__in=languages, path__isnull=False, page__login_required=False)
            .order_by('page__node__path')
        )
        excluded_titles_by_page = defaultdict(set)
        excluded_translations = (
            PageContent
            .objects
            .filter(language__in=languages, page__node__site=site)
            .exclude(Q(redirect='') | Q(redirect__isnull=True))
            .values_list('page', 'language')
        )

        for page_id, language in excluded_translations:
            excluded_titles_by_page[page_id].add(language)

        valid_urls = []

        for page_url in all_urls:
            excluded = excluded_titles_by_page.get(page_url.page_id, [])

            if page_url.language in excluded:
                continue
            valid_urls.append(page_url)
        return valid_urls

    def lastmod(self, page_url):
        return page_url.page.changed_date

    def location(self, page_url):
        return page_url.get_absolute_url(page_url.language)
