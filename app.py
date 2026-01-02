import streamlit as st
import edge_tts
import asyncio
import pygame
import hashlib
import tempfile
import random
from pathlib import Path
import re
import json
import threading
import time
import uuid

# -----------------------------
# Configuration
# -----------------------------
LISTS_DIR = Path(__file__).parent / "lists"
CACHE_DIR = Path(__file__).parent / "tts_cache"
CACHE_DIR.mkdir(exist_ok=True)

# -----------------------------
# Custom CSS with Dark Animated Background
# -----------------------------
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Fredoka+One&display=swap');
    
    /* Dark Animated Background */
    body, .stApp {
        margin: 0;
        padding: 0;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Animated gradient background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(-45deg, 
            #0a0a2a 0%, 
            #1a0033 25%, 
            #0d1b2a 50%, 
            #001524 75%, 
            #000814 100%);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        z-index: -2;
    }
    
    /* Particle overlay for depth */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(120, 219, 255, 0.1) 0%, transparent 50%);
        z-index: -1;
        pointer-events: none;
    }
    
    @keyframes gradientBG {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    /* Floating particles animation */
    .floating-particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        overflow: hidden;
    }
    
    .particle {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
        animation: float linear infinite;
    }
    
    @keyframes float {
        0% {
            transform: translateY(100vh) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 0.3;
        }
        90% {
            opacity: 0.3;
        }
        100% {
            transform: translateY(-100px) rotate(360deg);
            opacity: 0;
        }
    }
    
    /* Dark theme variables - Enhanced for animated background */
    :root {
        --primary: #818cf8;
        --primary-light: #a5b4fc;
        --secondary: #34d399;
        --secondary-light: #6ee7b7;
        --accent: #fbbf24;
        --danger: #f87171;
        --success: #34d399;
        --warning: #fbbf24;
        --dark-bg: rgba(15, 23, 42, 0.85);
        --dark-card: rgba(30, 41, 59, 0.9);
        --dark-text: #f1f5f9;
        --dark-border: rgba(51, 65, 85, 0.5);
        --dark-muted: #94a3b8;
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        --glow: 0 0 20px rgba(129, 140, 248, 0.4);
        --glass-effect: rgba(255, 255, 255, 0.05);
    }
    
    /* Base styles with glass effect */
    .stApp {
        background: transparent !important;
        font-family: 'Fredoka One', cursive;
        color: var(--dark-text);
        backdrop-filter: blur(10px);
    }
    
    /* Main container with glass morphism */
    .main {
        background: var(--dark-card);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 1rem auto;
        max-width: 1200px;
        border: 1px solid var(--dark-border);
        box-shadow: var(--shadow);
        position: relative;
        backdrop-filter: blur(10px);
        background: linear-gradient(
            135deg,
            rgba(30, 41, 59, 0.9) 0%,
            rgba(30, 41, 59, 0.7) 100%
        );
    }
    
    /* Glass border effect */
    .main::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 24px;
        padding: 2px;
        background: linear-gradient(
            135deg,
            rgba(129, 140, 248, 0.3),
            rgba(52, 211, 153, 0.3)
        );
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        color: var(--dark-text) !important;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    h1 {
        color: var(--primary-light) !important;
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
    }
    
    /* Buttons - Enhanced for dark theme */
    .stButton > button {
        font-family: 'Orbitron', sans-serif;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1.5rem;
        margin: 0.25rem;
        transition: all 0.3s ease;
        color: white !important;
        font-size: 0.9rem;
        box-sizing: border-box;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
        );
        transition: 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--glow);
    }
    
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    /* Button colors with glow effects */
    .stButton > button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, var(--secondary), var(--secondary-light)) !important;
        color: white !important;
        border: 1px solid rgba(52, 211, 153, 0.3) !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
        color: white !important;
        border: 2px solid var(--primary) !important;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.5) !important;
    }
    
    /* Check Answer button - EXTRA PROMINENT */
    .stButton > button:contains("✅ Check Answer") {
        border: 3px solid #10b981 !important;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.7) !important;
        position: relative;
        animation: pulse-glow 2s infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { 
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.6) !important;
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 0 35px rgba(16, 185, 129, 0.9) !important;
            transform: scale(1.02);
        }
    }
    
    /* Word display - Enhanced for dark theme */
    .word-display {
        font-family: 'Orbitron', monospace;
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: 0.5rem;
        text-align: center;
        padding: 2rem;
        margin: 2rem 0;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 20px;
        border: 3px solid var(--primary);
        box-shadow: var(--shadow);
        color: var(--dark-text) !important;
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        backdrop-filter: blur(5px);
        text-shadow: 0 0 10px rgba(129, 140, 248, 0.3);
    }
    
    .word-display.correct {
        border-color: var(--success);
        color: var(--success) !important;
        box-shadow: 0 0 30px rgba(52, 211, 153, 0.4);
        text-shadow: 0 0 10px rgba(52, 211, 153, 0.3);
    }
    
    .word-display.incorrect {
        border-color: var(--warning);
        color: var(--warning) !important;
        box-shadow: 0 0 30px rgba(251, 191, 36, 0.4);
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.3);
    }
    
    .word-display.revealed {
        border-color: var(--danger);
        color: var(--danger) !important;
        box-shadow: 0 0 30px rgba(248, 113, 113, 0.4);
        text-shadow: 0 0 10px rgba(248, 113, 113, 0.3);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--secondary), var(--primary));
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(129, 140, 248, 0.3);
    }
    
    /* Input field */
    .stTextInput > div > div > input {
        font-family: 'Fredoka One', cursive;
        font-size: 1.3rem;
        border-radius: 12px;
        border: 2px solid var(--dark-border);
        padding: 0.9rem 1rem;
        background: rgba(15, 23, 42, 0.7);
        color: var(--dark-text);
        transition: all 0.3s ease;
        height: 60px;
        backdrop-filter: blur(5px);
    }
    
    .dark-mode .stTextInput > div > div > input {
        border-color: var(--light-border);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        outline: none;
    }
    
    /* Input field placeholder - Better fitting */
    .stTextInput > div > div > input::placeholder {
        font-family: 'Fredoka One', cursive;
        color: var(--dark-muted);
        font-size: 1.1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--dark-card) !important;
        border-right: 1px solid var(--dark-border);
        backdrop-filter: blur(10px);
    }
    
    section[data-testid="stSidebar"] * {
        color: var(--dark-text) !important;
    }
    
    /* Metrics */
    .stMetric {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid var(--dark-border);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(5px);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 12px;
        border: 1px solid var(--dark-border);
        background: rgba(30, 41, 59, 0.8) !important;
        color: var(--dark-text) !important;
        backdrop-filter: blur(5px);
    }
    
    /* Form elements */
    .stCheckbox label,
    .stRadio label,
    .stSelectbox label,
    .stSlider label {
        color: var(--dark-text) !important;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--dark-card);
        color: var(--dark-text) !important;
        border: 1px solid var(--dark-border);
        border-radius: 8px;
    }
    
    .streamlit-expanderContent {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid var(--dark-border);
        border-top: none;
        border-radius: 0 0 8px 8px;
    }
    
    /* Captions */
    .stCaption {
        color: var(--dark-muted) !important;
    }
    
    /* Divider */
    hr {
        border-color: var(--dark-border) !important;
        margin: 2rem 0 !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--dark-border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }
    
    /* Toggle button styling */
    .stCheckbox label div {
        background: var(--dark-card) !important;
        border: 1px solid var(--dark-border) !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# Floating Particles Animation
# -----------------------------
def floating_particles_animation():
    return """
    <div class="floating-particles" id="particles-container"></div>
    
    <script>
    function createParticles() {
        const container = document.getElementById('particles-container');
        const particleCount = 30;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random size between 1px and 4px
            const size = Math.random() * 3 + 1;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            // Random starting position
            particle.style.left = `${Math.random() * 100}%`;
            
            // Random animation duration between 15s and 30s
            const duration = Math.random() * 15 + 15;
            particle.style.animationDuration = `${duration}s`;
            
            // Random delay
            particle.style.animationDelay = `${Math.random() * 5}s`;
            
            // Random color (subtle blues and purples)
            const colors = [
                'rgba(129, 140, 248, 0.3)',
                'rgba(120, 119, 198, 0.3)',
                'rgba(52, 211, 153, 0.2)',
                'rgba(251, 191, 36, 0.2)'
            ];
            particle.style.background = colors[Math.floor(Math.random() * colors.length)];
            particle.style.boxShadow = `0 0 ${size * 3}px currentColor`;
            
            container.appendChild(particle);
        }
    }
    
    // Create particles when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createParticles);
    } else {
        createParticles();
    }
    
    // Recreate particles on page navigation (for Streamlit)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                const particlesContainer = document.getElementById('particles-container');
                if (!particlesContainer || particlesContainer.children.length < 10) {
                    const oldContainer = document.querySelector('.floating-particles');
                    if (oldContainer) oldContainer.remove();
                    createParticles();
                }
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """

# ============================================================================
# LOCKED SECTION: Context Functionality - DO NOT MODIFY
# ============================================================================
# -----------------------------
# Audio Player with Caching (UNCHANGED - CONTEXT FUNCTIONALITY PRESERVED)
# -----------------------------
class TTSCacheManager:
    def __init__(self):
        self.cache_info_file = CACHE_DIR / "cache_info.json"
        self.cache_info = self._load_cache_info()
        self.pygame_initialized = False
        # CHANGED: Set US Male as default
        self.voice = "en-US-GuyNeural"
        self._init_pygame_once()
        
    def _load_cache_info(self):
        if self.cache_info_file.exists():
            try:
                with open(self.cache_info_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache_info(self):
        with open(self.cache_info_file, 'w') as f:
            json.dump(self.cache_info, f, indent=2)
    
    def _get_cache_key(self, text):
        text_hash = hashlib.md5(f"{self.voice}_{text}".encode()).hexdigest()
        return text_hash[:16]
    
    def _init_pygame_once(self):
        if not self.pygame_initialized:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.set_num_channels(8)
                self.pygame_initialized = True
            except Exception as e:
                st.warning(f"Audio init failed: {e}")
    
    async def _generate_audio(self, text):
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                temp_file = f.name
                await communicate.save(temp_file)
            return temp_file
        except Exception as e:
            print(f"TTS generation failed: {e}")
            return None
    
    def _play_audio(self, audio_file):
        try:
            sound = pygame.mixer.Sound(audio_file)
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound)
            else:
                sound.play()
            return True
        except Exception as e:
            print(f"Audio play failed: {e}")
            return False
    
    def speak(self, text):
        if not text or not self.pygame_initialized:
            return False
            
        cache_key = self._get_cache_key(text)
        cache_file = CACHE_DIR / f"{cache_key}.mp3"
        
        if cache_file.exists():
            return self._play_audio(str(cache_file))
        
        try:
            temp_file = asyncio.run(self._generate_audio(text))
            if temp_file and Path(temp_file).exists():
                import shutil
                shutil.move(temp_file, cache_file)
                self.cache_info[cache_key] = {
                    'text': text,
                    'voice': self.voice,
                    'created': time.time()
                }
                self._save_cache_info()
                return self._play_audio(str(cache_file))
        except Exception as e:
            print(f"Audio generation/play failed: {e}")
        
        return False
    
    def speak_async(self, text):
        if not text:
            return
        threading.Thread(target=self.speak, args=(text,), daemon=True).start()

# -----------------------------
# Data Loading (UNCHANGED - CONTEXT FUNCTIONALITY PRESERVED)
# -----------------------------
def load_spelling_list(grade_file: Path):
    words = []
    with open(grade_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Check if line has context separator
            if "|" in line:
                parts = line.split("|", 1)
                word_raw = parts[0].strip()
                context = parts[1].strip()
            else:
                word_raw = line
                context = ""  # Empty context if not provided
                
            # Remove non-letter/apostrophe/hyphen from start/end
            word = re.sub(r"^[^a-zA-Z'-]+|[^a-zA-Z'-]+$", "", word_raw).lower()
            if len(word) >= 1:
                words.append({"word": word, "context": context})
    return words

# ============================================================================
# END LOCKED SECTION
# ============================================================================

# -----------------------------
# Session Save/Load System (UNCHANGED)
# -----------------------------
def save_current_session():
    """Save current session to browser storage"""
    try:
        user_name = st.session_state.get("user_name", "").strip()
        if not user_name:
            return False
            
        session_data = {
            "user_name": user_name,
            "grade_file": st.session_state.get("grade_file", ""),
            "mode": st.session_state.get("mode_select", "Learning (Ordered)"),
            "current_index": st.session_state.index,
            "stats": st.session_state.stats.copy(),
            "sequence_length": len(st.session_state.sequence),
            "timestamp": time.time(),
            "version": "2.0"
        }
        
        # Save using JavaScript directly
        js_code = f"""
        <script>
        try {{
            const sessionData = {json.dumps(session_data)};
            localStorage.setItem('spelling_trainer_session', JSON.stringify(sessionData));
            console.log('Session saved for:', sessionData.user_name);
        }} catch (e) {{
            console.error('Failed to save session:', e);
        }}
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
        return True
    except Exception as e:
        print(f"Error saving session: {e}")
        return False

def clear_saved_session():
    """Clear saved session from storage"""
    try:
        js_code = """
        <script>
        try {
            localStorage.removeItem('spelling_trainer_session');
            console.log('Session cleared');
        } catch (e) {
            console.error('Failed to clear session:', e);
        }
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
        return True
    except Exception as e:
        print(f"Error clearing session: {e}")
        return False

# -----------------------------
# Session Initialization (CHANGED: Fixed Learning mode to not always start with same word)
# -----------------------------
def init_session(words, mode, start_index=0, saved_stats=None):
    sequence = list(words)
    
    # CHANGED: For Learning (Ordered) mode, rotate the sequence so it doesn't always start with the same word
    if mode == "Learning (Ordered)":
        # Only rotate if we're starting a fresh session (not loading a saved one)
        if saved_stats is None:
            # Choose a random starting position
            random_start = random.randint(0, len(sequence) - 1)
            # Rotate the sequence so it starts at the random position
            sequence = sequence[random_start:] + sequence[:random_start]
    elif mode == "Practice (Random)":
        random.shuffle(sequence)

    st.session_state.sequence = sequence
    st.session_state.index = start_index
    st.session_state.attempts = 0
    st.session_state.revealed_letters = 0
    st.session_state.correct_on_first_try = False
    st.session_state.feedback = ""
    st.session_state.speak_word = None
    st.session_state.trigger_animation = False
    
    # Clear the answer input when initializing session
    if 'answer_input' in st.session_state:
        st.session_state.answer_input = ""
    
    # Use saved stats or initialize new ones
    if saved_stats:
        st.session_state.stats = saved_stats
    else:
        st.session_state.stats = {
            "total_words": len(sequence),
            "correct_first_try": 0,
            "correct_after_hint": 0,
            "context_used": 0,
            "total_attempts": 0,
            "score": 0
        }

# -----------------------------
# Helpers (UNCHANGED)
# -----------------------------
def current_item():
    return st.session_state.sequence[st.session_state.index]

def masked_word(word, revealed):
    return " ".join(
        letter if i < revealed else "_"
        for i, letter in enumerate(word)
    )

# -----------------------------
# Initialize TTS Manager (UNCHANGED)
# -----------------------------
@st.cache_resource
def get_tts_manager():
    manager = TTSCacheManager()
    manager.voice_options = {
        "👨‍🏫 US Male (Guy)": "en-US-GuyNeural",
        "👩‍🏫 US Female (Aria)": "en-US-AriaNeural",
        "👩‍🏫 UK Female (Sonia)": "en-GB-SoniaNeural",
        "👨‍🏫 UK Male (Ryan)": "en-GB-RyanNeural",
        "👩‍🏫 Australian Female": "en-AU-NatashaNeural",
    }
    return manager

tts_manager = get_tts_manager()

# -----------------------------
# Initialize App
# -----------------------------
st.set_page_config(page_title="Spelling Trainer Pro", layout="centered", page_icon="🔤")

# Load CSS and animations
load_css()
st.markdown(floating_particles_animation(), unsafe_allow_html=True)

# Initialize session state variables
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'show_spell_out' not in st.session_state:
    st.session_state.show_spell_out = False
if 'session_initialized' not in st.session_state:
    st.session_state.session_initialized = False

# -----------------------------
# Check for saved session ONCE at app start
# -----------------------------
if 'saved_session_checked' not in st.session_state:
    st.session_state.saved_session_checked = True
    
    # Simple JavaScript to check for saved session
    js_code = """
    <script>
    try {
        const savedData = localStorage.getItem('spelling_trainer_session');
        if (savedData) {
            const parsedData = JSON.parse(savedData);
            const savedTime = parsedData.timestamp;
            const now = Date.now() / 1000;
            const hoursDiff = (now - savedTime) / 3600;
            
            if (hoursDiff <= 24) {
                window.hasSavedSession = true;
            } else {
                localStorage.removeItem('spelling_trainer_session');
                window.hasSavedSession = false;
            }
        } else {
            window.hasSavedSession = false;
        }
    } catch (e) {
        console.error('Error checking saved session:', e);
        window.hasSavedSession = false;
    }
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
col_header1, col_header2, col_header3 = st.columns([1, 3, 1])

with col_header1:
    st.markdown("### 🔤")

with col_header2:
    st.markdown("""
    <div style='text-align:center;'>
        <h1 style='margin-bottom:0;'>Spelling Trainer Pro</h1>
        <p style='margin-top:0;color:var(--dark-muted);font-family:Fredoka One;'>
            Master Your Spelling Skills
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_header3:
    # Removed dark mode toggle
    st.empty()

# Main container
st.markdown('<div class="main">', unsafe_allow_html=True)

# -----------------------------
# Sidebar Configuration (UNCHANGED)
# -----------------------------
with st.sidebar:
    # User Name Section
    st.markdown("### 👤 Your Name")
    user_name = st.text_input(
        "Enter your name to save progress:",
        value=st.session_state.user_name,
        key="user_name_input",
        placeholder="Type your name here",
        help="Enter your name to save your progress. Progress will not be saved without a name."
    )
    
    # Update session state with user name
    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
    
    # Show save status
    if user_name.strip():
        st.success(f"✅ Progress will be saved for: **{user_name}**")
    else:
        st.warning("⚠️ Enter your name above to save your progress")
    
    st.markdown("---")
    
    st.markdown("### 📚 Grade Level")
    grade_files = sorted(LISTS_DIR.glob("grade*.txt"))
    if not grade_files:
        st.error("No spelling lists found!")
        st.stop()
    
    grade_file = st.selectbox(
        "Select grade:",
        grade_files,
        format_func=lambda p: f"Grade {p.stem[-1]}",
        key="grade_select"
    )
    
    st.markdown("### 🎮 Training Mode")
    mode = st.radio(
        "Choose mode:",
        ["Learning (Ordered)", "Practice (Random)"],
        key="mode_select"
    )
    
    with st.expander("🎤 Voice Settings", expanded=False):
        voice_name = st.selectbox(
            "Voice:",
            list(tts_manager.voice_options.keys()),
            index=0,
            key="voice_select"
        )
        tts_manager.voice = tts_manager.voice_options[voice_name]
        
        # Spell Out Toggle
        st.session_state.show_spell_out = st.checkbox(
            "Show Spell Out Button",
            value=st.session_state.show_spell_out,
            help="Show button to spell word letter by letter"
        )
        
        if st.button("Test Voice", use_container_width=True):
            tts_manager.speak_async("Welcome!")
    
    st.markdown("### 💾 Session")
    col_sess1, col_sess2 = st.columns(2)
    with col_sess1:
        save_disabled = not st.session_state.user_name.strip()
        if st.button("💾 Save Now", 
                    use_container_width=True, 
                    type="secondary", 
                    disabled=save_disabled,
                    help="Save current session" if not save_disabled else "Enter your name above to save"):
            if save_current_session():
                st.success("Progress saved!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Failed to save progress")
    
    with col_sess2:
        if st.button("🔄 New Session", use_container_width=True, type="secondary"):
            clear_saved_session()
            words = load_spelling_list(grade_file)
            init_session(words, mode)
            st.rerun()

# -----------------------------
# Initialize Session
# -----------------------------
if "sequence" not in st.session_state or st.session_state.get("grade_file") != str(grade_file):
    words = load_spelling_list(grade_file)
    if not words:
        st.error("No words found in selected list!")
        st.stop()
    
    st.session_state.grade_file = str(grade_file)
    init_session(words, mode)

# -----------------------------
# Main Game Interface (UNCHANGED)
# -----------------------------
if not st.session_state.sequence:
    st.warning("Spelling list is empty.")
    st.stop()

item = current_item()
word = item["word"]
context = item.get("context", "")

# Progress Display
col_prog1, col_prog2, col_prog3 = st.columns([2, 1, 1])
with col_prog1:
    st.markdown(f"**Word {st.session_state.index + 1} of {len(st.session_state.sequence)}**")
    progress = (st.session_state.index / len(st.session_state.sequence))
    st.progress(progress)
with col_prog2:
    st.metric("Attempts", st.session_state.attempts)
with col_prog3:
    st.metric("Score", st.session_state.stats['score'])

# Audio Controls (UNCHANGED)
st.markdown("### 🔊 Listen")
col_audio1, col_audio2, col_audio3 = st.columns(3)
with col_audio1:
    if st.button("🔊 Hear Word", use_container_width=True, type="primary"):
        tts_manager.speak_async(word)

with col_audio2:
    # ============================================================================
    # LOCKED SECTION: Context Button - DO NOT MODIFY
    # ============================================================================
    if context and context.strip():
        if st.button("🎧 Context", use_container_width=True, type="secondary"):
            tts_manager.speak_async(context)
            st.session_state.stats["context_used"] += 1
            st.info("🎧 Playing context sentence...")
    else:
        st.button("🎧 Context", 
                 disabled=True, 
                 use_container_width=True, 
                 type="secondary",
                 help="No context available for this word")
    # ============================================================================
    # END LOCKED SECTION
    # ============================================================================

with col_audio3:
    if st.session_state.show_spell_out:
        if st.button("🔤 Spell Out", use_container_width=True, type="secondary"):
            spelled = ". ".join(word.upper()) + "."
            tts_manager.speak_async(spelled)

# Word Display
display_class = ""
if st.session_state.feedback == "correct":
    display_class = "correct"
    display_text = word
elif st.session_state.feedback == "incorrect":
    display_class = "incorrect"
    display_text = masked_word(word, st.session_state.revealed_letters)
else:
    display_text = masked_word(word, st.session_state.revealed_letters)

st.markdown(f"""
<div class="word-display {display_class}">
    {display_text}
</div>
""", unsafe_allow_html=True)

# Input Section
text_input_key = f"answer_input_{st.session_state.index}"

if 'last_word_index' not in st.session_state:
    st.session_state.last_word_index = st.session_state.index

if st.session_state.last_word_index != st.session_state.index:
    if text_input_key in st.session_state:
        del st.session_state[text_input_key]
    st.session_state.last_word_index = st.session_state.index

user_input = st.text_input(
    "",
    placeholder="Type answer here...",
    key=text_input_key,
    label_visibility="collapsed",
    autocomplete="off"
)

# Action Buttons
col_actions1, col_actions2 = st.columns(2)

with col_actions1:
    if user_input and user_input.strip():
        if st.button("✅ Check Answer", 
                    use_container_width=True,
                    type="primary",
                    key="check_answer_button"):
            st.session_state.attempts += 1
            st.session_state.stats["total_attempts"] += 1
            
            if user_input.lower().strip() == word:
                st.success("✅ **Correct!** Well done!")
                st.balloons()
                st.session_state.feedback = "correct"
                
                if st.session_state.attempts == 1 and not st.session_state.revealed_letters:
                    st.session_state.correct_on_first_try = True
                    st.session_state.stats["correct_first_try"] += 1
                    st.session_state.stats["score"] += 10
                else:
                    st.session_state.stats["correct_after_hint"] += 1
                    st.session_state.stats["score"] += 5
            else:
                st.error("❌ **Try again**")
                st.session_state.feedback = "incorrect"

with col_actions2:
    if (st.session_state.feedback == "incorrect" and 
        st.session_state.revealed_letters < len(word)):
        if st.button("💡 Hint", use_container_width=True, type="secondary"):
            st.session_state.revealed_letters += 1
            st.rerun()

# Next Word Navigation - AUTO-SAVE when moving to next word
if st.session_state.feedback == "correct":
    st.markdown("---")
    col_next1, col_next2 = st.columns(2)
    
    with col_next1:
        if st.session_state.index + 1 < len(st.session_state.sequence):
            if st.button("Next Word →", use_container_width=True, type="primary"):
                # Store current word results
                word_key = f"word_{st.session_state.index}"
                st.session_state[word_key] = {
                    "correct": st.session_state.feedback == "correct",
                    "first_try": st.session_state.correct_on_first_try,
                    "hints_used": st.session_state.revealed_letters,
                    "attempts": st.session_state.attempts
                }
                
                # Auto-save progress if user has name
                if st.session_state.user_name.strip():
                    save_current_session()
                
                if text_input_key in st.session_state:
                    del st.session_state[text_input_key]
                
                st.session_state.index += 1
                st.session_state.attempts = 0
                st.session_state.revealed_letters = 0
                st.session_state.correct_on_first_try = False
                st.session_state.feedback = ""
                
                next_text_input_key = f"answer_input_{st.session_state.index}"
                if next_text_input_key in st.session_state:
                    del st.session_state[next_text_input_key]
                
                st.rerun()
    
    with col_next2:
        if st.session_state.index + 1 >= len(st.session_state.sequence):
            if st.button("🏆 Finish", use_container_width=True, type="secondary"):
                # Store final word results
                word_key = f"word_{st.session_state.index}"
                st.session_state[word_key] = {
                    "correct": st.session_state.feedback == "correct",
                    "first_try": st.session_state.correct_on_first_try,
                    "hints_used": st.session_state.revealed_letters,
                    "attempts": st.session_state.attempts
                }
                
                # Auto-save final progress if user has name
                if st.session_state.user_name.strip():
                    save_current_session()
                
                st.balloons()
                st.success("🎉 **Session Complete!**")
                
                with st.expander("📊 Session Report", expanded=True):
                    col_sum1, col_sum2 = st.columns(2)
                    with col_sum1:
                        st.metric("Total Words", st.session_state.stats["total_words"])
                        st.metric("First Try", st.session_state.stats["correct_first_try"])
                        st.metric("Context Used", st.session_state.stats["context_used"])
                    with col_sum2:
                        st.metric("Score", st.session_state.stats["score"])
                        st.metric("With Hints", st.session_state.stats["correct_after_hint"])
                
                for key in list(st.session_state.keys()):
                    if key.startswith("answer_input_"):
                        del st.session_state[key]
                
                words = load_spelling_list(grade_file)
                init_session(words, mode)
                st.rerun()

# -----------------------------
# Sidebar Stats (UNCHANGED)
# -----------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📈 Stats")
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("Score", st.session_state.stats["score"])
        st.metric("Perfect", st.session_state.stats["correct_first_try"])
    with col_stat2:
        accuracy = 0
        if st.session_state.index > 0:
            total_correct = (st.session_state.stats["correct_first_try"] + 
                           st.session_state.stats["correct_after_hint"])
            accuracy = (total_correct / st.session_state.index) * 100
        st.metric("Accuracy", f"{accuracy:.0f}%")
        st.metric("Context", st.session_state.stats["context_used"])

# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# Instructions (UNCHANGED)
with st.expander("📚 How to Play", expanded=False):
    st.markdown("""
    <div style='font-family:Fredoka One;'>
    <h3>🎯 Your Mission:</h3>
    <ol>
        <li>🔊 <b>Listen</b> to the word by clicking "Hear Word"</li>
        <li>✍️ <b>Type</b> your spelling in the box</li>
        <li>✅ <b>Check</b> your answer (button appears when you type)</li>
        <li>🚀 <b>Advance</b> to the next word when correct</li>
    </ol>
    
    <h3>💡 Help Options:</h3>
    <ul>
        <li>🔊 <b>Hear Word:</b> Listen to the word again</li>
        <li>🎧 <b>Context:</b> Hear the word used in a sentence (audio only)</li>
        <li>💡 <b>Hint:</b> Reveal one letter at a time</li>
        <li>🔤 <b>Spell Out:</b> Hear letters individually (enable in Voice Settings)</li>
    </ul>
    
    <h3>🏆 Scoring System:</h3>
    <ul>
        <li>⭐ <b>Perfect First Try:</b> 10 points</li>
        <li>✨ <b>Correct with Hints:</b> 5 points</li>
    </ul>
    
    <h3>👤 Save Feature:</h3>
    <p><b>Enter your name in the sidebar to save your progress!</b><br>
    • Progress auto-saves after each word<br>
    • Use "💾 Save Now" to manually save<br>
    • Sessions expire after 24 hours</p>
    
    <h3>⚙️ Settings:</h3>
    <p>Enable "Show Spell Out Button" in Voice Settings if you want to hear words spelled letter by letter.</p>
    
    <h3>🎧 About Context:</h3>
    <p>The Context button plays a sentence using the word. This helps you understand 
    how the word is used in real life without giving away the spelling!</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:var(--dark-muted);padding:1rem;font-size:0.9rem;'>
    Spelling Trainer Pro • Made for young learners • Inspired by AMARI
</div>
""", unsafe_allow_html=True)

# Cleanup
import atexit
@atexit.register
def cleanup():
    if pygame.mixer.get_init():
        pygame.mixer.quit()