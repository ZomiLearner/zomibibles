# @title Bible scrapping codes
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

def human_sleep(base_min=0.3, base_max=1.2):
    """Randomized delay to avoid robotic timing."""
    delay = random.uniform(base_min, base_max)
    time.sleep(delay)


def human_type(element, text, min_delay=0.05, max_delay=0.25, pause_prob=0.08):
    """Type like a human: per-character delays and occasional pauses."""
    for ch in text:
        element.send_keys(ch)
        # small delay between keystrokes
        time.sleep(random.uniform(min_delay, max_delay))
        # occasional longer pause
        if random.random() < pause_prob:
            time.sleep(random.uniform(0.4, 1.0))


def human_scroll(driver, total_distance=800):
    """Scroll in small increments with pauses, sometimes overshooting."""
    scrolled = 0
    while scrolled < total_distance:
        step = random.randint(60, 160)
        driver.execute_script(f"window.scrollBy(0, {step});")
        scrolled += step
        human_sleep(0.2, 0.8)

        # occasional micro scroll back
        if random.random() < 0.15:
            back_step = random.randint(20, 80)
            driver.execute_script(f"window.scrollBy(0, {-back_step});")
            human_sleep(0.3, 0.9)


def human_move_to_element(driver, element, steps=12):
    """
    Approximate human mouse movement by moving in small steps
    toward the element using ActionChains.
    """
    actions = ActionChains(driver)
    loc = element.location
    size = element.size

    # target point with slight random offset
    target_x = loc["x"] + size["width"] * random.uniform(0.2, 0.8)
    target_y = loc["y"] + size["height"] * random.uniform(0.2, 0.8)

    # start from (0,0) relative moves
    current_x, current_y = 0, 0
    delta_x = target_x / steps
    delta_y = target_y / steps

    for i in range(steps):
        # add jitter
        jitter_x = random.gauss(0, 3)
        jitter_y = random.gauss(0, 3)
        move_x = delta_x + jitter_x
        move_y = delta_y + jitter_y

        actions.move_by_offset(move_x, move_y).perform()
        current_x += move_x
        current_y += move_y
        human_sleep(0.02, 0.08)

    # small settle jitter
    for _ in range(random.randint(1, 3)):
        actions.move_by_offset(random.gauss(0, 1), random.gauss(0, 1)).perform()
        human_sleep(0.02, 0.06)


def human_click(driver, element):
    """Move like a human, then click with a slight delay."""
    human_move_to_element(driver, element)
    human_sleep(0.05, 0.2)
    ActionChains(driver).click().perform()
    human_sleep(0.3, 1.0)
