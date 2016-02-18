from flask import Flask, render_template, request
import sys
app = Flask(__name__, static_url_path='views', template_folder='views')

eastVendDir = sys.argv[1]

@app.route("/")
def serve_index():
    return app.send_static_file('index.html')

@app.route('/confirm', methods=['POST'])
def store_email():
    name = request.form['name']
    studentIDStr = request.form['studentID']
    email = request.form['email']
    notifyFrequencyStr = request.form['notifyFrequency']

    try:
        studentIDNum = int(studentIDStr)
    except:
        return
    else:
        if studentIDNum < 10000000 || studentIDNum >= 100000000:
            return

    # TODO: Validation!

    freqLookup = {'immediately': 0,
                  'daily'      : 1,
                  'weekly'     : 7}

    notifyFreqDays = freqLookup[notifyFrequencyStr] \
                     if notifyFrequencyStr in freqLookup else 0

    toWriteToFile = '0\0000\000%s\000%d\000%s' % (email, notifyFreqDays, name)
    filePath = '%s/data/%d' % (eastVendDir, studentIDNum)

    print "Writing ``%s'' to file ``%s''" % (toWriteToFile, filePath)

    try:
        with open(filePath, 'w') as f:
            f.write(toWriteToFile)
    except IOError as e:
        print e

    # TODO: Send a confirmation page
    return serve_index()

@app.errorhandler(404)
def not_found():
    return app.send_static_file('404.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
