# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
search_listings searches the dataset loaded via load_listings() and filters the items by the description keywords, size matching, and maximum price boundaries. It returns a list of matching items sorted by closest match.


**Input parameters:**
- `description` (str): Search term or keyword to match against the item's title, description, or style_tags.
- `size` (str): The speicific size string to look for (ex: 'M' or 'US 7'). If None, size filtering is skipped.
- `max_price` (float): The upper price limit. If none, price filtering is skipped.

**What it returns:**
A list[dict] where each dictionary represents a found listing item containing the fields: id(str), title(str), description(str), category(str), category(str), Style_tags(list[str]), size(str), condition(str), price(float), colors(List[str]), brand(str/None), and platform[str].

**What happens if it fails or returns nothing:**
returns an empty list, []. The planning loop detects this empty list, stops the sequence, sets an informative message in session["error"], and asks the user to widen the parameters and to try again.
---

### Tool 2: suggest_outfit

**What it does:**
suggest_outfit takes the chosen listing item and the user's wardrobe dictionary, using the Groq LLM API, to generate an outfit syling recommendation that combines the new piece with existing items.
**Input parameters:**
- `new_item` (dict): The dictionary representation of the item selected from the search Listings.
- `wardrobe` (dict): The dictionary containing the user's wardrobe items list.

**What it returns:**
A str containing clear and smart styling advice that explicitly references items from the user's wardrobe to pair with the new item. 
**What happens if it fails or returns nothing:**
If the wardrobe is empty (ex: wardrobe["items"] ==[]), it falls back to generating general fashion advice on how to style the category of items.
---

### Tool 3: create_fit_card

**What it does:**
create_fit_card generates a sharable social media description(caption) for the full outfit utilizing the Groq LLM API.
**Input parameters:**

- `outfit` (Str): The text suggestion produced by suggest_outfit
- 'new_item' (dict) : The dictionary details of the newly discovered item.

**What it returns:**
a string that represents a casual, high-quality, with emojis caption that you would normally find only in a social media caption.

**What happens if it fails or returns nothing:**
If outfit string is empty or missing, It returns an error bypassing the LLM and returns an error string, "Error: cannot generate fit card due to incomplete outfit details. try widening your search!" to prevent a crash.
---




## Planning Loop

**How does your agent decide which tool to call next?**
The planning loop follows these strict conditions inside run_agent() based on the keys and values present in the session dictionary:

1) initialization: The agent extracts the search keywords, size, and price limits from the user's query text using an initial regex or explicit values.

2) Call search_listings(description, size, max_price).
     Branch A(Empty Path): if the return value is an empty list [], the agent sets session["error"] = "No items matched your description...", sets the selected item = none, and exits early.
     Branch B(Success Path): If items are found, set session["selected_item"] = results[0] (the top result), and continue.

3)  Outfit Styling: Inspect session["selected_item"]. if present, pass it along with the user's wardrobe array to suggest_outfit(). Save the returend text to session["Outfit suggestion"]

4) Caption Generation: Check if session["Outfit suggestion"] exists and isn't an error message. If valid, pass both the suggestion and session["selected_item"] to create_fit_card() and store the output string in session["fit_card"].

5) Termination: The loop is complete once session["fit_card"] is populated or when a branch sets session["error"] and exits early.
---




## State Management

**How does information from one tool get passed to the next?**

The system uses a persistent Python dictionary named session initialized at the beginning of the user interaction. The data is saved under explicit tracking keys and read by later components:

session["selected_item"]: Holds the full dictionary of the target listing item extracted by search_listings().

session["outfit_suggestion"]: Holds the string result of the styling instructions created by suggest_outfit().

session["fit_card"]: Holds the string result of the caption created by create_fit_card().

session["error"]: Holds any error string if a pipeline component breaks down or returns an empty value.
---




## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query |Halts the pipeline, sets session[error], and returns a static error string |
| suggest_outfit | Wardrobe is empty |Bypasses the wardrobe items and gives general fashion guidelines for the item type  |
| create_fit_card | Outfit input is missing or incomplete |Aborts the LLM call and populates session["fit_card"] with an error message that informs the user to try a different item. |

---




## Architecture

    User([User Input Query]) --> Loop{Planning Loop}
    
    Loop -->|1. Call| T1[search_listings]
    T1 -->|Returns []| Err1[Set session error: No listings found] --> End([Terminate & Return Session])
    T1 -->|Returns matches| State1[Save to session: selected_item = results0]
    
    State1 -->|2. Call| T2[suggest_outfit]
    T2 -->|Empty Wardrobe / Error| Fallback[Generate general category style advice] --> State2
    T2 -->|Wardrobe present| State2[Save to session: outfit_suggestion]
    
    State2 -->|3. Call| T3[create_fit_card]
    T3 -->|Missing Input| Err2[Set fit_card: Error message text] --> End
    T3 -->|Valid Input| State3[Save to session: fit_card] --> End
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
AI tool: Claude
Input: Individual blocks under tools, where i listed the plannings of the 3 tools, search_listings(), suggest_outfit(), and create_fit_card(), alongside code patterns from utils/ data_loader.py.
Output: Three fully fleshed out Python functions that match the qualifications of my planning to insert directly into tools.py.
Verification: I will run local variables and testing from instructions to ensure all cases from empty lists to empty inputs return predictable, safe values without generating runtime errors.

**Milestone 4 — Planning loop and state management:**
AI tool: Claude
Input: The Planning loop, State Management, and the architecture Mermaid diagram text directly from my planning.md file.
Output: The core wrapper logic for run_agent() inside agent.py and the updated mapping hooks inside app.py.
Verification: Run manual tests with the example query to print the session state tracking dictionary at each interval to ensure items flow seamlessly without losing formatting attributes.

---

## A Complete Interaction (Step by Step)

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
The planning loop parses out the requirements  and executes search_listings(description="vintage graphic tee", size = None, max_price = 30.0). It queries the database and grabs lst_002, because it matches the phrase keywords of "vintage", and "graphic tee", and has a price of 18, which is lower than 30. this dictionary is saved to session["Selected_item"].
**Step 2:**
The agent recognizes that session["selected_item"] is populated. It extracts the item alongside the user's active closet state via get_example_wardrobe() and passes them into suggest_outfit(). The LLM returns a string: "Pair this butterfly print Baby tee with your Baggy straight-leg jeans (Dark wash) and your Chunky white sneakers for a clean Y2K streetwear vibe." The text is saved to session["outfit_suggestion"].
**Step 3:**
The planning loop reads the active outfit instructions and triggers create_fit_card(), feeding it the styling text block. The LLM will then generate a casual post caption.
**Final output to user:**
The gradio application interface displays three filled output text frames:

1) item found: "Y2K Baby Tee - Butterfly Print - $18.00 on Depop

2) Styling advice: "Pair this butterfly print baby tee....."

3) Fit Caption: "Secured this tee... feelin good"