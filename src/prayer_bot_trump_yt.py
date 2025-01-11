import json
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_youtube_config():
    """
    Reads the latest_prayer.json file, generates a YouTube video title and description,
    and writes the result to youtube_video_config.json.
    """
    input_file = "latest_prayer.json"

    # Step 1: Read the input JSON file
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            prayer_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Ensure the file exists.")
        return

    # Extract data from the prayer JSON
    time_of_day = prayer_data.get("time_of_day", "morning")
    headlines = prayer_data.get("headlines_used", [])
    prayer_text = prayer_data.get("prayer_text", "")

    output_file = f'youtube_video_config_{time_of_day}.json'
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            previous_youtube_video_config = json.load(f)
    except FileNotFoundError:
        previous_youtube_video_config = ''

    # Step 2: Use OpenAI to generate a title and description
    headlines_str = "\n".join(headlines)
    prompt = f"""
    I am creating a YouTube video for an ongoing series of prayers led by a leader 
    who prays earnestly for the nation each {time_of_day}. Here are the headlines 
    influencing the prayer:
    
    {headlines_str}
    
    The prayer is heartfelt, addressing Jesus, and calls for guidance, forgiveness, 
    and hope for the challenges reflected in these headlines. Generate a catchy 
    and honest YouTube title and description for this video that captures the 
    reverence, sincerity, and the theme of morning prayers.

    Title should be brief and engaging. Description should provide context about 
    the prayer, reference the time of day, and mention the prayer's ongoing series.

    The morning series is titled "Dawn of Hope" and should not change.

    This was the previous youtube video config:
    {previous_youtube_video_config}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a creative assistant helping generate YouTube video titles and descriptions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )

    # Extract response from OpenAI
    result = response["choices"][0]["message"]["content"].strip()

    # Split the result into title and description (assuming OpenAI returns both)
    title, description = result.split("\n", 1)
    title = title.replace("Title:", "").strip()
    description = description.replace("Description:", "").strip()

    # Step 3: Save the output to a new JSON file
    youtube_config = {
        "title": title,
        "description": description,
        "time_of_day": time_of_day,
        "headlines_used": headlines,
        "prayer_text": prayer_text
    }

    print("\n=========== Donald Trump Prayer YouTube Config ===========")
    print(json.dumps(youtube_config, indent=2, ensure_ascii=False))
    print("=================================================\n")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(youtube_config, f, ensure_ascii=False, indent=2)

    print(f"YouTube video configuration saved to {output_file}")

if __name__ == "__main__":
    generate_youtube_config()
