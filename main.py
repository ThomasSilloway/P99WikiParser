from requests import get
from bs4 import BeautifulSoup


def main(name):
    # Do search & get the item page url
    search_string = 'Goblin Warbeads' # Partial match
    # search_string = 'Goblin beads' # match something with no quest
    # search_string = 'goblin warlord beads' # exact match
    # search_string = 'asdlikfjlaksdf' # no match
    search_string = search_string.replace(' ', '+')
    search_url = 'https://wiki.project1999.com/index.php?title=Special%3ASearch&profile=default&search={}&fulltext=Search'.format(search_string)
    webpage = get_html(search_url)

    item_name, item_url = parse_search_page_v2(webpage)

    if item_name is None:
        print("Failed to find matching page in search")
        return

    print(item_name)
    if item_url is None:
        print('Unable to continue search, try again with valid name')
        return

    item_url = 'https://wiki.project1999.com{}'.format(item_url)
    webpage = get_html(item_url)
    if webpage is None:
        print("Failed to download webpage")
        return

    if parse_quest(webpage) is None:
        print("Failed to parse quest")
        return


def parse_search_page_v2(webpage):
    # There are 4 options
    # - Exact match
    # - Partial match
    # - No match - possible results
    # - No match - no results
    soup = BeautifulSoup(webpage, 'html.parser')
    divs = soup.find_all("div")
    search_results_div = None
    for div in divs:
        if 'class' in div.attrs and div.attrs['class'] == ['searchresults']:
            search_results_div = div
            break

    if search_results_div is None:
        return None, None

    if "There were no results" in search_results_div.text:
        return None, None

    return parse_search_results(search_results_div)


def parse_search_results(search_results_div):

    # If you have a partial match you get this html:
    # <span class="mw-headline" id="Page_title_matches">Page title matches</span></h2>
    page_title_matches = search_results_div.find('span', id='Page_title_matches')
    if page_title_matches is not None:
        header = page_title_matches.parent
        new_line = header.next_sibling
        list_element = new_line.next_sibling
        link = list_element.li.div.a
        link_url = link.attrs['href']
        return "Partial match: {}".format(link.text), link_url

    # If you have an exact match you get this html:
    # <b>There is a page named "<a href="/Goblin_warlord_beads" title="Goblin warlord beads" class="mw-redirect">Goblin warlord beads</a>" on this wiki.</b></p>
    bold_tags = search_results_div.find_all("b")
    possible_link = None
    for tag in bold_tags:
        tag_children_list = list(tag.children)
        if len(tag_children_list) > 1:
            possible_link = tag

    if possible_link is not None:
        link = possible_link.a

        # Exact match will contain "There is a page named"
        if "There is a page named" in possible_link.text:
            link_url = link.attrs['href']
            return "Exact match: {}".format(link.text), link_url

        # No Match, but some results will contain Create the page
        if "Create the page" in possible_link.text:

            paragraph = possible_link.parent
            new_line = paragraph.next_sibling
            list_element = new_line.next_sibling
            link = list_element.li.div.a

            return "Closest match: {}".format(link.text), None

    return None, None


def parse_quest(webpage):
    soup = BeautifulSoup(webpage, 'html.parser')
    quest_title = soup.find("span", id="Related_quests")

    if quest_title is None:
        print('No Quests Found for this item')
        return 1
    # print(quest_title)
    quest = quest_title.parent.next_sibling.next_sibling.contents[0]
    # print('Quests: *' + str(quest) + '*')
    quest_strings = []
    print('Possible Quests:')
    while quest is not None:
        text = quest.a.text
        quest_strings.append(text)
        print(' - ' + str(text))
        quest = quest.next_sibling
    return 1


def get_html(url):
    resp = get(url)
    if resp.status_code == 200:
        return resp.text

    return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
