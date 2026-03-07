### 2.1 \- Unit Test Cases

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
| Comments | The JSONL format used to store the thesis text in the database stores a JSON object per line representing each page of the thesis, containing the page number as well as the text itself. |
| Created by | JS |
| Test environment(s) | Windows 11 |

**UT3 \- Durham E-Theses Webscraper** 

| Test Case ID | UT3 |
| :---- | :---- |
| Description of test | Test the scrape() function of the Durham E-Theses scraper scrapes metadata correctly and adds it to the database |
| Related requirement document details | None |
| Pre-requisites for test | PyTest is installed on the system and is being run from the python directory. |
| Test procedure | Create mock Thesis database Read sample HTML file of thesis page Call scrape() on this file Verify that the mock metadata contained in the HTML has been written to the mock database. Call scrape() on a nonexistent file Verify that nothing is written to the database and scrape() exits with code 1\. Call scrape() on sample HTML for the page of a thesis that has been removed from Durham E-Theses Verify that nothing is written to the database and scrape() exits with code 1\. Delete mock database |
| Equivalence Classes | Valid HTML \- contains the \<meta\> tags with the correct names as in Durham E-Theses Invalid HTML \- does not contain the correct formatting and \<meta\> tags, or is empty. Removed thesis HTML \- contains “\<p\>You seem to be attempting to access an item that has been removed from the repository.\</p\>” |
| Test material used | Test\_durham\_etheses\_scraper\_example.html \- sample HTML page of the same formatting as the thesis pages on Durham E-Theses Test\_durham\_etheses\_scraper.py \- automated PyTest script for testing scraper functionality PyTest |
| Expected result (test oracle) | Valid HTML \- scrape() exits with code 0 and the metadata is written to the database Invalid HTML and Removed Thesis HTML \- scrape() exits with code 1 and nothing is written to the database. |
| Comments | This tests the scrape function used to build and update the Durham-Etheses database, ensuring only inputted HTML of the correct formatting from the Durham Etheses website is used when adding rows to the database. |
| Created by | JS |
| Test environment(s) | Windows 11 |

**UT4 \-** 

| Test Case ID | UT4 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

**UT5 \-** 

| Test Case ID | UT5 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

- Credential checking and/or JWT checking/validation  
- Admin account creation/deletion  
- Unit test for durham etheses scrape function (?)  
- Unit test for loading thesis pages from db into AI summariser

### 2.2 \- System Test Cases

**ST1 \-** 

| Test Case ID | ST1 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

**ST2 \-** 

| Test Case ID | ST2 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

**ST3 \-** 

| Test Case ID | ST3 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

**ST4 \-** 

| Test Case ID | ST4 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

**ST5 \-** 

| Test Case ID | ST5 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

- Concurrent search request load test  
- Test with larger sample db (to simulate functioning on EThOS) (?)  
- Test requirements for search and AI summaries are met  
- Test full login flow with frontend integration and cookies ( is this integration testing?)   
- (?)

### 2.3 \- User Acceptance Test Cases

**UAT1 \-** 

| Test Case ID | UAT1 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

**UAT2 \-** 

| Test Case ID | UAT1 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

**UAT3 \-** 

| Test Case ID | UAT1 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

**UAT4 \-** 

| Test Case ID | UAT1 |
| :---- | :---- |
| Description of test |  |
| Related requirement document details |  |
| Pre-requisites for test |  |
| Test procedure |  |
| Equivalence Classes |  |
| Test material used |  |
| Expected result (test oracle) |  |
| Comments |  |
| Created by |  |
| Test environment(s) |  |

- Test search results/AI summaries meet client expectationsTest user-friendliness of UI (?)  
- (?)  
- (?)