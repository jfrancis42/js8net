#!/usr/bin/env python3
# coding: utf-8

global version
version='0.2'

#import pdb
import os
import sys
import time
import json
import argparse
import requests
import uuid
import csv
from os.path import exists
import threading
from threading import Thread
from yattag import Doc
import maidenhead as mh
from queue import Queue
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib
from io import BytesIO
import datetime
from js8net import *
import pyproj

global max_age
global listen

global calls
global prefixes
global friends

global id
id=0

global traffic
global traffic_lock
traffic=[]
traffic_lock=threading.Lock()
global stations
global stations_lock
stations={}
stations_lock=threading.Lock()
global grids
grids={}

global eom
global error
eom="♢"
error="…"

global commands
global commands_lock
commands={}
commands_lock=threading.Lock()

global css
global colors

colors={}
colors['color_friend']='#F1C40F'
colors['color_mycall']='#2ECC71'
colors['color_at']='#5DADE2'
colors['color_snr_supergreen']='#66FF00'
colors['color_snr_green']='#7CD342'
colors['color_snr_yellow']='#FDD835'
colors['color_snr_red']='#F4511E'
colors['color_heartbeat']='#FADBD8'
colors['color_query']='#D6EAF8'
colors['color_table_header_background']='#08389F'
colors['color_table_header_text']='#FFFFFF'
colors['color_link']='#000000'
colors['color_border_bottom_odd']='#DDDDDD'
colors['color_border_bottom_even']='#F3F3F3'
colors['color_border_bottom_last']='#009879'
colors['color_cq']='#FCF3CF'
colors['color_non_zombie_traffic']='#FFFFFF'

css=''
css+='a {'
css+='  color: '+colors['color_link']+';'
css+='  text-decoration: none;'
css+='  text-transform: uppercase;'
css+='}'
css+='.styled-table {'
css+='    border-collapse: collapse;'
css+='    margin: 25px 0;'
css+='    font-size: 0.9em;'
css+='    font-family: sans-serif;'
css+='    min-width: 400px;'
css+='    box-shadow: 0 0 20px rgba(0,0,0,0.5);'
css+='}'
css+='.embedded-table {'
css+='    border-collapse: collapse;'
css+='    margin: 25px 0;'
css+='    font-size: 0.9em;'
css+='    font-family: sans-serif;'
css+='}'
css+='.styled-table thead tr {'
css+='    background-color: '+colors['color_table_header_background']+';'
css+='    color: '+colors['color_table_header_text']+';'
css+='    text-align: left;'
css+='}'
css+='.styled-table th,'
css+='.styled-table td {'
css+='    padding: 12px 15px;'
css+='}'
css+='.styled-table tbody tr {'
css+='    border-bottom: 1px solid '+colors['color_border_bottom_odd']+';'
css+='}'
css+='.styled-table tbody tr:nth-of-type(even) {'
css+='    background-color: '+colors['color_border_bottom_even']+';'
css+='}'
css+='.styled-table tbody tr:last-of-type {'
css+='    border-bottom: 2px solid '+colors['color_border_bottom_last']+';'
css+='}'

prefixes=[['1A','Sov Mil Order of Malta'],['3A','Monaco'],['3B6','Agalega & St. Brandon'],['3B7','Agalega & St. Brandon'],
          ['3B8','Mauritius'],['3B9','Rodriguez Island'],['3C','Equatorial Guinea'],['3C0','Annobon Island'],
          ['3D2','Fiji'],['3DA','Kingdom of Eswatini'],['3V','Tunisia'],['TS','Tunisia'],['3W','Vietnam'],
          ['XV','Vietnam'],['3X','Guinea'],['4J','Azerbaijan'],['4K','Azerbaijan'],['4L','Georgia'],
          ['4O','Montenegro'],['4P','Sri Lanka'],['4Q','Sri Lanka'],['4R','Sri Lanka'],['4S','Sri Lanka'],
          ['4U1ITU','ITU HQ'],['4U1WRC','ITU HQ'],['4U2WRC','ITU HQ'],['4U1UN','United Nations HQ'],
          ['4W','Timor - Leste'],['4X','Israel'],['4Z','Israel'],['5A','Libya'],['5B','Cyprus'],['C4','Cyprus'],
          ['H2','Cyprus'],['P3','Cyprus'],['5H','Tanzania'],['5I','Tanzania'],['5N','Nigeria'],['5O','Nigeria'],
          ['5R','Madagascar'],['5S','Madagascar'],['6X','Madagascar'],['5T','Mauritania'],['5U','Niger'],
          ['5V','Togo'],['5W','Samoa'],['5X','Uganda'],['5Y','Kenya'],['5Z','Kenya'],['6V','Senegal'],
          ['6W','Senegal'],['6Y','Jamaica'],['7O','Yemen'],['7P','Lesotho'],['7Q','Malawi'],['7R','Algeria'],
          ['7T','Algeria'],['7U','Algeria'],['7V','Algeria'],['7W','Algeria'],['7X','Algeria'],['7Y','Algeria'],
          ['8P','Barbados'],['8Q','Maldives'],['8R','Guyana'],['9A','Croatia'],['9G','Ghana'],['9H','Malta'],
          ['9I','Zambia'],['9J','Zambia'],['9K','Kuwait'],['NLD','Kuwait'],['9L','Sierra Leone'],
          ['9M','West Malaysia'],['9W','West Malaysia'],['9M6','East Malaysia'],['9M8','East Malaysia'],
          ['9W6','East Malaysia'],['9W8','East Malaysia'],['9N','Nepal'],['9O','Dem. Rep. of the Congo'],
          ['9P','Dem. Rep. of the Congo'],['9Q','Dem. Rep. of the Congo'],['9R','Dem. Rep. of the Congo'],
          ['9S','Dem. Rep. of the Congo'],['9T','Dem. Rep. of the Congo'],['9U','Burundi'],['9V','Singapore'],
          ['S6','Singapore'],['9X','Rwanda'],['9Y','Trinidad & Tobago'],['9Z','Trinidad & Tobago'],['8O','Botswana'],
          ['A2','Botswana'],['A3','Tonga'],['A4','Oman'],['A5','Bhutan'],['A6','United Arab Emirates'],['A7','Qatar'],
          ['A9','Bahrain'],['6P','Pakistan'],['6Q','Pakistan'],['6R','Pakistan'],['6S','Pakistan'],['AP','Pakistan'],
          ['AQ','Pakistan'],['AR','Pakistan'],['AS','Pakistan'],['BS7H','Scarborough Reef'],['BM','Taiwan'],
          ['BN','Taiwan'],['BO','Taiwan'],['BP','Taiwan'],['BQ','Taiwan'],['BU','Taiwan'],['BV','Taiwan'],
          ['BW','Taiwan'],['BX','Taiwan'],['BM9P','Pratas Island'],['3H','China'],['3I','China'],['3J','China'],
          ['3K','China'],['3L','China'],['3M','China'],['3N','China'],['3O','China'],['3P','China'],['3Q','China'],
          ['3R','China'],['3S','China'],['3T','China'],['3U','China'],['B0','China'],['B2','China'],['B3','China'],
          ['B4','China'],['B5','China'],['B6','China'],['B7','China'],['B8','China'],['B9','China'],['BA','China'],
          ['BD','China'],['BG','China'],['BH','China'],['BI','China'],['BJ','China'],['BL','China'],['BT','China'],
          ['BY','China'],['BZ','China'],['XS','China'],['B1','China'],['C2','Nauru'],['C3','Andorra'],
          ['C5','The Gambia'],['C6','Bahamas'],['C8','Mozambique'],['C9','Mozambique'],['3G','Chile'],['CA','Chile'],
          ['CB','Chile'],['CC','Chile'],['CD','Chile'],['CE','Chile'],['XQ','Chile'],['XR','Chile'],
          ['3G0','Easter Island'],['CA0','Easter Island'],['CB0','Easter Island'],['CC0','Easter Island'],
          ['CD0','Easter Island'],['CE0','Easter Island'],['XQ0','Easter Island'],['XR0','Easter Island'],
          ['3Y','Antarctica'],['AX0','Antarctica'],['AY1Z','Antarctica'],['AY2Z','Antarctica'],['AY3Z','Antarctica'],
          ['AY4Z','Antarctica'],['AY5Z','Antarctica'],['AY6Z','Antarctica'],['AY7Z','Antarctica'],['AY8Z','Antarctica'],
          ['AY9Z','Antarctica'],['FT0Y','Antarctica'],['FT1Y','Antarctica'],['FT2Y','Antarctica'],['FT3Y','Antarctica'],
          ['FT4Y','Antarctica'],['FT5Y','Antarctica'],['FT6Y','Antarctica'],['FT7Y','Antarctica'],['FT8Y','Antarctica'],
          ['LU1Z','Antarctica'],['LU2Z','Antarctica'],['LU3Z','Antarctica'],['LU4Z','Antarctica'],['LU5Z','Antarctica'],
          ['LU6Z','Antarctica'],['LU7Z','Antarctica'],['LU8Z','Antarctica'],['LU9Z','Antarctica'],
          ['RI1AN','Antarctica'],['VI0','Antarctica'],['VK0','Antarctica'],['ZL5','Antarctica'],['ZM5','Antarctica'],
          ['ZS7','Antarctica'],['8J1RL','Antarctica'],['DP0GVN','Antarctica'],['DP1POL','Antarctica'],
          ['KC4AAA','Antarctica'],['KC4AAC','Antarctica'],['KC4USB','Antarctica'],['KC4USV','Antarctica'],
          ['VP8ADE','Antarctica'],['VP8ADE/B','Antarctica'],['CL','Cuba'],['CM','Cuba'],['CO','Cuba'],['T4','Cuba'],
          ['5C','Morocco'],['5D','Morocco'],['5E','Morocco'],['5F','Morocco'],['5G','Morocco'],['CN','Morocco'],
          ['CP','Bolivia'],['CQ','Portugal'],['CR','Portugal'],['CS','Portugal'],['CT','Portugal'],
          ['CQ2','Madeira Islands'],['CQ3','Madeira Islands'],['CQ9','Madeira Islands'],['CR3','Madeira Islands'],
          ['CR9','Madeira Islands'],['CS3','Madeira Islands'],['CS9','Madeira Islands'],['CT3','Madeira Islands'],
          ['CT9','Madeira Islands'],['CQ1','Azores'],['CQ8','Azores'],['CR1','Azores'],['CR2','Azores'],
          ['CR8','Azores'],['CS4','Azores'],['CS8','Azores'],['CT8','Azores'],['CU','Azores'],['CV','Uruguay'],
          ['CW','Uruguay'],['CX','Uruguay'],['CY0','Sable Island'],['CY9','St. Paul Island'],['D2','Angola'],
          ['D3','Angola'],['D4','Cape Verde'],['D6','Comoros'],['DA','Fed. Rep. of Germany'],
          ['DB','Fed. Rep. of Germany'],['DC','Fed. Rep. of Germany'],['DD','Fed. Rep. of Germany'],
          ['DE','Fed. Rep. of Germany'],['DF','Fed. Rep. of Germany'],['DG','Fed. Rep. of Germany'],
          ['DH','Fed. Rep. of Germany'],['DI','Fed. Rep. of Germany'],['DJ','Fed. Rep. of Germany'],
          ['DK','Fed. Rep. of Germany'],['DL','Fed. Rep. of Germany'],['DM','Fed. Rep. of Germany'],
          ['DN','Fed. Rep. of Germany'],['DO','Fed. Rep. of Germany'],['DP','Fed. Rep. of Germany'],
          ['DQ','Fed. Rep. of Germany'],['DR','Fed. Rep. of Germany'],['Y2','Fed. Rep. of Germany'],
          ['Y3','Fed. Rep. of Germany'],['Y4','Fed. Rep. of Germany'],['Y5','Fed. Rep. of Germany'],
          ['Y6','Fed. Rep. of Germany'],['Y7','Fed. Rep. of Germany'],['Y8','Fed. Rep. of Germany'],
          ['Y9','Fed. Rep. of Germany'],['4D','Philippines'],['4E','Philippines'],['4F','Philippines'],
          ['4G','Philippines'],['4H','Philippines'],['4I','Philippines'],['DU','Philippines'],['DV','Philippines'],
          ['DW','Philippines'],['DX','Philippines'],['DY','Philippines'],['DZ','Philippines'],['E3','Eritrea'],
          ['E4','Palestine'],['E5','South Cook Islands'],['E6','Niue'],['E7','Bosnia-Herzegovina'],['AM','Spain'],
          ['AN','Spain'],['AO','Spain'],['EA','Spain'],['EB','Spain'],['EC','Spain'],['ED','Spain'],['EE','Spain'],
          ['EF','Spain'],['EG','Spain'],['EH','Spain'],  ['AM6','Balearic Islands'],['AN6','Balearic Islands'],
          ['AO6','Balearic Islands'],['EA6','Balearic Islands'],['EB6','Balearic Islands'],['EC6','Balearic Islands'],
          ['ED6','Balearic Islands'],['EE6','Balearic Islands'],['EF6','Balearic Islands'],['EG6','Balearic Islands'],
          ['EH6','Balearic Islands'],['AM8','Canary Islands'],['AN8','Canary Islands'],['AO8','Canary Islands'],
          ['EA8','Canary Islands'],['EB8','Canary Islands'],['EC8','Canary Islands'],['ED8','Canary Islands'],
          ['EE8','Canary Islands'],['EF8','Canary Islands'],['EG8','Canary Islands'],['EH8','Canary Islands'],
          ['AM9','Ceuta & Melilla'],['AN9','Ceuta & Melilla'],['AO9','Ceuta & Melilla'],['EA9','Ceuta & Melilla'],
          ['EB9','Ceuta & Melilla'],['EC9','Ceuta & Melilla'],['ED9','Ceuta & Melilla'],['EE9','Ceuta & Melilla'],
          ['EF9','Ceuta & Melilla'],['EG9','Ceuta & Melilla'],['EH9','Ceuta & Melilla'],['EI','Ireland'],
          ['EJ','Ireland'],['EK','Armenia'],['5L','Liberia'],['5M','Liberia'],['6Z','Liberia'],['A8','Liberia'],
          ['D5','Liberia'],['EL','Liberia'],['9B','Iran'],['9C','Iran'],['9D','Iran'],['EP','Iran'],['EQ','Iran'],
          ['ER','Moldova'],['ES','Estonia'],['9E','Ethiopia'],['9F','Ethiopia'],['ET','Ethiopia'],['EU','Belarus'],
          ['EV','Belarus'],['EW','Belarus'],['EX','Kyrgyzstan'],['EY','Tajikistan'],['EZ','Turkmenistan'],
          ['F','France'],['HW','France'],['HX','France'],['HY','France'],['TH','France'],['TM','France'],
          ['TO','France'],['TP','France'],['TQ','France'],['TV','France'],['TX','France'],['FG','Guadeloupe'],
          ['FH','Mayotte'],['FJ','St. Barthelemy'],['FK','New Caledonia'],['FM','Martinique'],['FO','French Polynesia'],
          ['TX5N','Austral Islands'],['FP','St. Pierre & Miquelon'],['FR','Reunion Island'],['FS','St. Martin'],
          ['FT3G','Glorioso Islands'],['FT4G','Glorioso Islands'],['FT5G','Glorioso Islands'],['FT6G','Glorioso Islands'],
          ['FT7G','Glorioso Islands'],['FT8G','Glorioso Islands'],['FT9G','Glorioso Islands'],
          ['FT0E','Juan de Nova, Europa'],['FT0J','Juan de Nova, Europa'],['FT1E','Juan de Nova, Europa'],
          ['FT1J','Juan de Nova, Europa'],['FT2E','Juan de Nova, Europa'],['FT2J','Juan de Nova, Europa'],
          ['FT3E','Juan de Nova, Europa'],['FT3J','Juan de Nova, Europa'],['FT4E','Juan de Nova, Europa'],
          ['FT4J','Juan de Nova, Europa'],['FT6E','Juan de Nova, Europa'],['FT6J','Juan de Nova, Europa'],
          ['FT7E','Juan de Nova, Europa'],['FT7J','Juan de Nova, Europa'],['FT8E','Juan de Nova, Europa'],
          ['FT8J','Juan de Nova, Europa'],['FT9E','Juan de Nova, Europa'],['FT9J','Juan de Nova, Europa'],
          ['FT0T','Tromelin Island'],['FT1T','Tromelin Island'],['FT2T','Tromelin Island'],['FT3T','Tromelin Island'],
          ['FT4T','Tromelin Island'],['FT5T','Tromelin Island'],['FT6T','Tromelin Island'],['FT7T','Tromelin Island'],
          ['FT8T','Tromelin Island'],['FT9T','Tromelin Island'],['FT0W','Crozet Island'],['FT4W','Crozet Island'],
          ['FT5W','Crozet Island'],['FT8W','Crozet Island'],['FT0X','Kerguelen Islands'],['FT2X','Kerguelen Islands'],
          ['FT4X','Kerguelen Islands'],['FT5X','Kerguelen Islands'],['FT8X','Kerguelen Islands'],
          ['FT0Z','Amsterdam & St. Paul Is.'],['FT1Z','Amsterdam & St. Paul Is.'],['FT2Z','Amsterdam & St. Paul Is.'],
          ['FT3Z','Amsterdam & St. Paul Is.'],['FT4Z','Amsterdam & St. Paul Is.'],['FT5Z','Amsterdam & St. Paul Is.'],
          ['FT6Z','Amsterdam & St. Paul Is.'],['FT7Z','Amsterdam & St. Paul Is.'],['FT8Z','Amsterdam & St. Paul Is.'],
          ['FW','Wallis & Futuna Islands'],['TW','Wallis & Futuna Islands'],['FY','French Guiana'],['2E','England'],
          ['G','England'],['M','England'],['2D','Isle of Man'],['GD','Isle of Man'],['GT','Isle of Man'],
          ['MD','Isle of Man'],['MT','Isle of Man'],['2I','Northern Ireland'],['GI','Northern Ireland'],
          ['GN','Northern Ireland'],['MI','Northern Ireland'],['MN','Northern Ireland'],['2J','Jersey'],['GH','Jersey'],
          ['GJ','Jersey'],['MH','Jersey'],['MJ','Jersey'],['2A','Scotland'],['2M','Scotland'],['GM','Scotland'],
          ['GS','Scotland'],['MA','Scotland'],['MM','Scotland'],['MS','Scotland'],['2U','Guernsey'],['GP','Guernsey'],
          ['GU','Guernsey'],['MP','Guernsey'],['MU','Guernsey'],['2W','Wales'],['GC','Wales'],['GW','Wales'],
          ['MC','Wales'],['MW','Wales'],  ['H4','Solomon Islands'],['H40','Temotu Province'],['HA','Hungary'],
          ['HG','Hungary'],['HB','Switzerland'],['HE','Switzerland'],['HB0','Liechtenstein'],['HE0','Liechtenstein'],
          ['HC','Ecuador'],['HD','Ecuador'],['HC8','Galapagos Islands'],['HD8','Galapagos Islands'],['4V','Haiti'],
          ['HH','Haiti'],['HI','Dominican Republic'],['5J','Colombia'],['5K','Colombia'],['HJ','Colombia'],
          ['HK','Colombia'],['5J0','San Andres & Providencia'],['5K0','San Andres & Providencia'],
          ['HJ0','San Andres & Providencia'],['HK0','San Andres & Providencia'],['HJ0M','Malpelo Island'],
          ['HK0M','Malpelo Island'],['6K','Republic of Korea'],['6L','Republic of Korea'],['6M','Republic of Korea'],
          ['6N','Republic of Korea'],['D7','Republic of Korea'],['D8','Republic of Korea'],['D9','Republic of Korea'],
          ['DS','Republic of Korea'],['DT','Republic of Korea'],['HL','Republic of Korea'],['3E','Panama'],
          ['3F','Panama'],['H3','Panama'],['H8','Panama'],['H9','Panama'],['HO','Panama'],['HP','Panama'],
          ['HQ','Honduras'],['HR','Honduras'],['E2','Thailand'],['HS','Thailand'],['HV','Vatican City'],
          ['7Z','Saudi Arabia'],['8Z','Saudi Arabia'],['HZ','Saudi Arabia'],['4U','Italy'],['I','Italy'],
          ['IM0','Sardinia'],['IS','Sardinia'],['J2','Djibouti'],['J3','Grenada'],['J5','Guinea-Bissau'],
          ['J6','St. Lucia'],['J7','Dominica'],['J8','St. Vincent'],['7J','Japan'],['7K','Japan'],['7L','Japan'],
          ['7M','Japan'],['7N','Japan'],['8J','Japan'],['8K','Japan'],['8L','Japan'],['8M','Japan'],['8N','Japan'],
          ['JA','Japan'],['JE','Japan'],['JF','Japan'],['JG','Japan'],['JH','Japan'],['JI','Japan'],['JJ','Japan'],
          ['JK','Japan'],['JL','Japan'],['JM','Japan'],['JN','Japan'],['JO','Japan'],['JP','Japan'],['JQ','Japan'],
          ['JR','Japan'],['JS','Japan'],['JD1','Ogasawara'],['JT','Mongolia'],['JU','Mongolia'],['JV','Mongolia'],
          ['JW','Svalbard'],['JX','Jan Mayen'],['JY','Jordan'],['AA','United States'],['AB','United States'],
          ['AC','United States'],['AD','United States'],['AE','United States'],['AF','United States'],
          ['AG','United States'],['AI','United States'],['AJ','United States'],['AK','United States'],
          ['K','United States'],['N','United States'],['W','United States'],['4U1WB','United States'],
          ['AH0U','United States'],['AH0','Mariana Islands'],['KH0','Mariana Islands'],['NH0','Mariana Islands'],
          ['WH0','Mariana Islands'],['AH1','Baker & Howland Islands'],['KH1','Baker & Howland Islands'],
          ['NH1','Baker & Howland Islands'],['WH1','Baker & Howland Islands'],['AH2','Guam'],['KH2','Guam'],
          ['NH2','Guam'],['WH2','Guam'],['AH3','Johnston Island'],['KH3','Johnston Island'],['NH3','Johnston Island'],
          ['WH3','Johnston Island'],['AH4','Midway Island'],['KH4','Midway Island'],['NH4','Midway Island'],
          ['WH4','Midway Island'],['AH5','Palmyra & Jarvis Islands'],['KH5','Palmyra & Jarvis Islands'],
          ['NH5','Palmyra & Jarvis Islands'],['WH5','Palmyra & Jarvis Islands'],['AH6','Hawaii'],['AH7','Hawaii'],
          ['KH6','Hawaii'],['KH7','Hawaii'],['NH6','Hawaii'],['NH7','Hawaii'],['WH6','Hawaii'],['WH7','Hawaii'],
          ['AH8','American Samoa'],['KH8','American Samoa'],['NH8','American Samoa'],['WH8','American Samoa'],
          ['AH9','Wake Island'],['KH9','Wake Island'],['NH9','Wake Island'],['WH9','Wake Island'],['AL','Alaska'],
          ['KL','Alaska'],['NL','Alaska'],['WL','Alaska'],['KP1','Navassa Island'],['NP1','Navassa Island'],
          ['WP1','Navassa Island'],['KP2','US Virgin Islands'],['NP2','US Virgin Islands'],['WP2','US Virgin Islands'],
          ['K3BMG','US Virgin Islands'],['KP3','Puerto Rico'],['KP4','Puerto Rico'],['NP3','Puerto Rico'],
          ['NP4','Puerto Rico'],['WP3','Puerto Rico'],['WP4','Puerto Rico'],['KP5','Desecheo Island'],
          ['NP5','Desecheo Island'],['WP5','Desecheo Island'],['LA','Norway'],['LB','Norway'],['LC','Norway'],
          ['LD','Norway'],['LE','Norway'],['LF','Norway'],['LG','Norway'],['LH','Norway'],['LI','Norway'],
          ['LJ','Norway'],['LK','Norway'],['LL','Norway'],['LM','Norway'],['LN','Norway'],['AY','Argentina'],
          ['AZ','Argentina'],['L1','Argentina'],['L2','Argentina'],['L3','Argentina'],['L4','Argentina'],
          ['L5','Argentina'],['L6','Argentina'],['L7','Argentina'],['L8','Argentina'],['L9','Argentina'],
          ['LO','Argentina'],['LP','Argentina'],['LQ','Argentina'],['LR','Argentina'],['LS','Argentina'],
          ['LT','Argentina'],['LU','Argentina'],['LV','Argentina'],['LW','Argentina'],['LX','Luxembourg'],
          ['LY','Lithuania'],['LZ','Bulgaria'],['4T','Peru'],['OA','Peru'],['OB','Peru'],['OC','Peru'],
          ['OD','Lebanon'],['OE','Austria'],['C7A','Austria'],['OF','Finland'],['OG','Finland'],['OH','Finland'],
          ['OI','Finland'],['OJ','Finland'],['OF0','Aland Islands'],['OG0','Aland Islands'],['OH0','Aland Islands'],
          ['OI0','Aland Islands'],['OJ0','Market Reef'],['OK','Czech Republic'],['OL','Czech Republic'],
          ['OM','Slovak Republic'],['ON','Belgium'],['OO','Belgium'],['OP','Belgium'],['OQ','Belgium'],
          ['OR','Belgium'],['OS','Belgium'],['OT','Belgium'],['OX','Greenland'],['XP','Greenland'],
          ['OW','Faroe Islands'],['OY','Faroe Islands'],['5P','Denmark'],['5Q','Denmark'],['OU','Denmark'],
          ['OV','Denmark'],['OZ','Denmark'],['P2','Papua New Guinea'],['P4','Aruba'],['P5','DPR of Korea'],
          ['P6','DPR of Korea'],['P7','DPR of Korea'],['P8','DPR of Korea'],['P9','DPR of Korea'],
          ['PA','Netherlands'],['PB','Netherlands'],['PC','Netherlands'],['PD','Netherlands'],['PE','Netherlands'],
          ['PF','Netherlands'],['PG','Netherlands'],['PH','Netherlands'],['PI','Netherlands'],['PJ2','Curacao'],
          ['PJ4','Bonaire'],['PJ5','Saba & St. Eustatius'],['PJ6','Saba & St. Eustatius'],['PJ0','Sint Maarten'],
          ['PJ7','Sint Maarten'],['PJ8','Sint Maarten'],['PP','Brazil'],['PQ','Brazil'],['PR','Brazil'],
          ['PS','Brazil'],['PT','Brazil'],['PU','Brazil'],['PV','Brazil'],['PW','Brazil'],['PX','Brazil'],
          ['PY','Brazil'],['ZV','Brazil'],['ZW','Brazil'],['ZX','Brazil'],['ZY','Brazil'],['ZZ','Brazil'],
          ['PP0F','Fernando de Noronha'],['PZ','Suriname'],['RI1F','Franz Josef Land'],['S0','Western Sahara'],
          ['S2','Bangladesh'],['S3','Bangladesh'],['S5','Slovenia'],['S7','Seychelles'],['S9','Sao Tome & Principe'],
          ['7S','Sweden'],['8S','Sweden'],['SA','Sweden'],['SB','Sweden'],['SC','Sweden'],['SD','Sweden'],
          ['SE','Sweden'],['SF','Sweden'],['SG','Sweden'],['SH','Sweden'],['SI','Sweden'],['SJ','Sweden'],
          ['SK','Sweden'],['SL','Sweden'],['SM','Sweden'],['3Z','Poland'],['HF','Poland'],['SN','Poland'],
          ['SO','Poland'],['SP','Poland'],['SQ','Poland'],['SR','Poland'],['6T','Sudan'],['6U','Sudan'],
          ['ST','Sudan'],['6A','Egypt'],['6B','Egypt'],['SS','Egypt'],['SU','Egypt'],['J4','Greece'],
          ['SV','Greece'],['SW','Greece'],['SX','Greece'],['SY','Greece'],['SZ','Greece'],['J45','Dodecanese'],
          ['SV5','Dodecanese'],['SW5','Dodecanese'],['SX5','Dodecanese'],['SY5','Dodecanese'],['SZ5','Dodecanese'],
          ['J49','Crete'],['SV9','Crete'],['SW9','Crete'],['SX9','Crete'],['SY9','Crete'],['SZ9','Crete'],
          ['T2','Tuvalu'],['T30','Western Kiribati'],['T31','Central Kiribati'],['T32','Eastern Kiribati'],
          ['T33','Banaba Island'],['6O','Somalia'],['T5','Somalia'],['T7','San Marino'],['T8','Palau'],
          ['TA','Asiatic Turkey'],['TB','Asiatic Turkey'],['TC','Asiatic Turkey'],['YM','Asiatic Turkey'],
          ['TF','Iceland'],['TD','Guatemala'],['TG','Guatemala'],['TE','Costa Rica'],['TI','Costa Rica'],
          ['TE9','Cocos Island'],['TI9','Cocos Island'],['TJ','Cameroon'],['TK','Corsica'],
          ['TL','Central African Republic'],['TN','Republic of the Congo'],['TR','Gabon'],['TT','Chad'],
          ['TU', 'Cote d\'Ivoire'],['TY','Benin'],['TZ','Mali'],['R','European Russia'],['U','European Russia'],
          ['R8F','European Russia'],['R8G','European Russia'],['R8X','European Russia'],['R9F','European Russia'],
          ['R9G','European Russia'],['R9X','European Russia'],['RA2','Kaliningrad'],['U2F','Kaliningrad'],
          ['U2K','Kaliningrad'],['UA2','Kaliningrad'],['UB2','Kaliningrad'],['UC2','Kaliningrad'],
          ['UD2','Kaliningrad'],['UE2','Kaliningrad'],['UF2','Kaliningrad'],['UG2','Kaliningrad'],
          ['UH2','Kaliningrad'],['UI2','Kaliningrad'],['R0','Asiatic Russia'],['R8','Asiatic Russia'],
          ['R9','Asiatic Russia'],['RA0','Asiatic Russia'],['RA8','Asiatic Russia'],['RA9','Asiatic Russia'],
          ['RC0','Asiatic Russia'],['RC8','Asiatic Russia'],['RC9','Asiatic Russia'],['RD0','Asiatic Russia'],
          ['RD8','Asiatic Russia'],['RD9','Asiatic Russia'],['RE0','Asiatic Russia'],['RE8','Asiatic Russia'],
          ['RE9','Asiatic Russia'],['RF0','Asiatic Russia'],['RF8','Asiatic Russia'],['RF9','Asiatic Russia'],
          ['RG0','Asiatic Russia'],['RG8','Asiatic Russia'],['RG9','Asiatic Russia'],['RI0','Asiatic Russia'],
          ['RI8','Asiatic Russia'],['RI9','Asiatic Russia'],['RJ0','Asiatic Russia'],['RJ8','Asiatic Russia'],
          ['RJ9','Asiatic Russia'],['RK0','Asiatic Russia'],['RK8','Asiatic Russia'],['RK9','Asiatic Russia'],
          ['RL0','Asiatic Russia'],['RL8','Asiatic Russia'],['RL9','Asiatic Russia'],['RM0','Asiatic Russia'],
          ['RM8','Asiatic Russia'],['RM9','Asiatic Russia'],['RN0','Asiatic Russia'],['RN8','Asiatic Russia'],
          ['RN9','Asiatic Russia'],['RO0','Asiatic Russia'],['RO8','Asiatic Russia'],['RO9','Asiatic Russia'],
          ['RQ0','Asiatic Russia'],['RQ8','Asiatic Russia'],['RQ9','Asiatic Russia'],['RT0','Asiatic Russia'],
          ['RT8','Asiatic Russia'],['RT9','Asiatic Russia'],['RU0','Asiatic Russia'],['RU8','Asiatic Russia'],
          ['RU9','Asiatic Russia'],['RV0','Asiatic Russia'],['RV8','Asiatic Russia'],['RV9','Asiatic Russia'],
          ['RW0','Asiatic Russia'],['RW8','Asiatic Russia'],['RW9','Asiatic Russia'],['RX0','Asiatic Russia'],
          ['RX8','Asiatic Russia'],['RX9','Asiatic Russia'],['RY0','Asiatic Russia'],['RY8','Asiatic Russia'],
          ['RY9','Asiatic Russia'],['RZ0','Asiatic Russia'],['RZ8','Asiatic Russia'],['RZ9','Asiatic Russia'],
          ['U0','Asiatic Russia'],['U8','Asiatic Russia'],['U9','Asiatic Russia'],['UA0','Asiatic Russia'],
          ['UA8','Asiatic Russia'],['UA9','Asiatic Russia'],['UB0','Asiatic Russia'],['UB8','Asiatic Russia'],
          ['UB9','Asiatic Russia'],['UC0','Asiatic Russia'],['UC8','Asiatic Russia'],['UC9','Asiatic Russia'],
          ['UD0','Asiatic Russia'],['UD8','Asiatic Russia'],['UD9','Asiatic Russia'],['UE0','Asiatic Russia'],
          ['UE8','Asiatic Russia'],['UE9','Asiatic Russia'],['UF0','Asiatic Russia'],['UF8','Asiatic Russia'],
          ['UF9','Asiatic Russia'],['UG0','Asiatic Russia'],['UG8','Asiatic Russia'],['UG9','Asiatic Russia'],
          ['UH0','Asiatic Russia'],['UH8','Asiatic Russia'],['UH9','Asiatic Russia'],['UI0','Asiatic Russia'],
          ['UI8','Asiatic Russia'],['UI9','Asiatic Russia'],['UJ','Uzbekistan'],['UK','Uzbekistan'],
          ['UL','Uzbekistan'],['UM','Uzbekistan'],['UN','Kazakhstan'],['UO','Kazakhstan'],['UP','Kazakhstan'],
          ['UQ','Kazakhstan'],['EM','Ukraine'],['EN','Ukraine'],['EO','Ukraine'],['U5','Ukraine'],['UR','Ukraine'],
          ['US','Ukraine'],['UT','Ukraine'],['UU','Ukraine'],['UV','Ukraine'],['UW','Ukraine'],['UX','Ukraine'],
          ['UY','Ukraine'],['UZ','Ukraine'],['V2','Antigua & Barbuda'],['V3','Belize'],['V4','St. Kitts & Nevis'],
          ['V5','Namibia'],['V6','Micronesia'],['V7','Marshall Islands'],['V8','Brunei Darussalam'],['CF','Canada'],
          ['CG','Canada'],['CJ','Canada'],['CK','Canada'],['VA','Canada'],['VB','Canada'],['VC','Canada'],
          ['VE','Canada'],['VG','Canada'],['VX','Canada'],['VY9','Canada'],['XL','Canada'],['XM','Canada'],
          ['CH1','Canada'],['CH2','Canada'],['CI0','Canada'],['CI1','Canada'],['CI2','Canada'],['CY1','Canada'],
          ['CY2','Canada'],['CZ0','Canada'],['CZ1','Canada'],['CZ2','Canada'],['VD1','Canada'],['VD2','Canada'],
          ['VF1','Canada'],['VF2','Canada'],['VO1','Canada'],['VO2','Canada'],['VY0','Canada'],['VY1','Canada'],
          ['VY2','Canada'],['XJ1','Canada'],['XJ2','Canada'],['XK0','Canada'],['XK1','Canada'],['XK2','Canada'],
          ['XN1','Canada'],['XN2','Canada'],['XO0','Canada'],['XO1','Canada'],['XO2','Canada'],
          ['VER20221027','Canada'],['AX','Australia'],['VI','Australia'],['VJ','Australia'],['VK','Australia'],
          ['VL','Australia'],['AX9','Norfolk Island'],['VI9','Norfolk Island'],['VK9','Norfolk Island'],
          ['VP5','Turks & Caicos Islands'],['VQ5','Turks & Caicos Islands'],['VP6','Pitcairn Island'],
          ['VP8','Falkland Islands'],['CE9','South Shetland Islands'],['XR9','South Shetland Islands'],
          ['VP9','Bermuda'],['VQ9','Chagos Islands'],['VR','Hong Kong'],['8T','India'],['8U','India'],
          ['8V','India'],['8W','India'],['8X','India'],['8Y','India'],['AT','India'],['AU','India'],
          ['AV','India'],['AW','India'],['VT','India'],['VU','India'],['VV','India'],['VW','India'],
          ['VU4','Andaman & Nicobar Is.'],['VU7','Lakshadweep Islands'],['4A','Mexico'],['4B','Mexico'],
          ['4C','Mexico'],['6D','Mexico'],['6E','Mexico'],['6F','Mexico'],['6G','Mexico'],['6H','Mexico'],
          ['6I','Mexico'],['6J','Mexico'],['XA','Mexico'],['XB','Mexico'],['XC','Mexico'],['XD','Mexico'],
          ['XE','Mexico'],['XF','Mexico'],['XG','Mexico'],['XH','Mexico'],['XI','Mexico'],['4A4','Revillagigedo'],
          ['4B4','Revillagigedo'],['4C4','Revillagigedo'],['6D4','Revillagigedo'],['6E4','Revillagigedo'],
          ['6F4','Revillagigedo'],['6G4','Revillagigedo'],['6H4','Revillagigedo'],['6I4','Revillagigedo'],
          ['6J4','Revillagigedo'],['XA4','Revillagigedo'],['XB4','Revillagigedo'],['XC4','Revillagigedo'],
          ['XD4','Revillagigedo'],['XE4','Revillagigedo'],['XF4','Revillagigedo'],['XG4','Revillagigedo'],
          ['XH4','Revillagigedo'],['XI4','Revillagigedo'],['XT','Burkina Faso'],['XU','Cambodia'],['XW','Laos'],
          ['XX9','Macao'],['XY','Myanmar'],['XZ','Myanmar'],['T6','Afghanistan'],['YA','Afghanistan'],
          ['7A','Indonesia'],['7B','Indonesia'],['7C','Indonesia'],['7D','Indonesia'],['7E','Indonesia'],
          ['7F','Indonesia'],['7G','Indonesia'],['7H','Indonesia'],['7I','Indonesia'],['8A','Indonesia'],
          ['8B','Indonesia'],['8C','Indonesia'],['8D','Indonesia'],['8E','Indonesia'],['8F','Indonesia'],
          ['8G','Indonesia'],['8H','Indonesia'],['8I','Indonesia'],['PK','Indonesia'],['PL','Indonesia'],
          ['PM','Indonesia'],['PN','Indonesia'],['PO','Indonesia'],['YB','Indonesia'],['YC','Indonesia'],
          ['YD','Indonesia'],['YE','Indonesia'],['YF','Indonesia'],['YG','Indonesia'],['YH','Indonesia'],
          ['HN','Iraq'],['YI','Iraq'],['YJ','Vanuatu'],['6C','Syria'],['YK','Syria'],['YL','Latvia'],
          ['H6','Nicaragua'],['H7','Nicaragua'],['HT','Nicaragua'],['YN','Nicaragua'],['YO','Romania'],
          ['YP','Romania'],['YQ','Romania'],['YR','Romania'],['HU','El Salvador'],['YS','El Salvador'],
          ['YT','Serbia'],['YU','Serbia'],['4M','Venezuela'],['YV','Venezuela'],['YW','Venezuela'],
          ['YX','Venezuela'],['YY','Venezuela'],['4M0','Aves Island'],['YV0','Aves Island'],['YW0','Aves Island'],
          ['YX0','Aves Island'],['YY0','Aves Island'],['Z2','Zimbabwe'],['Z3','North Macedonia'],
          ['Z6','Republic of Kosovo'],['Z8','Republic of South Sudan'],['ZA','Albania'],['ZB','Gibraltar'],
          ['ZG','Gibraltar'],['ZC4','UK Base Areas on Cyprus'],['ZD7','St. Helena'],['ZD8','Ascension Island'],
          ['ZD9','Tristan da Cunha & Gough'],['ZF','Cayman Islands'],['ZK3','Tokelau Islands'],['ZK','New Zealand'],
          ['ZL','New Zealand'],['ZL50','New Zealand'],['ZM','New Zealand'],['ZL7','Chatham Islands'],
          ['ZM7','Chatham Islands'],['ZL8','Kermadec Islands'],['ZM8','Kermadec Islands'],
          ['ZL9','N.Z. Subantarctic Is.'],['ZP','Paraguay'],['H5','South Africa'],['S4','South Africa'],
          ['S8','South Africa'],['V9','South Africa'],['ZR','South Africa'],['ZS','South Africa'],
          ['ZT','South Africa'],['ZU','South Africa'],['ZR8','Pr. Edward & Marion Is.'],
          ['ZS8','Pr. Edward & Marion Is.'],['ZT8','Pr. Edward & Marion Is.'],['ZU8','Pr. Edward & Marion']]

def call_country(call):
    print('Looking up country for: '+str(call))
    global prefixes
    cty=list(sorted(list(filter(lambda n: call.upper().find(n[0])==0,prefixes)),key=lambda x: len(x[0]),reverse=True))
    print(cty)
    if(len(cty)>0):
        return(cty[0][1])
    else:
        return(False)

def call_info(call):
    print('Looking up info for: '+call)
    global calls
    if(call in calls):
        return(', '.join(calls[call]))
    else:
        return(False)

def call_friend(call):
    print('Looking up friend for: '+call)
    if(call in friends):
        return(friends[call])
    else:
        return(False)

def main_page ():
    global css
    doc, tag, text=Doc().tagtext()
    with tag('html', lang='en'):
        with tag('head'):
            with tag('style'):
                text(css)
        with tag('body'):
            with open('monitor.js','r') as file:
                js=file.read()
            with tag('script', type='text/javascript'):
                doc.asis(js)
            with tag('div', id='wrapper'):
                with tag('h1'):
                    text('Stations')
                with tag('table', id='stations', klass='styled-table'):
                    pass
                with tag('br'):
                    pass
                with tag('h1'):
                    text('Traffic')
                with tag('table', id='traffic', klass='styled-table'):
                    pass
                with tag('br'):
                    pass
                with tag('a', href='https://github.com/jfrancis42/js8net', target='_blank'):
                    text('js8net')
                text(' by ')
                with tag('a', href='https://www.qrz.com/db/N0GQ', target='_blank'):
                    text('N0GQ')
                with tag('br'):
                    pass
    return(doc.getvalue())

def missing_page ():
    doc, tag, text=Doc().tagtext()
    global refresh
    with tag('html', lang='en'):
        with tag('body'):
            with tag('div', id='wrapper'):
                text('This page does not exist...')
    return(doc.getvalue())

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global traffic
        global traffic_lock
        global stations
        global stations_lock
        global version
        doc, tag, text=Doc().tagtext()
        if(self.path=='/'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(main_page()))
        elif(self.path=='/sms.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/sms.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/gears.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/gears.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/ar.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/ar.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/chess.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/chess.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/gps.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/gps.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/amrron.jpg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            with open('images/amrron.jpg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/sota.jpg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            with open('images/sota.jpg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/pota.jpg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            with open('images/pota.jpg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/ahrn.jpg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            with open('images/ahrn.jpg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/key.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/key.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/zombie.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/zombie.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/mail.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/mail.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/heartbeat.svg'):
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            with open('images/heartbeat.svg','r') as file:
                img=file.read()
            self.wfile.write(str.encode(img))
        elif(self.path=='/colors'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str.encode(json.dumps(colors)))
        elif(self.path=='/stations'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with stations_lock:
                self.wfile.write(str.encode(json.dumps(stations)))
        elif(self.path=='/traffic'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with traffic_lock:
                self.wfile.write(str.encode(json.dumps(list(filter(lambda r: r['type']=='RX.DIRECTED',traffic)))))
        elif(self.path=='/favicon.ico'):
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(missing_page()))

    def do_POST(self):
        global traffic
        global traffic_lock
        global stations
        global stations_lock
        global listen
        global error
        global commands
        global calls
        global prefixes
        global id
        content_length=int(self.headers['Content-Length'])
        payload=self.rfile.read(content_length).decode('utf8')
        j=json.loads(payload)
        print('payload: '+payload)
        if(self.path=='/cmd'):
            with commands_lock:
                self.send_response(200)
                self.end_headers()
                print(commands.keys())
                commands[j['uuid']].put(j)
        if(self.path=='/traffic'):
            self.send_response(200)
            self.end_headers()
            if('traffic' in j):
                if('uuid' in j['traffic']):
                    id=id+1
                    print('Traffic from '+j['traffic']['uuid'])
                    rx=j['traffic']
                    if('FROM' in rx['params']):
                        fmcall=rx['params']['FROM'].split('/')[0]
                    else:
                        fmcall=False
                    if('TO' in rx['params']):
                        tocall=rx['params']['TO'].split('/')[0]
                    else:
                        tocall=False
                    if(tocall):
                        if(tocall[0]=='@'):
                            toat=True
                        else:
                            toat=False
                    else:
                        toat=False
                    rx['id']='trf_'+str(id)
                    rx['from_call']=fmcall
                    rx['to_call']=tocall
                    rx['to_at']=toat
                    if(fmcall and 'GRID' in rx['params']): # don't sub a less accurate grid
                        if(rx['params']['GRID']!=''):
                            if(fmcall in grids):
                                if(rx['params']['GRID'] in grids):
                                    pass
                                else:
                                    grids[fmcall]=rx['params']['GRID']
                            else:
                                grids[fmcall]=rx['params']['GRID']
                        elif(fmcall in grids):
                            rx['params']['GRID']=grids[fmcall]
                    if(fmcall and 'TEXT' in rx['params']):
                        tmp=rx['params']['TEXT'].split()
                        if(len(tmp)>3):
                            if(tmp[2]=='GRID'):
                                if(error in tmp[3]):
                                    pass
                                else:
                                    grids[fmcall]=tmp[3]
                    if(rx['type']=='RX.DIRECTED'):
                        rx['from_country']=call_country(fmcall)
                        if(tocall and not(toat)):
                            rx['to_country']=call_country(tocall)
                        else:
                            rx['to_country']=False
                        if(calls):
                            if(fmcall):
                                rx['from_info']=call_info(fmcall)
                            else:
                                rx['from_info']=False
                            if(tocall and not(toat)):
                                rx['to_info']=call_info(tocall)
                            else:
                                rx['to_info']=False
                        else:
                            rx['from_info']=False
                            rx['to_info']=False
                        if(friends):
                            rx['from_friend']=call_friend(fmcall)
                            if(tocall and not(toat)):
                                rx['to_friend']=call_friend(tocall)
                            else:
                                rx['to_friend']=False
                        else:
                            rx['from_friend']=False
                            rx['to_friend']=False
                        if('SNR' in rx['params']):
                            rx['snr']=rx['params']['SNR']
                        else:
                            rx['snr']=False
                        if('SPEED' in rx['params']):
                            rx['speed']=rx['params']['SPEED']
                        else:
                            rx['speed']=False
                        if('FREQ' in rx['params']):
                            rx['freq']=rx['params']['FREQ']
                        else:
                            rx['freq']=False
                        if('TEXT' in rx['params']):
                            rx['text']=rx['params']['TEXT']
                        else:
                            rx['text']=False
                        if(fmcall in grids):
                            rx['grid']=grids[fmcall]
                            if(len(rx['grid'])>8):
                                (lat,lon)=mh.to_location(rx['grid'][0:8])
                            else:
                                (lat,lon)=mh.to_location(rx['grid'])
                            rx['lat']=lat
                            rx['lon']=lon
                        else:
                            rx['grid']=False
                    with traffic_lock:
                        traffic.append(rx)
        if(self.path=='/station'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            if('station' in j):
                if('uuid' in j['station']):
                    print('Station info from '+j['station']['uuid'])
                    with commands_lock:
                        if(j['station']['uuid'] in commands):
                            pass
                        else:
                            commands[j['station']['uuid']]=Queue()
                    with stations_lock:
                        if('grid' in j['station']):
                            if(j['station']['grid']!=''):
                                if(len(j['station']['grid'])>8):
                                    (lat,lon)=mh.to_location(j['station']['grid'][0:8])
                                else:
                                    (lat,lon)=mh.to_location(j['station']['grid'])
                                j['station']['lat']=lat
                                j['station']['lon']=lon
                        stations[j['station']['uuid']]=j['station']
            flag=False
            with commands_lock:
                print('-=-=-=-=-=-=-=-=-')
                for k in commands.keys():
                    print(k)
                    print(list(commands[k].queue))
                print('-=-=-=-=-=-=-=-=-')
                if(commands[j['station']['uuid']].empty()):
                    pass
                else:
                    msg=commands[j['station']['uuid']].get()
                    if('cmd' in msg and 'uuid' in msg):
                        flag=True
            if(flag):
                self.wfile.write(str.encode(json.dumps(msg)))
            else:
                print('Sending null command...')
                self.wfile.write(str.encode(json.dumps({'cmd':False})))

def housekeeping_thread(name):
    global traffic
    global traffic_lock
    global stations
    global stations_lock
    global max_age
    global commands
    global commands_lock
    while(True):
        time.sleep(31)
        now=time.time()
        with traffic_lock:
            traffic=list(filter(lambda n: n['time'] > now-max_age,traffic))
            f=open('/tmp/traffic.json','w')
            f.write(json.dumps(traffic))
            f.write('\n')
            f.close()
        with stations_lock:
            for u in list(stations.keys()):
                if(stations[u]['time'] < now-max_age):
                    del(stations[u])
            f=open('/tmp/stations.json','w')
            f.write(json.dumps(stations))
            f.write('\n')
            f.close()

def housekeeping_thread(name):
    global traffic
    global traffic_lock
    global stations
    global stations_lock
    global max_age
    global commands
    global commands_lock
    while(True):
        time.sleep(31)
        now=time.time()
        with traffic_lock:
            traffic=list(filter(lambda n: n['time'] > now-max_age,traffic))
            f=open('/tmp/traffic.json','w')
            f.write(json.dumps(traffic))
            f.write('\n')
            f.close()
        with stations_lock:
#            for u in list(stations.keys()):
#                if(stations[u]['time'] < now-max_age):
#                    del(stations[u])
            f=open('/tmp/stations.json','w')
            f.write(json.dumps(stations))
            f.write('\n')
            f.close()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Main program.
if(__name__ == '__main__'):
    parser=argparse.ArgumentParser(description='Aggregate collected JS8call data from collectors.')
    parser.add_argument('--listen',default=False,help='Listen port for collector traffic (default 8000)')
    parser.add_argument('--max_age',default=False,help='Maximum traffic age (default 3600 seconds)')
    parser.add_argument('--localhost',default=False,help='Bind to localhost only (default 0.0.0.0)',
                        action='store_true')

    args=parser.parse_args()

    if(args.listen):
        listen=int(args.listen)
    else:
        listen=8000
    print('Listening on port: '+str(listen))

    if(args.max_age):
        max_age=int(args.max_age)
    else:
        max_age=3600
    print('Max age: '+str(max_age))

    if(args.localhost):
        localhost=True
    else:
        localhost=False

    if(exists('/tmp/traffic.json')):
        print('Loading cached traffic...')
        with traffic_lock:
            f=open('/tmp/traffic.json')
            traffic=json.load(f)
            f.close()
    else:
        print('Cached traffic file not found...')
    print('Done.')

    if(exists('/tmp/stations.json')):
        print('Loading cached station info...')
        with stations_lock:
            f=open('/tmp/stations.json')
            stations=json.load(f)
            f.close()
    else:
        print('Cached station info file not found...')
    print('Done.')
    
    thread0=Thread(target=housekeeping_thread,args=('Housekeeping Thread',),daemon=True)
    thread0.start()
    
    calls={}
    if(exists('EN.dat')):
        print('Loading callsign records...')
        with open('EN.dat', 'r', encoding='utf8') as ham_file:
            ham_reader=csv.reader(ham_file, delimiter='|')
            for row in ham_reader:
                call=row[4]
                name=row[7]
                city=row[16]
                state=row[17]
                calls[call]=[name,city,state]
    else:
        print('EN.dat not found, no loading callsign records...')
    print('Done.')

    prefixes=[]
    if(exists('arrl.cty')):
        print('Loading country prefixes...')
        country=False
        cty=open('arrl.cty', 'r', encoding='utf8')
        for line in cty:
            if(line[0]!='&'):
                tmp=line.split(':')
                country=tmp[0]
                tmp=line.strip()[38:].split(';')
                pf=tmp[0].split(',')
                for p in pf:
                    prefixes.append([p,country])
            else:
                tmp=line.strip()[38:].split(';')
                pf=tmp[0].split(',')
                for p in pf:
                    prefixes.append([p,country])
    else:
        print('EN.dat not found, no loading callsign records...')
    print('Done.')

    friends={}
    if(exists('friends.dat')):
        print('Loading friend records...')
        with open('friends.dat', 'r', encoding='utf8') as friend_file:
            friend_reader=csv.reader(friend_file, delimiter=',')
            for row in friend_reader:
                call=row[0].upper()
                name=row[1]
                color=row[2]
                friends[call]=[name,color]
    else:
        print('No friends found...')
    print('Done.')

#    pdb.set_trace()
    if(localhost):
        print('Running web server on localhost only...')
        httpd=HTTPServer(('127.0.0.1', listen), SimpleHTTPRequestHandler)
    else:
        print('Running web server on all interfaces...')
        httpd=HTTPServer(('0.0.0.0', listen), SimpleHTTPRequestHandler)
    httpd.serve_forever()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
