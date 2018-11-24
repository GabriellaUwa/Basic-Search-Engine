class Page():

    LINK_DICT = None
    CONTENT = None

    def set_content(self, content):

        """

        :param content: Is a dict of page info already counted
        :return:
        """
        self.CONTENT = content

    def set_links(self, links):

        """

        :param links: links is a list of links
        :return:
        """
        self.LINK_DICT = links

    def get_links(self):

        """

        :return: list of of links
        """
        return self.LINK_DICT

    def get_content(self):

        """

        :return: Counter object containing page content with number of occurrences
        """
        return self.CONTENT