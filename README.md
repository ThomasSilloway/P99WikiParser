# P99 Wiki Parser
Parse data from the P99 wiki - Ideally to be used by Twitch Bots

## Aspirations

Mode #1 Allow a twitch bot to accept the command !quest [itemname] and have it search the P99 wiki for that item & quest item names and/or links

Mode #2 Output an item url for the quest reward, so the image can pop up in OBS

## Current Status

Requires Python 2.7 - because Streamlabs chatbot

Parses search text & handles 4 cases:
 - Exact match
 - Partial Match
 - No match, but some related results
 - No matches at all

On a successful item search it handles reqporting if that item has no quests

Requirements: 
- beautifulsoup4
