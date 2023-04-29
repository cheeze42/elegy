with open("out.asm", 'w+') as asm_file:
    asm_file.write("""\
.device ATMega328P

.equ PINB  = 0x03
.equ DDRB  = 0x04
.equ PORTB = 0x05
.equ DDRD  = 0x0a
.equ PORTD = 0x0b
""")
    asm_file.write("\n.org 0x000\n")
    asm_file.write("  jmp main\n\n")
    asm_file.write("main:\n")
    asm_file.write("  clr r20\n")  # Using r21 to clear pixel output
    asm_file.write("  ser r16\n")  # Full register for outputs
    asm_file.write("  out DDRD, r16\n")  # All outputs (although we'll only really be using one of them)
    asm_file.write("  sbi DDRB, 0\n")  # Pin 8 for horizontal sync
    asm_file.write("  sbi DDRB, 1\n")  # Pin 9 for vertical sync
    asm_file.write("  cbi DDRB, 2\n")  # Pin 10 for button input
    asm_file.write("  sbi DDRB, 3\n")  # Pin 11 for LED output
    # Both sync pulses have negative polarity
    asm_file.write("  sbi PORTB, 0\n")
    asm_file.write("  sbi PORTB, 1\n")
    asm_file.write("  sbi PORTB, 2\n")  # Pullup resistor
    asm_file.write("  cbi PORTB, 3\n")
    cpp = 2  # Cycles per pixel
    loop_time = 4  # How many cycles is our inner pixel loop?
    stretch = loop_time * cpp  # Total stretch factor
    
    # LOOP START
    asm_file.write("vga_loop:\n")

    # Last part of the previous frame
    for _ in range(120//cpp - 4 - 2*20):
        asm_file.write("  nop\n")

    # Pixel rows
    asm_file.write("  ldi r26, low(0x100)\n")  # Where SRAM starts
    asm_file.write("  ldi r27, high(0x100)\n")
    for reg_idx in range(20):
        asm_file.write(f"  ld r{reg_idx}, X+\n")
    asm_file.write(f"  ldi r21, {400//stretch}\n")  # Outer row counter
    asm_file.write(f"  ldi r22, {stretch}\n")  # Inner row counter
    asm_file.write("pixel_row_loop:\n")
    asm_file.write("pixel_row_inner:\n")
    # 640 pixel visible area
    for reg_idx in range(20):
        for _ in range(7):
            asm_file.write(f"  out PORTD, r{reg_idx}\n")
            asm_file.write(f"  lsr r{reg_idx}\n")
        asm_file.write(f"  out PORTD, r{reg_idx}\n")
        asm_file.write("  nop\n")
    # 16 pixel front porch
    asm_file.write("  out PORTD, r20\n")
    for _ in range(16//cpp - 2):
        asm_file.write("  nop\n")
    # 64 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(64//cpp - 2):
        asm_file.write("  nop\n")
    # 120 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop the hsync  # 2
    for _ in range(120//cpp - 51):
        asm_file.write("  nop\n")
    asm_file.write("  dec r22\n")                         # 1
    asm_file.write("  breq pixel_row_inner_done\n")       # 1/2
    for _ in range(51 - 7):
        asm_file.write("  nop\n")
    asm_file.write("  jmp pixel_row_inner\n")             # 3
    asm_file.write("pixel_row_inner_done:\n")
    asm_file.write(f"  ldi r22, {stretch}\n")             # 1
    asm_file.write("  dec r21\n")                         # 1
    asm_file.write("  breq pixel_row_loop_done\n")        # 1/2
    for reg_idx in range(20):                             # 40
        asm_file.write(f"  ld r{reg_idx}, X+\n")
    asm_file.write("  jmp pixel_row_loop\n")              # 3
    asm_file.write("pixel_row_loop_done:\n")
    for _ in range(51 - 10):
        asm_file.write("  nop\n")
    asm_file.write("  ldi r16, 80\n")                     # 1

    # Vertical front porch, along with 80 blank lines
    # First line
    # 640 pixel visible area + 16 pixel front porch
    asm_file.write("  sbic PINB, 2\n")  # 1/2
    asm_file.write("  sbi PORTB, 3\n")   # 2
    asm_file.write("  sbis PINB, 2\n")
    asm_file.write("  cbi PORTB, 3\n")
    for _ in range(640//cpp + 16//cpp - 4):
        asm_file.write("  nop\n")
    # 64 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(64//cpp - 2):
        asm_file.write("  nop\n")
    # 120 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop hysnc  # 2
    for _ in range(120//cpp - 2):
        asm_file.write("  nop\n")

    # Rest of the lines
    asm_file.write("front_porch_loop:\n")
    # 640 pixel visible area + 16 pixel front porch
    for _ in range(640//cpp + 16//cpp):
        asm_file.write("  nop\n")
    # 64 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(64//cpp - 2):
        asm_file.write("  nop\n")
    # 120 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop hysnc  # 2
    for _ in range(120//cpp - 7):
        asm_file.write("  nop\n")
    asm_file.write("  dec r16\n")                     # 1
    asm_file.write("  breq front_porch_loop_done\n")  # 1/2
    asm_file.write("  jmp front_porch_loop\n")        # 3
    asm_file.write("front_porch_loop_done:\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")

    # Vertical sync
    for row_idx in range(3):
        # 640 pixel visible area + 24 pixel front porch
        if row_idx == 0:
            asm_file.write("  cbi PORTB, 1\n")  # Start the vertical pulse
        else:
            asm_file.write("  nop\n")
            asm_file.write("  nop\n")
        for _ in range(640//cpp + 24//cpp - 2):
            asm_file.write("  nop\n")
        # 64 pixel horizontal sync pulse
        asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
        for _ in range(64//cpp - 2):
            asm_file.write("  nop\n")
        # 120 pixel back porch
        asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
        for _ in range(120//cpp - 3):
            asm_file.write("  nop\n")
        if row_idx != 2:
            asm_file.write("  nop\n")
        else:
            asm_file.write("  ldi r16, 15\n")
   
    # Vertical back porch, 16 lines total
    # Lines 0 - 16
    asm_file.write("  sbi PORTB, 1\n")  # Stop the vertical pulse
    asm_file.write("  vertical_back_porch_loop:\n")
    # 640 pixel visible area + 24 pixel front porch
    for _ in range(640//cpp + 24//cpp - 2):
        asm_file.write("  nop\n")
    # 64 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(64//cpp - 2):
        asm_file.write("  nop\n")
    # 120 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
    for _ in range(120//cpp - 7):
        asm_file.write("  nop\n")
    asm_file.write("  dec r16\n")
    asm_file.write("  breq vertical_back_porch_loop_done\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  jmp vertical_back_porch_loop\n")
    asm_file.write("vertical_back_porch_loop_done:\n")

    # Line 16
    # 640 pixel visible area + 16 pixel front porch
    for _ in range(640//cpp + 16//cpp + 2):
        asm_file.write("  nop\n")
    # 64 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(64//cpp - 2):
        asm_file.write("  nop\n")
    # 120 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
    asm_file.write("  jmp vga_loop\n")  # Restart the loop
