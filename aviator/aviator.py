from browser.browser import Browser
import helium 
import aviator.vars as vars
import creds as creds
from selenium.webdriver.common.by import By
import time
from datetime import datetime 

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

class Aviator(Browser):
    '''
    this class will interact with the browser

    '''

    def __init__(self, headless=False, test=False, remote_driver=True,
                remote_address="127.0.0.1",remote_port=4446, use_cookies=False,
                debug=False):
        super().__init__(headless= headless, test=test, remote_driver=remote_driver,
                remote_address=remote_address,remote_port=remote_port,
                  use_cookies=use_cookies, profile_path=vars.profile_path)
        
        self.debug = debug

        helium.set_driver(self.driver)
        


    def login(self):
        helium.go_to("https://22bet-b.com")
        if not self.logged_in():
            helium.click("LOG IN")
            helium.write(creds.username, into="ID or Email")
            helium.write(creds.password, into="Password")
            helium.click("Remember")
            helium.click("LOG IN")
            input("press enter to continue")
        
        

    def logged_in(self):
        if self.debug:
            print("checking if logged in")
        element = helium.S("#user-money")
        if element.exists():
            if self.debug:
                print("logged in")
            return True
        else:
            if self.debug:
                print("not logged in")
            return False
        

    def in_game(self):
        '''
        check if we are in game
        '''
        if self.debug:
            print("checking if in game")

        element = self.find_elements(By.XPATH, vars.game_name, timeout=0.5)
        if element or self.driver.title == "Aviator":
            if self.debug:
                print("in game")
            return True

        if self.debug:
            print("not in game")
        return False            
    
    def get_last_game_result(self):
        '''
        get last game result
        '''
        # if self.debug:
        #     print("getting last game result")
        
        results = self.get_game_results()
        if len(results) > 0:
            return results[0]

    def get_game_results(self):
        '''
        get game result
        '''


        # Find the div element with class "payouts-block"
        payouts_div = self.find_elements(By.CLASS_NAME, "payouts-block")

        # Find all elements with class "bubble-multiplier" within the payouts div
        multiplier_elements = payouts_div.find_elements(By.CLASS_NAME, "bubble-multiplier")

        results = []
        # Extract the values
        try:
            for element in multiplier_elements:
                results.append(element.text.strip().replace("x", ""))
        except StaleElementReferenceException | NoSuchElementException:
            #refresh the page
            self.driver.refresh()
            pass
        



            
        if len(results) > 0:
            # if self.debug:
            #     print("got game results")
            return results
        else:
            if self.debug:
                print("could not get game results")


        return []


    def get_balance(self):
        '''
        get balance
        '''
        if self.debug:
            print("getting balance")
        element = self.find_elements(By.XPATH, vars.balance)
        #element is a span with the balance
        if element:
            if self.debug:
                print("got balance")
            return element.text
        else:
            if self.debug:
                print("could not get balance")
            return None

    def wait_for_game_to_finish(self):
        '''
        wait for game to finish
        since the game is in a loop, we need to wait for the game to finish
        the only way to check if the game is finished is to check if we have
        a new result different from the last one
        '''

        if self.debug:
            print("waiting for game to finish")
        last_result = self.get_last_game_result()
        while True:

            if self.get_last_game_result() != last_result:
                break
            if self.debug:
                print(".", end="")
            time.sleep(0.5)
        if self.debug:
            print("")
            print("game finished")
    
    def add_to_log(self, result):
        '''
        add result to results.txt in this 
        format timestamp (format dd-mm-yyyy hh:mm:ss),result
        '''
        if self.debug:
            print(f"adding result {result}  to log")
        with open("results.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')},{result}\n")

    def go_to_game(self):
        wait = WebDriverWait(self.driver, 10)

        helium.go_to("https://22bet-b.com/slots")
        helium.write("AVIATOR", into="SEARCH")
        #sleep for 2 seconds to let the search results load
        time.sleep(2)
        self.click_button(vars.play_free_button_of_first_search_result)

        #wait for the game to load
        time.sleep(2)

        # Store the ID of the original window
        original_window = self.driver.current_window_handle

        # Check we don't have other windows open already
        assert len(self.driver.window_handles) == 1

        # Click the link which opens in a new window
        self.click_button(vars.open_new_window_button)

        # Wait for the new window or tab
        wait.until(EC.number_of_windows_to_be(2))

        # Loop through until we find a new window handle
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break

        # Wait for the new tab to finish loading content
        wait.until(EC.title_is("Aviator"))

        #maximize window
        self.driver.maximize_window()
    
        #wait for the game to open in a new window
        time.sleep(2)


