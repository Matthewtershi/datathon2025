from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Set up the ChromeDriver using the Service class
service = Service(executable_path="C:\\Users\\ayue\\chromedriver-win64\\chromedriver.exe")  # Adjust the path if necessary
driver = webdriver.Chrome(service=service)

# Navigate to your game URL
driver.get("https://secure-bonus-377122.uc.r.appspot.com/level1")  # replace with the actual URL
time.sleep(0.005)

def get_light_state():
    """Check the current state of the light indicator (green or red)."""
    light = driver.find_element(By.ID, "light-indicator")
    class_list = light.get_attribute("class")
    return "green" if "green" in class_list else "red"

def get_active_players():
    """Retrieve all players that are not finished."""
    container = driver.find_element(By.ID, "players-container")
    players = container.find_elements(By.CLASS_NAME, "player")
    active_players = [p for p in players if "finished" not in p.get_attribute("class")]
    return active_players

def click_all_players():
    """Use JavaScript to click all players simultaneously."""
    players = get_active_players()
    player_ids = [player.get_attribute('data-id') for player in players]
    for player_id in player_ids:
        script = f"document.querySelector('.player[data-id=\"{player_id}\"]').click();"
        driver.execute_script(script)
        print(f"Clicked player {player_id}")

try:
    while True:
        # Get the current state of the light before starting to click
        light = get_light_state()

        # Only start clicking players if the light is green
        if light == "green":
            print("Green light - Clicking players simultaneously...")
            click_all_players()

            # After clicking, wait for a short time to let the players move
            time.sleep(0.001)  # Adjust this as needed

            # After clicking, check if the light turned red
            light = get_light_state()
            while light == "red":
                print("Red light - Waiting for green...")
                time.sleep(0.001)  # Check every 50ms for the light to turn green
                light = get_light_state()

        # If the light is red, just wait
        else:
            print("Red light - Waiting...")
            time.sleep(0.001)  # Check every 50ms for the light to turn green

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    driver.quit()

