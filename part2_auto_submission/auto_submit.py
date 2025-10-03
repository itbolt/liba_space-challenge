\
import argparse, asyncio, json, datetime, re
from playwright.async_api import async_playwright

BUTTON_TEXTS = ["Submit", "Apply", "Send Application", "Apply Now", "Finish"]

async def match_field(page, patterns):
    loc = page.locator("input,textarea")
    count = await loc.count()
    for i in range(count):
        handle = loc.nth(i)
        try:
            name = (await handle.get_attribute("name")) or ""
            _id = (await handle.get_attribute("id")) or ""
            aria = (await handle.get_attribute("aria-label")) or ""
            ph = (await handle.get_attribute("placeholder")) or ""
            text = (" ".join([name, _id, aria, ph])).lower()
            if any(p in text for p in patterns):
                return handle
        except Exception:
            pass
    return None

async def run(job_url, name, email, phone, resume_pdf):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(job_url, wait_until="domcontentloaded", timeout=60000)

        name_parts = name.strip().split()
        first = name_parts[0]
        last = name_parts[-1] if len(name_parts) > 1 else ""

        first_input = await match_field(page, ["first", "first name", "given"])
        last_input  = await match_field(page, ["last", "last name", "family", "surname"])
        full_input  = await match_field(page, ["name"])

        if first_input:
            await first_input.fill(first)
        if last_input:
            await last_input.fill(last)
        elif full_input and not first_input:
            await full_input.fill(name)

        email_input = await match_field(page, ["email"])
        if email_input:
            await email_input.fill(email)

        phone_input = await match_field(page, ["phone", "mobile"])
        if phone_input:
            await phone_input.fill(phone)

        # File upload
        file_inputs = page.locator("input[type=file]")
        if await file_inputs.count() > 0:
            await file_inputs.first.set_input_files(resume_pdf)

        # Click a submit/apply button
        clicked = False
        for txt in BUTTON_TEXTS:
            btn = page.get_by_role("button", name=re.compile(txt, re.I))
            if await btn.count() > 0:
                await btn.first.click()
                clicked = True
                break
        if not clicked:
            submits = page.locator("input[type=submit]")
            if await submits.count() > 0:
                await submits.first.click()
                clicked = True

        await page.wait_for_timeout(2500)

        result = {
            "job_url": job_url,
            "status": "submitted" if clicked else "attempted",
            "submitted_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        }
        print(json.dumps(result, indent=2))
        await browser.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--job_url", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--phone", required=True)
    ap.add_argument("--resume_pdf", required=True)
    args = ap.parse_args()
    asyncio.run(run(args.job_url, args.name, args.email, args.phone, args.resume_pdf))
