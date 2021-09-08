from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import time


def open_browser():
    # Allow notifications
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(
        "C:/Users/Robert Dutka/Desktop/showdown-project/webdrivers/chromedriver.exe"
    )

    driver = webdriver.Chrome(options=chrome_options, service=service)

    return driver


def login(driver, username, password):
    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".userbar button[name='login']")
            )
        )
        login_btn.click()
    except:
        print("Timed out or could not find login button.")

    try:
        username_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']"))
        )
        username_box.send_keys(username)
    except:
        print("Timed out or could not find username box.")

    try:
        username_submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".buttonbar button[type='submit']")
            )
        )
        username_submit_btn.click()
    except:
        print("Timed out or could not find username submit.")

    try:
        password_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_box.send_keys(password)
    except:
        print("Timed out or could not find password textbox.")

    try:
        password_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".buttonbar button[type='submit']")
            )
        )
        password_btn.click()
    except:
        print("Timed out or could not find password submit button.")


def select_format_home_page(driver, formatname):
    try:
        format_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='format']"))
        )
        format_btn.click()
    except:
        print("Timed out or could not find select format button.")

    css_selector = "button[value='" + formatname + "']"

    try:
        formats_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        formats_select.click()
    except:
        print("Timed out or could not find vgc2021 series10 button.")


def upload_team(driver, filename, formatname):
    try:
        teambuilder_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[value='teambuilder']"))
        )
        teambuilder_btn.click()
    except:
        print("Timed out or could not find team builder button.")

    try:
        newteam_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[value='team']"))
        )
        newteam_btn.click()
    except:
        print("Timed out or could not find team builder button.")

    try:
        import_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='import']"))
        )
        import_btn.click()
    except:
        print("Timed out or could not find import button.")

    with open(filename, "r") as f:
        team_string = f.read()

    try:
        teamtextarea = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".teamedit textarea"))
        )
        teamtextarea.click()
        teamtextarea.send_keys(team_string)
    except:
        print("Timed out or could not find team import text area button.")

    try:
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='saveImport']"))
        )
        save_btn.click()
    except:
        print("Timed out or could not find save import button.")

    try:
        selectformat_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".teamchartbox button[name='format']")
            )
        )
        selectformat_btn.click()
    except:
        print("Timed out or could not find team format button.")

    css_selector = ".popupmenu button[value='" + formatname + "']"

    try:
        format_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        format_btn.click()
    except:
        print("Timed out or could not find vgc2021 series 10 button.")

    try:
        home_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/']"))
        )
        home_btn.click()
    except:
        print("Timed out or could not find home button.")


def challenge_player(driver, opp_name, formatname):
    try:
        finduser_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='finduser']"))
        )
        finduser_btn.click()
    except:
        print("Timed out or could not find Find a User button.")
        return 0

    try:
        finduser_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".ps-popup input[name='data']")
            )
        )
        finduser_box.click()
        finduser_box.send_keys(opp_name)
    except:
        print("Timed out or could not find username text box.")
        return 0

    try:
        open_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".buttonbar button[type='submit']")
            )
        )
        open_btn.click()
    except:
        print("Timed out or could not find open button.")
        return 0

    try:
        challenge_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".ps-popup button[name='challenge']")
            )
        )
        challenge_btn.click()
    except:
        print("Timed out or could not find Challenge button.")
        return 0

    try:
        challenge_format_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "div.challenge button[name='format']",
                )
            )
        )
        challenge_format_btn.click()
    except:
        print("Timed out or could not find challenge format button.")
        return 0

    css_selector = ".popupmenu button[value='" + formatname + "']"

    try:
        challenge_format_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        challenge_format_btn.click()
    except:
        print("Timed out or could not find vgc2021 series 10 button.")
        return 0

    try:
        challenge_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button[name='makeChallenge']",
                )
            )
        )
        challenge_btn.click()
    except:
        print("Timed out or could not find Challenge 2 button.")
        return 0

    try:
        battle1 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "div.maintabbar div.inner ul:nth-of-type(2) a.roomtab.button.notifying.closable",
                )
            )
        )
    except:
        print("Timed out or could not find main tab bar")
        return 0

    return 1


def mute_battle(driver):
    try:
        volume_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button[name='openSounds']",
                )
            )
        )
        volume_btn.click()
    except:
        print("Timed out or could not find volume button.")

    try:
        mute_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "input[name='muted']",
                )
            )
        )
        mute_btn.click()
    except:
        print("Timed out or could not find mute button.")

    try:
        volume_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button[name='openSounds']",
                )
            )
        )
        volume_btn.click()
    except:
        print("Timed out or could not find volume button.")


def find_click_button_by_xpath_text(driver, word):
    try:
        pokemon_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='" + word + "']"))
        )
        pokemon_btn.click()
    except:
        print("Timed out or could not button.")
        print("//button[text()='" + word + "']")


def select_pokemon(driver, pokemonnamelist):
    for name in pokemonnamelist:
        find_click_button_by_xpath_text(driver, name)

    wait_for_animations_and_skip(driver)


def select_move(driver, movenum):
    try:
        move_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.movemenu button[value='" + movenum + "']")
            )
        )
        move_btn.click()
    except:
        print("Could not find the move")


def switch_pokemon(driver, pokemonname):
    try:
        move_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.switchmenu button[value='" + pokemonname + "']")
            )
        )
        move_btn.click()
    except:
        print("Could not find the pokemon.")


def wait_for_animations_and_skip(driver):
    # Try to see if you find the waiting for opponent or go straight to
    try:
        waiting_for = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//em[text()='Waiting for opponent...']")
            )
        )
    except:
        print("Could not find waiting for.")

    try:
        skipButton = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.battle-controls button[name='goToEnd']")
            )
        )
        skipButton.click()
    except:
        print("Could not find Skip To End button.")


def select_move_target(driver, targetnum):
    try:
        move_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[value='" + targetnum + "']")
            )
        )
        move_btn.click()
    except:
        print("Could not find the move")


def get_move_targetting(driver, movenum):
    move_btn = None
    try:
        move_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.movemenu button[value='" + movenum + "']")
            )
        )
    except:
        print("Could not find the move")
        return None

    move_targetting = move_btn.get_attribute("data-target")

    if move_targetting == "normal":
        return True

    if move_targetting == "adjacentAlly":
        return True

    return False


def pokemon_turn(driver):
    move = input("Select a move: ")

    if move == "switch":
        pokemon_switch = input("Select switch in: ")
        switch_pokemon(driver, pokemon_switch)
        return

    does_move_target = get_move_targetting(driver, move)

    if does_move_target == None:
        print("Error getting targeting information.")
        return

    select_move(driver, move)

    if does_move_target:  # TODO make this a general method
        movetarget = input("Select target: ")
        select_move_target(driver, movetarget)


def update_battle_history(driver, last_turn_num):
    css_selector = (
        "div.inner.message-log h2.battle-history:nth-of-type("
        + str(last_turn_num)
        + ")"
    )

    with open("battle-history.txt", "w") as f:
        result = 0
        #  0 = normal turn
        #  1 = end of battle
        # -1 = error
        message_div = None

        while 1:
            css_selector = css_selector + " + div"

            try:
                message_div = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                )
            except:
                f.close()
                return result

            message_class = message_div.get_attribute("class")

            if message_class == "spacer battle-history":
                pass
            elif message_class == "battle-history":
                if message_div.text.endswith("won the battle!"):
                    result = 1
                f.write(message_div.text)  # TODO pipe this to the predictor
                f.write("\n")

        return -1


def check_opponent_faint_switchin(driver):
    element_n = None
    try:
        element_n = WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.element_to_be_clickable(
                    (By.XPATH, "//em[text()='Waiting for opponent...']")
                ),
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.battle-controls div.controls div.whatdo")
                ),
            )
        )
    except:
        print("Could not find either waiting for, or next move.")
        return 1

    if element_n.get_attribute("class") != "whatdo":
        try:
            skipButton = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.battle-controls button[name='goToEnd']")
                )
            )
            skipButton.click()
        except:
            print("Could not find Skip To End button.")
    return 0


def get_opponents_team(driver, my_name):
    try:
        team = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.chat.battle-history"))
        )

        trainer = team.text.split("'")[0]

        if trainer != my_name.replace(" ", ""):
            opponent_team = team.text.split("\n")[1]
            print(opponent_team)
            return 0
        else:
            raise ValueError("This team is not the opponent.")
    except ValueError:
        try:
            team = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.chat.battle-history + div")
                )
            )

            trainer = team.text.split("'")[0]

            if trainer != my_name.replace(" ", ""):
                opponent_team = team.text.split("\n")[1]
                print(opponent_team)
                return 0
            else:
                raise ValueError("Could not find opponent team.")
        except:
            print("Could not find second team.")
            return 1
    except:
        print("Could not find first team")


def turnoff_nicknames(driver):
    try:
        battle_options = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.battle-options button.icon.button")
            )
        )
        battle_options.click()
    except:
        print("Could not find options button.")

    try:
        nickname_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.ps-popup input[name='ignorenicks']")
            )
        )
        nickname_btn.click()
    except:
        print("Could not find nickname off button.")

    try:
        close_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.ps-popup button[name='close']")
            )
        )
        close_btn.click()
    except:
        print("Could not find close button.")


def is_one_remaining(driver):
    num_fainted = 0
    for i in range(4):
        css_selector = "div.switchmenu button" + " + button" * i

        try:
            pokemon_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )

            pokemon_status = pokemon_btn.get_attribute("value")
            if pokemon_status in ["1", "2", "3", "4"]:
                continue

            pokemon_status = pokemon_status.split(",")[1]

            if pokemon_status == "fainted":
                num_fainted += 1
        except:
            print("Could not determine if pokemon has fainted or not")

    if num_fainted == 3:
        return True

    return False


def check_ally_faint_switchin(driver):
    try:
        switch_txt = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.controls.switch-controls .whatdo")
            )
        )

        switch_txt = switch_txt.text.split(" ")[0]

        print("Switch in text: ", switch_txt)

        switchin = input("Select a switchin: ")
        try:
            move_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[value='" + switchin + "']")
                )
            )
            move_btn.click()

        except:
            print("Could not find the move")
    except:
        print("Error checking if ally needs switch in")


def determine_state(driver):
    element_n = None
    try:
        element_n = WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.element_to_be_clickable(
                    (By.XPATH, "//em[text()='Waiting for opponent...']")
                ),
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.battle-controls div.controls div.whatdo")
                ),
                EC.element_to_be_clickable(  # Make this check for friendly switch
                    (By.CSS_SELECTOR, "div.controls.switch-controls .whatdo")
                ),
                EC.element_to_be_clickable(  # Make this check for friendly switch
                    (By.CSS_SELECTOR, "button[name='instantReplay']")
                ),
            )
        )
    except:
        print("Could not find either waiting for, or friendly switch or next move.")
        return -1

    # print("intermediate element tag: ", element_n.tag_name)
    # print("element text: ", element_n.text)

    if element_n.tag_name == "em":
        # print("Waiting for opponent found")
        return 1
    elif element_n.tag_name == "button":
        # print("This is the end of the battle")
        return 4
    elif element_n.text.startswith("What will "):
        # This should be to choose a move
        # print("This should be to choose a move")
        return 2
    else:  # startswith("Switch ")
        # this should be friendly switch
        # print("This should be to choose a switch")
        return 3


def switchin_ally(driver):
    switchin = input("Select a switchin: ")

    try:
        pokemon_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[value='" + switchin + "']")
            )
        )
        pokemon_btn.click()
    except:
        print("Could not find the pokemon")


# TODO
#       Determine the stage of the battle (need to select target,  battle is over, )
#       Implement control flow for battle
#       Make a find and click but for CSS Selectors (like the xpath one but for css)
#       Adjust timings for certain parts, like waiting for opponent
#       If dont find something, try to find it again
#
#
#       Check if you need to do a switchin before chosing a move
#       Check if battle has ended
#       Handle mid-turn switches from moves like uturn
# NoSuchElementException

#####START OF MAIN PROGRAM


##################################################
#####START
username = "My Name is John Shaft"

driver = open_browser()

driver.get("https://play.pokemonshowdown.com/")

login(driver, username, "PszczolaLata2189")

select_format_home_page(driver, "gen8vgc2021series10")

upload_team(driver, "palkiateam.txt", "gen8vgc2021series10")

battle_found = challenge_player(driver, "Dutmeister", "gen8vgc2021series10")

if battle_found:
    print("Battle was accepted")
    mute_battle(driver)
    turnoff_nicknames(driver)  ###

    get_opponents_team(driver, username)

    pokemonlist = []
    for i in range(4):
        pokemonlist.append(input("Select a pokemon: "))

    select_pokemon(driver, pokemonlist)

    # wait for opponent maybe

    i = 1
    while 1:
        pokemon_turn(driver)

        if not is_one_remaining(driver):
            pokemon_turn(driver)

        while 1:
            result = determine_state(driver)

            if result == 1:  # Waiting for
                wait_for_animations_and_skip(driver)
            elif result == 2:  # You choose next move
                break
            elif result == 3:  # You need to make a switch
                switchin_ally(driver)
                pass
            elif result == 4:  # Found end of battle text
                print("Battle has ended.")
                break
            else:
                print("Error with determining state.")
                break

        history = update_battle_history(driver, i)
        if history == 0:  # normal turn
            pass
        elif history == 1:  # end of battle
            print("Battle has ended.")
            break
        else:
            print("Error updating history.")
        i += 1
else:
    print("Battle was not accepted")
    driver.quit()
    exit(1)


driver.quit()
exit(0)

#####END
#######################################################
#####START


# NEW CONTROL LOOP AFTER CHOOSE MOVES
#
# while(1):
#     result = oppswitch_allyswitch_wait()
#
#     if(oppswitch):
#         do something
#     elif(allyswitch):
#         do something else
#     else:
#         break


# driver.quit()
