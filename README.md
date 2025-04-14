# fractal-notebooks
collection of python apps and jupyter notebooks for simulating self-affine fractals

# Build Documentation

To build the docs locally:

```
git clone https://github.com/tyson-swetnam/fractal-notebooks.git

pip install -r requirements.txt

python -m mkdocs serve
```
Open a browser and go to https://localhost:8000

# Fractal Chatbot Backend Setup
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
    *   Example requirements.txt:
      ```
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

*   **Docker and Docker Compose:** You need Docker Desktop (Windows/macOS) or Docker Engine + Docker Compose (Linux) installed. Verify installation:
    ```bash
    docker --version
    docker-compose --version # Or sometimes 'docker compose version' on newer installs
    ```
    If not installed, follow the official Docker installation guides for your operating system.
*   **Cohere API Key:** You need your API key from Cohere.

**Steps:**

-  **Create Project Files:** In your main backend project directory (e.g., `my_fractal_backend`), create two files:
    *   `docker-compose.yml` (defines the Weaviate service)
    *   `.env` (stores your secret API key securely)

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
    *   **`environment:`**: This is where we configure Weaviate:
        *   `ENABLE_MODULES`: Activates the Cohere modules.
        *   `DEFAULT_VECTORIZER_MODULE`: Sets the default vectorizer..
        *   `COHERE_APIKEY: ${COHERE_APIKEY}`: This tells Docker Compose to get the value for `COHERE_APIKEY` from the `.env` file..
        *   `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'`: Disables authentication for simpler local development access. **Do not use this setting in production.**
        *   Other settings configure data path, node name, etc.

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
    *   **Check Meta Endpoint:** Open your web browser or use `curl` to access Weaviate's meta endpoint:
        ```bash
        curl http://localhost:8080/v1/meta
        ```
        You should receive a JSON response containing information about your Weaviate instance, including the enabled modules (`"text2vec-cohere"`, `"generative-cohere"`) and the Weaviate version.

-  **Stopping Weaviate:** To stop the Weaviate container when you're done:

    ```bash
    docker-compose down
    ```
    This stops and removes the container *but keeps the `weaviate_data` volume* containing your data. If you want to remove the data volume as well use `docker-compose down -v`.

Now you have a Weaviate instance running locally via Docker, accessible at `http://localhost:8080`, and configured with the necessary Cohere modules using your API key securely read from the `.env` file. Your Python scripts can now connect to this instance.

4.  **API Keys:**
    *   Obtain API keys from Cohere and OpenAI.
    *   Store these keys securely, in your `.env` file in your project root:
        ```
        COHERE_API_KEY="your_cohere_api_key"
        OPENAI_API_KEY="your_openai_api_key"
        ```

5.  **Data Sources Access:**
    *   **GitHub Repository:** Ensure you know the URL of the public GitHub repository containing the Markdown documentation (e.g., `https://github.com/tyson-swetnam/fractal-notebooks`).
    *   **JSONL File:** Obtain the JSON Lines (`.jsonl`) file containing research paper metadata and *pre-computed embeddings*. You'll need a way to access this file (direct download or download script). Place it where your ingestion script can read it.

---

**Phase 2: Building the Data Ingestion Service (Conceptual Script)**

This script prepares and loads data into Weaviate. It should perform the following actions:

1.  **Load Configuration:** Read API keys from the `.env` file. Define constants like the GitHub repo URL, the local path to the JSONL file, the Weaviate instance URL, and desired Weaviate collection names (e.g., `FractalWebsite`, `FractalDatabaseEmbeddings`).
2.  **Fetch GitHub Documentation:**
    *   Implement logic to clone the specified GitHub repository into a temporary location.
    *   Navigate to the subdirectory containing the documentation (e.g., `docs`).
    *   Iterate through all files ending in `.md` within that directory.
    *   For each Markdown file, read its full content.
    *   Store the filename and content for later batch insertion into Weaviate.
3.  **Prepare Research Paper Data (Optional Download):**
    *   If the JSONL file is not already local, implement logic to download it. If it requires authentication (like the CyVerse example), handle credential input or secure retrieval. Use `requests` with streaming and `tqdm` for large files.
4.  **Connect to Weaviate:** Establish a connection to your Weaviate instance. Authenticate using the Cohere API key in the connection headers, as this is required by the Weaviate modules.
5.  **Define and Create Weaviate Collections:**
    *   **Check Existence:** Before creating, check if collections with the defined names already exist.
    *   **Recreate Strategy:** Implement a strategy for updates. The simplest (as in the example) is to *delete* the collection if it exists and then recreate it. *Warning: This deletes all data on each run.* A more advanced strategy would involve checking for existing data and only updating/adding new items.
    *   **Create `FractalWebsite` Collection:**
        *   Define properties: `filename` (Text), `content` (Text).
        *   Configure the vectorizer: Use `text2vec-cohere`, specifying the desired Cohere embedding model (e.g., `embed-english-v3.0`).
        *   Configure the generative module: Use `generative-cohere`, specifying the desired Cohere generation model (e.g., `command`).
    *   **Create `FractalDatabaseEmbeddings` Collection:**
        *   Define properties based on the JSONL structure: `title` (Text), `doi` (Text), `datePublished` (Date - handle potential format conversion from YYYY-MM-DD to RFC3339 needed by Weaviate), `creator` (Text Array), `publisher` (Text), `url` (Text), `content` (Text - representing the `fullText` from the JSONL). Add other relevant fields like `keyphrase`, `wordCount` etc. if needed for filtering later.
        *   **Crucially:** Configure this collection to *accept pre-computed vectors*. This means *not* specifying a vectorizer like `text2vec-cohere` in the main configuration, but *still* enabling the `generative-cohere` module for potential RAG use later.
6.  **Batch Import Data into Weaviate:**
    *   **Website Data:** Use Weaviate's batch import functionality. For each piece of GitHub documentation (filename, content), add an object to the `FractalWebsite` collection. Weaviate will automatically use the configured `text2vec-cohere` module to generate and store the vector based on the `content`. Assign a unique UUID (e.g., generated based on the filename).
    *   **Research Paper Data:** Read the JSONL file line by line. For each line (representing a paper):
        *   Parse the JSON data.
        *   Extract the required properties (`title`, `url`, `creator`, `content`/`fullText`, etc.).
        *   **Handle Date Format:** Convert the `datePublished` field to RFC3339 format if necessary.
        *   Extract the pre-computed `embedding` vector from the JSON.
        *   Use Weaviate's batch import. Add an object to the `FractalDatabaseEmbeddings` collection, providing *both* the properties *and* the `vector` explicitly using the extracted embedding.
        *   *Optional:* Filter out records that lack essential content (like `fullText`) before adding them.
7.  **Close Connection:** Close the Weaviate client connection.
8.  **Execution:** This script needs to be run whenever you want to update the Weaviate database with the latest data from GitHub or the JSONL file.

---

**Phase 3: Building the API Server (Conceptual Script)**

This script runs a web server to handle chat requests.

1.  **Setup Flask:**
    *   Import necessary libraries (`Flask`, `jsonify`, `request`, `Flask-Cors`, `os`, `weaviate`, `openai`, `dotenv`).
    *   Create a Flask application instance.
    *   Enable CORS for the app to allow requests from your frontend's domain.
    *   Load environment variables (`.env`) to get API keys.
    *   Initialize the OpenAI client using the OpenAI API key.
    *   Define constants for Weaviate collection names and the Weaviate URL.
2.  **Define API Endpoint:**
    *   Create a route (e.g., `/process_chat/fractal`) that accepts POST requests.
3.  **Handle Incoming Requests:** Inside the route handler:
    *   **Parse Request:** Get the JSON data from the incoming request body. Expect a structure containing the conversation history, likely a list of messages with `role` and `content` (e.g., `{"conversation": [{"role": "user", "content": "..."}]}`).
    *   **Extract Query:** Identify the latest user message from the conversation history. This will be the primary query for retrieval.
    *   **Connect to Weaviate:** Connect to the Weaviate instance, passing the Cohere API key in the headers.
    *   **Query Weaviate for Context:**
        *   Perform a search query (e.g., `hybrid` search combining keyword and vector search) against *both* the `FractalWebsite` collection and the `FractalDatabaseEmbeddings` collection.
        *   Use the latest user message as the query input.
        *   Limit the results from each collection (e.g., top 2 most relevant items).
        *   **Process Results:**
            *   From `FractalWebsite` results, extract the `content`.
            *   From `FractalDatabaseEmbeddings` results, extract `content` (the full text), `url`, and `creator` (authors).
        *   Store the extracted text content from both sources separately (e.g., in variables like `website_context` and `paper_context`). Also store the associated URLs and authors for the papers.
    *   **Close Weaviate Connection:** Ensure the Weaviate client connection is closed.
    *   **Prepare Prompt for LLM:**
        *   **System Instructions:** Define a detailed system prompt string. This crucial prompt should instruct the LLM on:
            *   Its role (e.g., helpful fractal expert).
            *   Tone and style.
            *   Scope (what topics it should/shouldn't answer).
            *   How to handle out-of-scope questions.
            *   **Mandatory Formatting:** How to format responses (e.g., Markdown).
            *   **Citation Rules:** *Strict* instructions on when and how to cite the retrieved context:
                *   Always link to relevant webpages using full URLs and descriptive titles.
                *   Provide a list of relevant webpage links with brief descriptions.
                *   Only include research paper links if relevant.
                *   Format paper citations with title, URL link, authors, and description.
                *   Specify the order (webpages first, then papers).
                *   Include the predefined list of website URLs and their descriptions within the system prompt so the LLM knows which URL corresponds to which topic.
        *   **Construct Messages:** Create the list of messages for the OpenAI API call:
            1.  `{"role": "system", "content": system_prompt_string}`
            2.  `{"role": "user", "content": f"Full conversation history: {conversation_history_string}"}` (Optional, but helpful for context)
            3.  `{"role": "user", "content": f"Use this website information as context: {website_context}. Do not explicitly mention retrieving it unless citing."}`
            4.  `{"role": "user", "content": f"Use this research paper information as context: {paper_context}. Associated URLs: {paper_urls}. Associated Authors: {paper_authors}. Cite papers only if relevant, using the title, URL, and authors."}`
            5.  `{"role": "user", "content": f"Respond to this query: {latest_user_message}"}`
    *   **Call OpenAI API:**
        *   Use the initialized OpenAI client to call the Chat Completions endpoint (`oai.chat.completions.create`).
        *   Provide the chosen model (e.g., `gpt-4o-mini`, `gpt-3.5-turbo`, or the specified `o3-mini`).
        *   Pass the constructed list of messages.
    *   **Extract Response:** Get the response content from the OpenAI API result.
    *   **Return Response:** Send a JSON response back to the chatbot frontend containing the LLM's generated answer (e.g., `{"response": generated_text}`). You might also include the context retrieved for debugging purposes on the frontend if desired.
    *   **Error Handling:** Include `try...except` blocks for robustness (e.g., connection errors, API errors, invalid request data).
4.  **Run the Server:** Add the standard Python `if __name__ == "__main__":` block to start the Flask development server. Configure it to listen on `0.0.0.0` (to be accessible externally/within Docker) and a specific port (e.g., 5006). Enable debug mode for development.

---

**Phase 4: Running the Backend**

1.  **Run Data Ingestion:** Execute the data ingestion script whenever you need to update the database:
    ```bash
    python your_ingestion_script.py
    ```
2.  **Run API Server:** Start the Flask application:
    ```bash
    python your_api_server_script.py
    ```
    This will make the `/process_chat/fractal` endpoint available for your chatbot frontend to call.

**Server Setup (Brief):**

*   **Development:** Running `python your_api_server_script.py` uses Flask's built-in development server. It's suitable for testing but not production.
*   **Production:** For a deployed application, you would typically:
    *   Use a production-grade WSGI server (like Gunicorn or uWSGI) to run the Flask app instead of the development server.
    *   Often place a reverse proxy (like Nginx) in front of the WSGI server to handle incoming connections, SSL termination, and static file serving.
    *   Run these components within Docker containers for easier deployment and management.
    *   Disable Flask's debug mode.
