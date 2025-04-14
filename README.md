# fractal-notebooks
collection of python apps and jupyter notebooks for simulating self-affine fractals

# Build Documentation

To build the docs locally:

```
git clone https://github.com/username/repository.git

cd repository

pip install -r requirements.txt

python -m mkdocs serve
```
Open a browser and go to https://localhost:8000

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

*   **Docker and Docker Compose:** You need Docker Desktop (Windows/macOS) or Docker Engine + Docker Compose (Linux) installed.
    If not installed, follow the official Docker installation guides for your operating system.
*   **Cohere API Key:** You need your API key from Cohere.

**Steps:**

-  **Create Project Files:** In your main backend project directory create two files:
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
    *   **GitHub Repository:** Ensure you know the URL of the public GitHub repository containing the Markdown documentation (e.g., `https://github.com/username/repository`).
    *   **JSONL File:** Obtain the JSON Lines (`.jsonl`) file containing research paper metadata and pre-computed embeddings. You'll need a way to access this file (direct download or download script). Place it where your ingestion script can read it.

---

**Building the Data Ingestion Service**

This script prepares and loads data into Weaviate. It should perform the following actions:

1.  **Load Configuration:** Read API keys from the `.env` file. Define constants like the GitHub repo URL, the local path to the JSONL file, the Weaviate instance URL, and desired Weaviate collection names (e.g., `Webpage`, `DatabaseEmbeddings`).
```
dotenv_path = "/home/your-path/.env"
load_dotenv(dotenv_path)

REPO_URLS = [
    "https://github.com/username/repository"
]
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
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Cloning {repo_url} into temporary directory: {temp_dir}")
            subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True, text=True)

            docs_dir = os.path.join(temp_dir, "docs")
            if not os.path.exists(docs_dir):
                print(f"Warning: 'docs' directory not found in {repo_url}")
                return []

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

    except subprocess.CalledProcessError as e:
        print(f"Git command failed:\n{e.stderr}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def read_markdown_file(file_path):
    with open(file_path, "r") as file_stream:
        file_content = file_stream.read()
        return file_content
```
3.  **Prepare Research Paper Data:**
    *   If the JSONL file is not already local, implement logic to download it. If it requires authentication, handle credential input or secure retrieval. Use `requests` with streaming and `tqdm` for large files.
```
def download_file(file_url, local_filename, username, password):
    try:

        with requests.get(file_url, auth=(username, password), stream=True) as response:
            response.raise_for_status()


            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                print("Failed to retrieve the file size. The progress bar may not display correctly.")

            block_size = 1024 * 1024
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

            with open(local_filename, 'wb') as f:
                for data in response.iter_content(block_size):
                    f.write(data)
                    progress_bar.update(len(data))
            progress_bar.close()

            if total_size != 0 and progress_bar.n != total_size:
                print("ERROR: Download incomplete.")
            else:
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
    *   **Recreate Strategy:** Implement a strategy for updates. The simplest is to *delete* the collection if it exists and then recreate it. Alternatively a more advanced strategy would check for existing data and not delete pages wich have not been edited.
    *   **Create Collection:**
        *   Define properties: `filename` (Text), `content` (Text).
        *   Configure the vectorizer: Use `text2vec-cohere`, specifying the desired Cohere embedding model (e.g., `embed-english-v3.0`).
        *   Configure the generative module: Use `generative-cohere`, specifying the desired Cohere generation model (e.g., `command`).
```
if COLLECTION_NAME_1 in client.collections.list_all():
    print(f"{COLLECTION_NAME_1} exists: Deleting and recreating")
    client.collections.delete(COLLECTION_NAME_1)
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
        *   Define properties based on the JSONL structure: `title` (Text), `doi` (Text), `datePublished` (Date - handle potential format conversion from YYYY-MM-DD to RFC3339 needed by Weaviate), `creator` (Text Array), `publisher` (Text), `url` (Text), `content` (Text - representing the `fullText` from the JSONL). Add other relevant fields like `keyphrase`, `wordCount` etc. if needed for filtering later.
        *   Configure this collection to accept pre-computed vectors. This means *not* specifying a vectorizer like `text2vec-cohere` in the main configuration, but still enabling the `generative-cohere` module for use later.
        
```
def convert_to_rfc3339(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").isoformat() + "Z"

properties = [
    wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="doi", data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="datePublished", data_type=wvc.config.DataType.DATE),
    wvc.config.Property(name="docType", data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="creator", data_type=wvc.config.DataType.TEXT_ARRAY),
    wvc.config.Property(name="isPartOf", data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="keyphrase", data_type=wvc.config.DataType.TEXT_ARRAY),
    wvc.config.Property(name="wordCount", data_type=wvc.config.DataType.INT),
    wvc.config.Property(name="pageCount", data_type=wvc.config.DataType.INT),
    wvc.config.Property(name="publisher", data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="url", data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT)
]

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
collection = client.collections.get(COLLECTION_NAME_1)

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
        *   **Handle Date Format:** Convert the `datePublished` field to RFC3339 format if necessary.
        *   Extract the pre-computed `embedding` vector from the JSON.
        *   Use Weaviate's batch import. Add an object to the `DatabaseEmbeddings` collection, providing *both* the properties *and* the `vector` explicitly using the extracted embedding.
        *   *Optional:* Filter out records that lack essential content (like `fullText`) before adding them.
```
def convert_to_rfc3339(date_str):
  try:
    return datetime.strptime(date_str, "%Y-%m-%d").isoformat() + "Z"
  except (ValueError, TypeError):
    return None

collection = client.collections.get(COLLECTION_NAME_2)
jsonlFile = "your_file.jsonl"

with open(jsonlFile, "r") as file:
    with collection.batch.rate_limit(requests_per_minute=50) as batch:

        for line in file:

            data = json.loads(line)
            embedding = data.get("embedding", [])

            rfc3339_date = None
            if "datePublished" in data and data["datePublished"]:
                rfc3339_date = convert_to_rfc3339(data["datePublished"])

            properties = {
                "title": data.get("title"),
                "url": data.get("url"),
                "datePublished": rfc3339_date,
                "creator": data.get("creator"),
                "publisher": data.get("publisher"),
                "content": data.get("fullText"),
                "doi": data.get("doi"),
                "docType": data.get("docType"),
                "isPartOf": data.get("isPartOf"),
                "keyphrase": data.get("keyphrase"),
                "wordCount": data.get("wordCount"),
                "pageCount": data.get("pageCount")
            }
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

**Building the API Server (Conceptual Script)**

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

dotenv_path = "/home/ubuntu/opendendro-chatbot/.env"
load_dotenv(dotenv_path)

WEAVIATE_COLLECTIONS = [
    "Webpage",
    "DatabaseEmbeddings"
]

ARTICLES = [
    "DatabaseEmbeddings"
]


COHERE_API_KEY = os.environ["COHERE_API_KEY"]


oai = OpenAI(api_key=os.getenv("REACT_APP_OPENAI_API_KEY"))
```
2.  **Define API Endpoint:**
    *   Create a route (e.g., `/process_chat/fractal`) that accepts POST requests.
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
    data = request.json

    if not data or "conversation" not in data:
        return jsonify({"error": "Missing 'conversation' field"}), 400

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
            *   From `DatabaseEmbeddings` results, extract `content` (the full text), `url`, and `creator`.
        *   Store the extracted text content from both sources separately. Also store the associated URLs and authors for the papers.
```
siteContext = []
articleContext = []
urls = []
authors = []
collections_queried = []

try:
    print("Querying Weaviate...")
    for col_name in WEAVIATE_COLLECTIONS:
        print(f"Working on collection: {col_name}\n")
        collections_queried.append(col_name + " loop was entered")

        collection = client.collections.get(col_name)

        response = collection.query.hybrid(
            query=latest_user_message,
            limit=2
        )

        is_article_collection = col_name in ARTICLES
        for obj in response.objects:
            content = obj.properties.get('content')
            if content:
                if is_article_collection:
                    articleContext.append(content)
                    urls.append(obj.properties.get('url'))
                    authors.append(obj.properties.get('creator'))
                    collections_queried.append(col_name + " was used (article)")
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
        *   **System Instructions:** Define a detailed system prompt string.
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
        openai_response = oai.chat.completions.create(
            model="o3-mini",
            messages=openai_messages
        )
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
