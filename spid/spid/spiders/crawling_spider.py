from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import queryURLsv2 as query
import search
import database as db
from spid.spid.items import SpidItem
class CrawlingSpider(CrawlSpider):
    name = "spidey"
    #allowed_domains = ["whitepages.com", 'privateeye.com', '.com'
    custom_settings = {
        'FEEDS' : {
            'rawdata.json' : {'format' : 'json', 'overwrite': True},
        }
    }
    def __init__(self, search_query=None, *args, **kwargs):
        self.search_query = search_query
        self.start_urls = []
        urls = query.get_URLs_from_file("formattedSearchURLs.txt")
        for url in urls:
            moo = query.fill_in_URL(url, search_query)
            self.start_urls.append(f"{moo}")
        
        # Setting rules dynamically based on the provided search query
        self.rules = (
            Rule(LinkExtractor(allow=()), callback='parse_item', follow=True),
        )
        
        super(CrawlingSpider, self).__init__(*args, **kwargs)
        self._compile_rules()

    def parse_item(self, response):
        spid_item = SpidItem()
        document = search.Document(response.url)
        document.info = query.highlight_names2(query.extract_text_from_html2(document.url, self.search_query))
        query.updateRelevance(self.search_query, document)
        if document.info:
            db.save_document_to_db(document)
#This part of the code is where I split the yields for each website
        spid_item = SpidItem()
        site_name = response.url.split('/')[2]
        if "checkmypostcode.uk" in site_name:
            yield self.parse_checkmypostcode(response)
        elif "biography.omicsonline.org" in site_name:
            yield self.parse_biography(response)
        elif "whoseno.com" in site_name:
            yield self.parse_whoseno(response)
        elif "offenderradar.com" in site_name:
            yield self.parse_offenderradar(response)
        elif "floridareg.com" in site_name:
            yield self.parse_floridareg(response)
        elif "doximity.com" in site_name:
            yield self.parse_doximity(response)
        elif "publicrecordsnow.com" in site_name:
            yield self.parse_publicrecordsnow(response)
        elif "telephonedirectories.us" in site_name:
            yield self.parse_telephonedirectories(response)
        elif "privateeye.com" in site_name:
            yield self.parse_privateeye(response)
        elif "cityzor.com" in site_name:
            yield self.parse_cityzor(response)
        elif "realpeoplesearch.com" in site_name:
            yield self.parse_realpeoplesearch(response)
        elif "advanced-people-search.com" in site_name:
            yield self.parse_advancedpeoplesearch(response)
        elif "backgroundcheck.run" in site_name:
            yield self.parse_backgroundcheckrun(response)
        elif "backgroundalert.com" in site_name:
            yield self.parse_backgroundalert(response)
        elif "spokeo.com" in site_name:
            yield self.parse_spokeo(response)
        elif "trustoria.com" in site_name:
            yield self.parse_trustoria(response)
        elif "18ip.selfie.systems" in site_name:
            yield self.parse_18ip(response)
        elif "asksuba.com" in site_name:
            yield self.parse_asksuba(response)
        elif "bisprofiles.com" in site_name:
            yield self.parse_bisprofiles(response)
        elif "opengovwa.com" in site_name:
            yield self.parse_opengovwa(response)
        elif "whitepages.com" in site_name:
            yield self.parse_whitepages(response)
        elif "peoplefinders.com" in site_name:
            yield self.parse_peoplefinders(response)
        elif "searchpeoplefree.com" in site_name:
            yield self.parse_searchpeoplefree(response)
        elif "fastpeoplesearch.com" in site_name:
            yield self.parse_fastpeoplesearch(response)
        elif "truepeoplesearch.com" in site_name:
            yield self.parse_truepeoplesearch(response)
        elif "findpeoplesearch.com" in site_name:
            yield self.parse_findpeoplesearch(response)
        elif "anywho.com" in site_name:
            yield self.parse_anywho(response)
        elif "thatsthem.com" in site_name:
            yield self.parse_thatsthem(response)
        elif "usphonebook.com" in site_name:
            yield self.parse_usphonebook(response)
        elif "usa-people-search.com" in site_name:
            yield self.parse_usapeoplesearch(response)
        elif "cocofinder.com" in site_name:
            yield self.parse_cocofinder(response)
        elif "idcrawl.com" in site_name:
            yield self.parse_idcrawl(response)
        elif "nuwber.com" in site_name:
            yield self.parse_nuwber(response)
        elif "peekyou.com" in site_name:
            yield self.parse_peekyou(response)
        elif "telephonedirectories.us" in site_name:
            yield self.parse_telephonedirectories(response)
        elif "centeda.com" in site_name:
            yield self.parse_centeda(response)
        elif "zosearch.com" in site_name:
            yield self.parse_zosearch(response)
        elif "findagrave.com" in site_name:
            yield self.parse_findagrave(response)
        elif "reversephonecheck.com" in site_name:
            yield self.parse_reversephonecheck(response)
        elif "people-background-check.com" in site_name:
            yield self.parse_peoplebackgroundcheck(response)
        elif "curadvisor.com" in site_name:
            yield self.parse_curadvisor(response)
        elif "kwold.com" in site_name:
            yield self.parse_kwold(response)
        elif "validnumber.com" in site_name:
            yield self.parse_validnumber(response)
        elif "dataveria.com" in site_name:
            yield self.parse_dataveria(response)
        elif "councilon.com" in site_name:
            yield self.parse_councilon(response)
        elif "wellnut.com" in site_name:
            yield self.parse_wellnut(response)
        elif "verecor.com" in site_name:
            yield self.parse_verecor(response)
        elif "veriforia.com" in site_name:
            yield self.parse_veriforia(response)
        elif "virtory.com" in site_name:
            yield self.parse_virtory(response)
        elif "quickpeopletrace.com" in site_name:
            yield self.parse_quickpeopletrace(response)
        else:
            self.logger.warning(f"No parsing method for site: {site_name}")
#THIS IS WHERE THE DATA IS YIELDED

    def parse_checkmypostcode(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['postcode']: response.css('div.postcode::text').get()
        }
        yield data

    def parse_biography(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.profile-header h1::text').get(),
            SpidItem['bio']: response.css('div.bio-content p::text').getall()
        }
        yield data

    def parse_whoseno(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_offenderradar(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_floridareg(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h2::text').get(),
            SpidItem['details']: response.css('div.details::text').getall()
        }
        yield data

    def parse_doximity(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.profile-name::text').get(),
            SpidItem['specialty']: response.css('div.profile-specialty::text').getall()
        }
        yield data

    def parse_publicrecordsnow(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.person-name h1::text').get(),
            SpidItem['address']: response.css('div.address p::text').get()
        }
        yield data

    def parse_telephonedirectories(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.person-name h1::text').get(),
            SpidItem['phone']: response.css('div.phone-number p::text').get()
        }
        yield data

    def parse_privateeye(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.person-name::text').get(),
            SpidItem['address']: response.css('div.address p::text').getall()
        }
        yield data

    def parse_cityzor(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h2::text').get(),
            SpidItem['details']: response.css('div.details p::text').getall()
        }
        yield data

    def parse_realpeoplesearch(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_advancedpeoplesearch(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_backgroundcheckrun(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_backgroundalert(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_spokeo(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_trustoria(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['details']: response.css('div.details p::text').getall()
        }
        yield data

    def parse_18ip(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['phone']: response.css('div.phone-number p::text').get()
        }
        yield data

    def parse_asksuba(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_bisprofiles(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['details']: response.css('div.details p::text').getall()
        }
        yield data

    def parse_opengovwa(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_whitepages(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_peoplefinders(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_searchpeoplefree(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_fastpeoplesearch(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_truepeoplesearch(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_findpeoplesearch(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['address']: response.css('div.address p::text').getall()
        }
        yield data

    def parse_anywho(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_thatsthem(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_usphonebook(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_usapeoplesearch(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['address']: response.css('div.address p::text').getall()
        }
        yield data

    def parse_cocofinder(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_idcrawl(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_nuwber(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_peekyou(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_centeda(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['details']: response.css('div.details p::text').getall()
        }
        yield data

    def parse_zosearch(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['phone']: response.css('div.phone-number p::text').get()
        }
        yield data

    def parse_findagrave(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_reversephonecheck(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['phone']: response.css('div.phone-number p::text').get()
        }
        yield data

    def parse_peoplebackgroundcheck(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_curadvisor(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['details']: response.css('div.details p::text').getall()
        }
        yield data

    def parse_kwold(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['phone']: response.css('div.phone-number p::text').get()
        }
        yield data

    def parse_validnumber(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['phone']: response.css('div.phone-number::text').get()
        }
        yield data

    def parse_dataveria(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_councilon(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['details']: response.css('div.details p::text').getall()
        }
        yield data

    def parse_wellnut(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_verecor(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['details']: response.css('div.details p::text').getall()
        }
        yield data

    def parse_veriforia(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('h1.name::text').get(),
            SpidItem['address']: response.css('div.address::text').getall()
        }
        yield data

    def parse_virtory(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['phone']: response.css('div.phone-number p::text').get()
        }
        yield data

    def parse_quickpeopletrace(self, response):
        data = {
            SpidItem["url"]: response.url,
            SpidItem['name']: response.css('div.name h1::text').get(),
            SpidItem['details']: response.css('div.details p::text').getall()
        }
        yield data
        yield SpidItem



#code GRAVEYARD
        # address = response.css("div.addressline-1").get()
        # relative = response.css("div.size-aware-h5.fw-m.primary--text").get()
        # firstName = response.css("div.addressline-1").get()
        # middleName = response.css("div.addressline-1").get()
        # lastName = response.css("div.addressline-1").get()
        # birthDay = response.css("div.addressline-1").get()
        # birthMonth = response.css("div.addressline-1").get()
        # birthYear = response.css("div.addressline-1").get()
        # phone = response.css("div.addressline-1").get()
        # age = response.css("div.addressline-1").get()
        # street = response.css("div.addressline-1").get()
        # city = response.css("div.addressline-1").get()
        # aprt = response.css("div.addressline-1").get()
        # hometown = response.css("div.addressline-1").get()
        # relative =  response.css("div.addressline-1").get()

        # yield {
        #     "url": response.url,
        #     "address": address,
        #     "relative": relative,
        # }
