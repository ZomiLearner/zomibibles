def fetch_tbs_verse(language_code, book, chapter, verse):
    driver = setup_selenium()

    try:
        url = f"https://www.tbsonlinebible.com/#{language_code}_{book}_{chapter}"
        driver.get(url)

        human_sleep(1.5, 3.0)
        human_scroll(driver, total_distance=random.randint(400, 900))

        element_id = f"{book}_{chapter}_{verse}"
        xpath = f"//*[@id='{element_id}']"
        element = driver.find_element(
            By.XPATH,
            xpath # f"//*[@id='{book}_{chapter}_{verse}']"
        )

        # Wait up to 10 seconds for the element to be present in DOM
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

        driver.execute_script("arguments[0].click();", element)

        driver.execute_script("""
            window._copiedValue = null;

            const originalWrite = navigator.clipboard.writeText;
            navigator.clipboard.writeText = function(text) {
                window._copiedValue = text;
                return Promise.resolve();
            };
        """)

        copy_btn = driver.find_element(
            By.XPATH,
            "//*[@id='selectMenu']/li[2]/a"
        )
        driver.execute_script("arguments[0].click();", copy_btn)

        copied_text = driver.execute_script(
            "return window._copiedValue;"
        )

        # if copied_text:
        #     print("Copied text:", copied_text.split("\n")[0])

        return copied_text.split("\n")

    finally:
        driver.quit()

# text = fetch_tbs_verse("smt", "GEN", "17", "25") # 
text = fetch_tbs_verse("smt", "GEN", "31", "40") 
print(text)
