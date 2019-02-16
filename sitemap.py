import datetime
from time import sleep
from urllib.parse import urlparse
from selenium import webdriver


class Crawler(object):
    def __init__(self, domain, driver="./chromedriver"):
        self.domain = domain
        self.sitemap_urls = [domain]
        self.driver = driver

    def process(self, domain=None):
        """
        Processes domain content url by url.

        :param domain: String value with protocol name http or https.
        :return: returns list of sitemap's urls.
        """
        url = domain or self.domain
        for url in self.get_urls(url):
            if url not in self.sitemap_urls:
                self.sitemap_urls.append(url)
                self.process(url)

    def is_url(self, url):
        """
        Checks if given value is an url.

        :param url: String value.
        :return: returns Boolean value.
        """
        excluded_chars = ['#']
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
            for excluded_char in excluded_chars:
                if excluded_char in url:
                    return False
            return True
        except ValueError:
            return False

    def get_urls(self, page):
        """
        Get urls from given content.

        :param page: String value representing content.
        :return: returns list of urls fetched from given content.
        """
        urls = set()

        browser = webdriver.Chrome(executable_path=self.driver)
        browser.get(page)

        sleep(2)

        for element in browser.find_elements_by_tag_name('a'):
            url = element.get_attribute('href')
            if self.is_url(url):
                urls.add(element.get_attribute('href'))

        browser.close()

        return list(urls)


class Sitemap(object):
    def __init__(self, urls, changefreq='monthly', priority=0.8, sitemap_path='sitemap.xml'):
        self.urls = urls
        self.changefreq = changefreq
        self.priority = priority
        self.sitemap_path = sitemap_path

    def process(self):
        template = '''
        <?xml version="1.0" encoding="UTF-8"?>
        {urlset}
        '''.format(urlset=self.urlset())

        with open(self.sitemap_path, 'a') as sitemap:
            sitemap.write(template)

    def url(self, loc, lastmod, changefreq, priority):
        template = '''
            <url>
                <loc>{loc}</loc>
                <lastmod>{lastmod}</lastmod>
                <changefreq>{changefreq}</changefreq>
                <priority>{priority}</priority>
            </url>
        '''.format(loc=loc, lastmod=lastmod, changefreq=changefreq, priority=priority)

        return template

    def urlset(self):
        urls = ''
        template = '''
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            {urls}
        </urlset>
        '''
        today = datetime.datetime.today().strftime('%Y-%m-%d')

        for item in self.urls:
            urls += self.url(item, today, self.changefreq, self.priority)

        return template.format(urls=urls)

def crawler(domain):
    """
    Function returns all urls included on given domain.

    :param domain: String value with protocol name http or https.
    :return: list of all urls of given domain.
    """
    instance = Crawler(domain)
    instance.process()

    return instance.sitemap_urls

def sitemap(domain):
    urls = crawler(domain)
    instance = Sitemap(urls)

    return instance.process()


if __name__ == "__main__":
    domain = "http://northmountain.pl"
    sitemap(domain)