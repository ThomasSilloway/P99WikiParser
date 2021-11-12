import requests
from bs4 import BeautifulSoup


def main(name):
    webpage = get_html()
    if webpage is None:
        print("Failed to download webpage")
        return

    if parse_quest(webpage) is None:
        print("Failed to parse quest")
        return


def parse_quest(webpage):
    soup = BeautifulSoup(webpage, 'html.parser')
    quest_title = soup.find("span", id="Related_quests")
    print(quest_title)
    quest = quest_title.parent.next_sibling.next_sibling.contents[0]
    print('Quests: *' + str(quest) + '*')
    quest_strings = []
    while quest is not None:
        text = quest.a.text
        quest_strings.append(text)
        print('Quest Strings: *' + str(text) + '*')
        quest = quest.next_sibling
    return 1


def get_html():
    url = 'https://wiki.project1999.com/Goblin_Warlord_Warbeads'
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.text

    return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
