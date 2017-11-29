#! /usr/bin/env python2
# -*- coding: utf-8 -*-

# Music from datasets
# by hordia
# Anomalia: Climate change visibility from estimated land-surface average temperature since 1750 to nowadays

import csv
import OSC
import time

# cloud_instrument$ python CloudInstrument.py 
print("API-Cultor Cloud Instrument must be running (OSC port 9001)") 

def registro_val(dictname, new_year, rowvalue):
	value = rowvalue
	if value.strip()=="NaN":
		value = 0
	value = abs( float(value) )
	try:
		dictname[new_year] += value
	except:
		dictname[new_year] = value

CANT = 12*3 -1 # 3 años
obra_mensual = dict() #registro mensual
obra_anual = dict() #registro anual
obra_cinco = dict() #registro 5 años
obra_diez = dict() #registro 10 años
obra_veinte = dict() #registro 20 años
with open('./Complete_TAVG_complete.csv', 'r') as csvfile:
	 spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	 first = True
	 year = -1
	 counter = CANT
	 for row in spamreader:
		if not first:
			if counter==CANT:
				new_year = int( row[0] )
				counter = 0

			#registro mensual
			registro_val(obra_mensual,new_year,row[2])

			#registro anual
			registro_val(obra_anual,new_year,row[4])
			
			#registro cinco
			registro_val(obra_cinco,new_year,row[6])

			#registro diez
			registro_val(obra_diez,new_year,row[8])
			
			#registro 20
			registro_val(obra_veinte,new_year,row[10])
			
			counter += 1
		else:
			 first = False

def send_osc(voice_number=1, duration=10, pitch_centroid=0, complexity=0, inharmonicity=0):
	#sends OSC to API-Cultor Cloud Instrument (which synths with supercollider)

	osc_client = OSC.OSCClient()
	osc_client.connect( ( '127.0.0.1', 9001 ) )

	#voice config
	msg = OSC.OSCMessage()
	msg.setAddress('/set_voices')
	msg.append( float(voice_number) )
	msg.append( 1 ) # enabled
	osc_client.send(msg)

	#duration
	msg = OSC.OSCMessage()
	msg.setAddress('/mir/duration')
	msg.append( duration )
	osc_client.send(msg)

	#pitch centroid
	msg = OSC.OSCMessage()
	msg.setAddress('/mir/pitch_centroid/mean')
	msg.append( pitch_centroid )
	osc_client.send(msg)
	
	#complexity
	msg = OSC.OSCMessage()
	msg.setAddress('/mir/spectral_complexity/mean')
	msg.append( complexity )
	osc_client.send(msg)

	#inharmonicity
	msg = OSC.OSCMessage()
	msg.setAddress('/mir/inharmonicity/mean')
	msg.append( inharmonicity )
	osc_client.send(msg)

	#retrieve a new sound
	msg = OSC.OSCMessage()
	msg.setAddress('/retrieve')
	msg.append( 1 )
	osc_client.send(msg)
#()

def calc_proyeccion(value,maxvalue):
	return float(value/maxvalue)

def calc_max(obra):
	max_value = 0
	for year,value in obra.iteritems():
		new_value = float(value)
		if new_value>max_value:
			max_value = new_value
	return max_value

#Máximo anual 
max_mensual = calc_max(obra_mensual)
max_anual = calc_max(obra_anual)
max_cinco = calc_max(obra_cinco)
max_diez = calc_max(obra_diez)
max_veinte = calc_max(obra_veinte)

umbral_disparo_mensual = 28 
# umbral_disparo_anual = 14
segundo = 0
disparo_anterior = False
voice = 0
for year,value in obra_mensual.iteritems():
	# print(year,value)
	if value>umbral_disparo_mensual and not disparo_anterior:
		pitch_centroid_val = calc_proyeccion(obra_anual[year],max_anual)
		complexity_val = calc_proyeccion(obra_veinte[year],max_veinte)
		inharmonicity_val = calc_proyeccion(obra_cinco[year],max_cinco)
		print(
			"T: %s // \
EVENTO: %s // \
MIR: PitchCentroid: %f, Complexity: %f, Inharmonicity: %f\
			"%( segundo,
				"Disparo sonido",
				pitch_centroid_val,
				complexity_val,
				inharmonicity_val
			)
		)
		max_duration = 30 #in seconds
		send_osc(voice, max_duration, pitch_centroid_val, complexity_val, inharmonicity_val )
		voice += 1
		if voice==9:
			voice = 1
		disparo_anterior = True
		time.sleep(1) #sleep X segundo(s) (time pass)
	else:
		print("T: %s"%(segundo) )
		time.sleep(1) #sleep un segundo (time pass)
		disparo_anterior = False

	segundo += 1



print("Max mensual (c/3) %f"%max_mensual)
print("Max anual %f"%max_anual)
print("Max 5 %f"%max_cinco)
print("Max 10 %f"%max_diez)
print("Max 20 %f"%max_veinte)
