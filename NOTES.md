receipt.py

I didn't need much setup here since every function just takes plain values and returns plain values. What shaped my tests most was the arithmetic — the rate, surcharge, and discount constants — so I made sure every rule had a test checking the exact number, not just "roughly right." I didn't test every boundary combination around the discount cutoff; I decided what I had was good enough.

logsweep.py

I had to use tmp_path to make fake log files, since I couldn't touch real files or leave anything behind, and capsys to check the printed output since that's most of what this program does. The trickiest part was the "worst file" logic, which uses strict > instead of >=, so I wrote a specific test for a tie. I also tested a line that starts with a level name but isn't an exact match, since the program checks with startswith.

depotwatch.py

This one needed the most setup — I used monkeypatch to fake requests.get so my tests could run without the depot server on, which is the whole point of this program. Since report() has two different error branches (bad status vs. can't reach the depot at all), I wrote a separate test for each, plus one for the normal success case. The other functions like heavy_shipments and unweighed didn't need any faking since they just take plain data.