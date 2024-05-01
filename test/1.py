import math

c = 299792458 
d =1

RSS1 = -28
RSS2 = -40

f = 2_452_000_000

Pr1 = 10 ** (RSS1 / 10)
Pr2 = 10 ** (RSS2 / 10)
Prd = Pr1 - Pr2

Ptd = Prd + 20 * math.log10(4 * math.pi / c) + 20 * math.log10(f) + 20 * math.log10(d)

RSSd = 10*math.log10(Ptd)

print(Ptd,RSSd)