import streamlit as st
import nltk
from nltk.corpus import words
import random
import string
import json

# --- 1. Password Generator Class Definitions ---
class RandomPasswordGenerator:
    def __init__(self, length=12, include_upper=True, include_lower=True, include_digits=True, include_symbols=False, exclude_similar=False, no_repeated=False):
        self.length = length
        self.include_upper = include_upper
        self.include_lower = include_lower
        self.include_digits = include_digits
        self.include_symbols = include_symbols
        self.exclude_similar = exclude_similar
        self.no_repeated = no_repeated

    def generate(self):
        chars = ""
        if self.include_upper: chars += string.ascii_uppercase
        if self.include_lower: chars += string.ascii_lowercase
        if self.include_digits: chars += string.digits
        if self.include_symbols: chars += string.punctuation

        if self.exclude_similar:
            for char in "Il1O0":
                chars = chars.replace(char, "")

        if not chars:
            raise ValueError("No character types selected!")

        if self.no_repeated and len(chars) < self.length:
             raise ValueError("Not enough unique characters for the requested length.")

        if self.no_repeated:
            return "".join(random.sample(chars, self.length))
        else:
            return "".join(random.choice(chars) for _ in range(self.length))

class MemorablePasswordGenerator:
    def __init__(self, no_of_words=4, separator='-', capitalization=True, vocabulary=None, suffix_length=0):
        self.no_of_words = no_of_words
        self.separator = separator
        self.capitalization = capitalization
        self.vocabulary = vocabulary if vocabulary else ["apple", "banana", "cherry"]
        self.suffix_length = suffix_length

    def generate(self):
        filtered_vocab = [w for w in self.vocabulary if 3 < len(w) < 8]
        if not filtered_vocab:
            filtered_vocab = self.vocabulary

        selected_words = random.sample(filtered_vocab, self.no_of_words)
        
        if self.capitalization:
            selected_words = [w.capitalize() for w in selected_words]
        else:
            selected_words = [w.lower() for w in selected_words]
            
        password = self.separator.join(selected_words)
        
        if self.suffix_length > 0:
            suffix = "".join(random.choices(string.digits, k=self.suffix_length))
            password += suffix
            
        return password

class PinCodeGenerator:
    def __init__(self, length=4):
        self.length = length

    def generate(self):
        return "".join(random.choices(string.digits, k=self.length))


# --- 2. Page Config and State ---
st.set_page_config(page_title="Password Generator", page_icon=":zap:", layout="centered")

if "generator" not in st.session_state:
    st.session_state.generator = None
if "password" not in st.session_state:
    st.session_state.password = None
if "password_history" not in st.session_state:
    st.session_state.password_history = []
if "last_option" not in st.session_state:
    st.session_state.last_option = None

# --- 3. CSS Styles ---
def apply_dark_mode():
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }
        h1, h2, h3, p, label, span, div, li {
            color: #FAFAFA !important;
        }
        code {
            background-color: #262730 !important;
            color: #ff4b4b !important;
        }
        .stRadio div[role='radiogroup'] label {
            color: #FAFAFA !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

apply_dark_mode()

# --- 4. Helper Functions ---
def compute_strength(pw: str) -> tuple[int, str]:
    if not pw: return 0, "Weak"
    length = len(pw)
    has_upper = any(c.isupper() for c in pw)
    has_lower = any(c.islower() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_symbol = any((not c.isalnum()) for c in pw)
    
    length_score = min(length - 4, 16) / 16 * 40 if length > 4 else 0
    classes = sum([has_upper, has_lower, has_digit, has_symbol])
    diversity_score = (classes / 4) * 40
    
    bonus = 20 if (has_digit and has_symbol) else (10 if (has_digit or has_symbol) else 0)
    score = int(min(100, round(length_score + diversity_score + bonus)))
    
    if score < 40: label = "Weak"
    elif score < 60: label = "Medium"
    elif score < 80: label = "Strong"
    else: label = "Very Strong"
    
    return score, label

@st.cache_data
def load_words():
    try:
        return words.words()
    except LookupError:
        nltk.download('words')
        return words.words()

# --- 5. User Interface ---
try:
    st.image('./images/banner.jpeg', use_container_width=True)
except:
    pass 

st.title(":zap: Password Generator")

option = st.radio("Password Type", ('Random Password', 'Memorable Password', 'Pin Code'), horizontal=True)

if st.session_state.last_option != option:
    st.session_state.password = None
    st.session_state.last_option = option

# --- 6. Selection Logic ---
if option == 'Random Password':
    length = st.slider("Length", min_value=5, max_value=50, value=12)
    st.write("**Character Types:**")
    c1, c2 = st.columns(2)
    with c1:
        inc_upper = st.checkbox("Uppercase (A–Z)", value=True)
        inc_num = st.checkbox("Numbers (0–9)", value=True)
    with c2:
        inc_lower = st.checkbox("Lowercase (a–z)", value=True)
        inc_sym = st.checkbox("Symbols (!@#...)", value=False)
    
    exc_sim = st.checkbox("Exclude similar (O, 0, l, 1, I)", value=False)
    no_rep = st.toggle("No Repeated Characters", value=False)

    if not (inc_upper or inc_lower or inc_num or inc_sym):
        st.warning("⚠️ Please select at least one character type!")
        st.session_state.generator = None
    else:
        st.session_state.generator = RandomPasswordGenerator(length, inc_upper, inc_lower, inc_num, inc_sym, exc_sim, no_rep)

elif option == 'Memorable Password':
    no_of_words = st.slider("Number of Words", 2, 10, 4)
    c1, c2 = st.columns(2)
    with c1:
        sep = st.text_input("Separator", value='-', max_chars=1)
    with c2:
        cap = st.checkbox("Capitalize words", value=True)
        suf = st.number_input("Suffix length", 0, 6, 0)

    word_list = load_words()
    st.session_state.generator = MemorablePasswordGenerator(no_of_words, sep, cap, word_list, suf)

else: # Pin Code
    length = st.slider("Length", 2, 50, 20)
    st.session_state.generator = PinCodeGenerator(length)

# --- 7. Generate and Display Button ---
if st.button("Generate New Password", type="primary"):
    if st.session_state.generator:
        try:
            new_pw = st.session_state.generator.generate()
            st.session_state.password = new_pw
            st.session_state.password_history.append(new_pw)
            st.rerun()
        except ValueError as e:
            st.error(f"❌ {str(e)}")

# If password is empty but generator exists (first run), generate one
if st.session_state.password is None and st.session_state.generator:
    try:
        init_pw = st.session_state.generator.generate()
        st.session_state.password = init_pw
        st.session_state.password_history.append(init_pw)
    except ValueError:
        pass

# Display Output
if st.session_state.password:
    pw = st.session_state.password
    st.write("Your password is:")
    st.code(pw, language=None)

    score, label = compute_strength(pw)
    emoji_map = {"Weak": "🔴", "Medium": "🟠", "Strong": "🟡", "Very Strong": "🟢"}
    
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown(f"<h4>{emoji_map.get(label)} {label}</h4>", unsafe_allow_html=True)
    with c2:
        st.progress(score / 100)

st.write("---")

with st.expander("⬇️ Download and Save Generated Password"):
    st.write("""
    After generating a password, you can download it.

    🔹 Download as TXT  
    Only the password itself is saved in a simple text file.

    🔹 Download as JSON  
    The password, along with its type and strength (score and security level), is saved in a JSON file.
    """)

    # --- Fix for repeated download bug ---
    if st.session_state.password:
        # Get password directly from session to avoid losing variable on rerun
        current_password = st.session_state.password
        
        # Recompute info for JSON to ensure data integrity
        current_score, current_label = compute_strength(current_password)
        
        # Prepare JSON content
        json_payload = {
            "password": current_password, 
            "type": option, 
            "strength": {"score": current_score, "label": current_label}
        }
        json_str_data = json.dumps(json_payload, ensure_ascii=False, indent=2)

        # Display buttons
        e1, e2 = st.columns(2)
        with e1:
            st.download_button(
                label="Download as TXT",
                data=current_password,
                file_name="password.txt",
                mime="text/plain",
                key="download_txt_btn"
            )
        with e2:
            st.download_button(
                label="Download as JSON",
                data=json_str_data,
                file_name="password.json",
                mime="application/json",
                key="download_json_btn"
            )
    else:
        st.info("⚠️ No password generated yet.")

st.write("---")
with st.expander("📖 Guide: Password Types, Privacy & Security"):
    st.markdown("""
    ### 🛡️ Why do you need this tool?
    Using repeated or simple passwords (like `123456` or `password`) is the biggest security risk for your accounts. This app helps you create passwords that **mathematics** makes unbreakable.

    ---

    ### ⚙️ Password Types in this App

    #### 1. Random Password
    This type offers the **highest security**.
    *   **Usage:** Suitable for sensitive accounts (like email, banking, crypto exchanges) where you will store the password in a Password Manager.
    *   **Feature:** These are a mix of uppercase, lowercase, numbers, and symbols with no predictable pattern. Even the most powerful computers would need centuries to crack them.

    #### 2. Memorable Password
    This method works based on a modern security theory (known as the XKCD method).
    *   **Usage:** Suitable for places where you need to type the password and remember it (like Windows login or phone unlock).
    *   **Logic:** Humans are much better at memorizing meaningful words (like `Apple-Sun-Beach`) than random strings (like `x9#mP2`).
    *   **Security:** The security lies in the **length**. 4 random words combined become so long that guessing them is practically impossible.

    #### 3. Pin Code
    *   **Usage:** Specific for bank cards, phone locks, or digital safes that only accept numbers.

    ---

    ### 🔒 Your Privacy and Security
    *   **No Storage:** The most important feature of this app is that **none** of the generated passwords are saved on any server or database.
    *   **Instant Oblivion:** As soon as you close the page or refresh, the generated passwords are wiped from the system memory forever.
    *   **Secure Download:** The download files (TXT or JSON) are created for you at that exact moment, and no copy remains with us.
    """)