# Rajasthan Royals: public context for the IPL 2027 auction layer

The handover refers to a supplied `context/rr_auction_context.md`. It was not in the repository, so this
file was assembled on 2026-11-11 from the competition data and a web search. Every line is tagged
**[data]** (derived from the supplied CSVs), **[sourced]** (a public report, link given) or
**[unverified]** (could not be confirmed from a primary source). Nothing here feeds the Unstop rankings.

## Season and squad

- **[data]** RR's IPL 2026 squad (comp_id 3298, team_id 3) lists 27 players. Twenty appeared in a match.
  Regulars by appearances: Vaibhav Sooryavanshi, Dhruv Jurel, Yashasvi Jaiswal, Jofra Archer (16 each),
  Donovan Ferreira (15), Riyan Parag (14, captain in 14), Ravindra Jadeja (14), Nandre Burger (13),
  Brijesh Sharma (13), Ravi Bishnoi (9), Shimron Hetmyer (8), Yash Punja (8).
- **[data]** RR played 16 matches in IPL 2026 and won 9.
- **[data]** Sanju Samson (player_id 2258) appears for Chennai Super Kings in IPL 2026, not RR.
- **[sourced]** RR finished fourth in the league phase and lost the Eliminator to Sunrisers Hyderabad.
  Coach Kumar Sangakkara said the side was 10 to 15 runs short.
  https://www.outlookindia.com/sports/cricket/indian-premier-league-2026-dispatch-may-24-rajasthan-royals-qualify-playoffs-decided
  https://newsable.asianetnews.com/sports/ipl-2026-rr-were-1015-runs-short-says-sangakkara-after-gt-loss-articleshow-vlzit24
- **[sourced]** Season reviews name two weaknesses: the middle order between the openers and the
  finishers, and the lack of a second strike bowler to share the load with Jofra Archer. Sam Curran missed
  the whole season through injury.
  https://www.sportsyaari.com/cricket/rr-ipl-2026-report-card-full-player-ratings-and-what-went-wrong-this-season-for-riyan-parags-side-27860/
  https://www.mrcricketuae.com/opinion/rajasthan-royals-ipl-2026-strengths-fault-lines-and-the-riyan-parag-test
- **[sourced]** Vaibhav Sooryavanshi scored 776 runs in 16 matches at a strike rate above 237.
  https://mobi.supersport.com/cricket/news/f556ff9c-fba9-4f1c-9f0c-a1229bc77e14/ipl-2026-wrap-kohli-s-double-crown-teen-sensation-stuns

## Auction rules

- **[sourced]** Retention and release lists for IPL 2027 are due to the BCCI by 15 November 2026 and the
  trade window closes on 9 December 2026. As of this writing the lists are not public, so availability
  of every player is "unknown, check after retention list".
  https://www.crictracker.com/cricket-news/bcci-sets-november-15-as-ipl-2027-retention-deadline-ahead-of-auction-3582/
- **[sourced, for IPL 2026]** Squad limit 25 players, at most 8 overseas players per squad, purse
  Rs 125 crore. https://www.deccanherald.com/sports/cricket/ipl-2026-auction-from-overseas-player-salary-cap-to-maximum-purse-all-rules-explained-3824968
- **[unverified for IPL 2027]** Whether the 2027 auction is a mini or a mega auction, the purse, and the
  number of retentions allowed. Reports conflict: one describes a mini-auction with no fixed retention
  cap, another a six-retention framework. Treat the 2026 figures as the working assumption and re-check.
- **[unverified, standard IPL playing condition]** At most 4 overseas players in the playing XI, with
  the Impact Player rule in force.
- **[data, derived]** Overseas status is not a column in the data. It is derived as "national team in the
  mapping file is not India" and is flagged as derived wherever it is used.
