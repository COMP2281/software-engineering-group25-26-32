# Handover Plan (Outlined in Mark Scheme)
- Identify how the project will be (or has been) handed over to the client to allow them to test the system. For example, this may involve hosting a public test server for the client, or integrating your solution into the clients current systems.
- Explain any important aspects of the user manual that the staff (and client) will need to know in order to use and run the system.

## Introduction

Hello! We're group 32 and we're excited to present to you our project we've been working on throughout the academic year! I'm Joseph, and I'll be running you through an introduction of who our client is, a basic overview of the product we've developed having taken into consideration our client's desires and expectations, as well as how we're handing the product over to our client. 
Our client is Catherine Montgomery, a Professor in the School of Education at University of Durham, and Deputy Executive Dean for the Faculty of Social Sciences and Health at the University of Durham.
In recent years, significant effort has been put into surfacing the 'hidden' knowledge found in hundreds of thousands of doctoral theses in the EThOS and Durham E-Theses repository. Having laboriously analysed theses by-hand, Professor Montgomery has been keen to assess whether the capabilities of AI could make exploring and discovering theses both efficient and effective. 
We have developed a web-based semantic AI search tool which facilitates efficient and effective research discovery and exploration of doctoral theses. 

## Slide 1: What the client is receiving

### Overview
The handover consists of a locally runnable product package plus documentation. 
The product package consists of four components: the applications, data packages, setup materials, and instructions on how to run the product. 

### Application

Firstly, there are two separate applications: the frontend served by Node.js, and the backend served by FastAPI. 
The frontend consists of html, javascript, and css files which collectively render the web UI for admin, login, search, and setup functionalities respectively.  

The backend first populates and enriches the thesis database, then prepares the data, builds the semantic search index, runs retrieval, generates thesis-specific AI responses, secures admin functionality, and serves the whole workflow through FastAPI.

### Data 

Secondly, the data that the client will receive is of three parts: an SQLite database which contains all the available information about each thesis on the Durham E-Theses website, and two files which collectively enable the model to map the theses' embeddings back to the database.  

### Setup materials 

The required materials to effectively setup the system locally consists of a set of prerequisites,
some environment configurations, and the deployment guide and admin setup found in the technical report. 
The first two prerequisites are obvious, that being Python and Node.js which are the main platforms needed for core system functionality. 
Git is required to clone the project's GitHub repository and `tessdata` folder. There are two respective .txt files containing the Windows and Mac/Linux modules needed to run the system effectively. 
There is also a `.env` file containing essential keys and paths information. 
The deployment guide is outlined in the technical report and contains explicit instructions for installing prerequisites, cloning the project repository, setting up the Python virtual environment with the required Python modules, downloading the pre-built database and model weights, and finally starting the server. 


### Run Instructions 

We wanted to make the system launch as simple as possible for the client. 
We condensed the server-start procedure into a single command-line execution via the root project directory - from there the frontend can be accessed.

## Slide 2: How did our client respond to our near-complete prototype?

Upon near-completion of the delivered product, we demonstrated the tool to Professor Montgomery online and enabled her to test it independently.
Her feedback has been extremely encouraging and satisfying to us, and has also made us aware of their concerns about the product.

## Slide 3: How we’re addressing client concerns about future development

These concerns are primarily focused on two areas:
1. Cross-thesis analysis: The tool lacks features capable of cross-analysing multiple theses so that a researcher using the tool might have a broader view of the field of study rather than from just one thesis. Having discussed with Professor Montgomery that this feature can only become operational with funding, we are currently looking at deploying the tool on a paid website to unlock the tool's potential. Though, this is only in the early stages. 
2. How GenAI analyses each thesis: it's currently unclear what an ideal synthesis would look like to us, so we're looking to work with Professor Montgomery to engineer the optimal GenAI prompt.
