from urllib.parse import urlparse, parse_qs

import openai
from youtube_transcript_api import YouTubeTranscriptApi

openai.api_key = 'your-openai-api-key'


def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'music.youtube.com',
                               'm.youtube.com'] and parsed_url.path == '/watch':
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None


def get_youtube_transcript(video_id):
    """
    Fetch the English transcript of a YouTube video.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        return transcript.fetch()
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return None


def ask_chatgpt(question, transcripts):
    """
    Feed multiple transcripts to ChatGPT and ask a question.
    """
    combined_transcript = "\n\n".join([" ".join([item['text'] for item in transcript]) for transcript in transcripts])

    try:
        response = openai.chat.completions.create(model="gpt-4",
                                                  messages=[{"role": "user", "content": combined_transcript},
                                                      {"role": "user", "content": question}])
        return response.choices[0].text.strip()
    except Exception as e:
        print("Error communicating with ChatGPT:", e)
        return None


def main():
    # Example usage
    video_urls = ['https://www.youtube.com/watch?v=vSQjk9jKarg']  # Replace with YouTube video URLs
    video_ids = [extract_video_id(url) for url in video_urls]
    transcripts = [get_youtube_transcript(video_id) for video_id in video_ids if
                   video_id and get_youtube_transcript(video_id)]

    if transcripts:
        response = ask_chatgpt("Your question here", transcripts)
        print("ChatGPT Response:", response)


if __name__ == "__main__":
    main()
