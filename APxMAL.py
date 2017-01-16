'''
MyAnimeList:AnimePlanet(x:y)
    - Completed:Watched (2:1)
    - Watching:Watching (1:2)
    - Dropped:Dropped (4:3)
    - On-Hold:Stalled (3:5)
    - Plan to Watch:Want to watch (6:4)
    - NONE:Won't watch (-1:6)
'''
'''
XML example:
<?xml version="1.0" encoding="UTF-8"?>
<entry>
	<episode>11</episode>
	<status>1</status>
	<score>7</score>
    #unimportant
	<storage_type></storage_type>
	<storage_value></storage_value>
	<times_rewatched></times_rewatched>
	<rewatch_value></rewatch_value>
	<date_start></date_start>
	<date_finish></date_finish>
	<priority></priority>
	<enable_discussion></enable_discussion>
	<enable_rewatching></enable_rewatching>
	<comments></comments>
	<fansub_group></fansub_group>
	<tags>test tag, 2nd tag</tags>
</entry>   
'''

import urllib.request
import html
import base64

def download_page(user, page):
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4"
    link = "http://www.anime-planet.com/users/%s/anime?page=%s" % (user, page)

    client = urllib.request.Request(link)
    client.add_header("User-Agent", user_agent)

    return str(urllib.request.urlopen(client).read())

class Anime(object):
    name = ""
    type = ""
    status = ""
    episodes = ""
    rating = ""

    def __init__(self, name, type, status, episodes, rating):
        self.name = name
        self.type = type
        self.status = status
        self.episodes = episodes
        self.rating = rating

def parse_ap_page(page, page_index, auth):
    ANIME_NUMBER_START = "<b>"
    ANIME_NUMBER_END = "</b> anime on this list"

    ANIME_TITLE_START = "<a title=\"<h5>"
    ANIME_TITLE_END = "</h5>"

    ANIME_TYPE_START = "<li class=\\'type\\'>"
    ANIME_TYPE_END = "</li>"

    ANIME_STATUS_START = "<span class=\\'status"
    ANIME_STATUS_END = "\\'>"

    ANIME_EPISODES_START = "span> "
    ANIME_EPISODES_END = "<div"
        
    ANIME_RATING_START = "ttRating\\'>"
    ANIME_RATING_END = "<"
            
    anime_list = list()

    index = 0
    total_anime = page[page.find(ANIME_NUMBER_START) + len(ANIME_NUMBER_START):page.find(ANIME_NUMBER_END)]

    pages = int(total_anime)//50
    last_page = int(total_anime)%50

    if last_page == 0:
        current_page = 50
    elif pages == 0 and last_page != 0:
        current_page = last_page
    if last_page != 0:
        pages += 1
    if page_index < pages:
        current_page = 50
    else:
        current_page = last_page

    start_index = 0
    end_index = 0
    while index < current_page:
        start_index = page.find(ANIME_TITLE_START, end_index) + len(ANIME_TITLE_START)
        end_index = page.find(ANIME_TITLE_END, start_index)
        anime_name = html.unescape(page[start_index:end_index])

        start_index = page.find(ANIME_TYPE_START, end_index) + len(ANIME_TYPE_START)
        end_index = page.find(ANIME_TYPE_END, start_index)
        anime_type = html.unescape(page[start_index:end_index])

        start_index = page.find(ANIME_STATUS_START, end_index) + len(ANIME_STATUS_START)
        end_index = page.find(ANIME_STATUS_END, start_index)
        anime_status = page[start_index:end_index]

        if anime_status != '6':
            start_index = page.find(ANIME_EPISODES_START, end_index) + len(ANIME_EPISODES_START)
            end_index = page.find(ANIME_EPISODES_END, start_index)
            anime_episodes = page[start_index:end_index]

            if anime_status != '4':
                if page.find(ANIME_RATING_START, end_index) < page.find(ANIME_TITLE_START, end_index):
                    start_index = page.find(ANIME_RATING_START, end_index) + len(ANIME_RATING_START)
                    end_index = page.find(ANIME_RATING_END, start_index)
                    anime_rating = page[start_index:end_index]
                else:
                    anime_rating = '0'

            anime_episodes = anime_episodes[:anime_episodes.find("\\t")]

            add_anime(anime_name, anime_type, anime_status, anime_episodes, anime_rating, auth)

        index += 1
    
    return anime_list

def add_anime(name, type, status, episodes, rating, auth):
    api_search = "https://myanimelist.net/api/anime/search.xml?"
    api_advanced_search = "https://myanimelist.net/anime.php?q=%s&type=%s"
    api_add = "https://myanimelist.net/api/animelist/add/%s.xml"
    api_update = "https://myanimelist.net/api/animelist/update/%s.xml"
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4"

    name = name.replace(" Boku-tachi ", " Bokutachi ")
    name = name.replace(" o ", " wo ")

    client = urllib.request.Request(api_search + urllib.parse.urlencode({'q' : name}))
    client.add_header("Authorization", "Basic %s" % auth)
    client.add_header("User-Agent", user_agent)

    anime = urllib.request.urlopen(client).read().decode("utf-8")
    id = anime[anime.find("<id>") + 4:anime.find("</id>")]
    title = anime[anime.find("<title>") + 7:anime.find("</title>")]

    try:
        print(name, '|', title, '|', id)
    except:
        print(id)

    TYPES = { "TV" : 1, "OVA" : 2, "Movie" : 3, "Special" : 4 } 
    STATUSES = { '1' : '2', '2' : '1', '3' : '4', '4' : '6', '5' : '3' } 

    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    xml += "<entry>\n"
        
    if status != '2':
        if type.count("TV") != -1:
            episodes = type[type.find('(') + 1:type.find(" ep")]
            type = "TV"
        elif type.count("DVD") != -1:
            episodes = type[type.find('(') + 1:type.find(" ep")]
            type = "Special"
        elif type.count("OVA") != -1:
            episodes = type[type.find('(') + 1:type.find(" ep")]
            type = "OVA"
        elif type.count("Movie") != -1:
            episodes = '1'
            type = "Movie"
    elif status == '2':
        episodes = episodes[episodes.find("- ") + 2:episodes.find('/')]

    xml += "\t<status>" + STATUSES[status] +"</status>\n"

    if status == '4' or status == '6':
        xml += "\t<episode></episode>\n"
    else:
        xml += "\t<episode>" + episodes + "</episode>\n"

    xml += "\t<score>" + str(int(float(rating)*2)) + "</score>\n"

    xml += "\t<downloaded_episodes></downloaded_episodes>\n"
    xml += "\t<storage_type></storage_type>\n"
    xml += "\t<storage_value></storage_value>\n"
    xml += "\t<times_rewatched></times_rewatched>\n"
    xml += "\t<rewatch_value></rewatch_value>\n"
    xml += "\t<date_start></date_start>\n"
    xml += "\t<date_finish></date_finish>\n"
    xml += "\t<priority></priority>\n"
    xml += "\t<enable_discussion></enable_discussion>\n"
    xml += "\t<enable_rewatching></enable_rewatching>\n"
    xml += "\t<comments></comments>\n"
    xml += "\t<fansub_group></fansub_group>\n"
    xml += "\t<tags></tags>\n"
    xml += "</entry>\n"
        
    values = {"id" : id, "data" : xml}

    client = urllib.request.Request(api_add % id, urllib.parse.urlencode(values).encode("utf-8"))
    client.add_header("Authorization", "Basic %s" % auth)
    client.add_header("User-Agent", user_agent)

    if name != title:
        return "Error with anime: " + name 
    else:
        added = False
        try:
            urllib.request.urlopen(client)
            added = True
        except:
            added = False
        if not added:
            try:
                client = urllib.request.Request(api_update % id, urllib.parse.urlencode(values).encode("utf-8"))
                client.add_header("Authorization", "Basic %s" % auth)
                client.add_header("User-Agent", user_agent)

                urllib.request.urlopen(client)
                added = True
            except:
                added = False

    return

auth_string = ""

def main():
    APuser = input("AP Username: ")
    MALuser = input("MAL Username: ")
    MALpassword = input("MAL Password: ")

    key = str("%s:%s" % (MALuser, MALpassword)).replace('\n', '')
    auth = str(base64.b64encode(bytes(key, "utf-8")), "utf-8")

    page = 1
    first_page = download_page(MALuser, page)
    anime_list = parse_ap_page(first_page, page, auth)
    
    ANIME_NUMBER_START = "<b>"
    ANIME_NUMBER_END = "</b> anime on this list"

    total_anime = int(first_page[first_page.find(ANIME_NUMBER_START) + len(ANIME_NUMBER_START):first_page.find(ANIME_NUMBER_END)])
    
    pages = total_anime // 50
    last_page = total_anime % 50

    if last_page !=0:
        pages += 1

    next_page = ""
    while page <= pages:
        page += 1
        next_page = download_page(MALuser, page)
        anime_list = parse_ap_page(next_page, page, auth)

if __name__ == "__main__":
    main()