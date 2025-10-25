from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# ✅ 텔레그램 설정
TELEGRAM_TOKEN = "5918666639:AAGBWCuYmgh1kZhp5uDIaqTYQe4SLji0hWU"
TELEGRAM_CHAT_ID = "5771657329"

URL = "https://flowoom.com/product/detail.html?product_no=2867&cate_no=83&display_group=1"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        res = requests.post(url, data=data)
        if res.status_code == 200:
            print("📨 텔레그램 메시지 전송 완료!")
        else:
            print("⚠️ 텔레그램 전송 실패:", res.text)
    except Exception as e:
        print("⚠️ 텔레그램 전송 오류:", e)


def main():
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--lang=ko-KR")
    chrome_opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_opts)

    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 10)

        # ✅ 1. 색상 옵션 클릭 (Cream)
        ul = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[option_product_no="2867"]')))
        li = driver.find_element(By.CSS_SELECTOR, 'ul[option_product_no="2867"] li[option_value="Cream"]')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", li)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", li)
        print("\n🎨 'Cream' 색상을 클릭했습니다.\n")

        # ✅ 2. 사이즈 옵션 로드 대기
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#product_option_id2")))
        time.sleep(1.5)

        select_elem = driver.find_element(By.CSS_SELECTOR, "#product_option_id2")
        options = select_elem.find_elements(By.TAG_NAME, "option")

        # ✅ 3. 품절 상태 판별 (텍스트 + disabled 동시 검사)
        size_info = []
        for opt in options:
            text = opt.text.strip()
            if not text or text.startswith("*") or "size 선택" in text or "----" in text:
                continue

            # 🔍 품절 조건 1: 텍스트에 [품절] 포함
            has_text_soldout = "[품절]" in text

            # 🔍 품절 조건 2: disabled 속성 존재
            is_disabled = opt.get_attribute("disabled") is not None

            # ✅ 둘 중 하나라도 참이면 품절
            if has_text_soldout or is_disabled:
                status = "품절"
            else:
                status = "재고 있음"

            size_info.append((text.replace("[품절]", "").strip(), status))

        # ✅ 4. 결과 정리 및 출력
        message_lines = ["🎨 [Flowoom] Cream 색상 재고 현황\n"]
        for size, status in size_info:
            line = f"❌ {size} 품절" if status == "품절" else f"✅ {size} 주문 가능"
            message_lines.append(line)
            print(line)

        sold_out = [s for s, st in size_info if st == "품절"]
        available = [s for s, st in size_info if st == "재고 있음"]

        summary = "\n\n📦 요약:\n"
        if available:
            summary += f"- 주문 가능: {', '.join(available)}\n"
        if sold_out:
            summary += f"- 품절: {', '.join(sold_out)}"

        message = "\n".join(message_lines) + summary
        # send_telegram_message(message)

    except Exception as e:
        print("에러 발생:", e)
        send_telegram_message(f"⚠️ [Flowoom] 오류 발생: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
