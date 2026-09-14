import streamlit as st

# --- STREAMLIT CONFIGURATION & PERSISTENT STATE ---
st.set_page_config(page_title="Cuby Asymmetric Logic Puzzle", layout="centered")

# Custom CSS to force columns to stay side-by-side even on narrow portrait mobile screens
st.markdown("""
    <style>
    [data-testid="column"] {
        min-width: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

if "num_blocks" not in st.session_state:
    st.session_state.num_blocks = 6

def initialize_game():
    N = st.session_state.num_blocks
    slots = N + 1
    st.session_state.left_side = {i: i if i < N else None for i in range(slots)}
    st.session_state.right_side = {i: None for i in range(slots)}
    st.session_state.free_slot = None
    st.session_state.game_won = False

if "left_side" not in st.session_state:
    initialize_game()

# --- THEME GENERATION ---
def get_block_theme(block_idx, num_blocks):
    crayola_box = [
        {"name": "Violet",          "hex": "#7851A9", "dark_text": False},
        {"name": "Plum",            "hex": "#8E4585", "dark_text": False},
        {"name": "Indigo",          "hex": "#4B0082", "dark_text": False},
        {"name": "Blue",            "hex": "#1F75FE", "dark_text": False},
        {"name": "Turquoise Blue",  "hex": "#77DDE7", "dark_text": True},
        {"name": "Teal Blue",       "hex": "#008080", "dark_text": False},
        {"name": "Green",           "hex": "#1CAC78", "dark_text": False},
        {"name": "Yellow Green",    "hex": "#C5E384", "dark_text": True},
        {"name": "Yellow",          "hex": "#FCE883", "dark_text": True},
        {"name": "Orange",          "hex": "#FF7538", "dark_text": False},
        {"name": "Scarlet",         "hex": "#FC2847", "dark_text": False},
        {"name": "Red",             "hex": "#EE204D", "dark_text": False}
    ]
    if num_blocks > 1:
        fraction = block_idx / (num_blocks - 1)
        idx = round(fraction * (len(crayola_box) - 1))
    else:
        idx = 0
    return crayola_box[idx]

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
    if all(st.session_state.right_side[i] == i for i in range(st.session_state.num_blocks)):
        st.session_state.game_won = True

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
    st.session_state.free_slot = block_num
    st.session_state.left_side[top_slot] = None

def drop_free_to_left():
    num_slots = st.session_state.num_blocks + 1
    if st.session_state.free_slot is None:
        st.toast("⚠️ No block to drop!", icon="❌")
        return
    if st.session_state.left_side[num_slots - 1] is not None:
        st.toast(f"⚠️ Slot {num_slots - 1} blocked.", icon="❌")
        return
    landing_slot = calculate_landing_slot(st.session_state.free_slot, st.session_state.left_side, num_slots)
    st.session_state.left_side[landing_slot] = st.session_state.free_slot
    st.session_state.free_slot = None
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
    from_dict[top_slot] = None
    to_dict[landing_slot] = block_num
    check_win()

# --- HTML/CSS RENDER HELPER (COMPACT FOR MOBILE) ---
def render_block_html(block_idx):
    if block_idx is None:
        return '<div style="height:30px; border:1px dashed #95A5A6; background-color:#1E293B; border-radius:4px; margin:2px 0;"></div>'
    theme = get_block_theme(block_idx, st.session_state.num_blocks)
    txt_color = "black" if theme["dark_text"] else "white"
    return f"""
    <div style="height:30px; display:flex; align-items:center; justify-content:center; 
                background-color:{theme['hex']}; color:{txt_color}; font-weight:bold; font-size:12px;
                border-radius:4px; box-shadow: 0px 2px 4px rgba(0,0,0,0.1); margin:2px 0; font-family:sans-serif;">
        [{block_idx}] {theme['name']}
    </div>
    """

# --- USER INTERFACE DESIGN ---
st.title("Cuby Puzzle 🧩")

# Config and settings
col_ctrl1, col_ctrl2 = st.columns([2, 1])
with col_ctrl1:
    new_blocks = st.slider("Blocks:", min_value=2, max_value=12, value=st.session_state.num_blocks, label_visibility="collapsed")
    if new_blocks != st.session_state.num_blocks:
        st.session_state.num_blocks = new_blocks
        initialize_game()
with col_ctrl2:
    if st.button("🔄 Reset", use_container_width=True):
        initialize_game()

if st.session_state.game_won:
    st.balloons()
    st.success(f"🎉 Solved for {st.session_state.num_blocks} blocks!")

# --- 1. ACTION CONTROLS PANEL ---
st.markdown("<h6 style='margin:0;'>🎮 Action Controls</h6>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1.2])
with btn_col1:
    st.button("🔼 Free", on_click=move_left_to_free, use_container_width=True, help="Left to Free")
with btn_col2:
    st.button("➡️ Right", on_click=move_side_to_side, args=("Left", "Right"), use_container_width=True, help="Left to Right")
with btn_col3:
    st.button("⬅️ Left", on_click=move_side_to_side, args=("Right", "Left"), use_container_width=True, help="Right to Left")
with btn_col4:
    st.button("🔽 Drop", on_click=drop_free_to_left, use_container_width=True, help="Drop Free to Left")

# --- 2. FREE SLOT DISPLAY ---
st.markdown("<div style='text-align: center; font-size:11px; color:#BDC3C7; font-weight:bold;'>FREE SLOT</div>", unsafe_allow_html=True)
_, f_mid, _ = st.columns([1, 2, 1])
with f_mid:
    if st.session_state.free_slot is not None:
        st.markdown(render_block_html(st.session_state.free_slot), unsafe_allow_html=True)
    else:
        st.markdown('<div style="height:30px; border:1px dashed #95A5A6; display:flex; align-items:center; justify-content:center; color:#95A5A6; font-size:11px; font-style:italic; border-radius:4px; font-family:sans-serif; margin-bottom:10px;">- Empty -</div>', unsafe_allow_html=True)

# --- 3. UNIFIED GAME BOARD GRID ---
num_slots = st.session_state.num_blocks + 1

# Column headers
hdr_l, hdr_m, hdr_r = st.columns([3, 1, 3])
hdr_l.markdown("<div style='text-align: center; color:#2980B9; font-weight:bold; font-size:12px;'>LEFT</div>", unsafe_allow_html=True)
hdr_m.markdown("<div style='text-align: center; color:#BDC3C7; font-weight:bold; font-size:12px;'>SLOT</div>", unsafe_allow_html=True)
hdr_r.markdown("<div style='text-align: center; color:#E67E22; font-weight:bold; font-size:12px;'>RIGHT</div>", unsafe_allow_html=True)

# Render compact side-by-side rows
for s_idx in range(num_slots - 1, -1, -1):
    col_l, col_m, col_r = st.columns([3, 1, 3])
    with col_l:
        st.markdown(render_block_html(st.session_state.left_side[s_idx]), unsafe_allow_html=True)
    with col_m:
        st.markdown(f"<div style='height:30px; display:flex; align-items:center; justify-content:center; color:#BDC3C7; font-weight:bold; font-size:11px; font-family:sans-serif;'>#{s_idx}</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown(render_block_html(st.session_state.right_side[s_idx]), unsafe_allow_html=True)
