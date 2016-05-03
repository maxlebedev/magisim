#!/bin/sh

mkdir sets
for set in '10E' '9ED' 'BFZ' 'DKA' 'GPT' 'LEA' 'M14' 'OGW' 'RAV' 'THS' 'WWK' '2ED' 'ALA' 'BNG' 'DRK' 'GTC' 'LEB' 'MBS' 'ONS' 'ROE' 'TMP' 'ZEN' '3ED' 'ALL' 'BOK' 'DST' 'HML' 'LEG' 'MIR' 'ORI' 'RTR' 'TOR' '4ED' 'APC' 'CHK' 'DTK' 'ICE' 'LGN' 'MMQ' 'PCY' 'SCG' 'TSP' '5DN' 'ARB' 'CHR' 'EVE' 'INV' 'LRW' 'MOR' 'PLC' 'SHM' 'UDS' '5ED' 'ARN' 'CON' 'EXO' 'ISD' 'M10' 'MRD' 'PLS' 'SOI' 'ULG' '6ED' 'ATH' 'CSP' 'FEM' 'JOU' 'M11' 'NMS' 'PO2' 'SOK' 'USG' '7ED' 'ATQ' 'DGM' 'FRF' 'JUD' 'M12' 'NPH' 'POR' 'SOM' 'VIS' '8ED' 'AVR' 'DIS' 'FUT' 'KTK' 'M13' 'ODY' 'PTK' 'STH' 'WTH';
do
	wget http://mtgjson.com/json/$set.json.zip;
	unzip $set.json.zip -d sets/$set.json;
done
rm *.json.zip
