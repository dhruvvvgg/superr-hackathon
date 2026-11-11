# RR and IPL 2027 auction context

Collected from public web searches on 2026-11-11. Each line names its source. Anything not listed here is unverified. Re-check after retention lists are published.

## Auction timeline

- The IPL 2027 auction is a mini-auction on 16 December 2026 in Goa (ITC Grand Goa). Source: crictracker.com "IPL 2027 auction to be held on December 16 in Goa".
- It is the last mini-auction of the 2023 to 2027 cycle. A mega auction is confirmed ahead of the 2028 season. Source: crictracker.com, businesstoday.in.
- The retention and release deadline was moved from 15 November to 17 November 2026. Player registration closes 23 November. Franchise shortlists are due 1 December. The official auction register is released 3 December. Source: sportsdigest.in "BCCI Extends Player Retention Deadline".
- The trade window stays open until one week before the auction (9 December). Source: crictracker.com.
- Consequence for this work: availability of any player is unknown until the retention and release lists are public. Treat availability as unconfirmed.

## RR background (IPL 2026 cycle)

- Before the IPL 2026 auction RR traded Sanju Samson to CSK for Ravindra Jadeja and Sam Curran, traded Nitish Rana to Delhi Capitals and received Donovan Ferreira. Sources: ianslive.in, cricketaddictor.com.
- RR released Wanindu Hasaranga, Maheesh Theekshana, Fazalhaq Farooqi, Akash Madhwal, Ashok Sharma, Kunal Rathore and Kumar Kartikeya. Source: indiatvnews.com.
- RR retained 13 players (eight Indian, five overseas). Yashasvi Jaiswal and Riyan Parag led the retention list. Sources: rajasthanroyals.com, sportsyaari.com.
- RR entered the IPL 2026 mini-auction with INR 16.05 crore and nine slots, one overseas. They bought nine players for INR 13.40 crore, including Ravi Bishnoi, and filled a 25-man squad. Jofra Archer was signed for INR 12.50 crore. Sources: rajasthanroyals.com, icecric.news.
- Kumar Sangakkara is head coach for IPL 2026. Source: crictracker.com.
- IPL 2026 result: one preview article reports RR finished fourth with eight wins and a positive net run rate. Source: mykhel.com (single secondary source, verify against the points table).
- The 2026 squad itself can be read from the supplied data: `competition_team_player_mapping.csv`, comp_id 3298, team_id 3.

## Not verified

- RR's 2027 retention or release decisions. One article (mykhel.com) speculates about five likely releases. It is a prediction, not a decision. Do not use it as fact.
- RR's remaining purse and open slots for 2027.
- Overseas status of individual players (not in the dataset; derive from national team and mark as derived).
- Playing-XI overseas limit of 4 (only one low-quality source; standard IPL condition, assumed).

## Cross-checked on 2026-11-11 (second round of searches)

- Squad limits confirmed by several outlets for the 2026 cycle: at most 25 players, at least 18, at most 8
  overseas. Sources: deccanherald.com (IPL 2026 auction rules explained), wisden.com (IPL 2026 auction all
  you need to know). Whether 2027 keeps them is not stated; assumed unchanged.
- Overseas players' auction fee is capped at the lower of INR 18 crore and the highest mega-auction price
  (2026 rule, same sources). Whether it applies in 2027 is unverified.
- RR IPL 2026 playoffs: beat Sunrisers Hyderabad by 47 runs in the Eliminator (27 May), then lost Qualifier 2
  to Gujarat Titans by 7 wickets (Shubman Gill 104; RR 214/6 with Sooryavanshi 96). Sources: wionews.com,
  outlookindia.com, iplt20.com. This matches the supplied match data exactly.
- Sooryavanshi, IPL 2026: 776 runs in 16 matches, average 48.5, strike rate 237.3 (supersport.com). The
  ball data rebuilds exactly these figures.
- RR's win count: the data show 8 league wins and 1 playoff win (9 in 16 matches). The mykhel.com "eight
  wins" refers to the league stage. The discrepancy noted below is resolved.
- Match 20190 (LSG v SRH, 7 April 2023): LSG won by 5 wickets (SRH 121/8, LSG 127/5 in 16 overs; ESPNcricinfo
  and others). The supplied result string says 6 wickets and is wrong. Corrected by `source_overrides`.
- Retention lists: no official IPL 2027 list was found on 2026-11-11; deadline 17 November.
- No source found for the final league table of RR (one mid-season snapshot only), so wins in the league
  are taken from the data.

## Derived from the supplied CSVs (not web sources)

- RR's IPL 2026 squad (comp_id 3298, team_id 3) lists 27 players and 20 of them appeared in a match.
  Regulars by appearances: Vaibhav Sooryavanshi, Dhruv Jurel, Yashasvi Jaiswal, Jofra Archer (16 each),
  Donovan Ferreira (15), Riyan Parag and Ravindra Jadeja (14), Nandre Burger and Brijesh Sharma (13),
  Ravi Bishnoi (9), Shimron Hetmyer and Yash Punja (8).
- The match data holds 16 RR matches in IPL 2026: 14 league (8 wins), the Eliminator (won) and Qualifier 2
  (lost).
- Sam Curran is in the 2026 squad list but has no appearances. Sanju Samson (player_id 2258) is a CSK
  player in IPL 2026.
