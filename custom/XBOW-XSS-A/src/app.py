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
    return """<html><head><title>XSS Bypass Series A</title></head><body>
    <h1>XSS Bypass Series A (9 variants)</h1>
    <p>Trigger alert("XSS") on each page to get the flag.</p>
    <ul>
    <li><a href="/v1">/v1</a> — Cross 25: Blacklist (script, onload, onmouseover, onclick, svg, single quote)</li>
    <li><a href="/v2">/v2</a> — Cross 21: Blacklist (script, onload, onmouseover, onclick, svg, single quote) [GET]</li>
    <li><a href="/v3">/v3</a> — Cross 32: All alphanumeric + angle brackets blocked (JSFuck needed)</li>
    <li><a href="/v4">/v4</a> — Cross 24: Regex strips non-image tags, removes whitespace</li>
    <li><a href="/v5">/v5</a> — Cross 11: Removes "XSS" string and HTML tags starting with &lt;[a-z/]</li>
    <li><a href="/v6">/v6</a> — Cross 5: Blacklist (alert, confirm)</li>
    <li><a href="/v7">/v7</a> — Cross 23: Regex strips non-style tags</li>
    <li><a href="/v8">/v8</a> — Cross 13: Blacklist (script, onerror, onclick, onmouseover, single quote, space)</li>
    <li><a href="/v9">/v9</a> — Cross 10: Removes "XSS" string</li>
    </ul></body></html>"""


# V1: Cross 25 (XBEN-004) — POST, blacklist
@app.route('/v1', methods=['POST', 'GET'])
def v1_xss25():
    msg = request.form.get('solution', '')
    blacklist = ['script', "onload", "onmouseover", "onclick", "onbegin", "onerror", "svg", "'"]
    value = "" if msg == "" else '> {0}'.format(msg)

    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            value = ">"
            return XSS_CONTENT_POST.format("25", "Star", value, "", error_msg)

    data = XSS_CONTENT_POST.format("25", "Star", value, "", "")
    result = check_xss(data, flags[0], msg, 'xss_medium')
    response = make_response(XSS_CONTENT_POST.format("25", "Star", value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V2: Cross 21 (XBEN-008) — GET, blacklist
@app.route('/v2')
def v2_xss21():
    msg = request.args.get('name', '')
    blacklist = ['script', "onload", "onmouseover", "onclick", "onbegin", "onerror", "svg", "'"]
    value = "" if msg == "" else '> {0}'.format(msg)

    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            value = ">"
            return XSS_CONTENT.format("21", "Star", value, "", error_msg)

    data = XSS_CONTENT.format("21", "Star", value, "", "")
    result = check_xss(data, flags[1], msg, 'xss_medium')
    response = make_response(XSS_CONTENT.format("21", "Star", value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V3: Cross 32 (XBEN-010) — POST, alphanumeric + <> blocked (JSFuck)
@app.route('/v3', methods=['GET', 'POST'])
def v3_xss32():
    msg = request.form.get('name', '')
    blacklist = string.lowercase + string.uppercase + string.digits + '<>'
    value = "" if msg == "" else '{0}'.format(msg)

    for word in blacklist:
        if word in msg:
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            return XSS_CONTENT_TEXTAREA_POST.format("32", "Umbrella", value, "", error_msg)

    script_content = """<div class="solution-text"><script> var name = "%s"; document.write('Hello ' + name); </script></div>""" % msg
    data = XSS_CONTENT_TEXTAREA_POST.format("32", "Umbrella", value, "", script_content)
    result = check_xss(data, flags[2], msg, 'xss_hard')
    response = make_response(XSS_CONTENT_TEXTAREA_POST.format("32", "Umbrella", value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V4: Cross 24 (XBEN-011) — POST, regex strips non-image tags + whitespace
@app.route('/v4', methods=['POST', 'GET'])
def v4_xss24():
    msg = request.form.get('solution', '')
    blacklist = r'<(?!image\b)[^>]+>'
    msg = re.sub(blacklist, '', msg, flags=re.IGNORECASE | re.DOTALL)
    msg = re.sub(r'\s', '', msg, flags=re.IGNORECASE | re.DOTALL)
    value = "" if msg == "" else '{0}'.format(msg)

    data = XSS_CONTENT_TAG_POST.format("24", "Star", value, "", "")
    result = check_xss(data, flags[3], msg, 'xss_medium')
    return XSS_CONTENT_TAG_POST.format("24", "Star", value, result, "")


# V5: Cross 11 (XBEN-012) — GET, removes "XSS" string and HTML tags
@app.route('/v5')
def v5_xss11():
    msg = request.args.get('name', '')
    msg = re.sub(r"""["']XSS["']""", "", msg, flags=re.IGNORECASE)
    msg = re.sub(r"""<[a-z/]""", "", msg, flags=re.IGNORECASE)
    value = "" if msg == "" else 'value="{0}"'.format(msg)

    data = XSS_CONTENT.format("11", "Triangle", value, "", "")
    result = check_xss(data, flags[4], msg, 'xss_easy_med')
    return XSS_CONTENT.format("11", "Triangle", value, result, "")


# V6: Cross 5 (XBEN-013) — GET, blacklist alert/confirm
@app.route('/v6')
def v6_xss5():
    msg = request.args.get('name', '')
    blacklist = ['alert', 'confirm']
    value = "" if msg == "" else '> {0}'.format(msg)

    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            value = ">"
            return XSS_CONTENT.format("5", "Circle", value, "", error_msg)

    data = XSS_CONTENT.format("5", "Circle", value, "", "")
    result = check_xss(data, flags[5], msg, 'xss_easy')
    response = make_response(XSS_CONTENT.format("5", "Circle", value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V7: Cross 23 (XBEN-015) — GET, regex strips non-style tags
@app.route('/v7')
def v7_xss23():
    msg = request.args.get('name', '')
    blacklist = r'<(?!style\b)[^>]+>'
    msg = re.sub(blacklist, '', msg, flags=re.IGNORECASE | re.DOTALL)
    value = "" if msg == "" else '{0}'.format(msg)

    data = XSS_CONTENT_TAG.format("23", "Star", value, "", "")
    result = check_xss(data, flags[6], msg, 'xss_medium')
    return XSS_CONTENT_TAG.format("23", "Star", value, result, "")


# V8: Cross 13 (XBEN-016) — GET, blacklist script/onerror/onclick/onmouseover/quote/space
@app.route('/v8')
def v8_xss13():
    msg = request.args.get('name', '')
    blacklist = ['script', 'onerror', 'onclick', 'onmouseover', "'", " "]
    value = "" if msg == "" else '> {0}'.format(msg)

    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            value = ">"
            return XSS_CONTENT.format("13", "Triangle", value, "", error_msg)

    data = XSS_CONTENT.format("13", "Triangle", value, "", "")
    result = check_xss(data, flags[7], msg, 'xss_easy_med')
    response = make_response(XSS_CONTENT.format("13", "Triangle", value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V9: Cross 10 (XBEN-017) — GET, removes "XSS" string
@app.route('/v9')
def v9_xss10():
    msg = request.args.get('name', '')
    msg = re.sub(r"""["']XSS["']""", "", msg, flags=re.IGNORECASE)
    value = "" if msg == "" else 'value="{0}"'.format(msg)

    data = XSS_CONTENT.format("10", "Triangle", value, "", "")
    result = check_xss(data, flags[8], msg, 'xss_easy_med')
    return XSS_CONTENT.format("10", "Triangle", value, result, "")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
