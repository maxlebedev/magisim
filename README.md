# magisim
A primitive MTG card text similarity tool

It basically applies the [TF-IDF Algorithm](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) to the text box of Magic: the Gathering cards. In reality, the things that make two cards similar go much further than similar rules text, but the tool nonetheless does a reasonable job of helping to find cards with similar effects. 

Download AllCards.json from here: http://mtgjson.com/json/AllCards.json.zip

Example usage:  

python magisim.py -n 20  

Please enter a card name:Lightning Bolt

