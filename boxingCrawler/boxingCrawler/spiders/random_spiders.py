from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

import requests
import random

import logging

# in case of a failed boxer name, the request for that boxer must have
# failed. Consult log file link to boxer.
logger = logging.getLogger()
logging.basicConfig(filename='spider_log', level=logging.WARNING)

class RandomSpider(CrawlSpider):
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
    allowed_urls = [boxer_url]
    start_urls = [boxer_url + "/348759"] # canelo alverez
    state = {
        "boxers" : {},           # boxer count by weight class
        "request errors" : 0,    # boxer request error count
        "closures" : 0,          # cyclic closure count
        "total closures" : 0,    # 'fighters with no unseen opponents' count
        "ftable dim errors" : 0, # unexpected fight table dimension count
        }

    rules = (
        # follow a fighters opponents
        # check regexp and link
        Rule(LinkExtractor(allow=('//bo[0-9]+'), restrict_xpaths='//*[@id="person_bout_history"]/div[6]/div/div/table/tbody'),
                 callback=parse_boxer, follow=True)
        )

    # should this be somewhere else?
    expected_ftable_dim=11
    ftable_failure_threshold=0.005 # 0.5%

    def __init__(self):
        pass

    def parse_boxer(self, response):
        # print status every 100 boxers
        if sum(state.boxers.values()) % 100 == 0:
            self.print_state()

        # popular name, not birth name
        name=response.xpath(
                '//*[@id="homeContent"]/div[1]/div/div[2]/div[4]/div[1]/h1/text()')
        # dob, stance, height, weightclass, etc
        stats=response.xpath('//*[@id="bo'+ boxer_id + '"]/div[2]/table/tr')
        # complete professional boxing record
        fights=response.xpath(
            '//*[@id="person_bout_history"]/div[6]/div/div/table/tbody')


        boxer_name = name.strip()
        boxer_id = grab_boxer_id(response.url) # unique id for boxer from URL
        boxer_stats=[]
        boxer_fights=[]

        # build boxer stats
        for stat in stats:
            # grab all stats
            # will use a dict of callbacks, indexed by stats table entry name
            # add boxer_name to fighter_stats
            pass

        # build boxer_fights
        if len(fights) != expected_ftable_dim: # check fight table dimensions
            self.state["ftable dim errors"] += 1
            # log error
            if not self.acceptable_ftable_errors():
                # log failure
                # raise exception
                pass
        else:
            fights = [f.xpath('tr[1]/td') for f in fights]
            for fight in fights:
                # grab all fights as a table
                # fight[0] = index
                # fight[1] = date/calander
                # fight[2] = opponent name/link
                # fight[3] = opponent record
                # fight[4] = location
                # fight[5] = result?
                # fight[6] = ?
                # fight[7] = ?
                # fight[8] = ?
                # fight[9] = ?
                # fight[10] = ?
                pass

        # update state after successfully yielding the boxer to database
        # 'some weightclass' comes from boxer_stats
        self.state['boxers']["some weightclass"] = self.state['boxers'].get("some wc", 0) + 1

        # yield all of boxer's info scraped from profile page
        yield {"id" : boxer_id
               "name" : boxer_name,
               "stats" : boxer_stats,
               "fights" : boxer_fights}

    @static
    def grab_boxer_id(url):
            return url[url.rfind('/')+1:]


    def process_links(self, links):
        """Used in rule for extracting opponents from fighters boxrec page.  Don't
        include duplicate fighters, don't include fighters already seen.
        """
        database=[]

        # database=None # fixme
        # num_closures=0
        # # recurse spider across opponents
        # for fight in boxer_fights
        #     fid = fight["opponent_id"]
        #     if fid not in database:
        #         closures += 1
        #         yield scrapy.Request(boxer_url+"/"+fid, callback=self.parse)
        #     else:
        #         self.state["closures"] += 1 # record that we've found a fighter we've seen

        # # record when a fighter has no unseen opponents
        # # this means we've bottomed out on this depth-first traversal
        # if num_closures = len(boxer_fights):
        #     self.state["total closures"] += 1

        return [link for link in set(links) if link in database]



    def print_state(self):
        # print number closures, boxers, errors, etc
        # called infrequently to give snapshot of traversal pattern
        pass

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

    def acceptable_ftable_errors(self):
        # if greater than some number of fighters so far and greater beyond
        # some threshold of error percentages, return false. Else, true
        pass
