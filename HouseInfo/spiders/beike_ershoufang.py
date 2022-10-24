import scrapy
from HouseInfo.items import HouseinfoItem
import time

districtDic = {
    'dongcheng': '东城', 
    'xicheng': '西城', 
    'chaoyang': '朝阳', 
    'haidian': '海淀', 
    'fengtai': '丰台', 
    'shijingshan': '石景山', 
    'tongzhou': '通州', 
    'changping': '昌平', 
    'daxing': '大兴', 
    'yizhuangkaifaqu': '亦庄开发区', 
    'shunyi': '顺义', 
    'fangshan': '房山', 
    'mentougou': '门头沟', 
    'pinggu': '平谷', 
    'huairou': '怀柔', 
    'miyun': '密云', 
    'yanqing': '延庆' 
}

district_time_base = 2000

sub_district_time_base = 200

sub_district_page_time_base = 10

class BeikeErshoufangSpider(scrapy.Spider):
    name = 'beike-ershoufang'
    allowed_domains = ['bj.ke.com']

    def start_requests(self):
        size = 0
        for key in districtDic.keys():
            me = {'delay_request_by': 5}
            yield scrapy.Request('http://bj.ke.com/ershoufang/{}'.format(key), self.districtPage, meta= me)
            size = size + 1
            # TODO 删了
            #return

    def districtPage(self, response):
        try:
            district = response.url.split("/")[4]
            self.logger.info("districtPage district:%s", district)
        except Exception as e:
            self.logger.error(e)
        subDistrictResultList = response.css('dd div > a') 
        size = 0
        for subDistrict in subDistrictResultList:
            urlPath = subDistrict.xpath("@href").extract_first()
            if ("ershoufang" in urlPath):
                isCity = False
                for key in districtDic.keys():
                    isCity = (("/" + key + "/") in urlPath)
                    if isCity:
                        self.logger.info("districtPage urlPath:%s is district", urlPath)
                        break
                if not isCity:
                    subDistrict = urlPath.split("/")
                    try:
                        subDistrictUrl = 'http://bj.ke.com/ershoufang/{}'.format(subDistrict[2])
                        self.logger.info("districtPage urlPath:%s is subDistrict, subDistrictUrl:%s to be crawl", urlPath, subDistrictUrl)
                        me = {'delay_request_by': 6}
                        yield scrapy.Request(subDistrictUrl, self.subDistrictPage, meta=me)
                        size = size + 1
                        # TODO 删了
                        # return
                    except Exception as e:
                        self.logger.error(e)
            else:
                self.logger.info("districtPage urlPath:%s not ershoufang", urlPath)
        
    def subDistrictPage(self, response):
        try:
            subDistrict = response.url.split("/")[4]
            self.logger.info("subDistrictPage subDistrict:%s", subDistrict)
        except Exception as e:
            self.logger.error(e)
        houseSize = response.css('.leftContent > div > .clear > .fl > span::text').get()
        pageSize = int(int(houseSize) / 30) + 1
        self.logger.info("板块：" + subDistrict + "，房屋数量：" + str(houseSize) + "，房屋页数：" + str(pageSize))
        size = 0
        for i in range(1, (pageSize + 1)):   
            subDistrictSubPageUrl = 'http://bj.ke.com/ershoufang/' + subDistrict + "/pg" + str(i)
            me = {'delay_request_by': 7}
            yield scrapy.Request(subDistrictSubPageUrl, self.subDistrictSubPage, meta= me)
            size = size + 1
            # TODO 删了
            # return
    
    def subDistrictSubPage(self, response):
        try:
            subDistrictSubPage = response.url.split("/")[4]
            self.logger.info("subDistrictSubPage subDistrictSubPageUrl:%s", subDistrictSubPage)
        except Exception as e:
            self.logger.error(e)
        priceItems = response.css('.totalPrice2 > span')
        self.logger.info("subDistrictSubPage priceItems:%s", priceItems)
        index = 0
        for eachHouseInfo in response.css('.title > .maidian-detail'):
            houseUrl = eachHouseInfo.xpath("@href").extract_first()
            houseUrlSplitResultList = houseUrl.split("/")
            roomId = houseUrlSplitResultList[len(houseUrlSplitResultList) - 1].split(".")[0]
            price = float(priceItems[index].xpath("text()").extract_first()) * 10000
            self.logger.info("subDistrictSubPage houseUrl:%s, roomId:%s, price:%i", houseUrl, roomId, price)
            index = index + 1
            objectId = ""
            if (objectId == ""):
                self.logger.info("subDistrictSubPage is new house")
                yield scrapy.Request(houseUrl, self.detail_page)
            else:   
                self.logger.info("subDistrictSubPage is old house")
            # TODO 删了
            # return

    def detail_page(self, response):
        splitResult = response.url.split("/")
        roomId = splitResult[len(splitResult) - 1].split(".")[0]
        districtInfo = response.css('.info > a').xpath("text()").extract_first()
        isOnline = response.css('.main > span').xpath("text()").extract_first()
        districtResult = districtInfo.split(" ")
        subDistrict = ""
        if(len(districtResult) > 1):
            subDistrict = districtResult[1]
        normalInfoResult = response.css('.base li').xpath("text()").extract_first().split(" ")
        businessInfoResult = response.css('.base li').xpath("text()").extract_first().split(" ")
        realArea = 0 
        hasElevator = False
        for info in normalInfoResult:
            if ("套内面积" in info):
                try:
                    realArea = float(info.replace("套内面积", "").replace("㎡", ""))
                except Exception as e:
                    self.logger.error(e)
            if ("配备电梯" in info):
                hasElevator = True
        businessInfoResult = response.css('.transaction li')
        lastBusinessTime = ""
        currentBusinessTime = ""
        businessOwner = ""
        ownership = ""
        houseUsage = ""
        mortgageInfo = ""
        houseSellTime = ""
        for infoE in businessInfoResult:
            info = infoE.get()
            self.logger.info("subDistrictSubPage infoE:%s", info)
            if ("挂牌时间" in info):
                currentBusinessTime = infoE.xpath("text()").extract_first()
            if ("上次交易" in info):
                lastBusinessTime = infoE.xpath("text()").extract_first()
            if ("交易权属" in info):
                businessOwner = infoE.xpath("text()").extract_first()
            if ("产权所属" in info):
                ownership = infoE.xpath("text()").extract_first()
            if ("房屋用途" in info):
                houseUsage = infoE.xpath("text()").extract_first()
            if ("抵押信息" in info):
                mortgageInfo = infoE.xpath("text()").extract_first()
            if ("房屋年限" in info):
                houseSellTime = infoE.xpath("text()").extract_first()
                # 是否有电梯
        span = response.css('.unit > span').xpath("text()").extract_first()
        spanN = 10000
        if("万" == span):
            spanN = 10000
        totalPrice = 0.0
        try:
            totalPrice = float(response.css('.total').xpath("text()").extract_first()) * spanN   
        except Exception as e:
            self.logger.error(e)
        
        area = 0.0
        try:
            area = float(response.css('.area > .mainInfo').xpath("text()").extract_first().replace("平米", ""))   
        except Exception as e:
            self.logger.error(e)

        community = response.css('.no_resblock_a').xpath("text()").extract_first()
        houseInfo = HouseinfoItem(
            roomId = roomId,
            url = response.url,
            title = response.css('.main').xpath("text()").extract_first(),
            totalPrice = totalPrice,
            area = area,
            realArea = realArea,
            roomLayout = response.css('.room > .mainInfo').xpath("text()").extract_first(),
            roomFloor = response.css('.room > .subInfo').xpath("text()").extract_first(),
            roomOrientation = response.css('.type > .mainInfo').xpath("text()").extract_first(),
            buildYear = response.css('.noHidden').xpath("text()").extract_first(),
            city = "beijing",
            district = districtResult[0],
            subDistrict = subDistrict,
            community = community,
            online = True,
            hasElevator = hasElevator,
            lastBusinessTime = lastBusinessTime,
            currentBusinessTime = currentBusinessTime,
            businessOwner = businessOwner,
            ownerShip = ownership,
            houseUsage = houseUsage,
            mortgageInfo = mortgageInfo,
            houseSellTime = houseSellTime,
        )
        return houseInfo


