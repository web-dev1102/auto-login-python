# import yaml
import undetected_chromedriver as uc
import mysql.connector
import os
import shutil
import tempfile
import requests
import time

# conf = yaml.load(open('loginDetails.yml'), Loader=yaml.FullLoader)
# myEmail = conf['fb_user']['email']
# myPassword = conf['fb_user']['password']
page_url = "https://www.data.ai/account/login/?_ref=bl"

class ProxyExtension:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    """

    def __init__(self, host, port, user, password):
        self._dir = os.path.normpath(tempfile.mkdtemp())

        manifest_file = os.path.join(self._dir, "manifest.json")
        with open(manifest_file, mode="w") as f:
            f.write(self.manifest_json)

        background_js = self.background_js % (host, port, user, password)
        background_file = os.path.join(self._dir, "background.js")
        with open(background_file, mode="w") as f:
            f.write(background_js)

    @property
    def directory(self):
        return self._dir

    def __del__(self):
        shutil.rmtree(self._dir)


def login(username, password):

    driver.get(page_url)
    time.sleep(5)
    try:
        site_key_element = driver.find_element_by_class_name('g-recaptcha')
        site_key = site_key_element.get_attribute("data-sitekey")
        print(site_key)
        key = 'a867a6c30ba00e9bb1a6c1962d106287'
        method = 'userrecaptcha'
        url = "http://2captcha.com/in.php?key={}&method={}&googlekey={}&pageurl={}".format(key, method, site_key, page_url)
        response = requests.get(url)

        if response.text[0:2] != 'OK':
            quit('Service error. Error code:' + response.text)
        captcha_id = response.text[3:]
        token_url = "http://2captcha.com/res.php?key={}&action=get&id={}".format(key, captcha_id)
        while True:
            time.sleep(10)
            response = requests.get(token_url)
            if response.text[0:2] == 'OK':
                break
        captha_results = response.text[3:]
        driver.execute_script(
            """document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(captha_results))
        driver.find_element_by_xpath('//form/button').click()

    except Exception as e:
        print("---before login-----")
        print(e)
    finally:
        print('final')
        print(driver.current_url)
        driver.find_element_by_name("username").send_keys(username)
        driver.find_element_by_xpath("//form/div/div[2]/input").send_keys(password)
        driver.find_element_by_xpath('//button[text()="Login"]').click()
        print("Logged in : {} {}".format(username, password))
        print("url {}".format(driver.current_url))
        try:
            site_key_element = driver.find_element_by_class_name('g-recaptcha')
            site_key = site_key_element.get_attribute("data-sitekey")
            print(site_key)
            key = 'a867a6c30ba00e9bb1a6c1962d106287'
            method = 'userrecaptcha'
            url = "http://2captcha.com/in.php?key={}&method={}&googlekey={}&pageurl={}".format(key, method, site_key, driver.current_url)
            response = requests.get(url)

            if response.text[0:2] != 'OK':
                quit('Service error. Error code:' + response.text)
            captcha_id = response.text[3:]
            token_url = "http://2captcha.com/res.php?key={}&action=get&id={}".format(key, captcha_id)
            while True:
                time.sleep(10)
                response = requests.get(token_url)
                if response.text[0:2] == 'OK':
                    break

            captha_results = response.text[3:]
            driver.execute_script(
                """document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(captha_results))
            driver.find_element_by_xpath('//form/button').click()
            updateState(username, password)

        except Exception as e:
            print("---after login-----")
            print(e)
        finally:
            time.sleep(3)
            driver.quit()


def updateState(email, password):
    try:
        myCursor = mydb.cursor()
        sql = "UPDATE dataai_accounts SET failed = NULL WHERE email = '{}' AND password = '{}'".format(email, password)
        myCursor.execute(sql)
        mydb.commit()
        print("updated : {} {}".format(email, password))
    except mysql.connector.Error as error:
        print("Failed to update : {}".format(error))


if __name__ == '__main__':
    proxy = ("zproxy.lum-superproxy.io", 22225, "lum-customer-c_5b54c192-zone-zone12", "en93f4r37zw7")  # your proxy with auth, this one is obviously fake
    proxy_extension = ProxyExtension(*proxy)

    options = uc.ChromeOptions()
    # options.headless = True
    # options.add_argument('--headless')
    options.add_argument(f"--load-extension={proxy_extension.directory}")

    try:
        mydb = mysql.connector.connect(host='185.253.219.240', database='Appanie', user='root', password='root', port=3178)
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM dataai_accounts where failed is NOT NULL")
        myresult = mycursor.fetchall()
        for x in myresult:
            driver = uc.Chrome(options=options)
            login(x[4], x[3])
    except mysql.connector.Error as error:
        print("Failed to create table in MySQL: {}".format(error))


