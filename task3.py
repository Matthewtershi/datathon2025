from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Set up the ChromeDriver using the Service class
service = Service(executable_path="C:\\Users\\ayue\\chromedriver-win64\\chromedriver.exe")  # Adjust the path if necessary
driver = webdriver.Chrome(service=service)

# ================================
# STEP 1: Scrape main page before login
# ================================
main_url = "https://level3-dot-secure-bonus-377122.uc.r.appspot.com/"
driver.get(main_url)
time.sleep(2)  # Let the page load

main_page_source = driver.page_source
main_soup = BeautifulSoup(main_page_source, 'html.parser')

# Find all encrypted class cards
encrypted_classes = []
main_cards = main_soup.find_all('div', class_='card')
for card in main_cards:
    card_text = card.get_text(separator=' ', strip=True)
    encrypted_code = card_text.split(": ")[-1].strip()
    encrypted_classes.append(encrypted_code)

print("Encrypted Class Card Info from Main Page:")
for entry in encrypted_classes:
    print(entry)

# ================================
# STEP 2: Log in to scrape player data
# ================================
login_url = "https://level3-dot-secure-bonus-377122.uc.r.appspot.com/scrape"
driver.get(login_url)

# Wait for login fields
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

username_field = driver.find_element(By.NAME, "username")
password_field = driver.find_element(By.NAME, "password")
username_field.send_keys("young-hee-admin")
password_field.send_keys("squidgame2025")
password_field.send_keys(Keys.RETURN)

# Wait for logged-in page
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "cards-container")))

# Scrape player data
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

cards_container = soup.find(id="cards-container")
players = []

if cards_container:
    player_cards = cards_container.find_all('div', class_='card')

    for card in player_cards:
        player_data = {
            'first_name': 'Unknown',
            'last_name': 'Unknown',
            'player_number': 'Unknown'
        }

        spans = card.find_all('span')
        for span in spans:
            label_tag = span.find('strong')
            if label_tag and label_tag.string:
                label = label_tag.string.strip().lower().replace(":", "")
                value = label_tag.next_sibling.strip() if label_tag.next_sibling else None
                if label in player_data and value:
                    player_data[label] = value

        players.append(player_data)

    print("\nLogged-in Player Information:")
    for player in players:
        print(f"Player Number: {player['player_number']}, Name: {player['first_name']} {player['last_name']}")
else:
    print("The cards container was not found!")



# ================================
# STEP 3: Decrypt player IDs and match with Hwang In-Ho or Oh Il-nam
# ================================
decrypted_players = []

for player in players:
    # Get the encrypted number from the player's div
    player_number = player['player_number']
    
# Wait for the player element containing the encrypted number
encrypted_element = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, f"//body//div[@class='player-list']//div[@class='player']//p[text()='{player_number}']"))
)

# Extract the encrypted number from the element
encrypted_number = encrypted_element.text.strip()

# Enter the encrypted number into the input field
encrypted_input = driver.find_element(By.ID, 'encryptedInput')
encrypted_input.clear()  # Clear any previous input
encrypted_input.send_keys(encrypted_number)

# Click the decrypt button
decrypt_button = driver.find_element(By.ID, 'decryptBtn')
decrypt_button.click()

# Wait for the decrypted output to appear
decrypted_output_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'decryptedOuput'))
)

# Get the decrypted output (player name)
decrypted_output = decrypted_output_element.text.strip()

# Check if the decrypted output matches Hwang In-Ho or Oh Il-nam
if decrypted_output == "Hwang In-Ho" or decrypted_output == "Oh Il-nam":
    print(f"Found {decrypted_output} with ID: {player_number}")
    decrypted_players.append({
        'player_number': player_number,
        'decrypted_name': decrypted_output
    })


# ================================
# Final Results
# ================================
print("\nDecrypted Players Found:")
for player in decrypted_players:
    print(f"Player ID: {player['player_number']}, Name: {player['decrypted_name']}")



# Quit the browser
driver.quit()
