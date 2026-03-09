# What we've achieved

- developed web-based AI search tool where theses are returned based on semantic similarity to user's search term in order of relevance 'score' 
    - via abstract and title
- implemented filters where users can modify number of results, what theses are returned based on year of publication (and whether to include ones without a publication year), search for theses written by certain author(s), and search for theses based on subject discipline.
    - Implemented via metadata and a slight permutation/similarity search over names
- displayed thesis metadata and enabled user to view and download thesis directly from search page
    - Taken from the ethesis durham website (publicly available information)
- enabled users to ask the system to generate an AI summary of a thesis, as well as ask specific questions about the thesis in question
    - Implemented using Gemini (publicly available API) which reads the thesis and is prompted to summarise it.
- offer 6 copy/pasteable citations for each thesis in different standards
    - ['UKHarvard', 'APA', 'MLA', 'Chicago', 'IEEE', 'Harvard']
- implemented a scalable tool (potentially) capable of handling entire EThOS dataset
    - Semantic search "learns" or returns better results based off of the amount and varying topics the data has, so theoretically, the EThOS dataset would improve the search's results compared to the smaller Durham dataset.

# What we haven't achieved, why, and how it could be in future

- implemented feature offering analysis of epistemic diversity of set of returned theses.
- - Why: would require group analysis of theses
- - How in future: (dependent on how much the theses' backgrounds impacts thesis' epistemology) when using AI API model with greater storage capacity

- implemented feature offering analysis/summary of how certain theses link/connect.
- - Why: would require group analysis of theses
- - How in future: when using AI API model with greater storage capacity

- implemented the tool which currently works with the EThOS dataset (actually only works with Durham E-Theses dataset).
- - Why: we have most of the metadata, but not the actual thesis content
- - How in future: current system should work with currently avaialble EThOS info, but because theses content isn't available, the summary and thesis Q&A wouldn't work. 

     - Either further use of an accessable AI tool like Gemini (via comparing theses) or by changing the semantic search to use more of a LLM + RAG approach which would likely scale better given time and resources
- implemented the tool which currently works with the EThOS dataset (actually only works with Durham E-Theses dataset, but we have a working prototype).
    - Simple switch over


- implemented filter/analysis based on background - potential feature for future development.
- supplying user with further background information about thesis (not just author and year of publication)
    - A further DB lookup or implementation with Orcid to lookup author(s)' information and display it
- enabled users to ask an unlimited number of questions - system currently only uses Gemini API Free tier, meaning the requests are limited to 20 per API key. Using free tier means some larger theses (400+ pages) cannot be summarised.  
    - Scaling by paying for a further API key or changing the model entirely to a more localised version (takes vast time and resources to be of a similar quality)
- security and login systems are not up to CIS standards (or any standard I suppose..)