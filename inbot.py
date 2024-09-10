import praw
import os
import requests
import time
from PIL import Image
from Naked.toolshed.shell import execute_js

subreddits = "memes"
hashtags = "#reddit #memes #meme #memes #bestmemes #instamemes #funny #funnymemes #dankmemes #edgymemes #nichememes #memepage #funniestmemes #dank #memesdaily #jokes #memesrlife #memestar #memesquad #humor #lmao #igmemes #lol #memeaccount #memer #relatablememes #funnyposts #sillymemes #nichememe #memetime"
posts_per_day = 24

def bot_login():
    print('Logging in...')
    r = praw.Reddit(username='YOUR REDDIT USERNAME HERE',
                    password='YOUR REDDIT PASSWORD HERE',
                    client_id='YOUR REDDIT CLIENT ID HERE',
                    client_secret='YOUR REDDIT CLIENT SECRET HERE',
                    user_agent='A Bot that reposts Reddit Posts onto Instagram')
    print('Logged in as user: "' + str(r.user.me()) + '"')
    print("------------------------------------------------------------------")
    return r

def is_image_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')
        return content_type.startswith('image/')
    except Exception as e:
        print(f"Error checking URL: {e}")
        return False

def save_image(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

def process_image(file_path):
    try:
        with Image.open(file_path) as img:
            img = img.convert("RGB")  # Ensure image is in RGB mode
            img.save(file_path)  # Save the image
    except Exception as e:
        print(f"Error processing image: {e}")

def run_bot(r, posts_found):
    for i in range(int(posts_per_day * 1.25 + 5)):
        print("Searching for top post in r/" + subreddits)
        try:
            submission = list(r.subreddit(subreddits).hot(limit=int(posts_per_day * 1.25 + 5)))[i]
            if submission.id not in posts_found:
                print(f"New hot post in r/" + subreddits + " rank({i + 1}) is post titled: " +
                      str(submission.title) + ", id number: " + str(submission.id))
                print("--------------------------------------------------")
                
                image_url = submission.url.replace("https", "http")
                if is_image_url(image_url):
                    print(f"url: {image_url}")
                    file_path = os.path.join('Images', f"{submission.id}.jpeg")
                    if save_image(image_url, file_path):
                        print(f"Saved Image: {submission.id} to folder")
                        process_image(file_path)
                        
                        # Add to the list of posts found
                        posts_found.append(submission.id)
                        update_saved_posts(posts_found)  # Save all post IDs to file
                        
                        # Only include the post title in the caption
                        with open("Memory/Caption.txt", "w") as f:
                            f.write(submission.title)
                        
                        print("Saved post id")
                        print("---------------------------------------------------")
                        print("Posting to Instagram")
                        # Run Instagram script
                        success = execute_js('Instagram.js')
                        if success:
                            print("Done")
                            os.remove(file_path)  # Delete the image after successful post
                        else:
                            print("Failed to upload")
                        break
                    else:
                        print("Failed to save image.")
                else:
                    print("Skipping non-image post:", image_url)
            else:
                print("Post already found, skipping... ID:", submission.id)
        except Exception as e:
            print(f"Post {i} is not compatible or error occurred: {e}")
            print("------------------------------------------------------")
            pass

def get_saved_posts():
    # Ensure the file exists to avoid FileNotFoundError
    if not os.path.exists("Memory/posts_found.txt"):
        open("Memory/posts_found.txt", 'w').close()  # Create the file if it doesn't exist
        return []
    
    # Read previously posted IDs
    with open("Memory/posts_found.txt", "r") as f:
        posts_found = f.read().splitlines()
    
    print(f"Loaded {len(posts_found)} previously saved posts.")
    return posts_found

def update_saved_posts(posts_found):
    with open("Memory/posts_found.txt", "w") as f:
        for post_id in posts_found:
            f.write(post_id + "\n")
    print(f"Updated posts_found.txt with {len(posts_found)} post IDs.")

# login to reddit
r = bot_login()
run_number = 1
while True:
    # Clear captions
    open("Memory/Caption.txt", 'w').close()
    open("Memory/Caption2.txt", 'w').close()
    
    # Get saved post IDs
    posts_found = get_saved_posts()
    
    # Run bot
    run_bot(r, posts_found)
    
    print("Run number: " + str(run_number))
    run_number += 1
    
    print(f"Waiting {str(24/posts_per_day)} hours before posting again")
    time.sleep(24/posts_per_day * 3600)
