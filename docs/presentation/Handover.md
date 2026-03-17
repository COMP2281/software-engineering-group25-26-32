# Handover Plan (Outlined in Mark Scheme)
- Identify how the project will be (or has been) handed over to the client to allow them to test the system. For example, this may involve hosting a public test server for the client, or integrating your solution into the clients current systems.
- Explain any important aspects of the user manual that the staff (and client) will need to know in order to use and run the system.

## Slide 1: What the client is receiving

### Overview
The handover consists of a locally runnable product package plus documentation. It is currently available on the internet at a disclosed address and is being ran locally from Jamie's laptop (whenever it is turned on and has Wi-Fi connection), with the frontend running at `localhost:8080` and the API at `localhost:8000`. 

The product package consists of four components: the applications, data packages, setup materials, and instructions on how to run the product. 

### Application

Firstly, there are two separate applications: the frontend served by Node.js, and the backend served by FastAPI. 

The frontend consists of four different html pages which render the bootrstrap templates adapted for the user interface for admin, login, search, and setup functionalities respectively. There are also the corresponding JavaScript files which make each web page dynamic and interactive, as well as a basic CSS file. The frontend Node.js server simply reroutes the user to their desired endpoint - Node.js is not involved in any further functionality. 

The backend consists of multiple python files which when combined, builds the database with thesis metadata and thesis text, cleans the data, builds the vector search files, runs semantic retrieval, handles per-thesis AI output, handles admin security, then exposes all of that through FastAPI.

### Data 

Secondly, the data that the client will receive is of three parts: an SQLite database, and two files which enable the model to map the theses' embeddings back to the database. 

The SQLite database contains all the available information about each thesis on the Durham E-Theses website including each thesis' id, title, abstract, author, year of publication, keywords, award, faculty, department, metadata url, thesis PDF url, and the thesis PDF text. It is important to note that the information in the database has been web-scraped and we have not gained access and downloaded the same database system the website uses. Unfortunately, some of the metadata for certain theses is missing which can negatively impact the product's search performance. 

The file referenced in the second row of the 'data' column seen on the slide contains the precomputed thesis embeddings in vector form. The file referenced in the third row of the 'data' column seen on the slide enables the thesis embeddings in the previous file to be correctly mapped to the corresponding thesis in the SQLite database. 




