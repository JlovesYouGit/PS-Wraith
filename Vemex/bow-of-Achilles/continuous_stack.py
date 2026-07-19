"""
continuous_stack.py — Mana Ciel Continuous UTXO Stacker
Generates wallets indefinitely, printing progress every batch.
Stop with Ctrl+C or kill the process.
"""

from mana_ciel.wallet import ManaCielWallet
from mana_ciel.narrative_timing import NarrativeTimer, narrative_sleep, get_narrative_state
import time

BATCH = 1000
w = ManaCielWallet()

print(f"Starting stacker | wallets={len(w.load_all())} | utxo={w.collective_utxo() / 100_000_000:.8f} BTC")
coordinate_q = 0
while True:
    with NarrativeTimer(f"batch_q{coordinate_q}") as t:
        for _ in range(BATCH):
            w.generate()
    state = get_narrative_state()
    elapsed = t.elapsed_ns / 1e9
    rate = BATCH / elapsed if elapsed > 0 else 0
    print(f"[pulse={state['pulse']}ns q={coordinate_q}] +{BATCH} wallets | total={len(w.load_all())} | utxo={w.collective_utxo() / 100_000_000:.8f} BTC | {rate:.1f} w/s | {t}")
    narrative_sleep(coordinate_q % 10)
    coordinate_q += 1
