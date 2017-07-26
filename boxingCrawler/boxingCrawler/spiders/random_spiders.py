from scrapy import Spider
from scrapy.selector import Selector

import requests
from urlparse import urlparse, urljoin
import time
import random

import logging

# in case of a failed region name, the request for that region must have
# failed. Consult log file link to region.
logger = logging.getLogger()
logging.basicConfig(filename='spider_log', level=logging.WARNING)


class RandomSpider(Spider):
    """
    Novel stochastic approach to scraping all of the boxers. start at
    prominant fighter, propogate recursively across his set of
    opponents. Assume relevant boxing world can be described with a single
    undirected graph. Handle closures by checking for existance in the set of
    fighter urls.
    """
    name = "random_spider"
    allowed_urls = ["http://boxrec.com/boxer"]
    start_urls = ["http://boxrec.com/boxer/1"] # needs to be updated with a set of initial boxers

    def __init__(self):
        pass

    def parse(self, response):
        usa_territories = self._parse_continent(response)

        num_regions = sum(map(lambda t: len(t[1]), usa_territories))
        print("Regions to scrape: {0:,}".format(num_regions))
        time.sleep(3)

        regions_scraped = 0
        regions_missed = 0
        for terr_name, region_links in usa_territories:
            for link in region_links:
                region = {"name": None, "posts": []}
                scraped = False
                attempts = 0
                # make three attempts to make scrape region
                while(~scraped and attempts <= 3):
                    try:
                        region = RegionSpider._get_posts(link)
                        scraped = True
                    except requests.ConnectionError:
                        logger.warn(
                            "Connection failure while requesting '%s'", link)
                        print "Waiting in response to connection failure..."
                        time.sleep(20)
                    attempts += 1
                if scraped:
                    regions_scraped += 1
                else:
                    regions_missed += 1
                print ("region {0:,}/{1:,} {2} at " +
                       "'{3}'").format(regions_scraped,
                                       num_regions,
                                       "scraped" if scraped else "missed",
                                       link)

                yield {"state": terr_name, "region": region}

        print ("\n\n{0:,}/{1,:} regions successfully " +
               "extracted. See logs for " +
               "failures.\n\n").format(regions_scraped, num_regions)

    @staticmethod
    def _get_posts(link):
        """
        Return the list of posts for the politics section for region at link.
        If region has subregions, return a list of results for those instead.
        """
        def structure((ps, sr_name)):
            return map(lambda p: {'entry': p, 'subregion': sr_name}, ps)

        region_banner = Selector(text=RegionSpider._get_content(link)).xpath(
            '//*[@id="topban"]/div[1]')
        region_name = region_banner.xpath('h2/text()')[0].extract()

        pol = urljoin(link, "/search/pol")
        subregions = region_banner.xpath('ul/li')
        if subregions:
            def make_link(ps):
                # there's definitely a cleaner way to build this url
                path = ps.xpath('a/@href').extract()[0].replace("/", "")
                return pol.replace("/search/", "/search/" + path + "/")

            def get_name(ps):
                return ps.xpath('a/@title').extract()[0]

            subregion_names = map(get_name, subregions)
            pol_links = map(make_link, subregions)
            postings = map(RegionSpider._grab_posts, pol_links)

            # flatten subregion postings
            posts = sum(map(structure, zip(postings, subregion_names)), [])
        else:
            posts = structure((RegionSpider._grab_posts(pol), None))

        return {'name': region_name, 'posts': posts}

    @staticmethod
    def _get_content(link):
        """
        Politely request the page content at link.
        """
        content = requests.get(link).text

        x = 3 + 2 * random.random()
        time.sleep(x)

        return content
