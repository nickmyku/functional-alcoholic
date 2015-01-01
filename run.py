from flask import Flask, render_template
execfile("/home/pi/functional-alcoholic/beer.py")

app = Flask(__name__)

PORT = 80

@app.route('/')
def keg_check():
	global v_offset
	global samples
	global conv_fact

	message_txt = [	"We regret to inform you that your life is over as you know it... your keg is now empty",
			"It would appear that your keg was mortally wounded and has lost a lot of fluid, we advice you get your keg to a medical professional at your earliest convenience",
			"Looks like your keg isn't in the best shape... you should take care of that",
			"So you still have a lot of beer left, but honestly is \"a lot\" really good enough for you?",
			"Your keg is in good shape... for now... we'll be watching you.",
			"Congradulations! its a keg!" ]

	n = getKegState("quarter")
	v = getVoltage(samples)
	w_lbs = toWeight(v,v_offset,conv_fact)
	w_kg = w_lbs/2.20462	# convert current weight to kilos	
	min_weight_kg = min_weight/2.2046	# convert min keg weight to kilos

	# print state of keg
	print "%d/5 of keg remaining (%.3f kg)" % (n,w_kg)  

	# if the state number is larger then the number of elements in array
	# ensure it doesnt address an element that doesnt exist
	if(n > len(message_txt)):
		n = len(message_txt)
	# make sure state number is not negative
	elif(n < 0):
		n = 0

	# render the webpage and pass variables to it
	return render_template("keg.html", state = n, text = message_txt[n], pounds = int(w_lbs - min_weight), kilos = int(w_kg - min_weight_kg))
	
		
if __name__ == '__main__':
	app.run(host='0.0.0.0', port = PORT)

