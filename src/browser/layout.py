def layout(text: str, h_step: int, v_step: int, width: int):
    display_list = []

    cursor_x, cursor_y = h_step, v_step
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += h_step

        if cursor_x >= width - h_step:
            cursor_y += v_step
            cursor_x = h_step
    return display_list
