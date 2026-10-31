"""Walk the kiosk through every screen. Used for screenshots and asset sizing.

    python tools/tour.py shots/      # save a PNG of each step (needs ImageMagick 'import')
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.argv = [sys.argv[0], "--windowed"] + sys.argv[1:]

import dmarby as d  # noqa: E402


def run(snapshot=None):
    d.install_bundled_fonts()
    root = d.tk.Tk()
    root.geometry("800x480+0+0")
    app = d.Kiosk(root)
    for job in list(app.jobs.values()):
        root.after_cancel(job)
    app.jobs.clear()
    root.after_cancel = lambda *a: None
    real_after = root.after
    root.after = lambda ms, fn=None, *a: "x"   # freeze timers; we drive everything
    n = [0]

    def snap(name):
        app.redraw()
        root.update()
        n[0] += 1
        if snapshot:
            snapshot(f"{n[0]:02d}_{name}")

    # Start
    snap("welcome")
    app.show("contact"); snap("contact")
    app.pick_lang("en"); snap("exchange_type")
    app.start_cash(); snap("choose_tx")
    # Bill to coins
    app.show("pick_bill"); app.stock[5] = 0; app.stock[20] = 0
    snap("pick_bill")
    app.stock = dict(d.START_STOCK); app.stock[5] = 0
    app.pick_bill(50)
    for _ in range(2): app.adjust(20, 1)
    for _ in range(5): app.adjust(1, 1)
    snap("build_mix_bill")
    app.fill_mix(); app.to_insert(); snap("insert_bill")
    app.bill_inserted(50); snap("insert_bill_checking")
    app.bill_checked(50, True); snap("insert_bill_done")
    app.to_review_from_insert(); snap("review_bill")
    # wrong bill
    app.reset_session(); app.pick_bill(50); app.fill_mix(); app.to_insert()
    app.bill_inserted(20); app.bill_checked(20, True); snap("wrong_bill")
    app.reroute_bill(); snap("build_mix_reroute")
    # bigger bill, can't cover
    app.reset_session(); app.pick_bill(50); app.fill_mix(); app.to_insert()
    saved = dict(app.stock); app.stock = {20: 0, 10: 0, 5: 0, 1: 60}
    app.bill_inserted(100); app.bill_checked(100, True); snap("incident_cant_change")
    app.stock = saved
    # Break coins
    app.reset_session(); app.show("coin_mode"); snap("coin_mode")
    app.show("pick_coin"); snap("pick_coin")
    app.pick_coin(20); app.adjust(10, 1)
    for _ in range(5): app.adjust(1, 1)
    snap("build_mix_break")
    app.fill_mix(); app.to_insert()
    app.coin_inserted(5); app.close_check(); app.coin_inserted(1); snap("insert_coins_counting")
    app.close_check(); snap("insert_coins")
    app.demo["reject"] = True; app.coin_inserted(10, None); snap("insert_coins_rejected")
    app.coin_inserted(10); app.close_check(); app.coin_inserted(1); app.close_check()
    app.coin_inserted(1); app.close_check(); app.coin_inserted(1); app.close_check()
    app.coin_inserted(1); app.close_check()
    app.to_review_from_insert(); snap("review_break")
    app.start_dispense(); app.coin_dropped(10); app.coin_dropped(1); app.coin_dropped(1)
    snap("dispensing")
    while app.dropped < len(app.queue):
        app.coin_dropped(app.queue[app.dropped])
    app.finish_dispense(); snap("done")
    # Combine coins
    app.reset_session(); app.show("have_coins")
    for _ in range(5): app.adjust_have(1, 1)
    app.adjust_have(5, 1); snap("have_coins")
    app.to_combine_choice(); snap("combine_choice")
    app.start_combine_insert(); app.coin_inserted(5); app.close_check(); snap("insert_combine")
    # Timeouts
    now = time.monotonic()
    app.show("insert", {"kind": "timeout_money", "deadline": now + 10}); snap("timeout_money")
    app.reset_session(); app.pick_bill(50); app.fill_mix(); app.to_insert()
    app.show("insert", {"kind": "timeout_empty", "deadline": now + 10}); snap("timeout_empty")
    # Jam
    app.reset_session(); app.pick_coin(10); app.fill_mix(); app.to_insert()
    app.coin_inserted(10); app.close_check(); app.to_review_from_insert(); app.start_dispense()
    app.coin_dropped(1); app.payout_fault(); snap("incident_jam")
    app.show("admin"); snap("admin")
    app.admin_fix()
    # Out of coins
    saved = dict(app.stock); app.stock = {c: 0 for c in d.COINS}
    app.show("out_of_coins"); snap("out_of_coins")
    app.stock = saved
    # GCash
    app.start_gcash(); snap("gc_amount_empty")
    for ch in "200": app.gc_amount_digit(ch)
    snap("gc_amount")
    app.gcash_balance = 100; app.gc_amount_next(); snap("gc_balance")
    app.gcash_balance = d.GCASH_START_BALANCE; app.show("gc_amount"); app.gc_amount_next()
    snap("gc_number_empty")
    for ch in "0917123456": app.gc_number_digit(ch)
    snap("gc_number_typing")
    app.gc_number_digit("7"); app.gc_number_next()
    app.bill_inserted(100); app.bill_checked(100, True); app.coin_inserted(20); app.close_check()
    snap("gc_insert")
    app.bill_inserted(50); app.bill_checked(50, True)
    app.coin_inserted(20); app.close_check(); app.coin_inserted(20); app.close_check()
    app.start_cashing(); snap("gc_cashing")
    app.cashing_result(False); snap("gc_error")
    app.reenter_number(); snap("gc_reenter")
    for ch in "09171234567": app.gc_number_digit(ch)
    app.gc_number_next(); app.cashing_result(True); snap("gc_success")
    root.destroy()


if __name__ == "__main__":
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if out:
        os.makedirs(out, exist_ok=True)
    run((lambda name: subprocess.run(["import", "-window", "root", os.path.join(out, name + ".png")]))
        if out else None)
