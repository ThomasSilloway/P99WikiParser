# P99 Wiki Parser
Parse data from the P99 wiki - Ideally to be used by Twitch Bots

## Aspirations

Allow a twitch bot to accept the command !quest [itemname] and have it search the P99 wiki for that item & quest item names and/or links

## Current Status

Parses search text & handles 4 cases:
 - Exact match
 - Partial Match
 - No match, but some related results
 - No matches at all

On matches - also handles if that item has no quests

Next step - Hook up with the [Streamlabs Chatbot](https://streamlabs.com/chatbot)

Currently runs with Python 3.7

Requirements: 
- beautifulsoup4
- requests
