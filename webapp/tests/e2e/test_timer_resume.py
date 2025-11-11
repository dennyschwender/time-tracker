import pytest

@pytest.mark.skip("Playwright not configured in CI; run locally following README instructions")
def test_timer_resume_smoke(page):
    # This is a Playwright test placeholder. It expects Playwright and the webapp running on localhost:5000.
    # Steps (manual/automated with Playwright):
    # - open /
    # - start timer with description 'E2E Test'
    # - stop timer
    # - click Resume on the created entry
    # - verify timer shows running
    page.goto('http://localhost:5000/')
    page.fill('#timer_description', 'E2E Test')
    page.click('#timer_start')
    page.wait_for_timeout(1500)
    page.click('#timer_stop')
    # find the resume button in entries
    resume_buttons = page.locator('text=Resume')
    assert resume_buttons.count() >= 1
    resume_buttons.nth(0).click()
    # timer should be running
    assert page.locator('#timer_status').inner_text().startswith('Running')
