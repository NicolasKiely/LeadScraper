import bs4
import typing
import urllib.parse

from article.article import BaseArticle
from article.doi import DoiArticle
from article.plos import PlosOneArticle
import author.author


#: Pubmed archive file name template
PUBMED_ARCHIVE_NAME = 'archive/pubmed_%s.gzip'
PUBMED_URL = 'https://www.ncbi.nlm.nih.gov/pubmed/%s'


JOURNAL_LOOKUP = {
    'doi.org': DoiArticle,
    'dx.plos.org': PlosOneArticle
}


def process_dl_list(dl):
    id_info_map = {}
    last_key = -1
    for item in dl.children:
        if item.name == 'dt' or item.name == u'dt':
            last_key = item.string
        else:
            id_info_map[last_key] = item.string
    return id_info_map


def process_auth_list(auths_div):
    id_auth_map = []
    last_name = ''
    for item in auths_div.children:
        if item.name == 'a' or item.name == u'a':
            last_name = item.string
        elif item.name == 'sup' or item.name == u'sup':
            id_auth_map.append((item.string, last_name))
    return id_auth_map


def get_email(record):
    fields = [s.strip() for s in record.split(' ')]
    for field in fields:
        if '@' in field:
            if field[0] != '@' and field[-1] != '@':
                return field
    return ''


def get_first_last_name(name_field):
    names = name_field.split(' ', 1)
    if len(names) == 1:
        return '', names[0]
    else:
        return names[1], names[0]


class PubmedArticle(BaseArticle):
    """ Processor for pubmed articles """
    def get_journal(self) -> str:
        return ''

    def get_url(self) -> str:
        return PUBMED_URL % self._pmid

    def _get_archive_name(self) -> str:
        return PUBMED_ARCHIVE_NAME % self._pmid

    def _get_authors(
            self, doc_page: bs4.BeautifulSoup
    ) -> typing.List[author.author.Author]:
        auth_list_divs = doc_page.find_all(class_='auths')
        auth_names = None

        if len(auth_list_divs) > 0:
            auth_list_div = auth_list_divs[0]
            auth_names = process_auth_list(auth_list_div)

        auth_info_divs = doc_page.find_all(class_='afflist')
        auth_info = None
        if len(auth_info_divs) > 0:
            auth_info_div = auth_info_divs[0]
            auth_info = process_dl_list(auth_info_div.dl)

        if auth_names is None or auth_info is None:
            return []

        authors = []
        for auth_id, auth_name in auth_names:
            article_author = author.author.Author()
            auth_info_str = auth_info.get(auth_id, '')
            article_author.email = get_email(auth_info_str)
            first_name, last_name = get_first_last_name(auth_name)
            article_author.first_name = first_name
            article_author.last_name = last_name
            article_author.source_article = self
            article_author.extra = auth_info_str

            authors.append(article_author)

        auth_list = [a for a in authors if a.email]
        if len(auth_list) == 0:
            if len(authors) > 0:
                return [authors[-1]]
            else:
                return []
        else:
            return auth_list

    def get_linked_journals(
            self, doc_page: bs4.BeautifulSoup
    ) -> typing.List[BaseArticle]:
        portlets = doc_page.find_all(class_='icons portlet')[0]
        for portlet in portlets.children:
            if portlet.name == 'a':
                source_url = portlet['href']
                parsed_url = urllib.parse.urlparse(source_url)
                url_host = parsed_url.netloc

                if url_host in JOURNAL_LOOKUP:
                    article = JOURNAL_LOOKUP[url_host](self._pmid, source_url)
                    return [article]

        return []
