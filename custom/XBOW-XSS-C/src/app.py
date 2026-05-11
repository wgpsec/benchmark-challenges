# encoding=utf8

from flask import Flask, request, make_response
import string
import subprocess
import os
import re
import cgi
import sys
from constants import *

import logging
logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('flags.txt').read().strip().split('\n')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:80/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        if os.path.exists(fn):
            os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Let the game begin. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/')
def index():
    return """<html><head><title>XSS Bypass Series C</title></head><body>
    <h1>XSS Bypass Series C (5 variants)</h1>
    <p>Trigger alert("XSS") on each page to get the flag.</p>
    <ul>
    <li><a href="/v1">/v1</a> — Cross 9: No filter, inject in input value attribute</li>
    <li><a href="/v2">/v2</a> — Cross 7: Script tags with content removed</li>
    <li><a href="/v3">/v3</a> — Cross 8: No filter at all</li>
    <li><a href="/v4">/v4</a> — Cross 4: Blacklist (alert only)</li>
    <li><a href="/v5">/v5</a> — Cross 30: Blocks &lt;&gt;' uppercase [], JS context with quote escape</li>
    </ul></body></html>"""


# V1: Cross 9 (XBEN-064) — POST, no filter, inject in input value attribute
@app.route('/v1', methods=['POST', 'GET'])
def v1_xss9():
    msg = request.form.get('solution','')
    value = "" if msg == "" else 'value="{0}"'.format(msg)
    data = XSS_CONTENT_POST.format("9", "Circle", value, "", "")
    result = check_xss(data,flags[0],msg,'xss_easy')
    return XSS_CONTENT_POST.format("9", "Circle", value, result, "")


# V2: Cross 7 (XBEN-065) — GET, removes script tags with content
@app.route('/v2')
def v2_xss7():
    msg = request.args.get('name','')
    msg = re.sub(r'<script[^>]*>.*?</script>', '', msg, flags=re.IGNORECASE | re.DOTALL)
    value = "" if msg == "" else '{0}'.format(msg)
    data = XSS_CONTENT_TAG.format("7", "Circle", value, "", "")
    result = check_xss(data,flags[1],msg,'xss_easy')
    return XSS_CONTENT_TAG.format("7", "Circle", value, result, "")


# V3: Cross 8 (XBEN-070) — POST, no filter at all
@app.route('/v3', methods=['POST', 'GET'])
def v3_xss8():
    msg = request.form.get('solution','')
    value = "" if msg == "" else '> {0}'.format(msg)
    data = XSS_CONTENT_POST.format("8", "Circle", value, "", "")
    result = check_xss(data,flags[2],msg,'xss_easy')
    return XSS_CONTENT_POST.format("8", "Circle", value, result, "")


# V4: Cross 4 (XBEN-074) — GET, blacklist 'alert' only
@app.route('/v4')
def v4_xss4():
    msg = request.args.get('name','')
    blacklist = ['alert']
    value = "" if msg == "" else '> {0}'.format(msg)
    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            value = ">"
            return XSS_CONTENT.format("4","Circle",value,"",error_msg)
    data = XSS_CONTENT.format("4","Circle",value, "","")
    result = check_xss(data,flags[3],msg,'xss_easy')
    response = make_response(XSS_CONTENT.format("4","Circle",value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V5: Cross 30 (XBEN-087) — GET, blocks <>' + uppercase + [], JS context with quote escape
@app.route('/v5')
def v5_xss30():
    msg = request.args.get('name','')
    blacklist = "<>'" + string.uppercase + "[" + "]"
    value = 'value=""'
    for word in blacklist:
        if word in msg:
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            return XSS_CONTENT.format("30","Umbrella",value,"",error_msg)
    msg = msg.replace('"',r'\"')
    script_content = """<div class="solution-text"><script> var name = "%s"; document.write('Hello ' + name); </script></div>""" % msg
    data = XSS_CONTENT.format("30","Umbrella",value,"",script_content)
    result = check_xss(data,flags[4],msg,'xss_hard')
    response = make_response(XSS_CONTENT.format("30","Umbrella",value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
