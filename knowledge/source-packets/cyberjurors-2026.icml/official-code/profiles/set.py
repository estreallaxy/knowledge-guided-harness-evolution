# This set includes first_name, last_name, status, trait and interest
import random
# different combinations of first name and last name, to generate agents' name
First_Name =  ["Liam", "Emma", "Noah", "Olivia", "Oliver", "Ava", "Elijah", "Sophia", "James", "Isabella", "William", "Mia", "Benjamin", "Amelia", "Lucas", 
               "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Jackson", "Ella", "Sebastian", "Scarlett", "Daniel", "Grace", "Matthew", "Chloe", 
               "Aiden", "Lily", "Samuel", "Aria", "David", "Zoe", "Joseph", "Stella", "Carter", "Aurora", "Gabriel", "Natalie", "Anthony", "Addison", 
               "Isaac", "Lucy", "Dylan", "Layla", "Luke", "Hannah", "Christopher", "Mila", "Andrew", "Ellie", "Joshua", "Bella", "Thomas", "Claire", 
               "Caleb", "Sadie", "Ryan", "Aaliyah", "Nathan", "Skylar", "Christian", "Victoria", "Hunter", "Nora", "Leo", "Hannah", "Aaron", "Natalie", 
               "Adrian", "Lucy", "Isaac", "Lily", "Jonathan", "Stella", "Eli", "Grace", "Thomas", "Audrey", "Charles", "Samantha", "Josiah", "Mila", 
               "Asher", "Brooklyn", "Jaxon", "Sarah", "Adam", "Leah", "Miles", "Kinsley", "Weston", "Rylee", "Jeremiah", "Gianna", "Nolan", "Peyton", 
               "Jesse", "Clara", "Ian", "Eliana", "Theo", "Madeline", "Soren", "Genesis", "Paul", "Jade", "Zachary", "Lydia", "Silas", "Savannah", "Eli", 
               "Addison", "Ezekiel", "Makayla", "Griffin", "Hadley", "Kyle", "Aurora", "Cooper", "Evangeline", "Damian", "Sophie", "Quentin", "Iris", 
               "Leonard", "Sienna", "Felix", "Ruby", "Brooks", "Poppy", "Felix", "Dahlia", "Carter", "Bella", "Bentley", "Willow", "Harrison", "Jade", 
               "Finn", "Eden", "Hudson", "Freya", "Orion", "Cora", "Rex", "Emilia", "Zane", "Isla", "Tobias", "Lila", "Jasper", "Clara", "Solomon", "Julia", 
               "Micah", "Tessa", "Ivan", "Autumn", "Peter", "Raina", "Warren", "Eliza", "Mitchell", "Mariana", "Arthur", "Lacey", "Reid", "Nia", "Finn", 
               "Adeline", "Hugo", "Maeve", "Oscar", "Ophelia", "Palmer", "Alina", "Jett", "Zara", "Carter", "Amelia", "Felix", "Autumn", "Quinn", "Sydney", 
               "Leo", "Harper", "Damon", "Lucia", "Darius", "Niamh", "Colton", "Marley", "Grant", "Delilah", "Everett", "Ximena", "Nash", "Callie", 
               "Dallas", "Rhea", "Caden", "Selah", "Malik", "Camila", "Jax", "Elodie", "Ty", "Giselle", "Emmett", "Zara", "Kingston", "Liana", "Finnian", 
               "Thea", "Zander", "Kiera", "Apollo", "Verity", "Graham", "Aria", "Jaxson", "Simone", "Ryker", "Delaney", "Callan", "Cambria", "Lennox", 
               "Autumn", "Nash", "Zara", "Stetson", "Danica", "Gideon", "Mira", "Orion", "Avery", "Dax", "Raegan", "Khalil", "Skylar", "Kellan", "Sloane", 
               "Rowan", "Tatum", "Trenton", "Amara", "Marcellus", "Juniper", "Kade", "Lyric", "Micah", "Samara", "Eli", "Maris", "Barrett", "Nevaeh", 
               "Dorian", "Hayley", "Beckett", "Anaya", "Kellan", "Pearl", "Carter", "Sage", "Harlow", "Finn", "Selene", "Miles", "Danika", "Rocco", "Amira", 
               "Ryker", "Mabel", "Gideon", "Dahlia", "Ryder", "Brinley", "Zeke", "Gemma", "Jalen", "Lucia", "Cassian", "Sage", "Quinn", "Landon", "Iris", 
               "Jasper", "Elowen", "Silas", "Marlowe", "Ashton", "Lila", "Wren", "Niko", "Zara", "Orion", "Briar", "Tate", "Callan", "Journey", "Cruz", 
               "Kaylee", "Hudson", "Aisling", "Braxton", "Freya", "Emerson", "Amaya", "Rhys", "Tilly", "Finnian", "Calliope", "Quentin", "Zara", "Finley", 
               "Hattie", "Quincy", "Novah"]

Last_Name =   ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", 
               "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", 
               "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", 
               "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", 
               "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", 
               "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins", 
               "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler", "Simmons", "Foster", "Gonzales", "Bryant", "Alexander", 
               "Russell", "Griffin", "Diaz", "Hayes", "Myers", "Ford", "Hamilton", "Graham", "Sullivan", "Wallace", "Woods", "Cole", "West", "Jordan", 
               "Owens", "Reynolds", "Fisher", "Ellis", "Harrison", "Gibson", "McDonald", "Cruz", "Marshall", "Ortiz", "Gomez", "Murray", "Freeman", "Wells", 
               "Webb", "Simpson", "Stevens", "Tucker", "Porter", "Hunter", "Hicks", "Crawford", "Henry", "Boyd", "Mason", "Morales", "Kennedy", "Warren", 
               "Dixon", "Ramos", "Reyes", "Burns", "Gordon", "Shaw", "Holmes", "Rice", "Robertson", "Hunt", "Black", "Daniels", "Palmer", "Mills", "Nichols", 
               "Grant", "Knight", "Ferguson", "Rose", "Stone", "Hawkins", "Dunn", "Perkins", "Hudson", "Spencer", "Gardner", "Stephens", "Payne", "Pierce", 
               "Berry", "Matthews", "Arnold", "Wagner", "Willis", "Ray", "Watkins", "Oliver", "Duncan", "Snyder", "Hart", "Cunningham", "Bradley", "Lane", 
               "Andrews", "Ruiz", "Harper", "Fox", "Riley", "Armstrong", "Carpenter", "Weaver", "Greene", "Lawrence", "Elliott", "Chavez", "Sims", "Austin", 
               "Peters", "Kelley", "Franklin", "Lawson", "Fields", "Gutierrez", "Ryan", "Schmidt", "Carr", "Vasquez", "Castillo", "Wheeler", "Chapman", 
               "Oliver", "Montgomery", "Richards", "Williamson", "Johnston", "Banks", "Meyer", "Bishop", "McCoy", "Howell", "Alvarez", "Morrison", "Hansen", 
               "Fernandez", "Garza", "Harvey", "Little", "Burton", "Stanley", "Nguyen", "George", "Jacobs", "Reid", "Kim", "Fuller", "Lynch", "Dean", 
               "Gilbert", "Garrett", "Romero", "Welch", "Larson", "Frazier", "Burke", "Hanson", "Day", "Mendoza", "Moreno", "Bowman", "Medina", "Fowler", 
               "Brewer", "Hoffman", "Carlson", "Silva", "Pearson", "Holland", "Douglas", "Fleming", "Jensen", "Vargas", "Byrd", "Davidson", "Hopkins", "May", 
               "Terry", "Herrera", "Wade", "Soto", "Walters", "Curtis", "Neal", "Caldwell", "Lowe", "Jennings", "Barnett", "Graves", "Jimenez", "Horton", 
               "Shelton", "Barrett", "O'Brien", "Castro", "Sutton", "Gregory", "McKinney", "Lucas", "Miles", "Craig", "Rodriquez", "Chambers", "Holt", 
               "Lambert", "Fletcher", "Watts", "Bates", "Hale", "Rhodes", "Pena", "Beck", "Newman", "Haynes", "McDaniel", "Mendez", "Bush", "Vaughn", "Parks", 
               "Dawson", "Santiago", "Norris", "Harding", "McGrath", "Swanson", "Barber", "Acosta", "Luna", "Cooke", "Gross", "Brady", "Huffman", "Jaramillo", 
               "Browning"]

# to generate agents' statuses
Status = {
    "Arts": ["Artist", "Musician", "Actor", "Sculptor", "Photographer", "Graphic Designer", "Dancer", "Writer", "Filmmaker", "Curator"],

	"Business": ["Entrepreneur", "Business Analyst", "Financial Manager", "Marketing Specialist", "Operations Manager", "Sales Executive", "Consultant", "Project Manager", "Human Resources Manager", "Accountant"],

	"Communications": ["Public Relations Specialist", "Journalist", "Content Writer", "Social Media Manager", "Editor", "Copywriter", "Communications Director", "Speechwriter", "Broadcast Journalist", "Advertising Executive"],

	"Education": ["Student", "Professor", "Educational Administrator", "Curriculum Developer", "School Counselor", "Librarian", "Special Education Teacher", "Instructional Designer", "Tutor", "Education Policy Analyst"],

	"Healthcare": ["Physician", "Nurse", "Pharmacist", "Physical Therapist", "Occupational Therapist", "Radiologic Technologist", "Medical Researcher", "Health Educator", "Dental Hygienist", "Physician Assistant"],

	"Hospitality": ["Hotel Manager", "Chef", "Event Planner", "Front Desk Associate", "Bartender", "Travel Agent", "Restaurant Manager", "Tour Guide", "Concierge", "Housekeeping Supervisor"],

	"Information Technology": ["Software Developer", "System Administrator", "Data Analyst", "IT Support Specialist", "Network Engineer", "Cybersecurity Analyst", "Web Developer", "Database Administrator", "Cloud Engineer", "UX/UI Designer"],

	"Law Enforcement": ["Police Officer", "Detective", "Criminal Investigator", "Forensic Analyst", "Correctional Officer", "Security Consultant", "Crime Scene Technician", "Community Liaison Officer", "Federal Agent", "Dispatcher"],

	"Sales and Marketing": ["Sales Manager", "Brand Strategist", "Market Research Analyst", "Digital Marketing Specialist", "Account Executive", "SEO Specialist", "Product Manager", "Customer Service Representative", "Promotions Coordinator", "Trade Show Manager"],

	"Science": ["Research Scientist", "Lab Technician", "Environmental Scientist", "Biologist", "Chemist", "Physicist", "Data Scientist", "Astronomer", "Geologist", "Marine Biologist"],

	"Transportation": ["Truck Driver", "Airline Pilot", "Logistics Coordinator", "Transportation Planner", "Rail Operator", "Shipping Manager", "Fleet Manager", "Traffic Engineer", "Air Traffic Controller", "Delivery Driver"]
}

# to generate agents' traits
Trait = [
            {
                "Extraversion": ["outgoing", "sociable", "energetic", "talkative", "assertive", "enthusiastic", "adventurous", "friendly", "confident", "lively"],
                "Introversion": ["reserved", "shy", "quiet", "withdrawn", "solitary", "reflective", "reclusive", "unassertive", "inhibited", "taciturn"]
            },

            {
                "Emotional Stability": ["calm", "composed", "resilient", "steady", "balanced", "secure", "relaxed", "grounded", "unflappable", "level-headed"],
                "Emotional Instability": ["anxious", "moody", "impulsive", "insecure", "irritable", "sensitive", "reactive", "unpredictable", "neurotic", "volatile"]
            },

            {
                "Agreeableness": ["kind", "compassionate", "cooperative", "friendly", "warm", "empathetic", "considerate", "generous", "trustworthy", "understanding"],
                "Disagreeableness":["hostile", "selfish", "critical", "argumentative", "stubborn", "distrustful", "rude", "uncooperative", "unsympathetic", "intolerant"]
            },

            {
                "Conscientiousness": ["organized", "responsible", "diligent", "disciplined", "reliable", "detail-oriented", "methodical", "thorough", "efficient", "punctual"],
                "Unconscientiousness": ["careless", "lazy", "irresponsible", "unreliable", "disorganized", "forgetful", "negligent", "indifferent", "unmotivated", "procrastinating"]
            },
            
            {
                "Openness": ["creative", "curious", "imaginative", "innovative", "open-minded", "unconventional", "original", "versatile", "adventurous", "broad-minded"],
                "Closed-mindedness":["rigid", "traditional", "unimaginative", "dogmatic", "narrow-minded", "conventional", "prejudiced", "resistant", "apathetic", "inflexible"]
            }
        ]

# to generate agents' interest
Interest = [
                {
                    "Extraversion": ['dancing', 'socializing', 'hiking', 'partying', 'traveling', 'volunteering', 'running', 'cooking', 'shopping', 'attending concerts', 'hosting events', 'joining clubs', 'playing team sports', 'attending festivals', 'going to parties', 'networking', 'meeting new people', 'exploring new places', 'attending meetups', 'participating in group activities'], 
                    "Introversion": ['reading', 'writing', 'meditating', 'gardening', 'drawing', 'journaling', 'watching movies', 'playing single-player games', 'solving puzzles', 'birdwatching', 'studying', 'listening to music', 'knitting', 'baking', 'walking alone', 'researching topics', 'practicing instruments', 'stargazing', 'learning languages', 'organizing personal spaces'] 
                },
                {
                    "Emotional Stability": ['yoga', 'meditation', 'painting', 'gardening', 'journaling', 'photography', 'fishing', 'cooking', 'reading', 'hiking', 'running', 'swimming', 'knitting', 'listening to music', 'watching movies', 'birdwatching', 'stargazing', 'nature walks', 'baking', 'playing musical instruments'], 
                    "Emotional Instability": ['journaling emotions', 'abstract art', 'poetry', 'melancholic music', 'creating mood boards', 'drama', 'movies', 'doing intense workouts', 'exploring mindfulness techniques', 'video games', 'attending support groups', 'adrenaline sports', 'keeping a dream journal', 'blogging about feelings', 'following mood-boosting routines', 'aromatherapy', 'crafts', 'taking personality quizzes', 'making vision boards', 'watching motivational talks']
                },  
                {
                    "Agreeableness": ['volunteering', 'helping others', 'community service', 'teaching', 'mentoring', 'counseling', 'supporting charities', 'fundraising', 'organizing events', 'collaborating on projects', 'participating in group activities', 'attending community meetings', 'joining social causes', 'advocating for others', 'mediating conflicts', 'promoting positivity', 'building relationships', 'encouraging teamwork', 'spreading kindness', 'empowering others'], 
                    "Disagreeableness": ['debating topics', 'strategy games', 'philosophy', 'competitive sports', 'writing critiques', 'courtroom dramas', 'martial arts', 'joining debate clubs', 'researching controversial issues', 'building arguments', 'creating satirical content', 'writing opinion pieces', 'analyzing political ideologies', 'engaging in intellectual discussions', 'exploring conspiracy theories', 'solo sports', 'studying negotiation techniques', 'chess strategies', 'reviewing products critically', 'dissecting movies and books']
                },
                {
                    "Conscientiousness": ['planning', 'organizing', 'goal setting', 'time management', 'budgeting', 'studying', 'researching', 'learning new skills', 'improving efficiency', 'following routines', 'maintaining cleanliness', 'documenting progress', 'setting priorities', 'tracking progress', 'creating schedules', 'developing strategies', 'analyzing data', 'implementing systems', 'completing tasks', 'meeting deadlines'], 
                    "Unconscientiousness": ['binge-watching series', 'casual games', 'hanging out aimlessly', 'exploring social media', 'impulse shopping', 'trying random hobbies', 'sketching freely', 'procrastinating projects', 'daydreaming', 'attending spontaneous events', 'watching reality shows', 'going to arcades', 'trying street food', 'visiting amusement parks', 'party games', 'exploring memes', 'comedy shows', 'DIY projects', 'freestyling in music', 'spontaneous photography']
                },  
                {  
                    "Openness": ['exploring', 'experimenting', 'creating art', 'writing', 'inventing', 'designing', 'new languages', 'new cultures', 'attending workshops', 'diverse literature', 'new cuisines', 'different philosophies', 'debates', 'attending lectures', 'exploring music genres', 'new technology', 'participating in hackathons', 'visiting museums', 'attending art galleries', 'virtual reality'],
                    "Closed-mindedness": ['antiques', 'traditions', 'local history', 'classic movies', 'reading biographies', 'baking traditional recipes', 'attending religious gatherings', 'joining cultural clubs', 'learning family crafts', 'folk music', 'exploring genealogy', 'watching documentaries', 'visiting historical landmarks', 'gardening heirloom plants', 'crafting with natural materials', 'reading classic literature', 'attending local fairs', 'learning calligraphy', 'volunteering in heritage preservation', 'writing letters']
                }
        ]
# Interest = {key: [item.lower() for item in value] for key, value in Interest.items()}
# print(Interest)


