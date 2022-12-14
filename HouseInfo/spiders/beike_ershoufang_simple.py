import scrapy
from HouseInfo.items import HouseinfoItem

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

class BeikeErshoufangSimpleSpider(scrapy.Spider):
    name = 'beike-ershoufang-simple'
    allowed_domains = ['bj.ke.com']

    custom_settings = {
        'DOWNLOAD_DELAY': '10',
    }


    def start_requests(self):
        for key in districtDic.keys():
            url = 'https://bj.ke.com/ershoufang/{}'.format(key) + "/"
            yield scrapy.Request(url, self.districtPage)
            # TODO 删了
            # return

    def districtPage(self, response):
        self.logger.info("districtPage 城区:%s 开始爬取", response.url)
        subDistrictResultList = response.css('dd div > a') 
        if (len(subDistrictResultList) == 0):
            self.logger.error("districtPage %s 没有数据", response.url)
        for subDistrict in subDistrictResultList:
            urlPath = subDistrict.xpath("@href").extract_first()
            if ("ershoufang" in urlPath):
                isCity = False
                for key in districtDic.keys():
                    isCity = (("/" + key + "/") in urlPath)
                    if isCity:
                        break
                if not isCity:
                    subDistrict = urlPath.split("/")
                    try:
                        subDistrictUrl = 'https://bj.ke.com/ershoufang/{}'.format(subDistrict[2]) + "/"
                        yield scrapy.Request(subDistrictUrl, self.subDistrictPage)
                        # TODO 删了
                        # return
                    except Exception as e:
                        self.logger.error(e)
        
    def subDistrictPage(self, response):
        try:
            subDistrict = response.url.split("/")[4]
        except Exception as e:
            self.logger.error(e)
        houseSize = response.css('.leftContent > div > .clear > .fl > span::text').get()
        pageSize = int(int(houseSize) / 30) + 1
        self.logger.info("板块：" + subDistrict + "，房屋数量：" + str(houseSize) + "，房屋页数：" + str(pageSize))
        for i in range(1, (pageSize + 1)):   
            subDistrictSubPageUrl = 'https://bj.ke.com/ershoufang/' + subDistrict + "/pg" + str(i) + "/"
            #subDistrictSubPageUrl = 'https://bj.ke.com/ershoufang/yangzhuang1/pg10/'
            yield scrapy.Request(subDistrictSubPageUrl, self.subDistrictSubPage)
            # TODO 删了
            # return
    
    def subDistrictSubPage(self, response):
        subDistrict = response.css('.leftContent > div > .clear > .fl > a::text').get().replace("二手房", "")
        priceItems = response.css('.totalPrice2 > span')
        communityItems = response.css('.flood a')
        houseSimpleInfoItems = response.css('.houseInfo')
        index = 0
        for eachHouseInfo in response.css('.title > .maidian-detail'):
            houseUrl = eachHouseInfo.xpath("@href").extract_first()
            houseUrlSplitResultList = houseUrl.split("/")
            houseTitle = eachHouseInfo.xpath("@title").extract_first()
            roomId = houseUrlSplitResultList[len(houseUrlSplitResultList) - 1].split(".")[0]
            price = float(priceItems[index].xpath("text()").extract_first()) * 10000
            community = communityItems[index].xpath("text()").extract_first()
            areaList = houseSimpleInfoItems[index].get().split("|")
            area = 0
            for mayArea in areaList:
                if ("平米" in mayArea):
                    area = float(mayArea.strip().replace("平米", "").replace("\n", ""))

            if (area == 0):
                self.logger.error("subDistrictSubPage area error areaList:%s", areaList)
            index = index + 1
            objectId = ""
            if (objectId == ""):
                houseInfo = HouseinfoItem(
                    roomId = roomId,
                    url = houseUrl,
                    title = houseTitle,
                    totalPrice = price,
                    area = area,
                    city = "beijing",
                    district = "",
                    subDistrict = subDistrict,
                    community = community,
                    online = True,
                    isZuFang = False
                    )
                yield houseInfo 
            else:   
                self.logger.info("subDistrictSubPage is old house")
