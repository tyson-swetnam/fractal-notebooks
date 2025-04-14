# fractal-notebooks
collection of python apps and jupyter notebooks for simulating self-affine fractals

# Build Documentation

To build the docs locally:

```
git clone https://github.com/CyVerse-learning-materials/fractal-notebooks.git

cd fractal-notebooks

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python -m mkdocs serve -a localhost:8000
```
Open a browser and go to https://localhost:8000. If there is already something else running on localhost:8000, just change the port in the command (eg, `python -m mkdocs serve -a localhost:8001`)

# Chatbot Backend Setup
The objective is to create a backend system that:

1.  **Collects Data:** Gathers information about fractals from Markdown documentation files in a GitHub repository and structured data (including pre-computed embeddings) from a .jsonl file.
2.  **Stores Data:** Loads the processed information into a Weaviate vector database, enabling vector searching.
3.  **Answers Prompts:** Provides an API endpoint that receives chat messages, queries the Weaviate database for relevant context (from both documentation and research papers), and uses OpenAI to generate an informed response based on the query and retrieved context.

**Components:**

1.  **Data Storing:** A script or process responsible for fetching, preparing, and loading data into Weaviate.
2.  **API Server:** A web server that listens for requests from the chatbot frontend.
3.  **Weaviate Database:** The vector database storing the information.
4.  **External Services:** Cohere (for embedding services via Weaviate integration) and OpenAI (for response generation).

---

**Prerequisites and Setup**

1.  **Python Environment:**
    *   Install Python 3.
    *   Set up a project directory and a virtual environment (e.g., using `venv`).
      ```
        #Update package list
        sudo apt update

        #Install Python3
        sudo apt install python3 python3-pip python3-venv -y

        #Create new directory
        mkdir dir_name
        cd dir_name

        #Set up a virtual environment
        python3 -m venv venv
        source venv/bin/activate
      ```
2.  **Required Libraries:** Install necessary Python libraries using pip. You will need libraries for:
    *   Interacting with Weaviate (`weaviate-client`).
    *   Making HTTP requests (`requests`).
    *   Running a web server (`Flask`).
    *   Handling Cross-Origin Resource Sharing (`Flask-Cors`).
    *   Interacting with the OpenAI API (`openai`).
    *   Loading environment variables (`python-dotenv`).
    *   Showing progress bars (`tqdm`).
    *   Interacting with Git command line (`subprocess`).
    *   Hosting Weaviate database locally (`docker`, `docker-compose`)
      ```
      #requirements.txt
      weaviate-client
      requests
      Flask
      Flask-Cors
      openai
      python-dotenv
      tqdm
      docker
      docker-compose
      ```
    * To install using requirements.txt run ``` pip install requirements.txt ```

**3. Weaviate Instance Setup (Docker)**

To run Weaviate locally and enable it to use Cohere for generating vector embeddings (`text2vec-cohere`) and for retrieval-augmented generation (`generative-cohere`), we'll use Docker and Docker Compose.

**Prerequisites:**

*   **Docker and Docker Compose:** You need Docker Engine + Docker Compose installed. If you do not have them installed, follow the [official Docker installation guides](https://docs.docker.com/engine/install/) for your operating system.
*   **Cohere API Key:** You need your API key from Cohere.

**Steps:**

-  **Create Project Files:** In your main backend project directory create two files:
    *   `docker-compose.yml` (defines the Weaviate service)
    *   `.env` (stores your API key securely)

-  **Populate `.env`:** Add your Cohere API key to the `.env` file. Docker Compose will automatically read this file.
    ```dotenv
    # .env file
    COHERE_APIKEY=your_cohere_api_key_here
    ```

-  **Populate `docker-compose.yml`:** Paste the following content into your `docker-compose.yml` file.

    ```yaml
    # docker-compose.yml
    version: '3.4'

    services:
      weaviate:
        image: semitechnologies/weaviate:1.25.1  # Use a specific recent version
        ports:
          - "8080:8080"  # REST API port
          - "50051:50051" # gRPC port
        volumes:
          - weaviate_data:/var/lib/weaviate # Persist data using a named volume
        restart: on-failure:0 # Don't restart automatically on error during setup
        environment:
          # --- Module Settings ---
          ENABLE_MODULES: 'text2vec-cohere,generative-cohere' # Enable desired modules
          DEFAULT_VECTORIZER_MODULE: 'text2vec-cohere' # Set default vectorizer
          COHERE_APIKEY: ${COHERE_APIKEY} # *** Reads key from .env file ***

          # --- Weaviate Core Settings ---
          AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true' # Disable auth for local dev
          PERSISTENCE_DATA_PATH: '/var/lib/weaviate' # Path inside the container for data
          CLUSTER_HOSTNAME: 'node1' # Name for this node (needed even for single node)
          QUERY_DEFAULTS_LIMIT: '25' # Default limit for query results
          # Add other environment variables if needed

    volumes:
      weaviate_data: {} # Define the named volume for data persistence
    ```

    *   **`image:`**: Specifies the Weaviate Docker image version. It's good practice to pin to a specific version (like `1.25.1` here - check Weaviate releases for the latest compatible version) instead of `latest` for reproducibility.
    *   **`ports:`**: Exposes Weaviate's REST port (8080) and gRPC port (50051) to your host machine.
    *   **`volumes:`**: Creates a Docker named volume `weaviate_data` and mounts it inside the container at `/var/lib/weaviate`. This ensures your Weaviate data persists even if you remove and recreate the container.
    *   **`environment:`**: This is where Weaviate is configured:
        *   `ENABLE_MODULES`: Activates the Cohere modules.
        *   `DEFAULT_VECTORIZER_MODULE`: Sets the default vectorizer..
        *   `COHERE_APIKEY: ${COHERE_APIKEY}`: This tells Docker Compose to get the value for `COHERE_APIKEY` from the `.env` file..

-  **Start Weaviate Service:** Open your terminal, navigate to the directory containing your `docker-compose.yml` and `.env` files, and run:

    ```bash
    docker-compose up -d
    ```
    *   `up`: Creates and starts the services defined in the YAML file.
    *   `-d`: Runs the containers in detached mode (in the background).
    *   Docker will download the Weaviate image if you don't have it locally, then create and start the container with the specified configuration.

-  **Verify Weaviate is Running:**
    *   **Check Logs:** You can view the logs to ensure it started correctly:
        ```bash
        docker-compose logs -f weaviate
        ```
        (Press `Ctrl+C` to stop following logs). Look for messages indicating the server is ready and the modules are loaded.
    *   **Check Meta Endpoint:** In a web browser or using `curl`, access Weaviate's meta endpoint:
        ```bash
        curl http://localhost:8080/v1/meta
        ```
        You should receive a JSON response containing information about your Weaviate instance, including the enabled modules (`"text2vec-cohere"`, `"generative-cohere"`) and the Weaviate version.

Now you have a Weaviate instance running locally via Docker, accessible at `http://localhost:8080`, and configured with the necessary Cohere modules using your API key securely read from the `.env` file. Your Python scripts can now connect to this instance.

4.  **API Keys:**
    *   Obtain API keys from Cohere and OpenAI if you haven't already.
    *   Store these keys securely, in your `.env` file in your project root if they are not:
        ```
        COHERE_API_KEY="your_cohere_api_key"
        OPENAI_API_KEY="your_openai_api_key"
        ```

5.  **Data Sources Access:**
    *   **GitHub Repository:** Have the URL of the public GitHub repository containing the Markdown documentation ready (e.g., `https://github.com/username/repository`).
    *   **JSONL File:** Obtain the JSON Lines (`.jsonl`) file containing research paper metadata and pre-computed embeddings. You'll need a way to access this file (direct download or download script). Place it where your ingestion script can read it.

---

**Building the Data Ingestion Service**

This script prepares and loads data into Weaviate. It should perform the following actions:

1.  **Load Configuration:** Read API keys from the `.env` file. Define constants like the GitHub repo URL, the local path to the JSONL file, the Weaviate instance URL, and desired Weaviate collection names (e.g., `Webpage`, `DatabaseEmbeddings`).
   ```
   #Load environment variables
   dotenv_path = "/home/your-path/.env"
   load_dotenv(dotenv_path)

   #Specify the names of github repositories to include
   REPO_URLS = [
       "https://github.com/username/repository"
   ]

   #Other global variables
   COLLECTION_NAME_1 = "Webpage"
   COLLECTION_NAME_2 = "DatabaseEmbeddings"
   WEAVIATE_URL = "http://localhost:8080"
   COHERE_API_KEY = os.environ["COHERE_API_KEY"]
   ```
2.  **Fetch GitHub Documentation:**
    *   Implement logic to clone the specified GitHub repository into a temporary location.
    *   Navigate to the subdirectory containing the documentation (e.g., `docs`).
    *   Iterate through all files ending in `.md` within that directory.
    *   For each Markdown file, read its full content.
    *   Store the filename and content for later batch insertion into Weaviate.
      ```
      def clone_or_pull_repo(repo_url):
          try:
              #Create a temporary clone of the repository
              with tempfile.TemporaryDirectory() as temp_dir:
                  print(f"Cloning {repo_url} into temporary directory: {temp_dir}")
                  subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True, text=True)

                  #Find the path to markdown files (In the docs folder)
                  docs_dir = os.path.join(temp_dir, "docs")
                  if not os.path.exists(docs_dir):
                      print(f"Warning: 'docs' directory not found in {repo_url}")
                      return []

                  #Create a batch object with the name and content from each markdown file
                  batch_objects = []
                  for filename in os.listdir(docs_dir):
                      if filename.endswith(".md"):
                          filepath = os.path.join(docs_dir, filename)
                          content = read_markdown_file(filepath)
                          batch_objects.append(
                              {
                                  "filename": filename,
                                  "content": content,
                              }
                          )
                          print(f"Processed: {filename}")
                  return batch_objects

          #Handle exceptions
          except subprocess.CalledProcessError as e:
              print(f"Git command failed:\n{e.stderr}")
              raise
          except Exception as e:
              print(f"An error occurred: {e}")
              raise

      #Helper function to open markdown files and return the text
      def read_markdown_file(file_path):
          with open(file_path, "r") as file_stream:
              file_content = file_stream.read()
              return file_content
      ```
3.  **Prepare Research Paper Data:**
    *   If the JSONL file is not already local, implement logic to download it. If it requires authentication, handle credential input or secure retrieval.
      ```
      def download_file(file_url, local_filename, username, password):
          try:
              #Stream the file to make it managable for reading
              with requests.get(file_url, auth=(username, password), stream=True) as response:
                  response.raise_for_status()
      
                  #Optionally implement logic for a progress bar (Good for processing large files)
      
              print(f"{local_filename} downloaded successfully.")
              return 0
      
          except Exception as e:
              print("Error encountered during download:", e)
              return 1
      ```
4.  **Connect to Weaviate:** Establish a connection to your Weaviate instance. Authenticate using the Cohere API key in the connection headers.
   ```
   client = weaviate.connect_to_local(
     headers={"X-Cohere-Api-Key": COHERE_API_KEY}
   )
   print("Weaviate client is ready: ", client.is_ready())
   ```
5.  **Define and Create Weaviate Collections:**
    *   **Check Existence:** Before creating, check if collections with the defined names already exist.
    *   **Recreate Strategy:** Implement a strategy for updates. The easiest is to delete the collection if it exists and then recreate it. Alternatively a more advanced strategy would check for existing data and not delete pages wich haven't been edited.
    *   **Create Collection:**
        *   Define properties: `filename` (Text), `content` (Text).
        *   Configure the vectorizer: Use `text2vec-cohere`, specifying the desired Cohere embedding model (e.g., `embed-english-v3.0`).
        *   Configure the generative module: Use `generative-cohere`, specifying the desired Cohere generation model (e.g., `command`).
      ```
      #Check if the collection exists on your local Weaviate cluster
      if COLLECTION_NAME_1 in client.collections.list_all():
          print(f"{COLLECTION_NAME_1} exists: Deleting and recreating")
      
          #Delete the collection
          client.collections.delete(COLLECTION_NAME_1)

          #Create a new collection with the same name and properties
          files = client.collections.create(
              name=COLLECTION_NAME_1,
              properties=[
                  Property(name="filename", data_type=DataType.TEXT),
                  Property(name="content", data_type=DataType.TEXT),
              ],
              vectorizer_config=wvc.Configure.Vectorizer.text2vec_cohere(
                  model="embed-english-v3.0",
              ),
               generative_config=wvc.Configure.Generative.cohere(
                  model="command"
              )
          )
      else:
          print(f"{COLLECTION_NAME_1} does not exist: Creating collection")

          #Create the same collection but there is no need to delete an existing one first
          files = client.collections.create(
              name=COLLECTION_NAME_1,
              properties=[
                  Property(name="filename", data_type=DataType.TEXT),
                  Property(name="content", data_type=DataType.TEXT),
              ],
              vectorizer_config=wvc.Configure.Vectorizer.text2vec_cohere(
                  model="embed-english-v3.0",
              ),
              generative_config=wvc.Configure.Generative.cohere(
                  model="command",
              )
          )
      ```

    *   **Create `DatabaseEmbeddings` Collection:**
        *   Define properties based on the JSONL structure.
        *   Configure this collection to accept pre-computed vectors. This means *not* specifying a vectorizer like `text2vec-cohere` in the main configuration, but still enabling the `generative-cohere` module for use later.
 
      ```
      #Save whatever properties you want, these are all highly relevant ones though
      properties = [
          wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
          wvc.config.Property(name="doi", data_type=wvc.config.DataType.TEXT),
          wvc.config.Property(name="creator", data_type=wvc.config.DataType.TEXT_ARRAY),
          wvc.config.Property(name="url", data_type=wvc.config.DataType.TEXT),
          wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT)
      ]

      #Follow the same process for deleting and creating a weaviate collection as before
      if COLLECTION_NAME_2 in client.collections.list_all():
          print(f"{COLLECTION_NAME_2} exists: Deleting and recreating")
          client.collections.delete(COLLECTION_NAME_2)
          collection = client.collections.create(
              name=COLLECTION_NAME_2,
              properties=properties,
              vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_cohere(
                  model="embed-english-v3.0",
              ),
              generative_config=wvc.config.Configure.Generative.cohere(
                  model="command",
              )
          )
      else:
          print(f"{COLLECTION_NAME_2} does not exist: Creating Collection")
          collection = client.collections.create(
              name=COLLECTION_NAME_2,
              properties=properties,
              vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_cohere(
                  model="embed-english-v3.0",
              ),
              generative_config=wvc.config.Configure.Generative.cohere(
                  model="command",
              )
          )
      ```
6.  **Batch Import Data into Weaviate:**
    *   **Website Data:** Use Weaviate's batch import functionality. For each piece of GitHub documentation (filename, content), add an object to the `Webpage` collection. Weaviate will automatically use the configured `text2vec-cohere` module to generate and store the vector based on the `content`. Assign a unique UUID (e.g., generated based on the filename).
      ```
      # Get the collection for markdown files
      collection = client.collections.get(COLLECTION_NAME_1)

      #Create a batch object for each markdown file that needs to be stored in weaviate
      with collection.batch.dynamic() as batch:
          for obj in all_batch_objects:
              batch.add_object(
                  properties=obj,
                  uuid=generate_uuid5(obj["filename"])
              )
              print(f"Added: {obj['filename']}")
      ```
    *   **Research Paper Data:** Read the JSONL file line by line. For each line (representing a paper):
        *   Parse the JSON data.
        *   Extract the required properties (`title`, `url`, `creator`, `content`/`fullText`, etc.).
        *   Extract the pre-computed `embedding` vector from the JSON.
        *   Use Weaviate's batch import. Add an object to the `DatabaseEmbeddings` collection, providing both the properties *and* the `vector` explicitly using the extracted embedding.
        *   Optionally if you have an incomplete dataset, filter out records that lack essential content (like `fullText`) before adding them.
      ```
      #Specify the collection and jsonl file
      collection = client.collections.get(COLLECTION_NAME_2)
      jsonlFile = "your_file.jsonl"

      #Read each entry in the jsonl file and create a batch object from the information
      with open(jsonlFile, "r") as file:
          with collection.batch.rate_limit(requests_per_minute=50) as batch:
      
              for line in file:
      
                  data = json.loads(line)

                  #Make sure to manually set the embedding (Using the one provided in the jsonl file)
                  embedding = data.get("embedding", [])
      
                  #Save whatever properties you want
                  properties = {
                      "title": data.get("title"),
                      "url": data.get("url"),
                      "creator": data.get("creator"),
                      "content": data.get("fullText"),
                      "doi": data.get("doi")
                  }

                  #Create the batch object
                  if(properties['content'] and embedding):
                      batch.add_object(
                          properties=properties,
                          vector=embedding
                      )
      
                      print(f"Added: {properties['title']}")
                  else:
                      print(f"Skipped: {properties['title']}")
      ```
7.  **Close Connection:** Close the Weaviate client connection.
   ```
   client.close()
   ```
8.  **Execution:** This script needs to be run whenever you want to update the Weaviate database with the latest data from GitHub or the JSONL file.
   ```
   def main():
       print("Starting update process...")
   
       all_batch_objects = []
       for repo_url in REPO_URLS:
           try:
               batch_objects = clone_or_pull_repo(repo_url)
               if batch_objects:
                   all_batch_objects.extend(batch_objects)
           except Exception:
               print(f"Skipping {repo_url} due to error.")
               continue
   
       client = weaviate.connect_to_local(
         headers={"X-Cohere-Api-Key": COHERE_API_KEY}
       )
       print("Weaviate client is ready: ", client.is_ready())
   
       update_collection(client, all_batch_objects)
   
       print("Loading your_file")
       local_filename = "your_file.jsonl"
       load_from_jsonl(client, local_filename)
   
       print("Update process completed.")
   
       client.close()
   
   if __name__ == "__main__":
       main()
   ```

---

**Building the API Server**

This script runs a web server to handle chat requests.

1.  **Setup Flask:**
    *   Import necessary libraries: `Flask`, `jsonify`, `request`, `Flask-Cors`, `os`, `weaviate`, `openai`, `dotenv`.
    *   Create a Flask application instance.
    *   Enable CORS for the app to allow requests from your frontend's domain.
    *   Load environment variables (`.env`) to get API keys.
    *   Initialize the OpenAI client using the OpenAI API key.
    *   Define constants for Weaviate collection names and the Weaviate URL.
   ```
   from flask import Flask, request, jsonify
   from flask_cors import CORS
   import os
   import weaviate
   import weaviate.classes as wvc
   from dotenv import load_dotenv
   from openai import OpenAI
   from openai import OpenAIError
   import json
   
   app = Flask(__name__)
   CORS(app)

   #Load environment variables
   dotenv_path = "/home/ubuntu/opendendro-chatbot/.env"
   load_dotenv(dotenv_path)

   #Establish which collections you want to pull context from (The ones you made in the other script)
   WEAVIATE_COLLECTIONS = [
       "Webpage",
       "DatabaseEmbeddings"
   ]

   #Keep track of which collections were made from databases
   ARTICLES = [
       "DatabaseEmbeddings"
   ]
   
   
   COHERE_API_KEY = os.environ["COHERE_API_KEY"]
   
   
   oai = OpenAI(api_key=os.getenv("REACT_APP_OPENAI_API_KEY"))
   ```
2.  **Define API Endpoint:**
    *   Create a route (e.g., `/process_chat/chatbot`) that accepts POST requests.
   ```
   @app.route("/process_chat/fractal", methods=["POST"])
   def process_chat():
   ```
3.  **Handle Incoming Requests:** Inside the route handler:
    *   **Parse Request:** Get the JSON data from the incoming request body. Frontend servers are set up to package existing conversations as a list of messages, each with a role and content ({"conversation": [{"role": "user", "content": "message"}]}).
    *   **Extract Query:** Identify the latest user message from the conversation history. This will be the primary query for retrieval.
      ```
      # Inside process_chat():
      print("POST request recieved.\n")
      try:
          #Extract data that was sent
          data = request.json
      
          if not data or "conversation" not in data:
              return jsonify({"error": "Missing 'conversation' field"}), 400

          #Check to make sure there was actually a prompt from the user
          user_messages = [msg["content"] for msg in data["conversation"] if msg["role"] == "user"]
          if not user_messages:
               return jsonify({"error": "No user messages found in conversation"}), 400
          latest_user_message = user_messages[-1]
      
          print("Got conversation data.\n")
          conversation = data["conversation"]
      
      except Exception as e:
           return jsonify({"error": f"Error processing request data: {str(e)}"}), 400
      ```
    *   **Connect to Weaviate:** Connect to the Weaviate instance, passing the Cohere API key in the headers.
      ```
      client = weaviate.connect_to_local(
            headers={"X-Cohere-Api-Key": COHERE_API_KEY}
          )
          print("Weaviate client is ready: ", client.is_ready())
      ```
    *   **Query Weaviate for Context:**
        *   Perform a search query (use `hybrid` search to combine keyword and vector search) against both the `Webpage` collection and the `DatabaseEmbeddings` collection.
        *   Use the latest user message as the query input.
        *   Limit the results from each collection (limiting to 2 ensures results are relevant to the prompt).
        *   **Process Results:**
            *   From `Webpage` results, extract the `content`.
            *   From `DatabaseEmbeddings` results, extract `content` (the full text), `url`, and `creator`, and/or any other information you want.
        *   Store the extracted text content from both sources separately.
      ```
      #Create lists to store information retrieved from relevant pages
      siteContext = []
      articleContext = []
      urls = []
      authors = []
      
      try:
          print("Querying Weaviate...")

          #Loop through all the specified weavaite collections
          for col_name in WEAVIATE_COLLECTIONS:
      
              collection = client.collections.get(col_name)

              #Complete similarity search based off user's most recent query
              response = collection.query.hybrid(
                  query=latest_user_message,
                  limit=2
              )

               #Check if the collection was created from a .jsonl file database
              is_article_collection = col_name in ARTICLES
              for obj in response.objects:
                  content = obj.properties.get('content')
                  if content:
                      #If the information was from a database, add it to articleContext and include the url and authors in addition to the content
                      if is_article_collection:
                          articleContext.append(content)
                          urls.append(obj.properties.get('url'))
                          authors.append(obj.properties.get('creator'))

                      #If the information was not from a database, add it to the siteContext and only include content
                      else:
                          siteContext.append(content)
                          collections_queried.append(col_name + " was used (website)")
      
      except Exception as e:
          print(f"An error occurred during Weaviate query: {e}")
      ```
    *   **Close Weaviate Connection:** Ensure the Weaviate client connection is closed.
      ```
      if client:
              client.close()
              print("Weaviate connection closed.")
      ```
    *   **Prepare Prompt for LLM:**
        *   **System Instructions:** Define a detailed system prompt string which specifies how you would like the responses to be formatted and use the context provided.
        *   **Construct Messages:** Create the list of messages for the OpenAI API call:
            1.  `{"role": "system", "content": system_prompt_string}`
            2.  `{"role": "user", "content": f"Full conversation history: {conversation_history_string}"}`.
            3.  `{"role": "user", "content": f"Use this website information as context: {website_context}. Do not explicitly mention retrieving it unless citing."}`
            4.  `{"role": "user", "content": f"Use this research paper information as context: {paper_context}. Associated URLs: {paper_urls}. Associated Authors: {paper_authors}. Cite papers only if relevant, using the title, URL, and authors."}`
            5.  `{"role": "user", "content": f"Respond to this query: {latest_user_message}"}`
    *   **Call OpenAI API:**
        *   Use the initialized OpenAI client to call the Chat Completions endpoint.
        *   Provide the chosen model (e.g., `o3-mini`).
        *   Pass the constructed list of messages.
      ```
      try:
              print("Calling OpenAI...")

              #Make call to openai, pass the messages created earlier to it
              openai_response = oai.chat.completions.create(
                  model="o3-mini",
                  messages=openai_messages
              )

              #Get the response from openai
              resp = openai_response.choices[0].message.content
      
              return jsonify({"response": resp})
      
          except OpenAIError as e:
              print(f"OpenAI API Error: {e}")
              return jsonify({"error": f"OpenAI API Error: {str(e)}"}), 500
      
          except Exception as e:
              print(f"Unexpected Error during OpenAI call: {e}")
              return jsonify({"error": str(e)}), 500
      ```
    *   **Extract Response:** Get the response content from the OpenAI API result.
    *   **Return Response:** Send a JSON response back to the chatbot frontend containing the LLM's generated answer (e.g., `{"response": generated_text}`). You might also include the context retrieved for debugging purposes on the frontend if desired.
    *   **Error Handling:** Include `try...except` blocks for robustness (e.g., connection errors, API errors, invalid request data).
4.  **Run the Server:** Add the standard Python `if __name__ == "__main__":` block to start the Flask development server. Configure it to listen on `0.0.0.0` (to be accessible externally/within Docker) and a specific port (e.g., 5000).
   ```
   if __name__ == "__main__":
       app.run(host="0.0.0.0", port=5000, debug=True)
   ```
