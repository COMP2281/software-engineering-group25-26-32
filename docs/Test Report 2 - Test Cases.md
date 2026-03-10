### 2.1 \- Unit Test Cases

Below are four examples of unit tests carried out and their results when ran against the final system.

**UT1 \- Credentials verification**

| Test Case ID | UT1 |
| :---- | :---- |
| Description of test | Ensure check\_creds() only returns True when valid credentials are passed to it  |
| Related requirement document details | None |
| Pre-requisites for test | PyTest is installed on the system and is being run from the python directory. |
| Test procedure | Create a mock users database with fake entries. Pass a valid username and password into check\_creds() Assert that it returns True Pass an invalid username and password into check\_creds() Assert that it returns False Pass a valid username and an invalid password into check\_creds() Assert that it returns False Pass empty username and password into check\_creds() Assert that it returns False Delete mock users database |
| Equivalence Classes | Valid data \- a valid username and password combination from the Admin database Invalid data \- an invalid username and an invalid password (or missing) Partially valid data \- valid username and invalid password and vice versa. |
| Test material used | test\_auth.py \- automated test script for auth functions, creates mock users database. PyTest |
| Expected result (test oracle) | The check\_creds() function should return True only if a valid username and a valid password are entered. If either (or both) of the username or password are invalid or missing, check\_creds() should return False. |
| Failure Severity | Critical \- Failure of this test would mean it is possible to gain unauthorised access to the system, or it is not possible to gain authorised access to the system. |
| Comments | None |
| Created by | JS |
| Test environment(s) | Windows 11 |

**UT2 \- Thesis text loading from JSONL**

| Test Case ID | UT2 |
| :---- | :---- |
| Description of test | Ensure load\_pages() correctly returns the thesis contents (stored as JSONL) of the provided id, including page numbers of each page, ready to be passed into Gemini |
| Related requirement document details | Feature 5 \- AI Summarisation |
| Pre-requisites for test | PyTest is installed on the system and is being run from the python directory. |
| Test procedure | Create mock Thesis database with a mock entry containing two pages stored as JSONL Call load\_pages() with the id of the mock entry Assert that the returned text contains the mock content and page numbers, and that the pages are in the correct order. Call load\_pages() with an id not in the mock database Assert that the empty string is returned Delete the mock Thesis database |
| Equivalence Classes | Valid IDs \- those that are in the database Invalid IDs \- those not in the database, of the wrong type or missing. |
| Test material used | test\_gemini\_ai\_summariser.py \- automated test script for the helper functions for producing AI summaries Pytest |
| Expected result (test oracle) | For valid IDs, load\_pages() should return a single string containing “PDF PAGE 1: \\n \< page 1 contents\> \\n PDF PAGE 2: \\n \<page 2 contents\> …. ”  Otherwise, return the empty string |
| Failure Severity | High \- Failure of this test would mean that the thesis contents and/or page numbers are not loaded correctly before being put into the Gemini prompt. This could lead to Gemini producing incorrect summaries, or with incorrect page numbers. |
| Comments | The JSONL format used to store the thesis text in the database stores a JSON object per line representing each page of the thesis, containing the page number as well as the text itself. |
| Created by | JS |
| Test environment(s) | Windows 11 |

**UT3 \- Durham Etheses Scraper functionality**

| Test Case ID | UT3 |
| :---- | :---- |
| Description of test | Test the scrape() function of the Durham E-Theses scraper scrapes metadata correctly and adds it to the database |
| Related requirement document details | None |
| Pre-requisites for test | Python httpx is installed on the system. PyTest is installed on the system and is being run from the python directory. |
| Test procedure | Create mock Thesis database Read sample HTML file of thesis page Call scrape() on this file Verify that the mock metadata contained in the HTML has been written to the mock database. Call scrape() on a nonexistent file Verify that nothing is written to the database and scrape() exits with code 1\. Call scrape() on sample HTML for the page of a thesis that has been removed from Durham E-Theses Verify that nothing is written to the database and scrape() exits with code 1\. Delete mock database |
| Equivalence Classes | Valid HTML \- contains the \<meta\> tags with the correct names as in Durham E-Theses Invalid HTML \- does not contain the correct formatting and \<meta\> tags, or is empty. Removed thesis HTML \- contains “\<p\>You seem to be attempting to access an item that has been removed from the repository.\</p\>” |
| Test material used | Test\_durham\_etheses\_scraper\_example.html \- sample HTML page of the same formatting as the thesis pages on Durham E-Theses Test\_durham\_etheses\_scraper.py \- automated PyTest script for testing scraper functionality PyTest |
| Expected result (test oracle) | Valid HTML \- scrape() exits with code 0 and the metadata is written to the database Invalid HTML and Removed Thesis HTML \- scrape() exits with code 1 and nothing is written to the database. |
| Failure Severity | Medium \- scraper functionality is useful for keeping the database up to date with the Durham thesis repository, but is not critical to achieving the client’s requirements. |
| Comments | This tests the scrape function used to build and update the Durham-Etheses database, ensuring only inputted HTML of the correct formatting from the Durham Etheses website is used when adding rows to the database. |
| Created by | JS |
| Test environment(s) | Windows 11 |

**UT4 \- Test search returns the correct fields**

| Test Case ID | UT4 |
| :---- | :---- |
| Description of test | Check that the /search API endpoint returns JSON results with the correct fields |
| Related requirement document details | BR2.2 \- returning search results and displaying to the user |
| Pre-requisites for test | PyTest is installed on the system and is being run from the python directory. |
| Test procedure | Mock the model search function to give fake results Make a POST request to the /search endpoint Assert that /search returns status 200 Assert that the returned data from the endpoint has the correct fields and data |
| Equivalence Classes | Query: A search query has been entered Null: No search query has been entered |
| Test material used | None |
| Expected result (test oracle) | If a query is entered, search should return the mock search results in JSON format with the following fields: name, author, year, abstract, department, pdf\_url, db\_id, score If no query is entered, return status 400 with an appropriate error message |
| Failure Severity | High \- If the search endpoint does not return the correct data in the correct format then the search results displayed to the user will be missing or incorrect. |
| Comments | None |
| Created by | JS |
| Test environment(s) | Windows 11 |

**Unit Test Results:**

| UT1 | Pass |
| :---- | :---- |
| **UT2** | Pass |
| **UT3** | Pass |
| **UT4** | Pass |
| **UT5** | Pass |

### 2.2 \- System Test Cases

**ST1 \- API Load Test**

| Test Case ID | ST1 |
| :---- | :---- |
| Description of test | Test search performance with different numbers of concurrent requests |
| Related requirement document details | BR1.2 \- accessing the API directly |
| Pre-requisites for test | API is running at localhost:8000 The Durham E-Theses database and corresponding model index and IDs files are loaded in the system. |
| Test procedure | Send one request to the /search endpoint Send 10 parallel requests to the /search endpoint Send 50 parallel requests to the /search endpoint Send 100 parallel requests to the /search endpoint For each, record the average and maximum response time. |
| Test material used | load\_test.py \- test file that sends the requests and records the times Load\_test\_results.txt \- text file where the results are stored |
| Expected result (test oracle) | For up to and including 100 concurrent requests, the average response time should not exceed 5 seconds and the maximum response time should not exceed 10 seconds. |
| Failure Severity | Low \- Failure of this test does not affect the functionality of the system, it only affects user experience. |
| Comments | The requests sent during these tests all had the following fields: count: 10, fromYear: 1700, toYear:2026, with the search term selected randomly from: "black holes", "computer vision", "history of France", "harry potter", "climate change", "world war 2", "renewable energy". |
| Created by | MT |
| Test environment(s) | Minimum Hardware Server: Windows 11, Intel Core  i7-1165G7, 16GB DDR4 RAM, no GPU Recommended Hardware Server: Windows 10, AMD Ryzen 7 7800X3D, 32GB DDR5 RAM, RTX 5070Ti |

**ST2 \- Search Functionality and Display of Results**

| Test Case ID | ST2 |
| :---- | :---- |
| Description of test | Test that users can enter a search term and the returned results are displayed back to the user. |
| Related requirement document details | BR2.1 \- entering a search query BR2.2 \- selecting relevant theses and displaying results to the user BR3.1 \- viewing the full theses for the returned results |
| Pre-requisites for test | The frontend server is running locally at localhost:8080 The API server is running locally at localhost:8000 |
| Test procedure | Navigate to the search page (localhost:8080) Enter a search term and click search button Select “View Full Thesis” for the top result |
| Test material used | Durham E-Theses database and corresponding model weights |
| Expected result (test oracle) | Search results are displayed to the user on the web page, ordered by relevance to the query entered), and the system opens the full thesis PDF when “View Full Thesis” is clicked. |
| Failure Severity | High \- The search functionality contains the main functionality of the system and is the most important feature to the client. |
| Comments | The search term entered for this test was “black holes”. |
| Created by | JS |
| Test environment(s) | Server: Windows 11, Intel Core  i5-13400F, 16GB RAM, Nvidia RTX 4060 Client: Windows 11, Google Chrome browser |

**ST3 \- AI Summarisation**

| Test Case ID | ST3 |
| :---- | :---- |
| Description of test | Test that users can obtain AI-generated summaries of the theses returned in search results |
| Related requirement document details | BR5.1 AI Summarisation |
| Pre-requisites for test | The frontend server is running locally at localhost:8080 The API server is running locally at localhost:8000 |
| Test procedure | Navigate to the search page (localhost:8080) Enter a search term and click search button For one of the search results, click the button to generate an AI summary of the returned thesis |
| Test material used | Durham E-Theses database and corresponding  model weights |
| Expected result (test oracle) | The system should display an AI generated summary of the selected thesis |
| Failure Severity | High \- AI summarisation is a key part of the system functionality, enabling the project to leverage the power of AI to reduce the workload of human researchers. |
| Comments | The search term entered was “black holes”, and the selected thesis to be summarised in this test was “Black Holes with Topological Defects: The C-metric in Three and Four Dimensions \- Scoins, Andrew David (2022)” |
| Created by | JS |
| Test environment(s) | Server: Windows 11, Intel Core  i5-13400F, 16GB RAM, Nvidia RTX 4060 Client: Windows 11, Google Chrome browser |

**ST4 \- Admin Page User Access**

| Test Case ID | ST4 |
| :---- | :---- |
| Description of test | Test that the admin page and admin functions can only be accessed by authenticated users  |
| Related requirement document details | None |
| Pre-requisites for test | The frontend server is running locally at localhost:8080 The API server is running locally at localhost:8000 |
| Test procedure | Attempt to navigate to localhost:8080/admin while unauthenticated. Make an unauthenticated API request to localhost:8000/downloadableFiles Authenticate through the login page Attempt to navigate to localhost:8080/admin again Make an authenticated API request to localhost:8000/downloadableFiles |
| Test material used | None |
| Expected result (test oracle) | Attempts to access the admin page while unauthenticated should redirect the user to the login screen Attempts to access the admin endpoints (e.g. downloadableFiles) while unauthenticated should return 401 Unauthorised. While authenticated, all requests should be successful. |
| Failure Severity | Critical \- Failure of this test opens up the administrative functions, including the management of the dataset, to anyone, creating a severe security risk. |
| Comments | The function used to check whether a user is authenticated is the same across all restricted API endpoints ,hence only the need to test one. |
| Created by | JS |
| Test environment(s) | Server: Windows 11, Intel Core  i5-13400F, 16GB RAM, Nvidia RTX 4060 Client: Windows 11, Google Chrome browser |

**System Test Results:**

| ST1 | Pass Min. hardware: Average Response: 4.65s, Max: 8.07s for 100 concurrent requests Recommended hardware: Average: 1.83s, Max: 4.27s for 100 concurrent requests |
| :---- | :---- |
| **ST2** | Pass |
| **ST3** | Pass |
| **ST4** | Pass |

### 2.3 \- User Acceptance Test Cases

**AT1 \- UI Simplicity**

| Test Case ID | AT1 |
| :---- | :---- |
| Description of test | Test that the user interface of the search tool is simple and easy to navigate |
| Related requirement document details | None |
| Pre-requisites for test | The frontend and API servers are running and accessible to the client |
| Test procedure | Demonstrate to the client how the search tool works and how to access the different functions Allow the client to spend some time playing around with the system and obtain their feedback on the simplicity of the UI |
| Test material used | Cloudflare tunnel to allow the system to be accessed by the client via the Internet. |
| Expected result (test oracle) | The client is able to navigate the system to perform search and summarisation operations |
| Failure Severity | Medium \- Failure of this test would mainly be due to a cosmetic issue, but would affect system usability. |
| Comments | None |
| Created by | JS |
| Test environment(s) | Server: Windows 11, Intel Core  i5-13400F, 16GB RAM, Nvidia RTX 4060 |

**AT2 \- Accessing the Full Theses**

| Test Case ID | AT2 |
| :---- | :---- |
| Description of test | Test that the full thesis PDFs can be accessed easily and quickly |
| Related requirement document details | BR3.1 Accessing full theses BR3.2 Downloading full theses |
| Pre-requisites for test | The frontend and API servers are running and accessible to the client |
| Test procedure | Demonstrate to the client how the search tool works and how to access the full thesis PDFs for download Allow the client to spend some time using the system Gather their feedback |
| Test material used | Cloudflare tunnel to allow the system to be accessed by the client via the Internet. |
| Expected result (test oracle) | Full thesis PDFs should be easily accessible for further reading and research. |
| Failure Severity | High \- being able to read the full thesis text is crucial for using the system to propagate future research |
| Comments | None |
| Created by | JS |
| Test environment(s) | Server: Windows 11, Intel Core  i5-13400F, 16GB RAM, Nvidia RTX 4060 |

**AT3 \- Quality of Search Results**

| Test Case ID | AT3 |
| :---- | :---- |
| Description of test | Test that the search results are relevant to the entered query |
| Related requirement document details | BR2.2 \- selecting relevant theses |
| Pre-requisites for test | The frontend and API servers are running and accessible to the client |
| Test procedure | Demonstrate to the client how to make searches Allow the client to experiment with a range of queries in research areas they are familiar Gather their feedback regarding the quality of search results relating to the entered queries |
| Test material used | Cloudflare tunnel to allow the system to be accessed by the client via the Internet. |
| Expected result (test oracle) | Search results should be listed by relevance and the quality of the results should exceed those of the pre-existing system of searching by hand. |
| Failure Severity | High \- returning relevant results is critical to the success of the system in reducing the time spent by researchers obtaining data from the thesis dataset |
| Comments | None |
| Created by | JS |
| Test environment(s) | Search results should be listed by relevance and the quality of the results should exceed those of the pre-existing system of searching by hand. |

**AT4 \- Quality of AI Summaries**

| Test Case ID | AT4 |
| :---- | :---- |
| Description of test | Test that the AI generated summaries accurately discuss the key ideas, methods and conclusions of the selected thesis |
| Related requirement document details | BR5.1 \- Generating AI Summaries BR5.2 \- Citations (page numbers) in summaries |
| Pre-requisites for test | The frontend and API servers are running and accessible to the client |
| Test procedure | Demonstrate how to generate AI summaries of a thesis to the client Allow the client to experiment with generating summaries of various theses in areas of research they are familiar with Gather their feedback into meaningful results |
| Test material used | Cloudflare tunnel to allow the system to be accessed by the client via the Internet. |
| Expected result (test oracle) | AI Summaries should be generated quickly, be well-structured and ideally free of hallucinations. |
| Failure Severity | High \- Using AI to reduce the workload of human researchers is one of the key aims of the project. |
| Comments | None |
| Created by | JS |
| Test environment(s) | Search results should be listed by relevance and the quality of the results should exceed those of the pre-existing system of searching by hand. |

**Acceptance Test Results:**

| Test | Status | Relevant Client Feedback |
| :---- | :---- | :---- |
| AT1 | Pass | *“The front end and design of the tool is actually very good. I like the simplicity of it and the way each thesis has a drop-down arrow which can be expanded or collapsed while still maintaining the full search list. The functions for each individual thesis are very well set out and easy to navigate. I like the way the individual thesis page indicates the date and whether it has an abstract.”* |
| AT2 | Pass | *“Also great that you can link to the pdf of the thesis. The link is very quick as well\! Almost immediate retrieval of the whole thesis.”* |
| AT3 | Pass | *“This is a fantastic tool that offers huge potential in exploring and summarising doctoral theses. I am really excited about it and I think it has definite potential to inform our further research work in this area.”* |
| AT4 | Pass | *“I like all the different functions: the summary using Al is excellent and of particular note in this is the structure of the summary…I really like the way it summarises the main arguments and then also provides details of methodology. That is excellent.”* |
