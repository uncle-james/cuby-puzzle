import streamlit as st
from collections import deque

# --- CONFIGURATION & CONSTANTS ---
CONFIG = {
    "BLOCK_HEIGHT": 30,
    "BLOCK_MARGIN": "2px 0",
    "BORDER_RADIUS": "4px",
    "SHADOW": "0px 2px 4px rgba(0,0,0,0.1)",
    "FONT_SIZE_BLOCK": "12px",
    "FONT_SIZE_LABEL": "11px",
    "COLORS": {
        "border_dashed": "#95A5A6",
        "bg_dark": "#1E293B",
        "text_secondary": "#BDC3C7",
        "header_left": "#2980B9",
        "header_right": "#E67E22",
    },
    "CRAYOLA_COLORS": [
        {"name": "Violet",          "hex": "#7851A9", "dark_text": False},
        {"name": "Plum",            "hex": "#8E4585", "dark_text": False},
        {"name": "Indigo",          "hex": "#4B0082", "dark_text": False},
        {"name": "Blue",            "hex": "#1F75FE", "dark_text": False},
        {"name": "Turquoise Blue",  "hex": "#77DDE7", "dark_text": True},
        {"name": "Teal Blue",       "hex": "#008080", "dark_text": False},
        {"name": "Green",           "hex": "#1CAC78", "dark_text": False},
        {"name": "Yellow Green",    "hex": "#9FD356", "dark_text": True},
        {"name": "Golden Yellow",   "hex": "#FFD700", "dark_text": True},
        {"name": "Orange",          "hex": "#FF7538", "dark_text": False},
        {"name": "Scarlet",         "hex": "#FC2847", "dark_text": False},
        {"name": "Red",             "hex": "#EE204D", "dark_text": False}
    ],
}

# --- STREAMLIT CONFIGURATION & PERSISTENT STATE ---
st.set_page_config(page_title="Cuby Asymmetric Logic Puzzle", layout="wide")

def inject_styles():
    """Inject all CSS styles at once for better maintainability."""
    st.markdown(f"""
        <style>
        /* REMOVED the broken data-testid column property that was collapsing the width */
        
        .block-container {{
            height: {block_height}px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: {CONFIG['FONT_SIZE_BLOCK']};
            border-radius: {CONFIG['BORDER_RADIUS']};
            box-shadow: {CONFIG['SHADOW']};
            margin: {CONFIG['BLOCK_MARGIN']};
            font-family: sans-serif;
        }}
        .block-empty {{
            height: {block_height}px;
            border: 1px dashed {CONFIG['COLORS']['border_dashed']};
            background-color: {CONFIG['COLORS']['bg_dark']};
            border-radius: {CONFIG['BORDER_RADIUS']};
            margin: {CONFIG['BLOCK_MARGIN']};
        }}
        .block-empty-free {{
            height: {block_height}px;
            border: 1px dashed {CONFIG['COLORS']['border_dashed']};
            display: flex;
            align-items: center;
            justify-content: center;
            color: {CONFIG['COLORS']['border_dashed']};
            font-size: {CONFIG['FONT_SIZE_LABEL']};
            font-style: italic;
            border-radius: {CONFIG['BORDER_RADIUS']};
            margin: {CONFIG['BLOCK_MARGIN']};
        }}
        .slot-label {{
            height: {block_height}px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: {CONFIG['COLORS']['text_secondary']};
            font-weight: bold;
            font-size: {CONFIG['FONT_SIZE_LABEL']};
            font-family: sans-serif;
        }}
        .header {{
            font-weight: bold;
            font-size: {CONFIG['FONT_SIZE_BLOCK']};
        }}
        .header-left {{
            text-align: center;
            color: {CONFIG['COLORS']['header_left']};
        }}
        .header-right {{
            text-align: center;
            color: {CONFIG['COLORS']['header_right']};
        }}
        .header-center {{
            text-align: center;
            color: {CONFIG['COLORS']['text_secondary']};
        }}
        .action-buttons {{
            margin-top: 25px !important;
        }}
        </style>
    """, unsafe_allow_html=True)

inject_styles()

if "num_blocks" not in st.session_state:
    st.session_state.num_blocks = 6

if "move_history" not in st.session_state:
    st.session_state.move_history = deque(maxlen=50)

if "move_count" not in st.session_state:
    st.session_state.move_count = 0

def initialize_game():
    N = st.session_state.num_blocks
    num_slots = N + 1
    st.session_state.left_side = {i: i if i < N else None for i in range(num_slots)}
    st.session_state.right_side = {i: None for i in range(num_slots)}
    st.session_state.free_slot = None
    st.session_state.game_won = False
    st.session_state.move_history.clear()
    st.session_state.move_count = 0

if "left_side" not in st.session_state:
    initialize_game()

# --- THEME GENERATION ---
def get_block_theme(block_idx, num_blocks):
    colors = CONFIG["CRAYOLA_COLORS"]
    if num_blocks > 1:
        fraction = block_idx / (num_blocks - 1)
        idx = round(fraction * (len(colors) - 1))
    else:
        idx = 0
    return colors[idx]

# --- PUZZLE CORE LOGIC UTILITIES ---
def get_top_block_info(side_dict, num_slots):
    for slot_idx in range(num_slots - 1, -1, -1):
        if side_dict[slot_idx] is not None:
            return slot_idx, side_dict[slot_idx]
    return None, None

def calculate_landing_slot(block_num, side_dict, num_slots):
    highest_occupied = -1
    for slot_idx in range(num_slots - 1, -1, -1):
        if side_dict[slot_idx] is not None:
            highest_occupied = slot_idx
            break
    return max(block_num, highest_occupied + 1)

def check_win():
    num_blocks = st.session_state.num_blocks
    if all(st.session_state.right_side[i] == i for i in range(num_blocks)):
        st.session_state.game_won = True

def save_move_state(description):
    """Save game state to history for undo functionality."""
    state = {
        "description": description,
        "left_side": st.session_state.left_side.copy(),
        "right_side": st.session_state.right_side.copy(),
        "free_slot": st.session_state.free_slot,
    }
    st.session_state.move_history.append(state)

def undo_move():
    """Restore the last game state."""
    if len(st.session_state.move_history) == 0:
        st.toast("⚠️ No moves to undo!", icon="❌")
        return
    state = st.session_state.move_history.pop()
    st.session_state.left_side = state["left_side"]
    st.session_state.right_side = state["right_side"]
    st.session_state.free_slot = state["free_slot"]
    st.session_state.move_count = max(0, st.session_state.move_count - 1)
    st.session_state.game_won = False

# --- ACTION LOGIC HANDLERS ---
def move_left_to_free():
    num_slots = st.session_state.num_blocks + 1
    if st.session_state.free_slot is not None:
        st.toast("⚠️ Free Slot occupied!", icon="❌")
        return
    top_slot, block_num = get_top_block_info(st.session_state.left_side, num_slots)
    if top_slot is None:
        st.toast("⚠️ Left side empty!", icon="❌")
        return
    save_move_state("Moved block to free slot")
    st.session_state.free_slot = block_num
    st.session_state.left_side[top_slot] = None
    st.session_state.move_count += 1
import streamlit as st
from collections import deque
import copy
from streamlit.components.v1 import html

# --- CONFIGURATION & CONSTANTS ---
CONFIG = {
    "BLOCK_MARGIN": "2px 0",
    "BORDER_RADIUS": "4px",
    "SHADOW": "0px 2px 4px rgba(0,0,0,0.1)",
    "FONT_SIZE_BLOCK": "12px",
    "FONT_SIZE_LABEL": "11px",
    "COLORS": {
        "border_dashed": "#95A5A6",
        "bg_dark": "#1E293B",
        "text_secondary": "#BDC3C7",
        "header_left": "#2980B9",
        "header_right": "#E67E22",
    },
    "CRAYOLA_COLORS": [
        {"name": "Violet",          "hex": "#7851A9", "dark_text": False},
        {"name": "Plum",            "hex": "#8E4585", "dark_text": False},
        {"name": "Indigo",          "hex": "#4B0082", "dark_text": False},
        {"name": "Blue",            "hex": "#1F75FE", "dark_text": False},
        {"name": "Turquoise Blue",  "hex": "#77DDE7", "dark_text": True},
        {"name": "Teal Blue",       "hex": "#008080", "dark_text": False},
        {"name": "Green",           "hex": "#1CAC78", "dark_text": False},
        {"name": "Yellow Green",    "hex": "#9FD356", "dark_text": True},
        {"name": "Golden Yellow",   "hex": "#FFD700", "dark_text": True},
        {"name": "Orange",          "hex": "#FF7538", "dark_text": False},
        {"name": "Scarlet",         "hex": "#FC2847", "dark_text": False},
        {"name": "Red",             "hex": "#EE204D", "dark_text": False}
    ],
}

# --- STREAMLIT CONFIGURATION & PERSISTENT STATE ---
st.set_page_config(page_title="Cuby Asymmetric Logic Puzzle", layout="wide")

if "num_blocks" not in st.session_state:
    st.session_state.num_blocks = 6

if "move_history" not in st.session_state:
    st.session_state.move_history = deque(maxlen=50)

if "move_count" not in st.session_state:
    st.session_state.move_count = 0

# --- DYNAMIC GRID SCALING CALCULATOR ---
# Shrink block heights dynamically as the board size grows so players don't have to scroll
current_n = st.session_state.num_blocks
if current_n <= 4:
    block_height = 42
elif current_n <= 7:
    block_height = 32
else:
    block_height = 24

def inject_styles():
    """Inject all CSS styles dynamically using the computed block height."""
    st.markdown(f"""
        <style>
        [data-testid="column"] {{
            min-width: 0px !important;
        }}
        .block-container {{
            height: {block_height}px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: {CONFIG['FONT_SIZE_BLOCK']};
            border-radius: {CONFIG['BORDER_RADIUS']};
            box-shadow: {CONFIG['SHADOW']};
            margin: {CONFIG['BLOCK_MARGIN']};
            font-family: sans-serif;
        }}
        .block-empty {{
            height: {block_height}px;
            border: 1px dashed {CONFIG['COLORS']['border_dashed']};
            background-color: {CONFIG['COLORS']['bg_dark']};
            border-radius: {CONFIG['BORDER_RADIUS']};
            margin: {CONFIG['BLOCK_MARGIN']};
        }}
        .block-empty-free {{
            height: {block_height}px;
            border: 1px dashed {CONFIG['COLORS']['border_dashed']};
            display: flex;
            align-items: center;
            justify-content: center;
            color: {CONFIG['COLORS']['border_dashed']};
            font-size: {CONFIG['FONT_SIZE_LABEL']};
            font-style: italic;
            border-radius: {CONFIG['BORDER_RADIUS']};
            margin: {CONFIG['BLOCK_MARGIN']};
        }}
        .slot-label {{
            height: {block_height}px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: {CONFIG['COLORS']['text_secondary']};
            font-weight: bold;
            font-size: {CONFIG['FONT_SIZE_LABEL']};
            font-family: sans-serif;
        }}
        .header {{
            font-weight: bold;
            font-size: {CONFIG['FONT_SIZE_BLOCK']};
        }}
        .header-left {{
            text-align: center;
            color: {CONFIG['COLORS']['header_left']};
        }}
        .header-right {{
            text-align: center;
            color: {CONFIG['COLORS']['header_right']};
        }}
        .header-center {{
            text-align: center;
            color: {CONFIG['COLORS']['text_secondary']};
        }}
        .action-buttons {{
            margin-top: 25px !important;
        }}
        </style>
    """, unsafe_allow_html=True)

inject_styles()

def initialize_game():
    N = st.session_state.num_blocks
    num_slots = N + 1
    st.session_state.left_side = {i: i if i < N else None for i in range(num_slots)}
    st.session_state.right_side = {i: None for i in range(num_slots)}
    st.session_state.free_slot = None
    st.session_state.game_won = False
    st.session_state.move_history.clear()
    st.session_state.move_count = 0

if "left_side" not in st.session_state:
    initialize_game()
# --- THEME GENERATION ---
def get_block_theme(block_idx, num_blocks):
    colors = CONFIG["CRAYOLA_COLORS"]
    if num_blocks > 1:
        fraction = block_idx / (num_blocks - 1)
        idx = round(fraction * (len(colors) - 1))
    else:
        idx = 0
    return colors[idx]

# --- PUZZLE CORE LOGIC UTILITIES ---
def get_top_block_info(side_dict, num_slots):
    for slot_idx in range(num_slots - 1, -1, -1):
        if side_dict[slot_idx] is not None:
            return slot_idx, side_dict[slot_idx]
    return None, None

def calculate_landing_slot(block_num, side_dict, num_slots):
    highest_occupied = -1
    for slot_idx in range(num_slots - 1, -1, -1):
        if side_dict[slot_idx] is not None:
            highest_occupied = slot_idx
            break
    return max(block_num, highest_occupied + 1)

def check_win():
    num_blocks = st.session_state.num_blocks
    if all(st.session_state.right_side[i] == i for i in range(num_blocks)):
        st.session_state.game_won = True

def save_move_state(description):
    state = {
        "description": description,
        "left_side": copy.deepcopy(st.session_state.left_side),
        "right_side": copy.deepcopy(st.session_state.right_side),
        "free_slot": st.session_state.free_slot,
    }
    st.session_state.move_history.append(state)

def undo_move():
    if len(st.session_state.move_history) == 0:
        st.toast("⚠️ No moves to undo!", icon="❌")
        return
    state = st.session_state.move_history.pop()
    st.session_state.left_side = state["left_side"]
    st.session_state.right_side = state["right_side"]
    st.session_state.free_slot = state["free_slot"]
    st.session_state.move_count = max(0, st.session_state.move_count - 1)
    st.session_state.game_won = False

# --- ACTION LOGIC HANDLERS ---
def move_left_to_free():
    num_slots = st.session_state.num_blocks + 1
    if st.session_state.free_slot is not None:
        st.toast("⚠️ Free Slot occupied!", icon="❌")
        return
    top_slot, block_num = get_top_block_info(st.session_state.left_side, num_slots)
    if top_slot is None:
        st.toast("⚠️ Left side empty!", icon="❌")
        return
    save_move_state("Moved block to free slot")
    st.session_state.free_slot = block_num
    st.session_state.left_side[top_slot] = None
    st.session_state.move_count += 1

def drop_free_to_left():
    num_slots = st.session_state.num_blocks + 1
    if st.session_state.free_slot is None:
        st.toast("⚠️ No block to drop!", icon="❌")
        return
    if st.session_state.left_side[num_slots - 1] is not None:
        st.toast(f"⚠️ Slot {num_slots - 1} blocked.", icon="❌")
        return
    landing_slot = calculate_landing_slot(st.session_state.free_slot, st.session_state.left_side, num_slots)
    save_move_state("Dropped block to left")
    st.session_state.left_side[landing_slot] = st.session_state.free_slot
    st.session_state.free_slot = None
    st.session_state.move_count += 1
    check_win()

def move_side_to_side(from_side, to_side):
    num_slots = st.session_state.num_blocks + 1
    from_dict = st.session_state.left_side if from_side == "Left" else st.session_state.right_side
    to_dict = st.session_state.right_side if from_side == "Left" else st.session_state.left_side
    
    if to_dict[num_slots - 1] is not None:
        st.toast(f"⚠️ {to_side} side blocked.", icon="❌")
        return
    top_slot, block_num = get_top_block_info(from_dict, num_slots)
    if top_slot is None:
        st.toast(f"⚠️ {from_side} side empty!", icon="❌")
        return
    landing_slot = calculate_landing_slot(block_num, to_dict, num_slots)
    save_move_state(f"Moved block from {from_side} to {to_side}")
    from_dict[top_slot] = None
    to_dict[landing_slot] = block_num
    st.session_state.move_count += 1
    check_win()

# --- HTML RENDER HELPERS ---
def render_block_html(block_idx):
    if block_idx is None:
        return '<div class="block-empty"></div>'
    theme = get_block_theme(block_idx, st.session_state.num_blocks)
    txt_color = "black" if theme["dark_text"] else "white"
    return f"""
    <div class="block-container" style="background-color:{theme['hex']}; color:{txt_color};">
        [{block_idx}] {theme['name']}
    </div>
    """

def render_empty_free_slot():
    return '<div class="block-empty-free">Empty</div>'

# --- USER INTERFACE DESIGN ---
st.title("Cuby Puzzle 🧩")

# Clean configurations row
st.markdown("### Puzzle Configurations")
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
with col_ctrl1:
    new_blocks = st.slider(
        "Choose Number of Blocks:", 
        min_value=2, 
        max_value=12, 
        value=st.session_state.num_blocks
    )
    if new_blocks != st.session_state.num_blocks:
        st.session_state.num_blocks = new_blocks
        initialize_game()
        st.rerun()

with col_ctrl2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Reset Board", use_container_width=True):
        initialize_game()
        st.rerun()
with col_ctrl3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    has_history = len(st.session_state.move_history) > 0
    if st.button("↶ Undo Move", disabled=not has_history, use_container_width=True):
        undo_move()
        st.rerun()

# Dynamic exponential warnings
if st.session_state.num_blocks >= 8:
    st.warning(f"💡 High difficulty active! An optimal solution for {st.session_state.num_blocks} blocks requires at least {2**(st.session_state.num_blocks+1) - st.session_state.num_blocks - 2} perfect moves.")

# Display win condition
if st.session_state.game_won:
    st.balloons()
    st.success(f"🎉 Solved for {st.session_state.num_blocks} blocks in {st.session_state.move_count} moves!")

# Display move counter
st.markdown(f"<div style='text-align: center; color:{CONFIG['COLORS']['text_secondary']}; font-size:14px; margin-top:15px;'>Moves Executed: <strong>{st.session_state.move_count}</strong></div>", unsafe_allow_html=True)

# --- KEYBOARD SHORTCUTS INTERCEPTOR ---
html("""
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    const key = e.key.toLowerCase();
    let btnLabel = "";
    if (key === 'w') btnLabel = "🔼 Free (W)";
    if (key === 'd') btnLabel = "➡️ Right (D)";
    if (key === 'a') btnLabel = "⬅️ Left (A)";
    if (key === 's') btnLabel = "🔽 Drop (S)";
    
    if (btnLabel) {
        const buttons = Array.from(doc.querySelectorAll('button'));
        const targetBtn = buttons.find(el => el.innerText.includes(btnLabel));
        if (targetBtn) {
            targetBtn.click();
        }
    }
});
</script>
""", height=0)

# --- 1. ACTION CONTROLS PANEL ---
st.markdown(f"<div class='action-buttons'><h6 style='margin:0;'>🎮 Action Controls (Click or tap W, A, S, D)</h6></div>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
with btn_col1:
    st.button("🔼 Free (W)", on_click=move_left_to_free, use_container_width=True)
with btn_col2:
    st.button("➡️ Right (D)", on_click=move_side_to_side, args=("Left", "Right"), use_container_width=True)
with btn_col3:
    st.button("⬅️ Left (A)", on_click=move_side_to_side, args=("Right", "Left"), use_container_width=True)
with btn_col4:
    st.button("🔽 Drop (S)", on_click=drop_free_to_left, use_container_width=True)

# --- 2. FREE SLOT DISPLAY ---
st.markdown(f"<div style='text-align: center; font-size:{CONFIG['FONT_SIZE_LABEL']}; color:{CONFIG['COLORS']['text_secondary']}; font-weight:bold; margin-top:15px;'>FREE SLOT</div>", unsafe_allow_html=True)
_, f_mid, _ = st.columns(3)
with f_mid:
    if st.session_state.free_slot is not None:
        st.markdown(render_block_html(st.session_state.free_slot), unsafe_allow_html=True)
    else:
        st.markdown(render_empty_free_slot(), unsafe_allow_html=True)

# --- 3. UNIFIED GAME BOARD GRID ---
num_slots = st.session_state.num_blocks + 1

# Column headers
hdr_l, hdr_m, hdr_r = st.columns(3)
hdr_l.markdown(f"<div class='header header-left'>LEFT</div>", unsafe_allow_html=True)
hdr_m.markdown(f"<div class='header header-center'>SLOT</div>", unsafe_allow_html=True)
hdr_r.markdown(f"<div class='header header-right'>RIGHT</div>", unsafe_allow_html=True)

# Render compact side-by-side rows
for s_idx in range(num_slots - 1, -1, -1):
    col_l, col_m, col_r = st.columns(3)
    with col_l:
        st.markdown(render_block_html(st.session_state.left_side[s_idx]), unsafe_allow_html=True)
    with col_m:
        st.markdown(f"<div class='slot-label'>#{s_idx}</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown(render_block_html(st.session_state.right_side[s_idx]), unsafe_allow_html=True)
