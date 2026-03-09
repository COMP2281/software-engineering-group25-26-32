# What we've achieved

- developed web-based AI search tool where theses are returned based on semantic similarity to user's search term in order of relevance 'score'
- implemented filters where users can modify number of results, what theses are returned based on year of publication (and whether to include ones without a publication year), search for theses written by certain author(s), and search for theses based on subject discipline.
- displayed thesis metadata and enabled user to view and download thesis directly from search page
- enabled users to ask the system to generate an AI summary of a thesis, as well as ask specific questions about the thesis in question
- offer 6 copy/pasteable citations for each thesis 
- implemented a scalable tool (potentially) capable of handling entire EThOS dataset

# What we haven't achieved

- implemented feature offering analysis of epistemic diversity of set of returned theses.
- implemented feature offering analysis/summary of how certain theses link/connect.
- implemented the tool which currently works with the EThOS dataset (actually only works with Durham E-Theses dataset).
- implemented filter/analysis based on background - potential feature for future development.
- supplying user with further background information about thesis (not just author and year of publication)
- enabled users to ask an unlimited number of questions - system currently only uses Gemini API Free tier, meaning the requests are limited to 20 per API key. Using free tier means some larger theses (400+ pages) cannot be summarised.