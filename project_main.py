from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

import time
from simulator_obj import simulator
import tkinter as tk
from tkinter import StringVar


def open_browser():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(
        # "C:/Users/Krzysztof Dutka/OneDrive/Desktop/Showdown Project/showdownproject/webdrivers/chromedriver.exe"
        "C:/Users/Robert Dutka/Desktop/showdown-project/webdrivers/chromedriver.exe"
    )

    driver = webdriver.Chrome(options=chrome_options, service=service)

    return driver


# Return 0 on success, returns error code on except
def click_button_xpath_noerror(driver, timeout, word, error_message, error_code):
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='" + word + "']"))
        )
        btn.click()
    except:
        print("Could not find button through XPATH: ", error_message)
        return error_code

    return 0


# Return 0 on success, returns error code on except
def click_pokemon_lead(driver, timeout, word, error_message, error_code):
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-tooltip='switchpokemon|" + word + "']")
            )
        )
        btn.click()
    except:
        print("Could not find button through CSS: ", error_message)
        return error_code

    return 0


# Returns 0 on success, returns error_code on except
def click_button_css(driver, timeout, css_text, error_message, error_code):
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_text))
        )
        btn.click()
    except:
        print("Could not find button through CSS: ", error_message)
        return error_code

    return 0


# Return 0 if found button and clicked, 1 otherwise
def try_click_css(num_attempts, driver, timeout, css_text, error_message, error_code):
    attempts = 0
    while attempts < num_attempts:
        if click_button_css(driver, timeout, css_text, error_message, error_code) == 0:
            return 0

        attempts += 1
    return error_code


# Return 1 on error, 0 on success
def login(driver, username, password):
    # Click login
    if try_click_css(2, driver, 5, ".userbar button[name='login']", "Login Button", 1):
        return 1

    # Type in username
    try:
        username_box = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']"))
        )
        username_box.send_keys(username)
    except:
        print("Timed out or could not find username box.")
        return 1

    # Click submit
    if try_click_css(
        2, driver, 5, ".buttonbar button[type='submit']", "Submit Button", 1
    ):
        return 1

    # Type in password
    try:
        password_box = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_box.send_keys(password)
    except:
        print("Timed out or could not find password textbox.")

    # Submit password
    if try_click_css(
        2, driver, 5, ".buttonbar button[type='submit']", "Submit Button", 1
    ):
        return 1

    return 0


# Returns 0 if select format successfully, 1 otherwise
def select_format_home_page(driver, formatname):
    # Click select format button
    if try_click_css(2, driver, 5, "button[name='format']", "Format Button", 1):
        return 1

    # Click specific format button
    if try_click_css(
        2, driver, 5, "button[value='" + formatname + "']", "Specific Format Button", 1
    ):
        return 1

    return 0


# Returns 0 if successfully upload team, 1 otherwise
def upload_team(driver, filename, formatname):
    # Click team builder button
    if try_click_css(
        2, driver, 5, "button[value='teambuilder']", "Teambuilder Button", 1
    ):
        return 1

    # Click team button
    if try_click_css(2, driver, 5, "button[value='team']", "Team Button", 1):
        return 1

    # Click import button
    if try_click_css(2, driver, 5, "button[name='import']", "Import Button", 1):
        return 1

    # Get team from specified team text file
    with open("teams/" + filename, "r") as f:
        team_string = f.read()

    try:
        teamtextarea = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".teamedit textarea"))
        )
        teamtextarea.click()
        teamtextarea.send_keys(team_string)
    except:
        print("Timed out or could not find team import text area button.")

    # Click save import button
    if try_click_css(
        2, driver, 5, "button[name='saveImport']", "Save Import Button", 1
    ):
        return 1

    # Click select format button
    if try_click_css(
        2, driver, 5, ".teamchartbox button[name='format']", "Select Format Button", 1
    ):
        return 1

    # Click specific format button
    if try_click_css(
        2,
        driver,
        5,
        ".popupmenu button[value='" + formatname + "']",
        "Select Specific Format Button",
        1,
    ):
        return 1

    # Click home button
    if try_click_css(2, driver, 5, "a[href='/']", "Home Button", 1):
        return 1

    return 0


# Return 0 if successfully challenge player and get accepted, 1 otherwise
def challenge_player(driver, opp_name, formatname):
    # Click home button
    if try_click_css(2, driver, 5, "button[name='finduser']", "Find User Button", 1):
        return 1

    # Type in username to challenge
    try:
        finduser_box = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".ps-popup input[name='data']")
            )
        )
        finduser_box.click()
        finduser_box.send_keys(opp_name)
    except:
        print("Timed out or could not find username text box.")
        return 1

    try:
        open_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".buttonbar button[type='submit']")
            )
        )
        open_btn.click()
    except:
        print("Timed out or could not find open button.")
        return 1

    time.sleep(1)

    # Click challenge button
    if try_click_css(
        2, driver, 5, ".ps-popup button[name='challenge']", "Challenge Button", 1
    ):
        return 1

    # Click format button
    if try_click_css(
        2, driver, 5, "div.challenge button[name='format']", "Format Button", 1
    ):
        return 1

    # Click specific format button
    if try_click_css(
        2,
        driver,
        5,
        ".popupmenu button[value='" + formatname + "']",
        "Specific Format Button",
        1,
    ):
        return 1

    # Click challenge button
    if try_click_css(
        2, driver, 5, "button[name='makeChallenge']", "Challenge Button", 1
    ):
        return 1

    # Click battle tab button
    if try_click_css(
        2,
        driver,
        20,
        "div.maintabbar div.inner ul:nth-of-type(2) a.roomtab.button.notifying.closable",
        "Battle Button",
        1,
    ):
        return 1

    return 0


# Return 0 if mute battle, 1 if error
def mute_battle(driver):
    # Click Sounds button
    if try_click_css(2, driver, 5, "button[name='openSounds']", "Sounds Button", 1):
        return 1

    # Click Mute button
    if try_click_css(2, driver, 5, "input[name='muted']", "Mute Button", 1):
        return 1

    # Close Sounds menu
    if try_click_css(
        2, driver, 5, "button[name='openSounds']", "Close Sounds Button", 1
    ):
        return 1

    return 0


# Select initial team TODO do checks to see if successful or failure
def select_pokemon(driver, pokemonnamelist):
    for name in pokemonnamelist:
        # Try to find it 1 more time if the first fails
        if click_pokemon_lead(driver, 10, name, "error finding " + name, 1):
            click_pokemon_lead(driver, 10, name, "error finding " + name, 1)

    wait_for_animations_and_skip(driver)


# Click on a specific move. Returns 0 on success, 1 otherwise.
def select_move(driver, movenum):
    # move must be between 1 and 4
    if int(movenum) < 1 or int(movenum) > 4:
        return 1

    # Click a Move Button
    if try_click_css(
        2, driver, 5, "div.movemenu button[value='" + movenum + "']", "Move Button", 1
    ):
        return 1

    return 0


# Return 0 on successfully choosing a switch, 1 otherwise
def switch_pokemon(driver, pokemonnum):
    # Swap in new pokemon
    if try_click_css(
        2,
        driver,
        5,
        "div.switchmenu button[value='" + pokemonnum + "']",
        "Pokemon Switch Button",
        1,
    ):
        return 1

    return 0


# Skip animations. TODO something with the return
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
        return 1

    # Click Skip Button
    if try_click_css(
        2, driver, 30, "div.battle-controls button[name='goToEnd']", "Skip Button", 1
    ):
        return 1

    return 0


# Selects a target for a move by number (-3 to 3). Return 0 on success, 1 otherwise
def select_move_target(driver, targetnum):
    # In a double battle, targets would only ever be from -2 to 2
    if int(targetnum) < -3 or int(targetnum) > 3:
        return 1

    # Click Skip Button
    if try_click_css(
        2, driver, 5, "button[value='" + targetnum + "']", "Targetting Button", 1
    ):
        return 1

    return 0


# Returns boolean whether or not a move needs to select a target. Returns None on error.
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


# Attempt to select a move for a pokemon for a turn. Return 0 on success, and 1 on failure
# TODO instead of input() tell predictor what you are expecting
def pokemon_turn(driver):
    global q
    move = q.get()

    if move == "switch":
        pokemon_switch = input("Select switch in: ")
        if switch_pokemon(driver, pokemon_switch):
            return 1
        return 0

    does_move_target = get_move_targetting(driver, move)

    if does_move_target == None:
        print("Error getting targeting information.")
        return 1

    if select_move(driver, move):
        return 1

    if does_move_target:
        movetarget = q.get()
        if select_move_target(driver, movetarget):
            return 1

    return 0


# Records the information from the previous turn and saves it into a file, overwriting the old information
# Returns -1 on failure, 0 if normal turn, 1 if the battle has ended
# TODO pipe input into predictor/have predictor read from file and signal it
def update_battle_history(driver, last_turn_num):
    css_selector = (
        "div.inner.message-log h2.battle-history:nth-of-type("
        + str(last_turn_num)
        + ")"
    )

    #  Find the leads and the pre-first turn stuff
    if last_turn_num == 0:
        css_selector = "div.inner.message-log div.chat.battle-history"

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
            except TimeoutException:
                f.close()
                return result
            except:
                f.close()
                return -1

            message_class = message_div.get_attribute("class")

            if message_class == "spacer battle-history":
                pass
            elif message_class == "battle-history":
                if message_div.text.endswith("won the battle!"):
                    result = 1
                f.write(message_div.text)
                f.write("\n")

    return -1


# Read the opponents team and send the info to the predictor
# Returns 0 on success, 1 otherwise
# TODO pipe into predictor instead of printing to console
def get_opponents_team(driver, my_name):
    try:
        team = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.chat.battle-history"))
        )

        trainer = team.text.split("'")[0]

        if trainer != my_name.replace(" ", ""):
            opponent_team = team.text.split("\n")[1]
            print(opponent_team)
            # print(opponent_team.replace(" ", "").split("/"))
            return opponent_team.replace(" ", "").split("/")
            # TODO Check to see if kris is this stupid
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
                return opponent_team.replace(" ", "").split("/")
            else:
                raise ValueError("Could not find opponent team.")
        except:
            print("Could not find second team.")
            return 1
    except:
        print("Could not find first team")
        return 1


# Turns off nicknames for a battle. If nicknames have failed to be turned off, do not save the battle
# Return 0 if nicknames disabled, 1 otherwise
def turnoff_nicknames(driver):
    # Click options Button
    if try_click_css(
        2, driver, 5, "div.battle-options button.icon.button", "Options Button", 1
    ):
        return 1

    # Disable nicknames
    if try_click_css(
        2, driver, 5, "div.ps-popup input[name='ignorenicks']", "Nicknames Button", 1
    ):
        return 1

    # Close Options
    if try_click_css(
        2, driver, 5, "div.ps-popup button[name='close']", "Close Options Button", 1
    ):
        return 1

    return 0


# Check if only 1 pokemon remains on your side
# Returns True, False, or None in case of error
def is_one_remaining(driver):
    num_fainted = 0
    for i in range(4):
        css_selector = "div.switchmenu button" + " + button" * i

        try:
            pokemon_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )

            pokemon_status = pokemon_btn.get_attribute("value")
            # If you can switchin in, value = #, otherwise it will say fainted, or active
            if pokemon_status in ["1", "2", "3", "4"]:
                continue

            pokemon_status = pokemon_status.split(",")[1]

            if pokemon_status == "fainted":
                num_fainted += 1
        except:
            print("Could not determine if pokemon has fainted or not")
            return None

    if num_fainted == 3:
        return True

    return False


# Determine the state of the battle and do appropriate action
# Returns -1 on error, 1-4 depending on the state
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
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.controls.switch-controls .whatdo")
                ),
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[name='instantReplay']")
                ),
            )
        )
    except:
        print("Could not find either waiting for, or friendly switch or next move.")
        return -1

    if element_n.tag_name == "em":
        # print("Waiting for opponent found")
        return 1
    elif element_n.tag_name == "button":
        # print("This is the end of the battle")
        return 4
    elif element_n.text.startswith("What will "):
        # print("This should be to choose a move")
        return 2
    elif (
        element_n.text.startswith("Switch ")
        or element_n.text.startswith("Back")
        or element_n.text.startswith("Choose")
    ):
        # print("This should be to choose a switch")
        return 3

    return -1


# Switch in ally. Returns 0 on success, 1 otherwise
def switchin_ally(driver):
    global q
    switchin = q.get()

    # Click on ally
    if try_click_css(
        2,
        driver,
        5,
        "button[value='" + switchin + "']",
        "Ally Switchin Button " + switchin,
        1,
    ):
        return 1

    return 0


# TODO s
#
#
#
#       Adjust timings for certain parts, like waiting for opponent
#       If dont find something, try to find it again
#
#
#
#
#
#       Be more comprehensive with exceptions where applicable
#       Save the battle after it concludes
#       Change some print statements so they output to a log file
#       Create a log file
#       If nicknames are not turned off, do not save battle
#       Do checks for errors in the main segment below
#       Fix switch ins - cant replicate the problem I had before so its fixed?
#       Handle mid turn forfeit
#       Say gg at the end of a battle/gl hf at the beginning
#       kris's simulator_obj breaks when parsing team with "Shiny: Yes"
#       kris's simulator_obj needs very specific format -- i need to generalize this so it doesnt break every time you use a new team. what im refering to is if a pokemon does not have 4 moves


##################################################
#####START OF MAIN PROGRAM
def play_game():
    username = entry_fields["username"].get()

    driver = open_browser()

    driver.get("https://play.pokemonshowdown.com/")

    login(driver, username, entry_fields["password"].get())

    select_format_home_page(driver, entry_fields["format"].get())

    upload_team(driver, entry_fields["team"].get(), entry_fields["format"].get())

    battle_found = challenge_player(driver, "Dutmeister", entry_fields["format"].get())

    if battle_found == 0:
        print("Battle was accepted")
        mute_battle(driver)
        turnoff_nicknames(driver)

        opponent_team = get_opponents_team(driver, username)

        print("Importing teams")
        s = simulator(entry_fields["team"].get(), opponent_team)
        q = s.get_output()

        print("Selecting lead")
        s.select_lead()

        pokemonlist = []
        for i in range(4):
            pokemonlist.append(q.get())

        select_pokemon(driver, pokemonlist)

        # wait for opponent maybe
        print("Finding leads")
        history = update_battle_history(driver, 0)
        print("Found leads")

        i = 1
        while 1:
            s.parse_battle_history()
            print("Running predictions")
            s.findBestMove(is_random=False)
            print("Finished predictions")
            pokemon_turn(driver)

            if not is_one_remaining(driver):
                pokemon_turn(driver)

            try_again = True
            while 1:
                result = determine_state(driver)
                print("Resulting State is: ", result)

                if result == 1:  # Waiting for
                    wait_for_animations_and_skip(driver)
                elif result == 2:  # You choose next move
                    break
                elif result == 3:  # You need to make a switch
                    s.select_replacement()
                    switchin_ally(driver)
                    pass
                elif result == 4:  # Found end of battle text
                    print("Battle has ended.")
                    break
                else:
                    print("Error with determining state.")
                    if try_again:
                        try_again = False
                        continue
                    else:
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


#
# GUI Part of the application - probably should be its own file but whatever
#


def test_gui():
    test_lbl.configure(text=entry_fields["team"].get())


window = tk.Tk()
window.title("Showdown Project Main")

start_btn = tk.Button(window, text="Start a Game", command=play_game)
start_btn.grid(row=0, column=0)

end_btn = tk.Button(window, text="Quit", command=quit)
end_btn.grid(row=0, column=4)


# To create a new field for the user to enter info, the tuple template is below. String Fields only
#   ("Dictionary ID", "Label Text", "Default Value")
user_fields = [
    ("username", "Choose Username", "Username"),
    ("password", "Enter Password", "Password"),
    ("team", "Choose Team File", "palkiateam.txt"),
    ("format", "Choose Format", "gen8vgc2022"),
]

entry_fields = {}

for i in range(0, len(user_fields)):
    tk.Label(window, text=user_fields[i][1]).grid(row=2 + i, column=0)
    default_val = StringVar(window, value=user_fields[i][2])
    entry_fields[user_fields[i][0]] = tk.Entry(window, textvariable=default_val)
    entry_fields[user_fields[i][0]].grid(row=2 + i, column=1)


test_btn = tk.Button(window, text="Test Button", command=test_gui)
test_btn.grid(row=1 + len(user_fields), column=4)
test_lbl = tk.Label(window, text="Test Text")
test_lbl.grid(row=2 + len(user_fields), column=4)


window.mainloop()
