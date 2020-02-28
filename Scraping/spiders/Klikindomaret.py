# -*- coding: utf-8 -*-
import datetime
import scrapy

class IndomaretSpider(scrapy.Spider):
    name = "indomaret"
    page = 1
    cat = 1
    scat = 1
    menu = 1
    start_urls = ['https://www.klikindomaret.com/category/handphone-1']
    def parse(self, response):
        wilayah = response.xpath('//div[1]/span/span[2]/text()').get()
        wilayah = wilayah.replace("Wilayah: ", " ")
        wilayah = wilayah.replace(", ", "")
        items = response.xpath('//div[@class="item"]/a/div[@class="each-item"]').getall()
        menu = response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/a/span/text()'.format(IndomaretSpider.menu)).get()
        kategori = response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/ul/li[{}]/a/text()'
                                  .format(IndomaretSpider.menu,IndomaretSpider.cat)).get()
        kategori = kategori.replace(",","&")
        subkategori = response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/ul/li[{}]/ul/li[{}]/a/text()'
                                     .format(IndomaretSpider.menu,IndomaretSpider.cat,IndomaretSpider.scat)).get()
        if subkategori is None:
            subkategori = '-'
        else :
            subkategori = subkategori.strip("\n")
            subkategori = subkategori.replace(",", "")
        nama_produk = response.xpath('//div[@class="wrp-content"]/div[contains(@class,"title")]/text()').extract()
        harga = response.xpath('//div[@class="vmiddle"]//span[@class="normal price-value"]/text()').extract()
        img_url = response.xpath('//div[@class="wrp-media"]/img/@data-src').extract()
        seller = response.xpath('//div[@class="wrp-content"]/span[@class="sendbyProduct"]/text()').extract()
        ketersediaan = response.xpath('//a/div/div/div[@class="wrp-btn"]/button/text()').getall()
        waktu = datetime.datetime.now()
        time = waktu.strftime("%X%f %x")

        for item in range(0, len(items)):
            pdname = nama_produk[item]
            pdname = pdname.strip("\n")
            pdname = pdname.replace(",", "")
            ava = ketersediaan[item]
            ava = ava.strip("\n")
            ava = ava.replace(",", "")
            if ava == "Beli":
                ava = "Tersedia"
            price_before = response.xpath('//div[{}]/a/div/div/div//span[@class="strikeout disc-price"]/text()'
                                          .format(item + 1)).get()
            if price_before is None:
                price_before = '-'
                discount = '-'
            else:
                price_before = price_before.strip("\n")
                price_before = price_before.replace("\" \"", "")
                discount = response.xpath('//div[{}]/a/div/div/div//span/span[@class="discount"]/text()'
                                          .format(item + 1)).get()
                discount = discount.strip("\n")
                discount = discount.replace(",", "")
            yield {
                'Wilayah' : wilayah,
                'Nama Produk': pdname,
                'Stok': ava,
                'Diskon': discount,
                'Harga Sebelum Diskon': price_before,
                'Harga': harga[item],
                'Penjual': seller[item],
                'URL Gambar': img_url[item],
                'Menu': menu,
                'Kategori': kategori,
                'Subkategori': subkategori,
                'Waktu': time
            }
        pagination = response.xpath('//div[@class="pagination"]//span[2]/text()').get()
        if pagination is not None :
            pagination = pagination.replace("dari ", "")
        else :
            pagination = IndomaretSpider.page
        jmenu = len(response.xpath('//div[2]/div/div/div/ul[2]/li/a').getall())
        jcat = len(response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/ul/li/a/@href'
                                  .format(IndomaretSpider.menu)).getall()) - 1
        jscat = len(response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/ul/li[{}]/ul/li/a'
                                   .format(IndomaretSpider.menu,IndomaretSpider.cat)).getall())
        if IndomaretSpider.page < int (pagination):
            IndomaretSpider.page += 1
            next_page = response.xpath('//div[@class="pagination"]//a[last()]/@href').get()
            yield response.follow(next_page, callback=self.parse)
        elif IndomaretSpider.menu <= jmenu :
            IndomaretSpider.page = 1
            if IndomaretSpider.cat <= jcat:
                if jscat is not None and IndomaretSpider.scat < jscat:
                    IndomaretSpider.scat += 1
                    url = response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/ul/li[{}]/ul/li[{}]/a/@href'
                                     .format(IndomaretSpider.menu,IndomaretSpider.cat,IndomaretSpider.scat)).get()
                    next_page = 'https://www.klikindomaret.com{}'.format(url)
                    yield response.follow(next_page, callback=self.parse)
                else:
                    if IndomaretSpider.cat == jcat :
                        IndomaretSpider.scat = 1
                        IndomaretSpider.cat = 1
                        IndomaretSpider.menu += 1
                        url = response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/ul/li[{}]/ul/li[{}]/a/@href'
                                             .format(IndomaretSpider.menu, IndomaretSpider.cat,
                                                     IndomaretSpider.scat)).get()
                        if url is None:
                            url = response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/ul/li[{}]/a/@href'
                                                 .format(IndomaretSpider.menu, IndomaretSpider.cat)).get()
                            if url is None :
                                exit()
                        next_page = 'https://www.klikindomaret.com{}'.format(url)
                        yield response.follow(next_page, callback=self.parse)
                    else :
                        IndomaretSpider.scat = 1
                        IndomaretSpider.cat += 1
                        url = response.xpath('//div[2]/div/div/div/ul[2]/li[{}]/ul/li[{}]/a/@href'
                                             .format(IndomaretSpider.menu,IndomaretSpider.cat)).get()
                        next_page = 'https://www.klikindomaret.com{}'.format(url)
                        yield response.follow(next_page, callback=self.parse)