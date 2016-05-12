from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
#SM imports
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.by import By
# from datetime import datetime
# from  collections import namedtuple
from pprint import pprint
import sys,os
import random
import time
from ..AmazonRunner import AmazonRunner


from ..SocketInterface import clientsocket
from ..MPLogger import loggingclient
from utils.lso import get_flash_cookies
from utils.firefox_profile import get_cookies  # todo: add back get_localStorage,
from utils.webdriver_extensions import scroll_down, wait_until_loaded, get_intra_links

# Library for core WebDriver-based browser commands

NUM_MOUSE_MOVES = 10  # number of times to randomly move the mouse as part of bot mitigation
RANDOM_SLEEP_LOW = 1  # low end (in seconds) for random sleep times between page loads (bot mitigation)
RANDOM_SLEEP_HIGH = 7  # high end (in seconds) for random sleep times between page loads (bot mitigation)

""" ********* AMAZON FUNCTIONS ********* """
#SM Stuff
# PriceRecord = namedtuple('PriceRecord',['vendor_index' ,'price', 'vendor', 'condition', 'delivery','shipping'])
def amazon_signin(webdriver, proxy_queue, browser_params):
    
    user = browser_params["creds_user"]
    password = browser_params["creds_password"]
    sign_in_url="http://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fref%3Dnav_signin"
    
    #sign in
    # def get_website(url, sleep, webdriver, proxy_queue, browser_params, extension_socket):
    get_website(sign_in_url,2, webdriver, proxy_queue, browser_params,None)
    email = webdriver.find_element(By.CSS_SELECTOR, "#ap_email").send_keys(user)
    password = webdriver.find_element(By.CSS_SELECTOR, "#ap_password").send_keys(password)
    webdriver.find_element_by_id("signInSubmit-input").click()
    print ("Signed in with %s"%user)

# def get_checkout_price(webdriver,browser_params):
    # pass
    # add to cart
    # proceed to checkout
    # ship to this address
    # continue
    # continue
    # div#subtotals-marketplace-table

    #option 1
    # a href="https://www.amazon.com/ref=ox_spc_footer_homepage"
    # a href="/gp/cart/view.html/ref=nav_crt_ewc_hd"
    # input value="Delete"
    # a a-link-normal sc-product-link

def get_price_list(webdriver,browser_params):
    """
    CSS Selectors:
    Prices  : span.a-size-large.a-color-price.olpOfferPrice-text-bold 
    Vendors : p.a-spacing-small.olpSellerName
    Delivery: div.a-column.a-span3.olpDeliveryColumn 
    """
    if  len(webdriver.find_elements(By.CSS_SELECTOR,"li#olpTabNew")) > 0:
        webdriver.find_element(By.CSS_SELECTOR,"li#olpTabNew").click()
        time.sleep(2)

    product_data = {'prices':[],'vendors':[],'condition':[],'delivery':[],'vendor_index':[],'shipping':[]}
    count = 1
    while not webdriver.find_elements(By.CSS_SELECTOR,'li.a-disabled.a-last'):
        print 'clicking next on offers list...'
        product_data['prices'] +=  [element.text for element in webdriver.find_elements(By.CSS_SELECTOR,"span.a-size-large.a-color-price.olpOfferPrice")]
        product_data['condition'] +=  [element.text for element in webdriver.find_elements(By.CSS_SELECTOR,"span.a-size-medium.olpCondition.a-text-bold")]
        product_data['delivery'] +=  [element.text.split('\n')[0] for element in webdriver.find_elements(By.CSS_SELECTOR,"div.a-column.a-span3.olpDeliveryColumn")]
        product_data['shipping'] += [ element.text for element in webdriver.find_elements(By.CSS_SELECTOR,"p.olpShippingInfo")]

        for element in webdriver.find_elements(By.CSS_SELECTOR,"h3.a-spacing-none.olpSellerName"):
            product_data['vendor_index'].append(count)
            count = count + 1
            if element.text:
                product_data['vendors'].append(element.text)
            else:
                product_data['vendors'].append(element.find_element_by_tag_name('img').get_attribute('alt'))
        webdriver.find_element(By.CSS_SELECTOR,"li.a-last").click()
        time.sleep(2)

    #we are done with pagination. Capture last page
    product_data['prices']     +=  [element.text for element in webdriver.find_elements(By.CSS_SELECTOR,"span.a-size-large.a-color-price.olpOfferPrice")]
    product_data['condition']  +=  [element.text for element in webdriver.find_elements(By.CSS_SELECTOR,"span.a-size-medium.olpCondition.a-text-bold")]
    product_data['delivery']   +=  [element.text.split('\n')[0] for element in webdriver.find_elements(By.CSS_SELECTOR,"div.a-column.a-span3.olpDeliveryColumn")]
    product_data['vendors']    +=  [ element.text if element.text else element.find_element_by_tag_name('img').get_attribute('alt') \
                                        for element in webdriver.find_elements(By.CSS_SELECTOR,"h3.a-spacing-none.olpSellerName")]
    for element in webdriver.find_elements(By.CSS_SELECTOR,"h3.a-spacing-none.olpSellerName"):
        product_data['vendor_index'].append(count)
        count = count + 1
        if element.text:
            product_data['vendors'].append(element.text)
        else:
            product_data['vendors'].append(element.find_element_by_tag_name('img').get_attribute('alt'))
    product_data['shipping'] += [element.text for element in webdriver.find_elements(By.CSS_SELECTOR,"p.olpShippingInfo")]

    num_items = len(product_data['prices'])
    
    pd = []
    for i in xrange(num_items):
        p = PriceRecord(product_data['vendor_index'][i],product_data['prices'][i],product_data['vendors'][i],product_data['condition'][i],product_data['delivery'][i],product_data['shipping'][i])
        pd.append(p)
    return pd


def amazon_get_prices(url,category,webdriver, proxy_queue, manager_params,browser_params):    
    # for debug
    # url = "http://www.amazon.com/Apple-iPhone-8GB-Black-Verizon/dp/B0074R0Z3O/ref=sr_1_cc_1?s=aps&ie=UTF8&qid=1429812402&sr=1-1-catcorr&keywords=Apple+iPhone+4+8GB+%28Black%29+-+Verizon" 

    product_data = {}
    try:
        # webdriver.get(url)
        
        get_website(url, 3,webdriver, proxy_queue, browser_params,None)
        amazon = AmazonRunner(webdriver, url, manager_params, browser_params )
        amazon.get_product_name()
        print amazon.product_data['name']
        if amazon.nav_to_offers():
            print 'Navigated to offers'
            offers = amazon.get_all_offers()
            for_check_out = amazon.get_products_for_check_out(offers)
            pprint(for_check_out)

            # amazon.get_add_to_cart()
            # print 'get website again'
            # get_website(url, 2,webdriver, proxy_queue, browser_params,None)
            # if amazon.nav_to_offers():
            #     print amazon.get_offer_details()
            # dump_amazon_data(amazon.product_data,category,webdriver, manager_params,browser_params,True)
        else:
            print 'Couldnt reach offers'
    except Exception, e:
        print 'got an exception!'
        exc_type, exc_obj, exc_tb = sys.exc_info()
        if exc_tb:
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        print e
## Not as Old
        # webdriver.find_element(By.CSS_SELECTOR,'[data-feature-name="title"]').text
        # # get product name
        # product_data['url'] = url
        # product_data['name'] = webdriver.find_element(By.CSS_SELECTOR,'[data-feature-name="title"]').text
        # product_data['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # desktop = [element for element in webdriver.find_elements(By.CSS_SELECTOR,"span.olp-padding-right > a") if "new" in element.text]
        # mobile = [element for element in webdriver.find_elements(By.CSS_SELECTOR,"div#olp > a") if "new" or "New" in element.text]
        # # print desktop
        # # print mobile
        # # pprint(product_data)
        # # print ("Got product %s"%product_data['name']) 
        # # if more than one vendor get list of vendor prices
        # if desktop :
        #     desktop[0].click()
        # elif len(mobile) > 0:
        #     mobile[0].click()
        #     try:
        #         product_data['prices'] = get_price_list(webdriver,product_data,browser_params)
        #         dump_amazon_data(product_data,category,webdriver, manager_params,browser_params,True)
        #     except Exception, e:
        #         print "ERROR!"
        #         print e        



##OLD
        # if desktop :
        #     try:
        #         desktop[0].click()
        #         time.sleep(2)
        #         product_data['prices'] = get_price_list(webdriver,product_data,browser_params)
        #         dump_amazon_data(product_data,category,webdriver, manager_params,browser_params,True)
        #     except Exception, e:
        #         print "ERROR!"
        #         print e
        # elif len(mobile) > 0:
        #     try:
        #         print "MOBILE"
        #         mobile[0].click()
        #         time.sleep(2)
        #         product_data = get_price_list(webdriver,product_data,browser_params)
        #         dump_amazon_data(product_data,category,webdriver,manager_params,browser_params,True)
        #     except Exception, e:
        #         print e
        # # else:        
        # #     try:
        # #         if len(webdriver.find_elements(By.CSS_SELECTOR,"span#priceblock_dealprice")) > 0:
        # #             product_data['prices'] =  webdriver.find_element(By.CSS_SELECTOR,"span#priceblock_dealprice").text
                
        # #         if len(webdriver.find_elements(By.CSS_SELECTOR,"span#priceblock_ourprice")) > 0:
        # #             product_data['prices'] =  webdriver.find_element(By.CSS_SELECTOR,"span#priceblock_ourprice").text
        # #         product_data['vendors']  = "(default)"
        # #         dump_amazon_data(product_data,category,webdriver, manager_params,browser_params,False)
        # #     except Exception, e:
        # #         print e



def dump_amazon_data(product_data,category,webdriver, manager_params,browser_params, multi_vendor):
    
    tab_restart_browser(webdriver)  # kills traffic so we can cleanly record data
    sock = clientsocket()
    sock.connect(*manager_params['aggregator_address'])
    print 'DUMPING DATA!'
    # pprint(product_data)
    account = ''
    if 'julia' not in  browser_params["creds_user"]:
        if 'mike' in browser_params["creds_user"]:
            account = 'mike'
        else:
            account = 'jeff'
    else:
        account = 'prime'
    
    for row in product_data['prices']:
        query = ("INSERT INTO productInfo (crawl_id,page_url,timestamp,name,account,price,vendor,vendor_index,delivery,shipping_price,condition,category,ua) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", \
                (browser_params['crawl_id'],product_data['url'], product_data['time'], product_data['name'],account,row.price,row.vendor,row.vendor_index,row.delivery,row.shipping,row.condition,\
                        category,browser_params['ua']))
        sock.send(query)
    sock.close()

""" ********* DEFAULT FUNCTIONS ********* """

def bot_mitigation(webdriver):
    """ performs three optional commands for bot-detection mitigation when getting a site """

    # bot mitigation 1: move the randomly around a number of times
    window_size = webdriver.get_window_size()
    num_moves = 0
    num_fails = 0
    while num_moves < NUM_MOUSE_MOVES + 1 and num_fails < NUM_MOUSE_MOVES:
        try:
            if num_moves == 0: #move to the center of the screen
                x = int(round(window_size['height']/2))
                y = int(round(window_size['width']/2))
            else: #move a random amount in some direction
                move_max = random.randint(0,500)
                x = random.randint(-move_max, move_max)
                y = random.randint(-move_max, move_max)
            action = ActionChains(webdriver)
            action.move_by_offset(x, y)
            action.perform()
            num_moves += 1
        except MoveTargetOutOfBoundsException:
            num_fails += 1
            #print "[WARNING] - Mouse movement out of bounds, trying a different offset..."
            pass

    # bot mitigation 2: scroll in random intervals down page
    scroll_down(webdriver)

    # bot mitigation 3: randomly wait so that page visits appear at irregular intervals
    time.sleep(random.randrange(RANDOM_SLEEP_LOW, RANDOM_SLEEP_HIGH))


def tab_restart_browser(webdriver):
    """
    kills the current tab and creates a new one to stop traffic
    note: this code if firefox-specific for now
    """
    if webdriver.current_url.lower() == 'about:blank':
        return

    switch_to_new_tab = ActionChains(webdriver)
    switch_to_new_tab.key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL)
    switch_to_new_tab.key_down(Keys.CONTROL).send_keys(Keys.PAGE_UP).key_up(Keys.CONTROL)
    switch_to_new_tab.key_down(Keys.CONTROL).send_keys('w').key_up(Keys.CONTROL)
    switch_to_new_tab.perform()
    time.sleep(0.5)


def get_website(url, sleep, webdriver, proxy_queue, browser_params, extension_socket):
    """
    goes to <url> using the given <webdriver> instance
    <proxy_queue> is queue for sending the proxy the current first party site
    """

    tab_restart_browser(webdriver)
    main_handle = webdriver.current_window_handle

    # sends top-level domain to proxy and extension (if enabled)
    # then, waits for it to finish marking traffic in proxy before moving to new site
    if proxy_queue is not None:
        proxy_queue.put(url)
        while not proxy_queue.empty():
            time.sleep(0.001)
    if extension_socket is not None:
        extension_socket.send(url)

    # Execute a get through selenium
    try:
        webdriver.get(url)
    except TimeoutException:
        pass

    # Sleep after get returns
    time.sleep(sleep)

    # Close modal dialog if exists
    try:
        WebDriverWait(webdriver, .5).until(EC.alert_is_present())
        alert = webdriver.switch_to_alert()
        alert.dismiss()
        time.sleep(1)
    except TimeoutException:
        pass

    # Close other windows (popups or "tabs")
    windows = webdriver.window_handles
    if len(windows) > 1:
        for window in windows:
            if window != main_handle:
                webdriver.switch_to_window(window)
                webdriver.close()
        webdriver.switch_to_window(main_handle)

    if browser_params['bot_mitigation']:
        bot_mitigation(webdriver)

def extract_links(webdriver, browser_params, manager_params):
    link_elements = webdriver.find_elements_by_tag_name('a')
    link_urls = set(element.get_attribute("href") for element in link_elements)

    sock = clientsocket()
    sock.connect(*manager_params['aggregator_address'])
    create_table_query = ("""
    CREATE TABLE IF NOT EXISTS links_found (
      found_on TEXT,
      location TEXT
    )
    """, ())
    sock.send(create_table_query)

    if len(link_urls) > 0:
        current_url = webdriver.current_url
        insert_query_string = """
        INSERT INTO links_found (found_on, location)
        VALUES (?, ?)
        """
        for link in link_urls:
            sock.send((insert_query_string, (current_url, link)))

    sock.close()

def browse_website(url, num_links, sleep, webdriver, proxy_queue,
                   browser_params, manager_params, extension_socket):
    """
    calls get_website before visiting <num_links> present on the page
    NOTE: top_url will NOT be properly labeled for requests to subpages
          these will still have the top_url set to the url passed as a parameter
          to this function.
    """
    # First get the site
    get_website(url, sleep, webdriver, proxy_queue, browser_params, extension_socket)

    # Connect to logger
    logger = loggingclient(*manager_params['logger_address'])

    # Then visit a few subpages
    for i in range(num_links):
        links = get_intra_links(webdriver, url)
        links = filter(lambda x: x.is_displayed() == True, links)
        if len(links) == 0:
            break
        r = int(random.random()*len(links)-1)
        logger.info("BROWSER %i: visiting internal link %s" % (browser_params['crawl_id'], links[r].get_attribute("href")))

        try:
            links[r].click()
            wait_until_loaded(webdriver, 300)
            time.sleep(max(1,sleep))
            if browser_params['bot_mitigation']:
                bot_mitigation(webdriver)
            webdriver.back()
        except Exception, e:
            pass

def dump_flash_cookies(top_url, start_time, webdriver, browser_params, manager_params):
    """ Save newly changed Flash LSOs to database

    We determine which LSOs to save by the `start_time` timestamp.
    This timestamp should be taken prior to calling the `get` for
    which creates these changes.
    """
    # Set up a connection to DataAggregator
    tab_restart_browser(webdriver)  # kills traffic so we can cleanly record data
    sock = clientsocket()
    sock.connect(*manager_params['aggregator_address'])

    # Flash cookies
    flash_cookies = get_flash_cookies(start_time)
    for cookie in flash_cookies:
        query = ("INSERT INTO flash_cookies (crawl_id, page_url, domain, filename, local_path, \
                  key, content) VALUES (?,?,?,?,?,?,?)", (browser_params['crawl_id'], top_url, cookie.domain,
                                                          cookie.filename, cookie.local_path,
                                                          cookie.key, cookie.content))
        sock.send(query)

    # Close connection to db
    sock.close()

def dump_profile_cookies(top_url, start_time, webdriver, browser_params, manager_params):
    """ Save changes to Firefox's cookies.sqlite to database

    We determine which cookies to save by the `start_time` timestamp.
    This timestamp should be taken prior to calling the `get` for
    which creates these changes.

    Note that the extension's cookieInstrument is preferred to this approach,
    as this is likely to miss changes still present in the sqlite `wal` files.
    This will likely be removed in a future version.
    """
    # Set up a connection to DataAggregator
    tab_restart_browser(webdriver)  # kills traffic so we can cleanly record data
    sock = clientsocket()
    sock.connect(*manager_params['aggregator_address'])

    # Cookies
    rows = get_cookies(browser_params['profile_path'], start_time)
    if rows is not None:
        for row in rows:
            query = ("INSERT INTO profile_cookies (crawl_id, page_url, baseDomain, name, value, \
                      host, path, expiry, accessed, creationTime, isSecure, isHttpOnly) \
                      VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (browser_params['crawl_id'], top_url) + row)
            sock.send(query)

    # Close connection to db
    sock.close()
