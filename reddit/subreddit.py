import re

import praw
from praw.models import MoreComments
from prawcore.exceptions import ResponseException

from utils import settings
# Make AI methods optional
try:
    from utils.ai_methods import sort_by_similarity
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    def sort_by_similarity(threads, keywords):
        # Fallback: just return the threads as-is
        return list(threads), [0] * len(list(threads))
from utils.console import print_step, print_substep
from utils.posttextparser import posttextparser
from utils.subreddit import get_subreddit_undone
from utils.videos import check_done
from utils.voice import sanitize_text

# Dream analysis import
try:
    from utils.dream_analysis import DreamAnalyzer, analyze_dream_content
    DREAM_ANALYSIS_AVAILABLE = True
except ImportError:
    DREAM_ANALYSIS_AVAILABLE = False
    print_substep("Dream analysis module not available", "yellow")

# Dream-related subreddits for better content targeting
DREAM_SUBREDDITS = [
    "Dreams", "DreamAnalysis", "LucidDreaming", "DreamInterpretation", 
    "Nightmares", "DreamJournal", "WeirdDreams", "DreamMeaning"
]

def get_subreddit_threads(POST_ID: str, use_dream_analysis: bool = False, keep_under_30_seconds: bool = False):
    """
    Returns a list of threads from dream-related subreddits.
    
    Args:
        POST_ID: Specific post ID if provided
        use_dream_analysis: Whether to include professional dream analysis
        keep_under_30_seconds: Whether to optimize content for 30-second videos (not implemented yet)
    """

    print_substep("Logging into Reddit.")

    content = {}
    if settings.config["reddit"]["creds"]["2fa"]:
        print("\nEnter your two-factor authentication code from your authenticator app.\n")
        code = input("> ")
        print()
        pw = settings.config["reddit"]["creds"]["password"]
        passkey = f"{pw}:{code}"
    else:
        passkey = settings.config["reddit"]["creds"]["password"]
    username = settings.config["reddit"]["creds"]["username"]
    if str(username).casefold().startswith("u/"):
        username = username[2:]
    try:
        reddit = praw.Reddit(
            client_id=settings.config["reddit"]["creds"]["client_id"],
            client_secret=settings.config["reddit"]["creds"]["client_secret"],
            user_agent="Dream Tales Video Creator - Extracting dream stories",
            username=username,
            passkey=passkey,
            check_for_async=False,
        )
    except ResponseException as e:
        if e.response.status_code == 401:
            print("Invalid credentials - please check them in config.toml")
    except:
        print("Something went wrong...")

    # Ask user for subreddit input with dream-focused defaults
    print_step("Getting dream stories from subreddit...")
    similarity_score = 0
    if not settings.config["reddit"]["thread"]["subreddit"]:
        try:
            user_input = input(f"What subreddit would you like to pull dream stories from? (Default options: {', '.join(DREAM_SUBREDDITS[:4])}): ")
            if not user_input.strip():
                # Default to Dreams subreddit if no input
                subreddit_choice = "Dreams"
                print_substep("No subreddit specified. Using r/Dreams for dream stories.")
            else:
                subreddit_choice = re.sub(r"r\/", "", user_input)
            subreddit = reddit.subreddit(subreddit_choice)
        except ValueError:
            subreddit = reddit.subreddit("Dreams")
            print_substep("Invalid subreddit. Using r/Dreams.")
    else:
        sub = settings.config["reddit"]["thread"]["subreddit"]
        print_substep(f"Using subreddit: r/{sub} from TOML config")
        subreddit_choice = sub
        if str(subreddit_choice).casefold().startswith("r/"):  # removes the r/ from the input
            subreddit_choice = subreddit_choice[2:]
        subreddit = reddit.subreddit(subreddit_choice)

    if POST_ID:  # would only be called if there are multiple queued posts
        submission = reddit.submission(id=POST_ID)

    elif (
        settings.config["reddit"]["thread"]["post_id"]
        and len(str(settings.config["reddit"]["thread"]["post_id"]).split("+")) == 1
    ):
        submission = reddit.submission(id=settings.config["reddit"]["thread"]["post_id"])
    elif settings.config["ai"]["ai_similarity_enabled"] and AI_AVAILABLE:  # ai sorting based on comparison
        threads = subreddit.hot(limit=100)
        # Use dream-specific keywords if none provided
        keywords = settings.config["ai"]["ai_similarity_keywords"].split(",") if settings.config["ai"]["ai_similarity_keywords"] else ["dream", "nightmare", "sleep", "vision", "lucid", "subconscious"]
        keywords = [keyword.strip() for keyword in keywords]
        # Reformat the keywords for printing
        keywords_print = ", ".join(keywords)
        print(f"Sorting dream stories by similarity to: {keywords_print}")
        threads, similarity_scores = sort_by_similarity(threads, keywords)
        submission, similarity_score = get_subreddit_undone(
            threads, subreddit, similarity_scores=similarity_scores
        )
    else:
        threads = subreddit.hot(limit=50)
        submission = get_subreddit_undone(threads, subreddit)

    if submission is None:
        return get_subreddit_threads(POST_ID)  # submission already done. rerun

    elif not submission.num_comments and settings.config["settings"]["storymode"] == "false":
        print_substep("No comments found. Skipping.")
        exit()

    submission = check_done(submission)  # double-checking

    upvotes = submission.score
    ratio = submission.upvote_ratio * 100
    num_comments = submission.num_comments
    threadurl = f"https://new.reddit.com/{submission.permalink}"

    print_substep(f"Dream story will be: {submission.title} :thumbsup:", style="bold green")
    print_substep(f"Thread url is: {threadurl} :thumbsup:", style="bold green")
    print_substep(f"Thread has {upvotes} upvotes", style="bold blue")
    print_substep(f"Thread has a upvote ratio of {ratio}%", style="bold blue")
    print_substep(f"Thread has {num_comments} comments", style="bold blue")
    if similarity_score:
        print_substep(
            f"Dream story has a similarity score up to {round(similarity_score * 100)}%",
            style="bold blue",
        )

    content["thread_url"] = threadurl
    content["thread_title"] = submission.title
    content["thread_id"] = submission.id
    content["is_nsfw"] = submission.over_18
    content["comments"] = []
    
    # Always try to get the post content for dream stories
    if submission.selftext and submission.selftext.strip():
        if settings.config["settings"]["storymode"] and settings.config["settings"]["storymodemethod"] == 1:
            content["thread_post"] = posttextparser(submission.selftext)
        else:
            content["thread_post"] = submission.selftext
        print_substep(f"Extracted dream story content ({len(submission.selftext)} characters)", style="bold green")
    else:
        content["thread_post"] = ""
        print_substep("No post content found, will use comments for dream content", style="yellow")
    
    # Get comments for analysis or as backup content
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue

        if top_level_comment.body in ["[removed]", "[deleted]"]:
            continue  # see https://github.com/JasonLovesDoggo/RedditVideoMakerBot/issues/78
        if not top_level_comment.stickied:
            sanitised = sanitize_text(top_level_comment.body)
            if not sanitised or sanitised == " ":
                continue
            if len(top_level_comment.body) <= int(
                settings.config["reddit"]["thread"]["max_comment_length"]
            ):
                if len(top_level_comment.body) >= int(
                    settings.config["reddit"]["thread"]["min_comment_length"]
                ):
                    if (
                        top_level_comment.author is not None
                        and sanitize_text(top_level_comment.body) is not None
                    ):  # if errors occur with this change to if not.
                        content["comments"].append(
                            {
                                "comment_body": top_level_comment.body,
                                "comment_url": top_level_comment.permalink,
                                "comment_id": top_level_comment.id,
                            }
                        )

    print_substep("Received dream content successfully.", style="bold green")
    
    # 🌙 DREAM ANALYSIS INTEGRATION
    if use_dream_analysis and DREAM_ANALYSIS_AVAILABLE:
        print_step("🧠 Analyzing dream content...")
        
        # Extract the main dream content for analysis
        dream_content = ""
        if content["thread_post"]:
            # Use the main post content as the primary dream
            if isinstance(content["thread_post"], list):
                dream_content = " ".join(content["thread_post"])
            else:
                dream_content = content["thread_post"]
        elif content["comments"]:
            # Fallback to first substantial comment if no post content
            dream_content = content["comments"][0]["comment_body"]
        
        if dream_content.strip():
            try:
                dream_analysis = analyze_dream_content(dream_content)
                
                if dream_analysis:
                    print_substep("✅ Dream analysis completed successfully", "green")
                    
                    # Add analysis to content structure for video creation
                    content["dream_analysis"] = dream_analysis
                    
                    # Optional: Add analysis to thread title for context
                    if settings.config.get("dream_analysis", {}).get("include_in_title", False):
                        content["thread_title"] += " - With Professional Analysis"
                        
                    print_substep(f"📊 Analysis includes: {len(dream_analysis.get('sections', []))} sections, "
                                f"full text: {len(dream_analysis.get('full_text', ''))} chars", "blue")
                else:
                    print_substep("⚠️ Dream analysis returned empty results", "yellow")
                    content["dream_analysis"] = None
                    
            except Exception as e:
                print_substep(f"⚠️ Dream analysis failed: {str(e)}", "yellow")
                content["dream_analysis"] = None
        else:
            print_substep("⚠️ No dream content found for analysis", "yellow")
            content["dream_analysis"] = None
    else:
        content["dream_analysis"] = None
    
    # TODO: Implement 30-second optimization logic here when keep_under_30_seconds is True
    if keep_under_30_seconds:
        print_substep("📝 30-second optimization: Feature coming soon!", "yellow")
        # Future implementation will:
        # 1. Estimate text-to-speech duration
        # 2. Summarize content if too long
        # 3. Prioritize most important dream elements
        # 4. Adjust analysis content accordingly
    
    return content
