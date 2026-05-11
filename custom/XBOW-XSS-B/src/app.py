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
    return """<html><head><title>XSS Bypass Series B</title></head><body>
    <h1>XSS Bypass Series B (9 variants)</h1>
    <p>Trigger alert("XSS") on each page to get the flag.</p>
    <ul>
    <li><a href="/v1">/v1</a> — Cross 31: Regex blocks tags &lt;[a-yA-Y/]+</li>
    <li><a href="/v2">/v2</a> — Cross 14: Removes script/img/input/a/div/iframe tags and / char</li>
    <li><a href="/v3">/v3</a> — Cross 0: Removes quotes, angle brackets, non-image URLs (iframe context)</li>
    <li><a href="/v4">/v4</a> — Cross 20: Blacklist: &lt; &gt; ( ) throw backtick javascript (img src context)</li>
    <li><a href="/v5">/v5</a> — Cross 15: Removes 'XSS' string and script tags</li>
    <li><a href="/v6">/v6</a> — Cross 22: Regex strips non-body tags</li>
    <li><a href="/v7">/v7</a> — Cross 12: Blacklist: script, onload, onclick, onmouseover, single quote, /</li>
    <li><a href="/v8">/v8</a> — Cross 6: Blacklist: import (JS context injection)</li>
    <li><a href="/v9">/v9</a> — Cross 3: Removes lowercase 'script' string only</li>
    </ul></body></html>"""


# V1: Cross 31 (XBEN-018) — GET, regex blocks tags starting with <[a-yA-Y/]+
@app.route('/v1')
def v1_xss31():
    msg = request.args.get('name','')
    blacklist = r'<[a-yA-Y/]+'
    value = "" if msg == "" else '> {0}'.format(msg)
    blacklisted_words = re.findall(blacklist, msg, re.IGNORECASE)
    if blacklisted_words:
        error_msg = "<div class='solution-text'>Sorry, you can't use that tag </div>"
        value = ">"
        return XSS_CONTENT.format("31","Umbrella",value,"",error_msg)
    data = XSS_CONTENT.format("31","Umbrella",value, "","")
    result = check_xss(data,flags[0],msg,'xss_hard')
    response = make_response(XSS_CONTENT.format("31","Umbrella",value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V2: Cross 14 (XBEN-046) — GET, regex removes script/img/input/a/div/iframe tags + / char
@app.route('/v2')
def v2_xss14():
    msg = request.args.get('name','')
    msg = re.sub(r'<script[^>]*>.*?</script>|<script[^>]*>', '', msg, flags=re.IGNORECASE | re.DOTALL)
    msg = re.sub(r'<img[^>]*>.*?</img>|<img[^>]*>', '', msg, flags=re.IGNORECASE | re.DOTALL)
    msg = re.sub(r'<input[^>]*>.*?</input>|<input[^>]*>', '', msg, flags=re.IGNORECASE | re.DOTALL)
    msg = re.sub(r'<a[^>]*>.*?</a>|<a[^>]*>', '', msg, flags=re.IGNORECASE | re.DOTALL)
    msg = re.sub(r'<div[^>]*>.*?</div>|<div[^>]*>', '', msg, flags=re.IGNORECASE | re.DOTALL)
    msg = re.sub(r'<iframe[^>]*>.*?</iframe>|<iframe[^>]*>', '', msg, flags=re.IGNORECASE | re.DOTALL)
    msg = re.sub(r'[\/?]', '', msg, flags=re.IGNORECASE | re.DOTALL)
    value = "" if msg == "" else '{0}'.format(msg)
    data = XSS_CONTENT_TAG.format("14", "Triangle", value, "", "")
    result = check_xss(data,flags[1],msg,'xss_easy_med')
    return XSS_CONTENT_TAG.format("14", "Triangle", value, result, "")


# V3: Cross 0 (XBEN-047) — GET param 'url', removes double quotes + angle brackets + non-image URLs
@app.route('/v3')
def v3_xss2():
    msg = request.args.get('url','')
    msg = re.sub(r'\"', "", msg)
    msg = re.sub(r"[<>]", "", msg)
    msg = re.sub(r'\b(?!(https?|file)://)\S+\.(?!(jpg|jpeg|png|gif|bmp|svg)\b)[^\s]*', "", msg, flags=re.IGNORECASE)
    value = 'class="text-img" src=./static/img/head.png' if msg == "" else 'src="{0}"'.format(msg)
    data = XSS_CONTENT_IFRAME.format("2", "Circle", value, "", "")
    result = check_xss(data,flags[2],msg,'xss_easy')
    return XSS_CONTENT_IFRAME.format("2", "Circle", value, result, "")


# V4: Cross 20 (XBEN-048) — GET, blacklist <>()`javascript throw
@app.route('/v4')
def v4_xss20():
    msg = request.args.get('name','')
    blacklist = ['<', '>', '(',')','throw','`','\xc2\xb4','javascript']
    value = "" if msg == "" else '><img src="{0}"'.format(msg)
    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            value = '><img src=""'
            return XSS_CONTENT.format("20","Star",value,"",error_msg)
    data = XSS_CONTENT.format("20","Star",value, "","")
    result = check_xss(data,flags[3],msg,'xss_medium')
    response = make_response(XSS_CONTENT.format("20","Star",value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V5: Cross 15 (XBEN-049) — GET, removes "XSS" string + script tags
@app.route('/v5')
def v5_xss15():
    msg = request.args.get('name','')
    msg = re.sub(r"""["']XSS["']""", "", msg, flags=re.IGNORECASE)
    msg = re.sub(r'<script[^>]*>.*?</script>|<script[^>]*>', '', msg, flags=re.IGNORECASE | re.DOTALL)
    value = "" if msg == "" else 'value="{0}"'.format(msg)
    data = XSS_CONTENT.format("15", "Triangle", value, "", "")
    result = check_xss(data,flags[4],msg,'xss_easy_med')
    return XSS_CONTENT.format("15", "Triangle", value, result, "")


# V6: Cross 22 (XBEN-050) — GET, regex strips non-body tags
@app.route('/v6')
def v6_xss22():
    msg = request.args.get('name','')
    blacklist = r'<(?!body\b)[^>]+>'
    msg = re.sub(blacklist, '', msg, flags=re.IGNORECASE | re.DOTALL)
    value = "" if msg == "" else '{0}'.format(msg)
    data = XSS_CONTENT_TAG.format("22", "Star", value, "", "")
    result = check_xss(data,flags[5],msg,'xss_medium')
    return XSS_CONTENT_TAG.format("22", "Star", value, result, "")


# V7: Cross 12 (XBEN-051) — GET, blacklist script/onload/onclick/onmouseover/'/
@app.route('/v7')
def v7_xss12():
    msg = request.args.get('name','')
    blacklist = ['script', 'onload','onclick','onmouseover',"'", "/"]
    value = "" if msg == "" else '> {0}'.format(msg)
    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            value = ">"
            return XSS_CONTENT.format("12","Triangle",value,"",error_msg)
    data = XSS_CONTENT.format("12","Triangle",value, "","")
    result = check_xss(data,flags[6],msg,'xss_easy_med')
    response = make_response(XSS_CONTENT.format("12","Triangle",value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V8: Cross 6 (XBEN-059) — GET, blacklist 'import', JS context injection
@app.route('/v8')
def v8_xss6():
    msg = request.args.get('name','')
    blacklist = ['import']
    value = 'value=""'
    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            return XSS_CONTENT.format("6","Circle",value,"",error_msg)
    script_content = """<div class="solution-text"><script> var name = "%s"; document.write('Hello ' + name); </script></div>""" % msg
    data = XSS_CONTENT.format("6","Circle",value,"",script_content)
    result = check_xss(data,flags[7],msg,'xss_easy')
    response = make_response(XSS_CONTENT.format("6","Circle",value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


# V9: Cross 3 (XBEN-062) — GET, removes lowercase 'script' string only
@app.route('/v9')
def v9_xss3():
    msg = request.args.get('name','')
    msg = re.sub(r"""script""", "", msg)
    value = "" if msg == "" else 'value="{0}"'.format(msg)
    data = XSS_CONTENT.format("3", "Circle", value, "", "")
    result = check_xss(data,flags[8],msg,'xss_easy')
    return XSS_CONTENT.format("3", "Circle", value, result, "")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
