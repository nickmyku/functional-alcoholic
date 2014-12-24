from flask import Flask, render_template
execfile("beer.py")

app = Flask(__name__)

PORT = 80

@app.route('/')
def keg_check():
	global v_offset
	global samples
	global conv_fact

	n = getKegState("quarter")
	v = getVoltage(samples)
	w = toWeight(v,v_offset,conv_fact)
	
	print "%d/5 of keg remaining (%.3f lbs)" % (n,w)  
	if n == 0:
			return render_template('keg_0.html')
	elif n == 1:
			return render_template('keg_1.html')
	elif n == 2:
			return render_template('keg_2.html')
	elif n == 3:
			return render_template('keg_3.html')
	elif n == 4:
			return render_template('keg_4.html')
	else:# n == 5:
			return render_template('keg_5.html')   
			
if __name__ == '__main__':
	app.run(host='192.168.1.159', port = PORT)

