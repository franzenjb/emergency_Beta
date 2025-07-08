# Disaster Response Emergency Detector

This project contains a Python script to analyze submissions in an ArcGIS Feature Layer, flag potential emergencies, and update the layer for visualization in ArcGIS Online.

## Workflow

1.  **Connect**: The script connects to your ArcGIS Online account and a specified Feature Layer.
2.  **Analyze**: It reads new submissions from a text field that have not yet been analyzed.
3.  **Flag**: It uses an analysis function to determine if the submission is an emergency. You can choose between a simple keyword search or a more advanced AI model (OpenAI's GPT).
4.  **Update**: It updates an `ai_flag` field in the feature layer with the result (`911_REVIEW` or `OK`).
5.  **Visualize**: You can then use this `ai_flag` field in your ArcGIS Online map or dashboard to apply special symbology (e.g., a pulsing red icon) to highlight critical emergencies.

## Setup

### 1. Install Dependencies

Install the required Python packages using pip and the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 2. Configure the Script

Open `emergency_detector.py` and update the `CONFIGURATION` section at the top of the file with your specific details:

-   `FEATURE_LAYER_URL`: **This is the most important field to change.** Paste the full REST services URL to your ArcGIS Feature Layer.
-   `NOTES_FIELD`: The name of the field in your layer that contains the text to analyze (e.g., `submission_text`, `description`).
-   `ARCGIS_USERNAME`: Your ArcGIS username. You can leave this as `None` to be prompted for it when the script runs.

### 3. Choose an Analysis Method

In the `main()` function of `emergency_detector.py`, near the bottom of the script, you will find a section to choose your analysis method.

-   **Keyword (Default, Recommended for testing):** Simple, fast, and free.
    ```python
    is_emergency = is_emergency_keyword(text_to_analyze)
    # is_emergency = is_emergency_openai(text_to_analyze)
    ```
-   **OpenAI (Advanced):** More accurate but requires an API key and has associated costs. To use it:
    1.  Make sure you have an OpenAI API key.
    2.  Set it as an environment variable named `OPENAI_API_KEY`.
        -   On macOS/Linux: `export OPENAI_API_KEY='your-key-here'`
        -   On Windows: `setx OPENAI_API_KEY 'your-key-here'`
    3.  Comment out the `is_emergency_keyword` line and uncomment the `is_emergency_openai` line.
        ```python
        # is_emergency = is_emergency_keyword(text_to_analyze)
        is_emergency = is_emergency_openai(text_to_analyze)
        ```

## How to Run

Once configured, execute the script from your terminal:

```bash
python emergency_detector.py
```

The script will connect to your layer, process any new submissions (where the `ai_flag` field is not yet set), and print its progress to the console. You can run this script manually or set it up as a scheduled task (e.g., using cron on Linux or Task Scheduler on Windows) to run periodically. 