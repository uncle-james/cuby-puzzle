import streamlit as st

# --- STREAMLIT CONFIGURATION & PERSISTENT STATE ---
st.set_page_config(page_title="Cuby Asymmetric Logic Puzzle", layout="centered")

# Initialize persistent session states if they don't exist yet
if "num_blocks" not in st.session_state:
    st.session_state.num_blocks = 6

# Helper function to reset or initialize game state logic
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
        st.toast("⚠️ Action Invalid: The Free Slot is already occupied!", icon="❌")
        return
    top_slot, block_num = get_top_block_info(st.session_state.left_side, num_slots)
    if top_slot is None:
        st.toast("⚠️ Action Invalid: The Left side is completely empty!", icon="❌")
        return
    st.session_state.free_slot = block_num
    st.session_state.left_side[top_slot] = None

def drop_free_to_left():
    num_slots = st.session_state.num_blocks + 1
    if st.session_state.free_slot is None:
        st.toast("⚠️ Action Invalid: There is no block in the Free Slot to drop!", icon="❌")
        return
    if st.session_state.left_side[num_slots - 1] is not None:
        st.toast(f"⚠️ Action Invalid: Slot {num_slots - 1} on the Left side is blocked.", icon="❌")
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
        st.toast(f"⚠️ Action Invalid: Slot {num_slots - 1} on the {to_side} side is blocked.", icon="❌")
        return
    top_slot, block_num = get_top_block_info(from_dict, num_slots)
    if top_slot is None:
        st.toast(f"⚠️ Action Invalid: The {from_side} side is completely empty!", icon="❌")
        return
    landing_slot = calculate_landing_slot(block_num, to_dict, num_slots)
    from_dict[top_slot] = None
    to_dict[landing_slot] = block_num
    check_win()

# --- HTML/CSS RENDER HELPER ---
def render_block_html(block_idx):
    if block_idx is None:
        return '<div style="height:48px; border:2px dashed #95A5A6; background-color:#1E293B; border-radius:6px; margin:4px 0;"></div>'
    theme = get_block_theme(block_idx, st.session_state.num_blocks)
    txt_color = "black" if theme["dark_text"] else "white"
    return f"""
    <div style="height:48px; display:flex; align-items:center; justify-content:center; 
                background-color:{theme['hex']}; color:{txt_color}; font-weight:bold; 
                border-radius:6px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); margin:4px 0; font-family:sans-serif;">
        [{block_idx}] {theme['name']}
    </div>
    """

# --- USER INTERFACE DESIGN ---
st.title("Cuby Asymmetric Logic Puzzle 🧩")

# Control configuration layout
col_ctrl1, col_ctrl2 = st.columns([2, 1])
with col_ctrl1:
    new_blocks = st.slider("Select Number of Blocks:", min_value=2, max_value=12, value=st.session_state.num_blocks)
    if new_blocks != st.session_state.num_blocks:
        st.session_state.num_blocks = new_blocks
        initialize_game()
with col_ctrl2:
    st.write("##")
    if st.button("🔄 Reset Puzzle", use_container_width=True):
        initialize_game()

if st.session_state.game_won:
    st.balloons()
    st.success(f"🎉 Incredible! You successfully solved the puzzle for {st.session_state.num_blocks} blocks!")

st.markdown("---")

# --- FREE SLOT COMPONENT ---
st.markdown("<h4 style='text-align: center; margin-bottom: 2px;'>FREE SLOT (LEFT ONLY)</h4>", unsafe_allow_html=True)
f_col1, f_col2, f_col3 = st.columns([1, 2, 1])
with f_col2:
    if st.session_state.free_slot is not None:
        st.markdown(render_block_html(st.session_state.free_slot), unsafe_allow_html=True)
    else:
        st.markdown('<div style="height:48px; border:2px dashed #95A5A6; display:flex; align-items:center; justify-content:center; color:#95A5A6; font-style:italic; border-radius:6px; font-family:sans-serif;">- Empty -</div>', unsafe_allow_html=True)
    
    st.button("🔽 Drop to Left", on_click=drop_free_to_left, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- GAME COLUMNS GRID ---
num_slots = st.session_state.num_blocks + 1
grid_left, grid_mid, grid_right = st.columns([3, 1, 3])

with grid_left:
    st.markdown("<h4 style='text-align: center; color:#2980B9;'>LEFT SIDE</h4>", unsafe_allow_html=True)
    act1, act2 = st.columns(2)
    act1.button("🔼 To Free", on_click=move_left_to_free, use_container_width=True)
    act2.button("➡️ To Right", on_click=move_side_to_side, args=("Left", "Right"), use_container_width=True)
    
    for s_idx in range(num_slots - 1, -1, -1):
        st.markdown(render_block_html(st.session_state.left_side[s_idx]), unsafe_allow_html=True)

with grid_mid:
    st.markdown("<h4 style='text-align: center; color:#BDC3C7;'>SLOT</h4>", unsafe_allow_html=True)
    st.write("##") # spacing alignment
    for s_idx in range(num_slots - 1, -1, -1):
        st.markdown(f"<div style='height:48px; display:flex; align-items:center; justify-content:center; color:#BDC3C7; font-weight:bold; margin:4px 0; font-family:sans-serif;'>#{s_idx}</div>", unsafe_allow_html=True)

with grid_right:
    st.markdown("<h4 style='text-align: center; color:#E67E22;'>RIGHT SIDE</h4>", unsafe_allow_html=True)
    st.button("⬅️ To Left", on_click=move_side_to_side, args=("Right", "Left"), use_container_width=True)
    
    for s_idx in range(num_slots - 1, -1, -1):
        st.markdown(render_block_html(st.session_state.right_side[s_idx]), unsafe_allow_html=True)
