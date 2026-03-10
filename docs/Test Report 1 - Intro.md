This test report outlines the objectives, methodology and results of the testing process used throughout the development process, including Unit Testing, System Testing and User Acceptance Testing.

### 1.1 Unit Testing

Unit testing was used to ensure that each component of our API logic worked as it should with respect to the behavioural requirements and our planned system design. As such, test oracles for these tests were primarily devised from our system requirements as outlined in the Requirements Document, or alternatively were drawn up as a result of system design decisions made by the team during development. These tests are automated (using PyTest) and ensured that unit functionality would not be impacted by any modifications or additions made to the system. Unit tests covered the majority of authentication and helper functions used in the system, as well as the behaviour of each API endpoint. Complex features such as the search function itself, the embeddings model, AI summaries and OCR could not be tested via quick automated testing, thus the testing of these features fell under System Testing and UAT.

The below table is a broad overview of the key components of the system covered by unit testing (not detailing the many additional helper functions also being unit tested): 

| Component | Unit Test | Test Oracle (brief) |
| :---- | :---- | :---- |
| Auth  | check\_creds() \- Credential checking | Accept if and only if a valid username/password combination is entered, otherwise reject. |
| Auth  | validate\_token() \- JWT validation | JWT validation should return the username encoded within the token if the token is valid, otherwise return None. Only tokens generated with the secret key should be validated. |
| Admin | create\_admin() \- Admin user creation | Add the input username and password to the Admins database. If the user already exists, return an error. |
| Admin | delete\_admin() \- Admin user deletion | Delete the row in the Admins database with the entered username, if it exists. Otherwise, do nothing. |
| Durham E-Theses Scraper | scrape() \- Metadata scraping | Extract metadata from the input URL to a thesis page from Durham E-Theses and add it to the database. If the page doesn't exist or is incorrectly formatted, do nothing. |
| PDF Text Extractor | pdf\_to\_text\_json() \- Extraction of text from a PDF (non-OCR case) | Extract text from the input PDF file into a JSONL format, with one line per page of the PDF containing metadata including the source URL and page number. |
| AI Summariser  | load\_pages() \- Correctly loads thesis content from database | Unpack the JSONL format used to store the thesis text and return the full text as a string, including page numbers with each page. |
| API  | All endpoints \- Status code checks | API endpoints return 200 when successful and return 40x when failing. |
| API | /upload \- DB/Model file upload | Replace the active database and model files if the uploaded files are valid, otherwise return 400 with an appropriate error message |
| API | /login and /logout \- managing auth cookie | Successful login should save the JWT to a cookie. Successful logout should remove this cookie. |

### 1.2 System testing

System testing involved testing the full coherent system, ensuring that the system developed matches the behavioural requirements. Test oracles for these tests came directly from the requirements themselves. System testing also included performance testing of the API and whether menus appeared/redirected as expected. 
User Acceptance testing was performed by giving potential end users access to our system, testing whether our product met their expectations.

“Minimum” and “Recommended” specifications were found from testing different machines/configurations and comparing performance.

The following section of this report lists some sample test cases for each of the above types of testing:
| Test | Test Oracle (brief) |
| :--- | :--- |
| API performance testing for searching | For up to and including 100 concurrent requests, the average search response time should not exceed 5 seconds and the maximum response time should not exceed 10 seconds. |
| Search Functionality | When a user enters a search query, relevant results should be displayed, with the ability to view the full thesis for each result. |
| AI Summarisation functionality | When the user clicks the “Generate Summary” button, the system should generate an AI summary of the respective thesis. |
| Admin page authentication | Only users with a valid authentication token can access the admin page or any of the restricted API endpoints. |

### 1.3 User Acceptance Testing
User Acceptance testing involved giving the client access to the system and gathering their feedback on the system’s usability and the quality of the search results and AI generated summaries produced by the system.