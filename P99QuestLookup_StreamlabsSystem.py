#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Look up an item on P99's wiki"""
#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import json
import os
import re
from bs4 import BeautifulSoup
#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "P99QuestLookup"
Website = "https://github.com/ThomasSilloway"
Creator = "Thomas Silloway"
Version = "1.0.0"
Description = "Finds quests for an item you can search on the P99 wiki"
#---------------------------------------
# Versions
#---------------------------------------
"""
1.0.0 - Initial Release
"""
#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
#---------------------------------------
# Classes
#---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else: #set variables if no custom settings file is found
            self.Commands = "!quest item_name"
            self.OutputMessage = "$match_type: $item_name\nPossible Quests:$quest_strings"
            self.CommandCooldown = 1

    # Reload settings on save through UI
    def ReloadSettings(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        """Save settings to files (json and js)"""
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
        return

#---------------------------------------
# Settings functions
#---------------------------------------
def ReloadSettings(jsondata):
    """Reload settings on Save"""
    # Reload saved settings
    MySet.ReloadSettings(jsondata)
    # End of ReloadSettings

def SaveSettings(self, settingsFile):
    """Save settings to files (json and js)"""
    with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
        json.dump(self.__dict__, f, encoding='utf-8-sig')
    with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
        f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
    return

#---------------------------------------
# System functions
#---------------------------------------

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    """data on Load, required function"""
    global MySet
    # Load in saved settings
    MySet = Settings(settingsFile)
    # End of Init
    global commandlist 
    commandlist = MySet.Commands.lower().split()
    return

def Execute(data):
    """Required Execute data function"""
    if data.IsChatMessage() and data.GetParam(0).lower() in commandlist and Parent.IsOnUserCooldown(ScriptName,str(commandlist),data.User):
        message = "Time Remaining " + str(Parent.GetUserCooldownDuration(ScriptName,str(commandlist),data.User))
        SendResp(data, "Stream Chat", message)
        return
 
    #   Check if the propper command is used, the command is not on cooldown and the user has permission to use the command
    if data.IsChatMessage() and data.GetParam(0).lower() in commandlist and not Parent.IsOnUserCooldown(ScriptName,str(commandlist),data.User):
        num_params = data.GetParamCount()
        item_name = ""
        for i in range(1, num_params):
            item_name += " " + data.GetParam(i)
        error_msg, found_item_name, match_type, quests_string = search_for_item(item_name)

        if error_msg is not None:
            found_item_name = found_item_name or "None"
            match_type = match_type or "None"

            message = error_msg + " \n - Found Item Name: *" + found_item_name + "* Match Results: *" + match_type + "*"
        else:
            message = MySet.OutputMessage
            message = message.replace("$match_type", match_type)
            message = message.replace("$item_name", found_item_name)
            message = message.replace("$quest_strings", quests_string)
        SendResp(data, "Stream Chat", message)
        Parent.AddUserCooldown(ScriptName,str(commandlist),data.User,MySet.CommandCooldown)  # Put the command on cooldown
        return
        
    return
def Tick():
    """Required tick function"""
    return

#---------------------------------------
# Parse functions
#---------------------------------------

def SendResp(data, Usage, Message):
    """Sends message to Stream or discord chat depending on settings"""
    Message = Message.replace("$user", data.UserName)
    Message = Message.replace("$currencyname", Parent.GetCurrencyName())

    l = ["Stream Chat", "Chat Both", "All", "Stream Both"]
    if not data.IsFromDiscord() and (Usage in l) and not data.IsWhisper():
        Parent.SendStreamMessage(Message)

    l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
    if not data.IsFromDiscord() and data.IsWhisper() and (Usage in l):
        Parent.SendStreamWhisper(data.User, Message)

    l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
    if data.IsFromDiscord() and not data.IsWhisper() and (Usage in l):
        Parent.SendDiscordMessage(Message)

    l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
    if data.IsFromDiscord() and data.IsWhisper() and (Usage in l):
        Parent.SendDiscordDM(data.User, Message)

#---------------------------------------
# UI functions
#---------------------------------------    


def search_for_item(search_string):
    # Do search & get the item page url

    search_string = search_string.replace(' ', '+')
    search_url = 'https://wiki.project1999.com/index.php?title=Special%3ASearch&profile=default&search={}&fulltext=Search'.format(search_string)
    webpage = get_html(search_url)

    seach_accuracy, item_name, item_url = parse_search_page_v2(webpage)

    if item_name is None:
        return "Failed to find matching page in search", None, None, None

    if item_url is None:
        return 'Unable to find URL for item page', item_name, seach_accuracy, None

    item_url = 'https://wiki.project1999.com{}'.format(item_url)
    webpage = get_html(item_url)
    if webpage is None:
        return 'Failed to download webpage: ' + item_url, item_name, seach_accuracy, None

    is_success, return_quests_string = parse_quest(webpage)
    if is_success is None:
        return 'Failed to parse webpage for quest: ' + item_url, item_name, seach_accuracy, None
    else:
        return None, item_name, seach_accuracy, return_quests_string

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
        return None, None, None

    if "There were no results" in search_results_div.text:
        return None, None, None

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
        return "Partial match", link.text, link_url

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
            return "Exact match", link.text, link_url

        # No Match, but some results will contain Create the page
        if "Create the page" in possible_link.text:

            paragraph = possible_link.parent
            new_line = paragraph.next_sibling
            list_element = new_line.next_sibling
            link = list_element.li.div.a

            found_link_text = link.text
            # found_link = str(possible_link.parent)
            # found_link += "\n Expected newline *" + str(new_line)
            # found_link += "* \n expected list element *" + str(list_element)
            # found_link += "* \n expected link *" + str(link) + "*"

            link_url = link.attrs['href']

            return "Closest match", found_link_text, link_url

    return None, None, None


def parse_quest(webpage):
    soup = BeautifulSoup(webpage, 'html.parser')
    quest_title = soup.find("span", id="Related_quests")

    if quest_title is None:
        return 1, '\n - No Quests Found for this item'
    # print(quest_title)
    quest = quest_title.parent.next_sibling.next_sibling.contents[0]

    if "no related quests" in quest.text:
        return 1, '\n - No Quests Found for this item'

    # print('Quests: *' + str(quest) + '*')

    quest_string = ""
    while quest is not None and quest.a is not None:
        text = quest.a.text
        quest_string += '\n - ' + str(text)
        quest = quest.next_sibling

    return 1, quest_string


def get_html(url):
    # resp = get(url)
    headers = {}
    resp = Parent.GetRequest(url, headers)

    resp = json.loads(resp)
    if resp["status"] == 200:
        return resp["response"]

    return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    search_name = 'Goblin Warbeads'  # Partial match
    # search_name = 'Goblin beads' # match something with no quest
    # search_name = 'goblin warlord beads' # exact match
    # search_name = 'asdlikfjlaksdf' # no match
    error_msg, found_item_name, match_type, quests_string = search_for_item(search_name)
    if error_msg is not None:
        print("ERROR: " + error_msg)
    else:
        print(match_type + ": " + found_item_name)
        print("Possible Quests:" + quests_string)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

