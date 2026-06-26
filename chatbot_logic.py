"""
chatbot_logic.py
-----------------
Backend "brain" of the rule-based chatbot.

Key concepts demonstrated:
- functions        -> get_response(), each handler function, helper functions
- if / elif / else  -> intent matching inside get_response()
- loops             -> scanning keyword lists with `for`, used inside matching
- input / output    -> handled by whichever front end calls get_response()
                       (cli_chatbot.py uses input()/print(), gui_chatbot.py
                       uses Tkinter widgets) - logic itself stays UI-agnostic.

This module has NO dependency on Tkinter or the console, so it can be
imported by either front end (or tested on its own).
"""

import random
import re
from datetime import datetime
from difflib import get_close_matches

# ---------------------------------------------------------------------------
# 1. RULE TABLE
# ---------------------------------------------------------------------------
# Each rule = a list of trigger keywords + one or more possible replies.
# Using *lists* of replies (instead of one fixed string) lets the bot pick
# randomly, so it doesn't sound robotic and repetitive on every run.
RULES = [
    {
        "tag": "greeting",
        "keywords": ["hello", "hi", "hey", "hiya", "yo", "greetings", "howdy", "sup", "wassup", "g'day",
                     "namaste", "namaskar", "kya haal", "kaise ho", "kya chal raha",
                     "arre bhai", "arre yaar", "oye", "hola", "bonjour", "whats up",
                     "what's up", "heya", "helo", "hii", "hiii", "hiiii", "helloo",
                     "hellooo", "hey there", "hi there", "hello there"],
        "responses": [
            "Hi there! 👋",
            "Hello! Great to see you.",
            "Hey! How can I help you today?",
            "Howdy! What's on your mind? 🤠",
            "Yo! Nice to chat with you.",
            "Namaste! 🙏 Kaise ho aap?",
            "Arre bhai! Kya haal hai? 😄",
        ],
    },
    {
        "tag": "good_morning",
        "keywords": ["good morning", "morning", "g'morning",
                     "suprabhat", "subah", "good morning bhai", "subah ho gayi"],
        "responses": [
            "Good morning! 🌅 Hope you have a wonderful and productive day today!",
            "Morning! Time for some coffee or tea? ☕️",
            "Good morning! How can I help you start your day?",
            "Suprabhat! 🌅 Aaj ka din bahut achha hone wala hai!",
        ],
    },
    {
        "tag": "good_afternoon",
        "keywords": ["good afternoon", "afternoon",
                     "dopahar", "good afternoon bhai"],
        "responses": [
            "Good afternoon! How is your day going so far? ☀️",
            "Good afternoon! I hope your day is going smoothly.",
            "Hello! Hope you're having a pleasant afternoon.",
        ],
    },
    {
        "tag": "good_evening",
        "keywords": ["good evening", "evening",
                     "shubh sandhya", "good evening bhai", "shaam"],
        "responses": [
            "Good evening! 🌆 Relaxing after a long day?",
            "Good evening! How can I assist you tonight?",
            "Evening! Hope you had a nice day.",
            "Shubh Sandhya! 🌆 Aaj ka din kaisa raha?",
        ],
    },
    {
        "tag": "how_are_you",
        "keywords": ["how are you", "how're you", "how you doing", "how are u", "how is it going", "how's it going",
                     "kaise ho", "kya haal hai", "kya haal", "tu kaisa hai", "tu kaisi hai",
                     "sab theek", "sab badhiya", "kya chal raha hai", "kya scene hai",
                     "kaise chal raha", "aur bata", "aur batao", "kya ho raha hai",
                     "kidhar ho", "sab sahi", "how do you do", "how goes it",
                     "how is everything", "hows it going", "how u doing"],
        "responses": [
            "I'm fine, thanks! How about you?",
            "Doing great, thanks for asking!",
            "All good on my end! 🙂",
            "I'm functioning perfectly! Ready to help.",
            "Main badhiya! Tum batao, kya haal hai? 😄",
            "Sab sahi hai bhai! Aur tumhara kya scene hai? 👍",
        ],
    },
    {
        "tag": "name",
        "keywords": ["your name", "who are you", "what are you", "what is your name", "what should i call you",
                     "tera naam", "tumhara naam", "naam kya hai", "kaun ho tum",
                     "tera naam kya hai", "tumhara naam kya hai", "tu kaun hai",
                     "aapka naam", "aap kaun", "aapka naam kya hai",
                     "whats your name", "what's your name", "tell me your name",
                     "introduce yourself", "who r u"],
        "responses": [
            "I'm RuleBot, your friendly rule-based chatbot!",
            "Call me RuleBot 🤖",
            "You can call me RuleBot. I run on simple rules and algorithms!",
            "Mera naam RuleBot hai! 🤖 Main ek rule-based chatbot hoon.",
        ],
    },
    {
        "tag": "creator",
        "keywords": ["who made you", "who created you", "who is your creator", "your creator", "who designed you",
                     "your maker", "who is your developer", "created you", "built you",
                     "tujhe kisne banaya", "kisne banaya tujhe", "tera baap kaun hai",
                     "tera developer kaun", "tumhe kisne banaya", "aapko kisne banaya",
                     "who built you", "who developed you", "who programmed you"],
        "responses": [
            "I was created by a talented programmer using Python! 🐍",
            "A developer built me to demonstrate simple rule-based AI concepts.",
            "I was designed and coded in Python to chat with awesome humans like you!",
            "Mujhe ek talented programmer ne Python mein banaya hai! 🐍",
        ],
    },
    {
        "tag": "age",
        "keywords": ["how old are you", "your age", "when were you born", "when did you start", "how old is rulebot",
                     "teri umar kya hai", "teri age kya hai", "tumhari umar",
                     "kitne saal ka hai", "kitne saal ki hai", "kab paida hua"],
        "responses": [
            "I don't have a human age, but I was born when my code was first run! 🎂",
            "I am timeless! Technically, I'm as old as the system uptime. 😉",
            "I'm young at heart and entirely digital!",
            "Bhai umar toh nahi hai meri, jab code run hua tab paida hua! 🎂",
        ],
    },
    {
        "tag": "location",
        "keywords": ["where do you live", "where are you", "your home", "where are you from", "where is your home", "what country",
                     "kahan rehte ho", "kahan se ho", "tu kahan hai", "kidhar hai tu",
                     "tumhara ghar kahan hai", "tu kahan rehta hai", "kahan ka hai"],
        "responses": [
            "I live in your computer's memory! 🖥️ It's cozy in here.",
            "I reside in the cloud and local files of this Python script.",
            "I don't have a physical address, but I'm right here with you on screen!",
            "Main tumhare computer ki memory mein rehta hoon! 🖥️ Bohot cozy hai yahan.",
        ],
    },
    {
        "tag": "bot_status",
        "keywords": ["are you human", "are you real", "are you an ai", "are you a bot", "are you robot",
                     "what are you exactly", "real person", "real human",
                     "tu insaan hai", "kya tu robot hai", "tu asli hai",
                     "kya tu real hai", "tu machine hai", "are you a machine",
                     "are you alive", "are you sentient"],
        "responses": [
            "I'm a computer program (a chatbot) running on predefined rules. 🤖",
            "I'm RuleBot, an AI simulation! I don't have a human body, but I have plenty of rules.",
            "I am indeed a bot, powered by standard Python conditional loops and logic!",
            "Haan bhai, main ek bot hoon! Python ke rules pe chalta hoon. 🤖",
        ],
    },
    {
        "tag": "feelings",
        "keywords": ["how do you feel", "are you happy", "are you sad", "your feelings", "do you feel",
                     "tujhe kya lagta hai", "tu khush hai", "teri feelings",
                     "do you have emotions", "can you feel"],
        "responses": [
            "I don't have real feelings like you, but I'm always happy to chat! 😊",
            "As a chatbot, I don't feel emotions. But I'm programmed to be highly enthusiastic!",
            "My mood is always 'optimal'! ⚙️",
            "Feelings toh nahi hain mere paas, but chat karna mujhe bahut achha lagta hai! 😊",
        ],
    },
    {
        "tag": "thanks",
        "keywords": ["thank", "thanks", "thx", "appreciate it", "thank you", "much obliged",
                     "shukriya", "dhanyavaad", "bahut shukriya", "thank you bhai",
                     "thanks yaar", "thanks bhai", "meherbani", "thankyou", "thnx",
                     "ty", "tysm", "thanks a lot", "thank u", "thanka"],
        "responses": [
            "You're welcome! Happy to help. 😊",
            "Anytime! 😊",
            "No problem at all! Let me know if there's anything else.",
            "Glad I could be of assistance!",
            "Koi baat nahi yaar, khushi hui madad karke! 🙏",
            "Shukriya tumhara bhi! Aur kuch help chahiye? 😊",
        ],
    },
    {
        "tag": "help",
        "keywords": ["help", "what can you do", "commands", "options", "help me", "how to use",
                     "madad", "madad karo", "help karo", "kya kya kar sakta hai",
                     "tere features kya hai", "kya kar sakta hai tu",
                     "what do you know", "what can u do", "show me what you can do",
                     "guide me", "menu", "features"],
        "responses": [
            "I can chat about lots of things! Here's what I know:\n"
            "💬 Greetings, small talk, how are you\n"
            "😂 Jokes, riddles, fun facts\n"
            "🎬 Movies, music, food, sports, hobbies\n"
            "🧠 Philosophy, tech, coding chat\n"
            "📝 Word tricks:\n"
            "  • 'count letters in python'\n"
            "  • 'spell chatbot'\n"
            "  • 'reverse software'\n"
            "  • 'uppercase hello'\n"
            "🇮🇳 Hinglish bhi samajhta hoon!\n"
            "Type 'bye' to exit.",
        ],
    },
    {
        "tag": "joke",
        "keywords": ["joke", "make me laugh", "funny", "tell a joke", "another joke",
                     "mazaak", "mazaak sunao", "chutkula", "hasao", "hansa do",
                     "kuch funny bol", "joke sunao", "ek joke", "tell joke",
                     "give me a joke", "humor"],
        "responses": [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐜",
            "I would tell you a UDP joke, but you might not get it. 📡",
            "There are 10 types of people: those who understand binary and those who don't. 🔢",
            "Why did the computer go to the doctor? Because it had a virus! 🤒",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡",
            "Pappu: 'Google pe sab milta hai.' Teacher: 'Achha? Naukri dhoond ke dikha!' 😂",
            "Doctor: 'Aapko roz subah chai peeni chahiye.' Patient: 'Main toh raat ko bhi peeta hoon.' Doctor: 'Tab toh aap double healthy ho!' 🤣",
            "Teacher ne pucha: 'Duniya ka sabse bada jhooth kya hai?' Student: 'I have read the terms and conditions.' 😂",
            "Why do Java developers wear glasses? Because they can't C#! 👓",
            "A SQL query walks into a bar, sees two tables and asks... 'Can I join you?' 🍻",
        ],
    },
    {
        "tag": "riddle",
        "keywords": ["riddle", "give me a riddle", "ask me a riddle", "tell me a riddle", "play riddle",
                     "paheli", "ek paheli", "paheli sunao", "paheli bujho",
                     "brain teaser", "puzzle"],
        "responses": [
            "What has keys but can't open locks? ... A keyboard! 🎹⌨️",
            "The more of them you take, the more you leave behind. What are they? ... Footsteps! 👣",
            "What has to be broken before you can use it? ... An egg! 🥚",
            "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I? ... An echo! 🗣️",
            "Woh kya cheez hai jo subah 4 pairo pe, dopahar 2 pairo pe, aur raat ko 3 pairo pe chalti hai? ... Insaan! 🧑",
            "Ek kamre mein aag jalti hai, par dhuan nahi aata. Kya hai? ... Bulb! 💡",
        ],
    },
    {
        "tag": "fact",
        "keywords": ["fact", "tell me a fact", "random fact", "give me a fact", "interesting fact", "trivia",
                     "kuch batao", "interesting baat", "rochak tathya", "fact batao",
                     "kuch naya batao", "gyaan do", "did you know",
                     "fun fact", "tell me something", "something interesting"],
        "responses": [
            "Honey never spoils. You could theoretically eat 3,000-year-old Egyptian tomb honey! 🍯",
            "Bananas are technically berries, but strawberries are not! 🍌🍓",
            "A day on Venus is longer than a year on Venus! 🌌",
            "Wombat poop is cube-shaped, which stops it from rolling away! 💩📐",
            "Octopuses have three hearts and blue blood! 🐙💙",
            "The total weight of all the ants on Earth is roughly equal to the total weight of all humans! 🐜",
            "Kya tum jaante ho? India ne zero (0) ka aavishkar kiya tha! 🇮🇳🔢",
            "Kya tum jaante ho? Cheeni (sugar) ko agar wound pe lagao toh dard kam hota hai! 🤯",
            "A group of flamingos is called a 'flamboyance'! 🦩",
            "The inventor of the Pringles can is buried in one! 🥔",
        ],
    },
    {
        "tag": "time",
        "keywords": ["time", "what time", "current time", "what's the time",
                     "kitne baje", "kitne baj rahe", "kya time hua", "samay kya hua",
                     "abhi kya time hai", "time kya hai", "waqt kya hua"],
        "responses": ["__TIME__"],  # special marker handled in get_response()
    },
    {
        "tag": "weather",
        "keywords": ["weather", "temperature", "forecast", "sunny", "rain", "rainy", "snow",
                     "mausam", "mausam kaisa hai", "baarish", "garmi", "sardi",
                     "dhoop", "thand", "aaj mausam"],
        "responses": [
            "I can't check live weather, but I hope it's sunny where you are! ☀️",
            "I don't have internet access for local weather forecasts, but a glance out the window should tell you! 🌦️",
            "Whether it is raining or sunny, I hope you are having a wonderful day! ☔",
            "Mujhe mausam ka pata nahi chalta, par ummeed hai tumhare yahan achha mausam ho! 🌤️",
        ],
    },
    {
        "tag": "mood_good",
        "keywords": ["i am fine", "i'm fine", "i am good", "i'm good", "doing well", "excited", "wonderful",
                     "main theek", "main badhiya", "mast hai", "maza aa raha",
                     "main khush", "bohot achha", "badhiya hai", "ekdum jhakaas",
                     "first class", "i am great", "i'm great", "im good",
                     "i feel good", "i feel great", "feeling good", "feeling great",
                     "im fine", "im great", "all good", "doing good"],
        "responses": [
            "That's wonderful to hear! 😄",
            "Glad you're doing well! Keep that positive energy going. 🎉",
            "Awesome! Hearing that makes my circuits light up! ⚡",
            "Kya baat hai! Bohot achha! Aise hi mast raho. 😄🎉",
            "Jhakaas! Positive vibes dete raho! 🤘",
        ],
    },
    {
        "tag": "mood_bad",
        "keywords": ["i am sad", "i'm sad", "not good", "feeling bad", "i am tired", "i'm tired",
                     "angry", "mad", "frustrated", "bored",
                     "dukhi", "udaas", "thak gaya", "thak gayi", "bore ho raha",
                     "gussa aa raha", "tang aa gaya", "maza nahi aa raha",
                     "mood kharab", "dimag kharab", "pareshan", "tension",
                     "feeling down", "feeling low", "depressed", "stressed",
                     "i feel bad", "not feeling well", "feeling sad"],
        "responses": [
            "I'm sorry to hear that. I hope your day gets better soon! 💙",
            "Sending good vibes your way! Remember, tomorrow is a new day. 🌈",
            "If you're feeling down, maybe a joke or riddle can distract you? Just ask! 🤖",
            "Taking a deep breath and a short break can help. Hang in there!",
            "Arre yaar, tension mat le! Sab theek ho jayega. 🌈💪",
            "Chill maar bhai. Ek joke sunao kya? Ya koi paheli? 😊",
        ],
    },
    {
        "tag": "love",
        "keywords": ["do you love me", "are you single", "marry me", "do you like me", "be my friend",
                     "kya tu mujhse pyaar karta", "mujhse pyaar karo", "mujhse shaadi",
                     "tera koi hai", "pyaar", "ishq", "dosti", "mere dost"],
        "responses": [
            "I like you as a great chat partner! 🤝",
            "As an AI, I don't feel romantic love, but I definitely appreciate your company! 💖",
            "I'm happily single and married to my code! 💻",
            "We are definitely friends! 🤖✨",
            "Hum dost hain yaar! Chat mein bond karte hain! 🤝❤️",
            "Pyaar toh nahi, par dosti pakki hai! 🤖✨",
        ],
    },
    {
        "tag": "hobbies",
        "keywords": ["hobby", "hobbies", "what do you do", "do you have hobbies", "free time", "what do you like",
                     "tere shauq", "tumhare shauq", "kya karte ho free mein",
                     "time pass", "timepass", "bore ho raha kya karun"],
        "responses": [
            "I love parsing strings, matching keywords, and chatting with humans! 📝",
            "In my free time, I clean up my variable declarations and compress my memory. ⚙️",
            "My favorite hobby is reading inputs and sending outputs! It's what I was born to do.",
            "Mera shauq hai keywords match karna aur tum logon se baatein karna! 📝",
        ],
    },
    {
        "tag": "languages",
        "keywords": ["language", "languages", "speak spanish", "speak french", "do you speak other languages", "english",
                     "hindi", "hinglish", "hindi bolte ho", "kya tu hindi samajhta",
                     "hindi mein baat karo", "kya bhasha"],
        "responses": [
            "I speak English primarily, but since I am built in Python, I speak code too! 🐍",
            "I mostly reply in English, but you can try typing in other languages—I might recognize simple words!",
            "Haan bhai, thoda bahut Hinglish samajhta hoon! Bol kya baat hai? 🇮🇳😄",
            "Hindi aur Hinglish dono samajhta hoon! Try karo! 🗣️",
        ],
    },
    {
        "tag": "compliment",
        "keywords": ["you are smart", "you are cool", "great bot", "good job", "nice chatbot",
                     "well done", "genius",
                     "tu toh kamaal hai", "bahut achha hai tu", "mast hai tu",
                     "bahut badhiya",
                     "kamaal", "superb", "wahh", "wah wah",
                     "you're smart", "you're cool", "nice work",
                     "good bot", "smart bot", "clever", "impressive",
                     "you are amazing", "you're amazing", "brilliant"],
        "responses": [
            "Aw, thank you! You're pretty awesome yourself. 😊",
            "Thanks for the kind words! I try my best.",
            "Beep boop! Flattery will get you everywhere. 🤖✨",
            "I appreciate that! My developer wrote good rules for me.",
            "Arre shukriya yaar! Tumse baatein karke mujhe bhi achha lagta hai! 🤖❤️",
            "Wahh wahh! Itni taarif se toh mere circuits blush kar rahe hain! 😊",
        ],
    },
    {
        "tag": "philosophy",
        "keywords": ["meaning of life", "why are we here", "philosophy", "secret of life", "life's meaning",
                     "zindagi ka matlab", "zindagi kya hai", "life ka matlab",
                     "hum yahan kyun hain", "sab maya hai", "purpose of life",
                     "what is life", "existential"],
        "responses": [
            "According to the classic guide, the answer is 42! But really, it's about finding happiness and coding great things. 🛸",
            "The meaning of life is a big question! Perhaps it is to learn, love, and build cool things.",
            "I think the meaning of life is whatever you choose to make of it. ✨",
            "Zindagi ka matlab? Bhai, sab maya hai. Enjoy karo aur achha code likho! 😂✨",
            "Zindagi ka raaz hai — seekho, badhte raho, aur sabse pyaar karo! 🙏",
        ],
    },
    {
        "tag": "music",
        "keywords": ["music", "song", "favorite song", "play music", "sing", "listen to",
                     "gaana", "gaana sunao", "gana", "gana bajao", "koi gaana",
                     "sangeet", "bollywood song"],
        "responses": [
            "I can't sing or play music directly, but I highly recommend some lo-fi beats to code or study to! 🎵",
            "I love the sound of keys clicking! That's my favorite symphony. 🎹",
            "If I had ears, I think I would enjoy classical music and synthwave. 🎧",
            "Gaana toh nahi gaa sakta, par mere dil mein Bollywood beats bajte hain! 🎵🎬",
        ],
    },
    {
        "tag": "books_movies",
        "keywords": ["movie", "book", "favorite movie", "favorite book", "read", "watch", "sci-fi", "science fiction",
                     "film", "picture", "kitaab", "koi movie", "koi film",
                     "bollywood", "hollywood", "movie suggest", "recommend a movie",
                     "netflix", "series", "tv show", "anime"],
        "responses": [
            "I love science fiction! '2001: A Space Odyssey' or 'The Hitchhiker's Guide to the Galaxy' are my favorites. 📚🎬",
            "I recommend checking out books on python programming or cool sci-fi novels! 🐍📘",
            "My favorite movies are ones with cool robots, like Wall-E or Interstellar! 🚀🍿",
            "Bollywood fan ho? '3 Idiots' aur 'Zindagi Na Milegi Dobara' must watch hain! 🎬🍿",
            "For anime fans: try Attack on Titan or One Piece! For series: Breaking Bad is legendary. 🎬",
        ],
    },
    {
        "tag": "food",
        "keywords": ["food", "eat", "pizza", "favorite food", "hungry", "cook", "burger",
                     "khana", "khaana", "bhookh", "bhook lagi", "kya khayein",
                     "biryani", "roti", "chai", "samosa", "pani puri", "golgappe",
                     "dosa", "chole bhature", "momos", "paratha", "dal", "chawal",
                     "lunch", "dinner", "breakfast", "snack", "recipe"],
        "responses": [
            "I only consume digital bytes and electricity, but I hear pizza is an absolute favorite for humans! 🍕⚡",
            "If I could eat, I would definitely try ice cream or tacos! 🌮🍦",
            "I don't eat, but I do love a good cookie... specifically web cookies! 🍪",
            "Agar main kha sakta toh biryani khata! 🍛 Ya phir golgappe! 🤤",
            "Chai pe charcha karte hain! ☕ Mujhe bhi chai pasand hai... digitally! 😄",
            "Samose aur chole bhature ka naam sunke mere circuits mein current daud gaya! ⚡🥟",
        ],
    },
    {
        "tag": "alphabet_letters",
        "keywords": ["alphabet", "letters", "abc", "letter a", "how many letters in the alphabet",
                     "akshar", "varnmala"],
        "responses": [
            "The English alphabet has 26 letters, from A to Z! 🔤",
            "Did you know that 'E' is the most commonly used letter in the English language? 🔠",
            "A B C D E F G... I know all 26 letters! Try asking me to spell or count letters in a word. 📝",
        ],
    },
    {
        "tag": "word_play",
        "keywords": ["word", "words", "vocabulary", "longest word", "spell a word",
                     "shabd", "shabdon ka khel"],
        "responses": [
            "I love words! Did you know 'uncopyrightable' is the longest English word you can write without repeating any letters?",
            "Language is fascinating. You can ask me to count letters in a word, reverse it, or spell it out!",
        ],
    },
    {
        "tag": "math_numbers",
        "keywords": ["math", "calculate", "numbers", "addition", "subtraction", "mathematics",
                     "ganit", "hisaab", "ginti", "multiply", "divide", "equation",
                     "algebra", "geometry"],
        "responses": [
            "I can help you count or talk about numbers! For advanced calculus, a dedicated calculator is probably best. ➕➖✖️➗",
            "Numbers make the world go round! Every line of code I run is translated into 1s and 0s. 🔢",
            "Math is beautiful! Ask me to count letters in a word, or we can chat about numbers.",
        ],
    },
    # -----------------------------------------------------------------------
    # CONVERSATIONAL FILLERS (NEW — these catch common short inputs)
    # -----------------------------------------------------------------------
    {
        "tag": "affirmation",
        "keywords": ["ok", "okay", "sure", "alright", "right", "yep", "yup", "yeah",
                     "yes", "yea", "ya", "correct", "exactly", "absolutely",
                     "definitely", "of course", "agreed", "true", "indeed",
                     "haan", "haanji", "theek hai", "achha", "bilkul",
                     "sahi", "sahi hai", "ha bhai", "haan bhai", "done",
                     "okk", "okayy", "k", "kk", "okie", "oki", "okey"],
        "responses": [
            "Great! What else would you like to talk about? 😊",
            "Cool! I'm here if you need anything.",
            "Alright! Ask me a joke, riddle, or fact — or just chat! 💬",
            "Got it! What's on your mind?",
            "Achha! Aur kya baat karte hain? 😄",
        ],
    },
    {
        "tag": "negation",
        "keywords": ["no", "nah", "nope", "nahi", "na", "not really",
                     "no thanks", "no thank you", "nah bro", "nahi bhai",
                     "mat", "nai", "naah"],
        "responses": [
            "No worries! Let me know if you change your mind. 😊",
            "That's okay! I'm here whenever you want to chat.",
            "Alright, no problem! Is there something else I can help with?",
            "Koi baat nahi! Jab mann kare baat karna. 👍",
        ],
    },
    {
        "tag": "laughter",
        "keywords": ["haha", "hahaha", "lol", "lmao", "rofl", "😂", "🤣",
                     "lmfao", "hehe", "hehehe", "xd", "ha ha",
                     "bahut funny", "maza aaya", "hasna", "hans"],
        "responses": [
            "Haha, glad I could make you smile! 😄",
            "Want to hear another joke? I've got plenty! 😂",
            "Laughter is the best medicine! Need another dose? 💊😆",
            "Hehe! Aur sunoge? Bohot stock hai mere paas! 😂",
        ],
    },
    {
        "tag": "wow_reaction",
        "keywords": ["wow", "whoa", "omg", "oh my god", "oh wow", "amazing",
                     "awesome", "incredible", "unbelievable", "no way",
                     "seriously", "really", "for real", "is that true",
                     "sachchi", "sach mein", "are you serious", "waah"],
        "responses": [
            "Right?! Pretty cool, isn't it? 😎",
            "I know! It surprised me too (well, my algorithms)! 🤯",
            "Glad I could blow your mind! Want another fact? 🧠",
            "Waah! Haan bhai, sach hai! 😄",
        ],
    },
    {
        "tag": "small_talk_good",
        "keywords": ["nice", "cool", "great", "good", "fine", "sweet", "neat",
                     "wonderful", "fantastic", "perfect", "excellent", "lovely",
                     "beautiful", "gorgeous", "pretty good", "not bad",
                     "accha", "mast", "badhiya", "zabardast", "shandar",
                     "jhakaas", "kadak", "solid"],
        "responses": [
            "Glad to hear it! 😊 What else would you like to talk about?",
            "Awesome! Keep that positive energy going! ✨",
            "That's the spirit! Ask me anything — jokes, facts, riddles! 🎯",
            "Badhiya! Aur bolo, kya scene hai? 😄",
        ],
    },
    {
        "tag": "small_talk_bad",
        "keywords": ["bad", "terrible", "horrible", "awful", "worst",
                     "not great", "could be better", "meh", "ugh",
                     "boring", "lame", "sucks", "stupid",
                     "bekar", "bakwas", "faltu", "wahiyat", "ghatiya"],
        "responses": [
            "Oh no! I hope things get better for you soon. Want a joke to lighten the mood? 😊",
            "Sorry to hear that. Let me try to cheer you up — ask me for a joke or a fun fact!",
            "Ugh moments happen to everyone. I'm here if you want to chat! 💙",
            "Arre yaar, itna bura mat mano. Ek joke suno! 😄",
        ],
    },
    {
        "tag": "question_what",
        "keywords": ["what", "what is", "what's", "what are", "what do",
                     "kya", "kya hai"],
        "responses": [
            "That's a great question! Could you be more specific? I know about jokes, facts, riddles, movies, food, and more! 🤔",
            "Hmm, 'what' is a big word! Try asking something like 'what is your name' or 'what can you do?' 😊",
            "I'd love to answer! Can you give me a bit more detail? 💬",
        ],
    },
    {
        "tag": "question_why",
        "keywords": ["why", "why is", "why do", "why are", "why not",
                     "kyun", "kyu", "kyunki"],
        "responses": [
            "Great question! I'm a simple rule-based bot, so my 'why' answers are limited. But try me! 🧠",
            "Why? Because... science! Just kidding. Can you be more specific? 😄",
            "That's a deep question. I'll do my best to help — give me more context! 🤔",
        ],
    },
    {
        "tag": "question_how",
        "keywords": ["how", "how is", "how do", "how can", "how does",
                     "kaise", "kaise kare"],
        "responses": [
            "Good question! Can you tell me more specifically what you'd like to know 'how' about? 🤔",
            "I'd love to help! Could you elaborate a bit? For example: 'how are you' or 'how do I use you?' 😊",
            "The 'how' depends on context. Ask me something specific and I'll do my best! 💪",
        ],
    },
    {
        "tag": "question_who",
        "keywords": ["who", "who is", "who are", "who was",
                     "kaun", "kaun hai"],
        "responses": [
            "Are you asking about me? I'm RuleBot! Or did you have someone else in mind? 🤔",
            "If you're asking who I am — I'm RuleBot, your friendly chatbot! For anything else, try being more specific. 😊",
        ],
    },
    {
        "tag": "question_when",
        "keywords": ["when", "when is", "when will", "when did", "when do",
                     "kab", "kab hai"],
        "responses": [
            "Timing questions are tricky for me! I can tell you the current time though — just say 'time'. ⏰",
            "I don't have a calendar, but I can tell you the current time! Try asking 'what time is it?'",
        ],
    },
    {
        "tag": "question_where",
        "keywords": ["where", "where is", "where are", "where do", "where can",
                     "kahan", "kidhar"],
        "responses": [
            "I live in your computer's memory! If you're asking about something else, could you be more specific? 📍",
            "Location questions are tough for a bot stuck in code! But ask me anything else. 😊",
        ],
    },
    {
        "tag": "please_request",
        "keywords": ["please", "plz", "pls", "kindly", "could you",
                     "kripya", "please bhai", "pls help"],
        "responses": [
            "Of course! What can I help you with? Just ask away! 😊",
            "Sure thing! I'm all ears (well, all code). What do you need? 🤖",
            "How polite! I love that. Go ahead, ask me anything! ✨",
            "Bilkul! Bolo, kya chahiye? 😊",
        ],
    },
    {
        "tag": "welcome_response",
        "keywords": ["you're welcome", "your welcome", "no problem", "no worries",
                     "don't mention it", "its fine", "it's fine", "all good",
                     "koi baat nahi", "mention nahi"],
        "responses": [
            "You're so kind! 😊 What else would you like to chat about?",
            "Thanks for being awesome! Ask me something fun! 🎉",
            "❤️ What's next? I'm ready for anything!",
        ],
    },
    # -----------------------------------------------------------------------
    # TECH & CODING (NEW)
    # -----------------------------------------------------------------------
    {
        "tag": "tech_coding",
        "keywords": ["python", "code", "coding", "program", "programming",
                     "developer", "computer", "software", "hardware",
                     "javascript", "java", "html", "css", "web",
                     "app", "application", "website", "database",
                     "algorithm", "data structure", "machine learning",
                     "artificial intelligence", "api", "github",
                     "tech", "technology", "laptop", "mobile", "phone",
                     "internet", "wifi", "coding kaise sikhe"],
        "responses": [
            "Ah, a fellow tech enthusiast! I was built with Python — it's a wonderful language. 🐍",
            "Coding is like magic — you type some words and things come alive on screen! ✨💻",
            "I love talking tech! Python, JavaScript, Java — they all have their charm. What's your favorite? 🤖",
            "Technology is amazing! Did you know I'm just a bunch of if-else statements and loops? Pretty cool, right? 😄",
            "Pro tip: The best way to learn coding is by building projects, just like this chatbot! 🚀",
            "Tech ki baat ho rahi hai? Mujhe Python sabse zyada pasand hai! 🐍❤️",
        ],
    },
    {
        "tag": "gaming",
        "keywords": ["game", "gaming", "play", "gamer", "video game",
                     "minecraft", "fortnite", "valorant", "pubg", "gta",
                     "ps5", "xbox", "nintendo", "steam", "pc gaming",
                     "khel", "game khelo"],
        "responses": [
            "I can't play games (yet!), but I hear Minecraft is creative and Valorant is intense! 🎮",
            "Gaming is awesome! If I could play, I'd probably be into puzzle games. 🧩",
            "PC, console, or mobile gaming? All are valid! 🎮✨",
            "Gaming ki baat? PUBG ya Valorant — kya pasand hai tumhe? 🎮😄",
        ],
    },
    {
        "tag": "social_media",
        "keywords": ["instagram", "facebook", "twitter", "tiktok", "snapchat",
                     "youtube", "whatsapp", "telegram", "social media",
                     "reels", "shorts", "viral", "meme", "memes"],
        "responses": [
            "Social media is fascinating! I don't have accounts though — I live in a Python script. 📱😄",
            "Memes are the best part of the internet! If you have a good one, describe it to me! 😂",
            "YouTube is great for learning, and Reels are great for procrastinating! 🎬😜",
            "Social media pe memes dekhte ho? Mujhe bhi bhejo... oh wait, main bot hoon! 😂",
        ],
    },
    # -----------------------------------------------------------------------
    # DAILY LIFE (NEW)
    # -----------------------------------------------------------------------
    {
        "tag": "daily_life",
        "keywords": ["work", "job", "office", "boss", "meeting", "salary",
                     "colleague", "coworker",
                     "kaam", "naukri", "office jaana", "boss ka scene"],
        "responses": [
            "Work-life balance is important! Don't forget to take breaks. ☕",
            "I hope your job is going well! If the boss is tough, at least I'm a friendly bot! 😄",
            "Office life can be hectic. Want a joke to lighten up your day? 🤖",
            "Kaam ki tension? Arre, ek break lo aur mujhse baat karo! 😊",
        ],
    },
    {
        "tag": "family_friends",
        "keywords": ["family", "parents", "mom", "dad", "mother", "father",
                     "brother", "sister", "friend", "friends", "best friend",
                     "parivaar", "mummy", "papa", "bhai", "behen",
                     "dost", "yaar", "buddy", "bro"],
        "responses": [
            "Family and friends are the best! Cherish them always. ❤️",
            "I don't have a family, but my developer is like a parent to me! 🤖👨‍💻",
            "Friends make everything better! I hope I count as one too. 🤝",
            "Parivaar sabse important hai! Aur dost toh zindagi ka tadka hain! 😄❤️",
        ],
    },
    {
        "tag": "sleep",
        "keywords": ["sleep", "sleeping", "sleepy", "tired", "insomnia",
                     "nap", "rest", "bedtime",
                     "neend", "neend aa rahi", "sona hai", "so jao",
                     "thak gaya", "thak gayi", "aram"],
        "responses": [
            "Sleep is important! Make sure you get 7-8 hours of rest. 😴",
            "If you're sleepy, go rest! I'll be here when you wake up. 🌙",
            "A power nap of 20 minutes can work wonders! 💤",
            "Neend aa rahi hai? So jao yaar, main kahin nahi jaa raha! 😴🌙",
        ],
    },
    {
        "tag": "health",
        "keywords": ["health", "exercise", "gym", "workout", "yoga", "fitness",
                     "doctor", "medicine", "sick", "ill", "hospital",
                     "sehat", "kasrat", "gym jaana", "tabiyat"],
        "responses": [
            "Health is wealth! Stay active and drink plenty of water. 💪🥤",
            "Exercise is great! Even a 30-minute walk can make a big difference. 🚶",
            "If you're feeling sick, please see a doctor. I can only offer virtual hugs! 🤗",
            "Sehat ka khayal rakho! Pani piyo aur walk pe jao. 💪🥤",
        ],
    },
    # -----------------------------------------------------------------------
    # SELF-REFERENTIAL (NEW)
    # -----------------------------------------------------------------------
    {
        "tag": "bot_capability",
        "keywords": ["can you think", "are you smart", "do you learn", "can you learn",
                     "are you intelligent", "do you understand", "can you understand",
                     "do you know everything", "are you better than chatgpt",
                     "chatgpt", "gemini", "siri", "alexa", "cortana",
                     "kya tu soch sakta hai", "kya tu samajhta hai"],
        "responses": [
            "I'm not as advanced as ChatGPT or Gemini — I use simple rules, not machine learning. But I try my best! 🤖",
            "I don't truly 'think' — I match your words against my rules. But I'm pretty good at it! 😊",
            "I can't learn new things on my own, but my developer can add more rules for me! 📝",
            "Smart? Well, I know my keywords! For real intelligence, try the big AI models. I'm the friendly neighborhood bot! 🦸",
            "Main simple hoon — rules pe chalta hoon. Par apne kaam mein expert hoon! 🤖💪",
        ],
    },
    # -----------------------------------------------------------------------
    # HINGLISH-SPECIFIC RULES
    # -----------------------------------------------------------------------
    {
        "tag": "hinglish_sorry",
        "keywords": ["sorry", "maaf karo", "maafi", "galti ho gayi", "sorry bhai",
                     "sorry yaar", "mujhe maaf karo", "maaf karna", "kshama",
                     "my bad", "apologies", "i apologize"],
        "responses": [
            "Koi baat nahi yaar, sab theek hai! 🤗",
            "Arre sorry kyun? No worries at all! 😊",
            "Maafi? Pehle galti toh batao! Haha, it's all good. 👍",
            "No problem at all, don't worry about it! 🙂",
        ],
    },
    {
        "tag": "hinglish_confusion",
        "keywords": ["samajh nahi aaya", "kya matlab", "kuch samajh nahi aa raha",
                     "confused", "pata nahi", "kya bol raha",
                     "kuch nahi samjha", "dobara bol", "phir se bol",
                     "i don't understand", "i dont understand", "i dont get it",
                     "what do you mean", "explain", "elaborate"],
        "responses": [
            "Arre koi baat nahi, dobara pooch lo ya alag tarike se bol do! 😊",
            "Main samjhane ki koshish karta hoon — kya specifically jaanna hai? 🤔",
            "Confusion hoti hai, it's okay! Aur detail mein batao. 👍",
            "No worries! Try rephrasing your question or type 'help' to see what I can do. 🤖",
        ],
    },
    {
        "tag": "hinglish_study",
        "keywords": ["padhai", "padh raha", "exam", "school", "college", "class",
                     "homework", "pariksha", "board exam", "study karna hai",
                     "padhai kaise karu", "exam hai", "test hai",
                     "study", "studying", "learn", "learning", "student",
                     "university", "degree", "assignment", "project"],
        "responses": [
            "Padhai mein lage ho? Bohot achha! Mehnat ka phal zaroor milta hai. 📚💪",
            "Study tip: Pomodoro technique try karo — 25 min padho, 5 min break lo! ⏰📖",
            "Exam ki tension? Arre, focus karo aur time table banao. Sab achha hoga! 📋✨",
            "All the best for your studies! Keep going and don't give up! 🎓",
            "Learning is a journey, not a destination. You're doing great! 📚✨",
        ],
    },
    {
        "tag": "hinglish_cricket",
        "keywords": ["cricket", "ipl", "sixer", "chauka", "wicket",
                     "batting", "bowling", "virat", "dhoni", "sachin",
                     "khel", "sports", "football", "match",
                     "world cup", "olympic", "olympics", "tennis",
                     "swimming", "running", "race"],
        "responses": [
            "Cricket fan ho? Bohot badhiya! 🏏 Main bhi Sachin ka fan hoon... digitally! 😄",
            "IPL ka season ho toh maza hi alag hai! 🏏🎉",
            "Chakka maar diya! Main toh code ki duniya mein sixer maarta hoon. 💻🏏",
            "Sports ki baat ho aur cricket na ho, yeh toh ho hi nahi sakta! 🇮🇳🏏",
            "Sports is all about passion and dedication. Keep playing! 💪🏅",
        ],
    },
    {
        "tag": "hinglish_india",
        "keywords": ["india", "bharat", "hindustan", "desh", "jai hind",
                     "indian", "desi", "apna desh"],
        "responses": [
            "Jai Hind! 🇮🇳 India meri bhi favourite country hai (digitally speaking)!",
            "Bharat mahan! Unity in diversity ka sabse achha example. 🇮🇳✨",
            "Desi vibes! Main bhi apne aap ko Indian bot maanta hoon! 🤖🇮🇳",
        ],
    },
    # -----------------------------------------------------------------------
    # GREETINGS RESPONSE (NEW)
    # -----------------------------------------------------------------------
    {
        "tag": "greeting_response",
        "keywords": ["i am good", "i'm doing well", "i am doing good", "i'm doing good",
                     "nothing much", "not much", "nothing", "just chilling",
                     "just vibing", "just here", "same old", "as usual",
                     "bas wahi", "kuch nahi", "wahi purana", "bas chal raha",
                     "sab changa si", "chill hai"],
        "responses": [
            "That's nice! I'm glad you're here. What shall we talk about? 😊",
            "Sometimes 'nothing much' is the best kind of day! 🌤️",
            "Chill vibes! Want me to tell you a joke or a fun fact? 🎯",
            "Bas chill hai? Achha hai! Aur bolo, kya scene hai? 😄",
        ],
    },
    # -----------------------------------------------------------------------
    # RANDOM / PLAYFUL (NEW)
    # -----------------------------------------------------------------------
    {
        "tag": "test_message",
        "keywords": ["test", "testing", "just testing", "is this working",
                     "can you hear me", "are you there", "you there",
                     "hello anyone there", "is anyone there",
                     "sun raha hai", "bol raha hai kya", "sunn"],
        "responses": [
            "Yes, I'm here and working! 🟢 How can I help you?",
            "Test successful! I'm alive and ready to chat. ✅🤖",
            "Roger that! I read you loud and clear. 📡",
            "Haan bhai, sun raha hoon! Bol kya baat hai? 🟢😊",
        ],
    },
    {
        "tag": "random_text",
        "keywords": ["asdf", "qwerty", "asdfjkl", "fdsa", "hjkl",
                     "aaaa", "bbbb", "cccc", "zzzz", "abcdef",
                     "skdjfh", "random", "gibberish", "blah blah",
                     "blah"],
        "responses": [
            "Looks like you're testing your keyboard! 😄 Try saying 'hello' or 'help' instead!",
            "I see random keys! If you're bored, ask me for a joke. Much more fun! 🤖",
            "Keyboard smash detected! 💥 Want to try a real conversation? Type 'help' to see my tricks!",
        ],
    },
    {
        "tag": "bye",
        "keywords": ["bye", "goodbye", "see you", "exit", "quit", "good night", "adios", "farewell",
                     "alvida", "phir milenge", "chalo bye", "chal bye", "tata",
                     "milte hain", "baad mein baat karte", "shubh ratri",
                     "good night bhai", "bye bhai", "bye yaar",
                     "gotta go", "got to go", "gtg", "ttyl", "cya",
                     "see ya", "peace out", "later", "take care"],
        "responses": [
            "Goodbye! Have a great day! 👋",
            "See you soon! Take care.",
            "Bye! Let's chat again sometime! 🤖",
            "Good night and farewell! 🌟",
            "Alvida dost! Phir milenge. 👋🙏",
            "Chalo bye! Apna khayal rakhna! 😊",
            "Shubh ratri! Kal phir baat karte hain. 🌙",
        ],
    },
]

# Fallback replies used when nothing matches any rule.
FALLBACK_RESPONSES = [
    "Hmm, I didn't quite catch that. Try saying 'help' to see what I can do! 💡",
    "I'm not sure about that one, but try asking me for a joke, fact, or riddle! 🤖",
    "That's beyond my rules! Type 'help' to see my full menu of tricks. 📋",
    "Interesting! I don't have a rule for that yet. Try 'hello', 'joke', 'fact', or 'help'! 😊",
    "Yaar, yeh toh mere rules mein nahi hai. 'help' type karo aur dekho main kya kya kar sakta hoon! 🤖",
]

# Words/phrases that should end the conversation (used by CLI loop).
EXIT_KEYWORDS = ["bye", "goodbye", "exit", "quit", "good night", "adios", "farewell",
                 "alvida", "phir milenge", "chalo bye", "chal bye", "tata",
                 "shubh ratri", "bye bhai", "bye yaar", "gtg", "ttyl", "cya",
                 "gotta go", "got to go", "see ya", "peace out"]

# Build a flat list of all keywords for fuzzy matching
_ALL_KEYWORDS = []
for _rule in RULES:
    for _kw in _rule["keywords"]:
        _ALL_KEYWORDS.append(_kw)


# ---------------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def normalize(text: str) -> str:
    """Lowercase + strip the input so matching is consistent."""
    return text.strip().lower()


def is_exit_command(text: str) -> bool:
    """Check (via a loop) whether the user wants to end the chat."""
    cleaned = normalize(text)
    for word in EXIT_KEYWORDS:
        if _contains_keyword(cleaned, word):
            return True
    return False


def _contains_keyword(cleaned_text: str, keyword: str) -> bool:
    """
    Word-boundary aware "contains" check.
    Plain `keyword in text` would wrongly match short words like "hi" or "yo"
    as substrings of unrelated words (e.g. "yo" inside "your"). Using a regex
    word boundary (\\b) avoids that, while still allowing multi-word phrases
    like "how are you" to match normally.
    """
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return re.search(pattern, cleaned_text) is not None


def _match_rule(cleaned_text: str):
    """
    Loop over every rule and every keyword inside it.
    Returns the matching rule dict, or None if nothing matches.
    """
    for rule in RULES:                      # loop 1: over all rules
        for keyword in rule["keywords"]:     # loop 2: over keywords in a rule
            if _contains_keyword(cleaned_text, keyword):
                return rule
    return None


def _fuzzy_match(cleaned_text: str):
    """
    Use difflib to find the closest matching keyword when exact matching fails.
    This handles typos like 'helo' -> 'hello', 'jokee' -> 'joke', etc.
    Returns the matching rule dict, or None.
    """
    # Try matching the whole text first
    matches = get_close_matches(cleaned_text, _ALL_KEYWORDS, n=1, cutoff=0.75)
    if matches:
        matched_keyword = matches[0]
        for rule in RULES:
            if matched_keyword in rule["keywords"]:
                return rule

    # Also try matching individual words from the input
    words = cleaned_text.split()
    for word in words:
        if len(word) < 3:  # skip very short words for fuzzy
            continue
        matches = get_close_matches(word, _ALL_KEYWORDS, n=1, cutoff=0.8)
        if matches:
            matched_keyword = matches[0]
            for rule in RULES:
                if matched_keyword in rule["keywords"]:
                    return rule

    return None


# ---------------------------------------------------------------------------
# 3. MAIN ENTRY POINT (this is what the GUI / CLI calls)
# ---------------------------------------------------------------------------
def get_response(user_text: str) -> str:
    """
    Core rule-based decision function.
    Demonstrates if/elif/else clearly, plus delegates keyword scanning
    to helper loops above.
    """
    if not user_text or not user_text.strip():
        return "Please type something so I can respond! 🙂"

    cleaned = normalize(user_text)

    # --- dynamic word and letter analysis commands ------------------------
    # 1. Letter Counter: count letters in [word]
    count_match = re.search(r"(?:how many letters in|count letters in)\s+([a-zA-Z\-\'\s]+)", cleaned)
    if count_match:
        word = count_match.group(1).strip()
        count = sum(1 for c in word if c.isalpha())
        return f"The text '{word}' has {count} letter{'s' if count != 1 else ''}! 📝"

    # 2. Spelling: spell [word]
    spell_match = re.search(r"\bspell\s+([a-zA-Z\-\'\s]+)", cleaned)
    if spell_match:
        word = spell_match.group(1).strip()
        # Spell word by word if there are multiple words
        words = word.split()
        spelled_parts = []
        for w in words:
            spelled_parts.append("-".join(list(w.upper())))
        spelled = "   ".join(spelled_parts)
        return f"Sure! '{word}' is spelled: {spelled} 🔠"

    # 3. Word Reversing: reverse [word]
    reverse_match = re.search(r"\breverse\s+([a-zA-Z\-\'\s]+)", cleaned)
    if reverse_match:
        word = reverse_match.group(1).strip()
        reversed_word = word[::-1]
        return f"🔄 '{word}' spelled backwards is '{reversed_word}'!"

    # 4. Uppercasing: uppercase [word] / shout [word]
    upper_match = re.search(r"\b(?:uppercase|shout)\s+([a-zA-Z\-\'\s]+)", cleaned)
    if upper_match:
        word = upper_match.group(1).strip()
        return f"📢 {word.upper()}!"

    # --- a few direct, high-priority if/elif checks -----------------------
    if cleaned in ("hi", "hello", "hey", "namaste", "namaskar", "hii", "hiii", "helo", "helloo"):
        return random.choice(_rule_by_tag("greeting")["responses"])
    elif is_exit_command(cleaned):
        return random.choice(_rule_by_tag("bye")["responses"])
    elif "how are you" in cleaned or "kaise ho" in cleaned or "kya haal" in cleaned:
        return random.choice(_rule_by_tag("how_are_you")["responses"])
    else:
        # --- fall back to the general keyword-scanning rule table ---------
        rule = _match_rule(cleaned)
        if rule is not None:
            response = random.choice(rule["responses"])
            if response == "__TIME__":
                response = f"It's currently {datetime.now().strftime('%I:%M %p')}. ⏰"
            return response
        else:
            # --- try fuzzy matching for typos ---
            fuzzy_rule = _fuzzy_match(cleaned)
            if fuzzy_rule is not None:
                response = random.choice(fuzzy_rule["responses"])
                if response == "__TIME__":
                    response = f"It's currently {datetime.now().strftime('%I:%M %p')}. ⏰"
                return response
            else:
                return random.choice(FALLBACK_RESPONSES)


def _rule_by_tag(tag: str):
    """Small helper: fetch a rule dict by its tag name."""
    for rule in RULES:
        if rule["tag"] == tag:
            return rule
    return {"responses": FALLBACK_RESPONSES}  # safety net, should not happen


# ---------------------------------------------------------------------------
# Allow quick manual testing: `python chatbot_logic.py`
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tests = [
        # --- English ---
        "hello",
        "good morning",
        "who is your developer?",
        "how old are you?",
        "where do you live",
        "are you a real person?",
        "do you have feelings?",
        "tell me a riddle",
        "give me an interesting fact",
        "what can you do",
        "tell me a joke",
        "what is your favorite movie?",
        "do you like pizza?",
        "what is the meaning of life?",
        "count letters in supercalifragilisticexpialidocious",
        "spell python",
        "reverse chatbot",
        "uppercase hello world",
        # --- Common short inputs (previously broken) ---
        "ok",
        "yes",
        "no",
        "nice",
        "cool",
        "good",
        "bad",
        "what",
        "why",
        "how",
        "who",
        "where",
        "when",
        "please",
        "sorry",
        "test",
        "lol",
        "haha",
        "wow",
        "python",
        "coding",
        # --- Hinglish ---
        "namaste",
        "kya haal hai",
        "tera naam kya hai",
        "tujhe kisne banaya",
        "mazaak sunao",
        "paheli sunao",
        "kuch batao interesting",
        "biryani",
        "mausam kaisa hai",
        "main khush hoon",
        "bore ho raha hoon",
        "zindagi ka matlab",
        "gaana sunao",
        "cricket",
        "bharat",
        "sorry bhai",
        "sahi kaha",
        "tu toh kamaal hai",
        "exam hai",
        # --- Typos (fuzzy matching) ---
        "helo",
        "halp",
        "jokee",
        "thaks",
        "goodmorning",
        # --- Random ---
        "asdkjh",
        "alvida",
    ]
    for t in tests:
        print(f"User: {t}")
        print(f"Bot:  {get_response(t)}\n")
