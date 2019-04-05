import typing


class Author(object):
    """ Represents an author """
    def __init__(self):
        self._first_name = None
        self._last_name = None
        self._email = None
        self._article = None
        self._extra = None

    @property
    def first_name(self) -> str:
        return self.as_string(self._first_name)

    @first_name.setter
    def first_name(self, first_name: str):
        self._first_name = first_name

    @property
    def last_name(self) -> str:
        return self.as_string(self._last_name)

    @last_name.setter
    def last_name(self, last_name: str):
        self._last_name = last_name

    @property
    def email(self) -> str:
        return self.as_string(self._email)

    @email.setter
    def email(self, email: str):
        self._email = email

    @property
    def source_article(self):
        return self._article

    @source_article.setter
    def source_article(self, source):
        self._article = source

    @property
    def journal(self) -> str:
        if self._article:
            return self._article.get_journal()
        else:
            return ''

    @property
    def source_url(self) -> str:
        if self._article:
            return self._article.get_url()
        else:
            return ''

    @property
    def extra(self) -> str:
        return self.as_string(self._extra)

    @extra.setter
    def extra(self, extra: str):
        self._extra = extra

    @staticmethod
    def as_string(field: typing.Optional[str]) -> str:
        """ Returns field if defined, or empty string """
        if field is None:
            return ''
        else:
            return field
