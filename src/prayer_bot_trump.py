import openai
import requests
import json
import datetime
import random
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
news_api_key = os.getenv('NEWS_API_KEY')


def fetch_raw_headlines_from_newsapi(endpoint='everything', search='q=Trump'):
    """
    Fetches headlines from NewsAPI based on the provided endpoint and search query.
    Makes the function idempotent by saving results to a local file named with today's date,
    e.g., news_api_2025-01-10.json. If that file exists, we use the cached data
    instead of calling the API again.

    Parameters:
    - endpoint (str): 'everything' or 'top-headlines'
    - search (str): Query parameters (e.g., 'q=Trump&sortBy=popularity', 'country=us')

    Requires: 
    - news_api_key in your environment variables
    """
    today_str = datetime.datetime.today().strftime('%Y-%m-%d')
    filename = f"news_api_{today_str}_{endpoint}_{search}.json"

    # 1. If today's file exists, load data from it
    if os.path.exists(filename):
        print(f"[fetch_raw_headlines_from_newsapi] Using cached data from {filename}")
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # 2. Otherwise, call the NewsAPI
        print(f"[fetch_raw_headlines_from_newsapi] Fetching new data from NewsAPI for {today_str}")
        news_api_url = f"https://newsapi.org/v2/{endpoint}?{search}&apiKey={news_api_key}"
        response = requests.get(news_api_url)
        data = response.json()

        # 3. Save the fetched data to a file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Combine each article's title and description into one string
    articles = data.get('articles', [])
    headlines = [
        f"Date: {article['publishedAt']}; Title: {article['title']}; Description: {article.get('description', '')}"
        for article in articles
        if article.get('title')
    ]
    return headlines

def fetch_headlines_for_jesus():
    """
    1. Fetch raw headlines from a news source.
    2. Use OpenAI to determine the top 3-5 headlines that would be most interesting to Jesus if he were POTUS.
    3. Return those top headlines as a list of strings.
    """
    today_str = datetime.datetime.today().strftime('%Y-%m-%d')
    # Fetch raw headlines from a placeholder or real function
    trump_headlines = fetch_raw_headlines_from_newsapi('everything', 'q=Trump&sortBy=popularity')
    us_headlines = fetch_raw_headlines_from_newsapi('top-headlines', 'country=us')
    
    # Construct a prompt to ask OpenAI to pick the top 3-5 headlines
    prompt = f"""
    Below is a list of headlines about Donald Trump and the US.
    Please select 3 headlines that would be most interesting if Jesus were POTUS.
    Pay attention to relevance of the timing.  Today is {today_str} and the headline date is indicated by Date:
    Pay attention to relevance of the role of POTUS.
    Pay attention to the most important commandment to love God and neighbors.
    Do not assume that modern science understands climate change.
    Do not assume that modern science understands healing mental and physical disease.
    Do not assume that modern economics is good.
    Assume that we are on the verge of a breakthrough in Artificial Intelligence.
    Assume that we will need to move towards a new economy where all people receive their needs through automation.
    Assume that those needs include teachers and preachers and therapists who make use of AI.
    Assume that the most fundamental labor will be optimized with AI.
    Provide only the selected headlines, one per line, without commentary.
    Ignore [Removed]
    
    Headlines About Trump ordered by popularity:
    {json.dumps(trump_headlines, indent=2)}
    Headlines About US:
    {json.dumps(us_headlines, indent=2)}
    Now respond:
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        # model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert assistant helping to filter news headlines."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=256,
        temperature=0.2,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    
    # Get the text and split by lines
    filtered_response = response.choices[0].message.content.strip().split("\n")

    
    # Clean up any blank lines
    selected_headlines = [line.strip() for line in filtered_response if line.strip()]
    
    # We want only up to 5
    selected_headlines = selected_headlines[:5]
    
    return selected_headlines

def improve_ssml(text, system_prompt='you are helping generate speech for a reverent private prayer'):
    prompt = f"""
    Considerations:
        Where there are break times of 200ms, randomize it between 100ms-250ms.
        Where there are break times of 900ms, randomize it between 700ms-1100ms.
        Where there is a word which is easily mispronounced:
            <speak>
                Grant them the courage and resources they need to protect and save <phoneme alphabet="ipa" ph="laɪvz">lives</phoneme>.
            </speak>
            <speak>
                He <phoneme alphabet="ipa" ph="lɪvz">lives</phoneme> in us.
            </speak>

    Now use the considerations to improve the following SSML so that the US English is pronounced properly and sounds more natural:
    {text}
    """
    # Call OpenAI API for SSML improvement
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048,
        temperature=0.2,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content.strip()

def create_prayer_text(headlines, time_of_day="morning"):
    """
    Uses OpenAI to create a ~10-minute prayer that:
      - Focuses on the character of Jesus (no explicit Bible verse references).
      - Incorporates the headlines in a prayerful manner.
      - Portrays Donald Trump as genuinely seeking guidance, aiming to serve Jesus
        as a Christian, husband, father, and POTUS.
      - Maintains a reverent, intimate, and accessible tone for everyday people.
      - Around 1,000-1,500 words (less than 3000 characters).
    """
    # Join the headlines into a single string
    headlines_str = ". ".join(headlines)

    # Construct the prompt
    prompt = f"""
    Act as if you are composing a heartfelt, reverent prayer spoken by Donald Trump to God.
    This prayer should be accessible to everyday people who know Jesus primarily by character 
    (kindness, love, forgiveness, guidance) but without explicit Bible references.
    
    Requirements:
      - Portray Donald Trump as sincerely striving to be a faithful Christian, 
        acknowledging Jesus as King and seeking to follow His example.
      - Touch on how Trump aims to serve Jesus in his roles as a Christian, husband, father, and President.
      - Reference these current headlines in a prayerful way: {headlines_str}.
      - Keep the tone humble, expressing gratitude, reflection, repentance if applicable,
        and hope for the future, always centered on Jesus' loving character.
      - The prayer should be around 1,000 to 1,500 words (less than 3000 characters).
      - Adjust slightly based on whether it's morning or evening, e.g., “Thank you for this day” (morning)
        or “Thank you for seeing me through this day” (evening).
      - Avoid directly referencing the headlines and pray for the people impacted by the headlines and the responsibility of the POTUS in caring for those people.
      - Avoid mentioning company names.
    
    Begin the prayer now for time of day being {time_of_day}:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        # model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a thoughtful, reverent prayer helper."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    prayer_text = response.choices[0].message.content.strip()
    # Wrap the prayer text in SSML for reverent delivery
    ssml_prayer = f"""
    <speak>
        <prosody rate="85%" pitch="-5st">
            <break time="500ms"/>
            {prayer_text.replace('.', '<break time="900ms"/>').replace(',', '<break time="200ms"/>')}
            <break time="500ms"/>
        </prosody>
    </speak>
    """
    print("ssml_prayer:" + ssml_prayer)
    improved_ssml = improve_ssml(ssml_prayer)
    print("improved_ssml:\n" + improved_ssml)
    return prayer_text

def generate_prayer_data():
    """
    Main function that:
      1. Determines morning or evening.
      2. Fetches top 3 headlines relevant to Trump serving Jesus.
      3. Creates the prayer text via OpenAI.
      4. Stores the results in a dictionary (which you can then
         export to JSON or pass to a TTS module).
    """
    # Determine if it's morning or evening
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    
    # 1. Fetch headlines
    headlines = fetch_headlines_for_jesus()
    
    # 2. Create prayer text
    prayer_text = create_prayer_text(headlines, time_of_day=time_of_day)
    prayer_text = prayer_text.replace('\n', ' ')
    
    # 3. Store the results in a dictionary
    #    This structure can easily be saved to JSON or passed to TTS
    prayer_data = {
        "time_of_day": time_of_day,
        "headlines_used": headlines,
        "prayer_text": prayer_text
    }
    
    return prayer_data

def main():
    # Generate prayer data
    prayer_data = generate_prayer_data()
    
    # Option 1: Print to console
    print("\n=========== Donald Trump Prayer (Data) ===========")
    print(json.dumps(prayer_data, indent=2, ensure_ascii=False))
    print("=================================================\n")
    
    # Option 2: Save to a JSON file for further processing (e.g., TTS)
    with open("latest_prayer.json", "w", encoding="utf-8") as f:
        json.dump(prayer_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
