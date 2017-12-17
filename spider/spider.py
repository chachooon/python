from .models import NmapList, NmapBoundaryList #, NmapContents
from bs4 import BeautifulSoup
import requests, json, asyncio

class NmapScrapable():
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        # 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    def request(self,**kwarg):
        url = "http://map.naver.com/search2/interestSpot.nhn?"
        category = kwarg['category']
        boundary = kwarg['boundary']
        playload = {
            'type': category,
            'boundary': boundary,
            'pageSize': '100'
        }
        respond = requests.get(url, headers=self.header, params=playload)
        res = respond.status_code
        if res == 200:
            if 'result' in respond.json():
                results = list(respond.json()['result']['site'])
                if len(results)==100:
                    return boundary
                else:
                    self.create(results=results, category=category, boundary=boundary)
                    return 1
            else: return 1
        else: return 1

    def request_contents(self, id):
        url = 'https://store.naver.com/restaurants/detail?'
        playload = {'id': id }
        req = requests.get(url, headers=self.header, params=playload)
        soup = BeautifulSoup(req.text, 'html.parser')
        soup_parse = soup.footer.next_sibling.string.split('window.PLACE_STATE=')[1]
        result = json.loads(soup_parse)
        return result

    def create(self, **kwarg):
        results = kwarg['results']
        boundary = kwarg['boundary']
        category = kwarg['category']
        cnt =0
        for result in results:
            try:
                id = int(result['id'][1:])
                nmaplist, created = NmapList.objects.update_or_create(
                    id=id,
                    name=result['name'],
                    category=category,
                    x=result['x'],
                    y=result['y'],
                    defaults={
                        'id': id,
                        'name': result['name'],
                        'category': category,
                        'x': result['x'],
                        'y': result['y']
                    }
                )
                if created:
                    cnt += 1
                    contents = self.request_contents(id)['business']
                    nmaplist.update(contents = contents)

            except: pass

        NmapBoundaryList.objects.update_or_create(
            boundary=boundary,
            category=category,
            defaults={
                'boundary': boundary,
                'category': category
            }
        )
        print(str(cnt) + '건 - ' + boundary)



    def iter(self):
        category = 'DINING'
        x_min = 1250
        x_max = 1310
        y_min = 330
        y_max = 390


        for x in range(x_min, x_max):
            print('x:'+str(x))
            for y in range(y_min, y_max):
                boundary = str(round(x * 0.1,7))+';'+str(round(y * 0.1,7))+';'+ \
                           str(round((x+1)* 0.1,7))+';'+str(round((y+1)* 0.1,7))
                results = self.request(boundary=boundary, category=category)
                if results != 1:
                    xx = x * 10
                    yy = y * 10
                    print('re request '+str(xx))
                    for xx in range(xx,xx+10):
                        for yy in range(yy,yy+10):
                            boundary = str(round(xx * 0.01, 7)) + ';' + str(round(yy * 0.01, 7)) + ';' + \
                                       str(round((xx+1) * 0.01, 7)) + ';' + str(round((yy+1) * 0.01, 7))
                            result = self.request(boundary=boundary, category=category)
                            if result != 1:
                                xxx = xx * 10
                                yyy = yy * 10
                                print('re request ' + str(xxx))
                                for xxx in range(xxx, xxx+10):
                                    for yyy in range(yyy,yyy+10):
                                        boundary = str(round(xxx * 0.001, 7)) + ';' + str(round(yyy * 0.001, 7)) + ';' + \
                                                   str(round((xxx + 1) * 0.001, 7)) + ';' + str(round((yyy + 1) * 0.001, 7))
                                        self.request(boundary=boundary, category=category)
                #else: #print('y:' + str(y))



