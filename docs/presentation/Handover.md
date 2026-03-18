# Handover Plan (Outlined in Mark Scheme)
- Identify how the project will be (or has been) handed over to the client to allow them to test the system. For example, this may involve hosting a public test server for the client, or integrating your solution into the clients current systems.
- Explain any important aspects of the user manual that the staff (and client) will need to know in order to use and run the system.


## Introduction

Hello! We're group 32 and we're excited to present to you our project we've been working on throughout the academic year! I'm Joseph, and I'll be running you through an introduction of who our client is, a basic overview of the product we've developed having taken into consideration our client's desires and expectations, as well as how we're handing the product over to our client. 
Our client is Catherine Montgomery, a Professor in the School of Education at University of Durham, and Deputy Executive Dean for the Faculty of Social Sciences and Health at the University of Durham.
In recent years, significant effort has been put into surfacing the 'hidden' knowledge found in hundreds of thousands of doctoral theses in the EThOS and Durham E-Theses repository. Having laboriously analysed theses by-hand, Professor Montgomery has been keen to explore whether the capabilities of AI could make exploring and discovering theses both efficient and effective. 
We have developed a web-based semantic AI search tool which facilitates efficient and effective research discovery and exploration of doctoral theses. 

## Slide 1: What the client is receiving

### Overview
The handover consists of a locally runnable product package plus documentation. It is currently available on the internet at a disclosed address and is being ran locally from Jamie's laptop (whenever it is turned on and has Wi-Fi connection), with the frontend running at `localhost:8080` and the API at `localhost:8000`. 
The product package consists of four components: the applications, data packages, setup materials, and instructions on how to run the product. 

### Application

Firstly, there are two separate applications: the frontend served by Node.js, and the backend served by FastAPI. 
The frontend consists of four different html pages which render the bootrstrap templates adapted for the user interface for admin, login, search, and setup functionalities respectively. There are also the corresponding JavaScript files which make each web page dynamic and interactive, as well as a basic CSS file. The frontend Node.js server simply reroutes the user to their desired endpoint - Node.js is not involved in any further functionality. 
The backend consists of multiple python files which when combined, builds the database with thesis metadata and thesis text, cleans the data, builds the vector search files, runs semantic retrieval, handles per-thesis AI output, handles admin security, then exposes all of that through FastAPI.

### Data 

Secondly, the data that the client will receive is of three parts: an SQLite database, and two files which collectively enable the model to map the theses' embeddings back to the database. 
The SQLite database contains all the available information about each thesis on the Durham E-Theses website including each thesis' id, title, abstract, author, year of publication, keywords, award, faculty, department, metadata url, thesis PDF url, and the thesis PDF text. It is important to note that the information in the database has been web-scraped and we have not gained access and downloaded the same database system the website uses. Unfortunately, some of the metadata for certain theses is missing which can negatively impact the product's search performance. 
The file referenced in the second row of the 'data' column seen on the slide contains the precomputed thesis embeddings in vector form. The file referenced in the third row of the 'data' column seen on the slide enables the thesis embeddings in the previous file to be correctly mapped to the corresponding thesis in the SQLite database. 

### Setup materials 

The required materials to effectively setup the system locally consists of a set of prerequisites, some environment configurations, and the deployment guide and admin setup found in the technical report. 
The first two prerequisites are obvious, that being Python and Node.js which are the main platforms needed for core system functionality. Git is required to clone the project's GitHub repository and `tessdata` folder.
The requirements.txt file contains all the Windows packages needed to run the system effectively. It includes key modules such as FastAPI, FAISS (used to build the thesis embeddings file), sentence transformers (used to access the model), and Google GenAI (used for AI summaries and per-thesis Q&A) to list a few. 
The environment configurations inside a `.env` file includes the path to the downloaded `tessdata` folder containing the OCR-processing files, the path to the database location, the generated Gemini API key, and a randomly generated secret key used to hash authentication tokens. 
The deployment guide outlined in section 3.2 of the technical report contains explicit instructions for installing prerequisites, cloning the project repository, setting up the Python virtual environment with the required Python modules, downloading the pre-built database and model weights, and finally starting the server. 
To then setup the admin account for the first time, via terminal and inside the `python` directory, a python file is ran with the user's username and password passed in as the two command-line arguments. The admin page can then be accessed using these credentials. 

### Run Instructions 

We wanted to make the system launch as simple as possible for the client. 
We condensed the server-start procedure into a single command-line execution via the root project directory - the frontend can now be accessed at port 8080.
An admin can easily be created using the command line seen on the slide, and the credentials used there are the ones to sign in on the admin page.
From there, the admin has full access to the tool. 

## Slide 2: How we’re addressing client concerns about future development
