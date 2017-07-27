from scrapy import Spider
from scrapy.selector import Selector

import requests
from urlparse import urlparse, urljoin
import time
import random

import logging

# in case of a failed boxer name, the request for that boxer must have
# failed. Consult log file link to boxer.
logger = logging.getLogger()
logging.basicConfig(filename='spider_log', level=logging.WARNING)

n
class RandomSpider(Spider):
    """Novel stochastic approach to scraping all of the boxers. Start at prominant
    fighter, propogate recursively across his set of opponents. Assume
    relevant boxing world can be described with a single undirected
    graph. Handle closures by checking for existance in the set of scraped
    fighter urls, which are unique, an O(1) process. Mathematical
    justification for this intuition being reasonable is beyond me at the
    moment.
    """
    name = "random_spider"
    boxer_url = "http://boxrec.com/boxer"
    allowed_urls = ["http://boxrec.com/boxer"]
    start_urls = ["http://boxrec.com/boxer/1"] # needs to be updated with a set of initial boxers
    status = {"boxer" : 0, "error" : 0, "closures" : 0} # should this be somewhere else?

    def __init__(self):
        pass

    def parse(self, response):

        # unique id for boxer in the URL
        boxer_id=response.url[response.url.rfind('/')+1:]
        # popular name, not birth name
        name=response.xpath(
                '//*[@id="homeContent"]/div[1]/div/div[2]/div[4]/div[1]/h1/text()')
        # dob, stance, height, weightclass, etc
        stats=response.xpath('//*[@id="bo'+ boxer_id + '"]/div[2]/table/tr')
        # complete professional boxing record
        fights=response.xpath(
            '//*[@id="person_bout_history"]/div[6]/div/div/table/tbody')

        boxer_name = boxer_name.strip()

        boxer_stats=[]
        for stat in boxer_stats:
            # grab all stats
            # add boxer_name to fighter_stats
            pass

        boxer_fights=[]
        for fight in fights:
            # grab all fights as a table
            pass

        # yield all of boxer's info scraped from profile page
        yield {"id" : boxer_id
               "name" : boxer_name,
               "stats" : boxer_stats,
               "fights" : boxer_fights}

        database=None # fixme
        # recurse spider across opponents
        for fight in boxer_fights
            fid = fight["opponent_id"]
            if fid not in database:
                yield scrapy.Request(boxer_url+"/"+fid, callback=self.parse)
            else:
                self.status["closures"] += 1 # record that we've found a fighter we've seen

     def errback_httpbin(self, failure):
         """
         Handle request failures
         """
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)


        failed_lookups.append(failure.request.url)
