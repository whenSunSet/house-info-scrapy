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

beike_url = "https://bj.zu.ke.com/"
base_url = "https://bj.zu.ke.com/zufang/"

class BeikeZufangSimpleSpider(scrapy.Spider):
    name = 'beike-zufang-simple'
    allowed_domains = ['bj.zu.ke.com']

    custom_settings = {
        'DOWNLOAD_DELAY': '10',
    }

    def start_requests(self):
        for key in districtDic.keys():
            url = base_url + '{}'.format(key) + "/"
            yield scrapy.Request(url, self.districtPage)
            # TODO 删了
            # return

    def districtPage(self, response):
        self.logger.info("districtPage 城区:%s 开始爬取", response.url)
        subDistrictResultList = response.css('.filter__item--level3 > a') 
        if (len(subDistrictResultList) == 0):
            self.logger.error("districtPage %s 没有数据", response.url)
        for subDistrict in subDistrictResultList:
            urlPath = subDistrict.xpath("@href").extract_first()
            if ("zufang" in urlPath):
                isCity = False
                for key in districtDic.keys():
                    isCity = (("/" + key + "/") in urlPath)
                    if isCity:
                        break
                if not isCity:
                    subDistrict = urlPath.split("/")
                    try:
                        subDistrictUrl = base_url + '{}'.format(subDistrict[2]) + "/"
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
        houseSize = response.css('.content__title--hl::text').get()
        pageSize = int(int(houseSize) / 30) + 1
        self.logger.info("板块：" + subDistrict + "，房屋数量：" + str(houseSize) + "，房屋页数：" + str(pageSize))
        for i in range(1, (pageSize + 1)):   
            subDistrictSubPageUrl = base_url + subDistrict + "/pg" + str(i) + "/"
            yield scrapy.Request(subDistrictSubPageUrl, self.subDistrictSubPage)
            # TODO 删了
            # return
    
    def subDistrictSubPage(self, response):
        titleItems = response.css('.twoline')
        priceItems = response.css('em')
        communityItems = response.css('.content__list--item--des > a')
        houseSimpleInfoItems = response.css('.content__list--item--des')
        index = 0
        for eachHouseInfo in response.css('.content__list--item--title'):
            price = float(priceItems[index].xpath("text()").extract_first()) * 10000
            district = communityItems[3 * index].xpath("text()").get()
            subDistrict = communityItems[1 + 3 * index].xpath("text()").get()
            community = communityItems[2 + 3 * index].xpath("text()").get()
            houseUrl = beike_url + titleItems[index].xpath("@href").extract_first()
            houseUrlSplitResultList = houseUrl.split("/")
            roomId = houseUrlSplitResultList[len(houseUrlSplitResultList) - 1].split(".")[0]
            houseTitle = titleItems[index].xpath("text()").extract_first().strip()
            areaList = houseSimpleInfoItems[index].get().split("<i>/</i>")
            area = 0
            for mayArea in areaList:
                if ("㎡" in mayArea):
                    area = float(mayArea.strip().replace("㎡", "").replace("\n", ""))

            #self.logger.error("subDistrictSubPage price:%f, district:%s subDistrict:%s, community:%s, houseUrl:%s, houseTitle:%s, roomId:%s, areaList:%s, area:%f", price, district, subDistrict, community, houseUrl, houseTitle, roomId, areaList, area)
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
                    district = district,
                    subDistrict = subDistrict,
                    community = community,
                    online = True,
                    isZuFang = True
                    )
                yield houseInfo 
            else:   
                self.logger.info("subDistrictSubPage is old house")
