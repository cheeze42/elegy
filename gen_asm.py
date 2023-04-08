with open("out.asm", 'w+') as asm_file:
    asm_file.write(".device ATMega328P\n")
    asm_file.write(".equ DDRB = 0x04\n")
    asm_file.write(".equ PORTB = 0x05\n")
    asm_file.write(".equ DDRD = 0x0a\n")
    asm_file.write(".equ PORTD = 0x0b\n")
    asm_file.write("\n")
    asm_file.write(".org 0x000\n")
    asm_file.write("  jmp main\n\n")
    asm_file.write("main:\n")
    asm_file.write("  clr r2\n")  # Using r2 to clear pixel output
    asm_file.write("  out DDRD, r2\n")  # Pins 0-7 for pixel output
    asm_file.write("  sbi DDRB, 0\n")  # Pin 8 for horizontal sync
    asm_file.write("  sbi DDRB, 1\n")  # Pin 9 for vertical sync
    # Both sync pulses have negative polarity
    asm_file.write("  sbi PORTB, 0\n")
    asm_file.write("  sbi PORTB, 1\n")
    cpp = 2  # Cycles per pixel
    loop_time = 4  # How many cycles is our inner pixel loop?
    stretch = loop_time * cpp  # Total stretch factor
    
    # LOOP START
    asm_file.write("vga_loop:\n")

    # Last part of the previous frame
    for _ in range(128//cpp - 9):
        asm_file.write("  nop\n")

    # Pixel rows
    asm_file.write("  ldi r30, low(image_data<<1)\n")  # Load base image pointer
    asm_file.write("  ldi r31, high(image_data<<1)\n")
    asm_file.write(f"  ldi r16, {480//stretch}\n")  # Outer row counter
    asm_file.write(f"  ldi r17, {stretch}\n")
    asm_file.write("  lpm r18, Z+\n")  # Load the first pixel from memory
    asm_file.write("pixel_row_loop:\n")
    asm_file.write("pixel_row_inner:\n")
    # 640 pixel visible area
    for _ in range(640//stretch - 1):
        asm_file.write("  out PORTD, r18\n")  # Write the pixel out
        asm_file.write("  lpm r18, Z+\n")  # Load the pixel from memory
    asm_file.write("  out PORTD, r18\n")  # Write the final pixel out
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    # 24 pixel front porch
    asm_file.write("  out PORTD, r2\n")  # Clear the pixel output
    for _ in range(24//cpp - 1):
        asm_file.write("  nop\n")
    # 40 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(40//cpp - 2):
        asm_file.write("  nop\n")
    # 128 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
    for _ in range(128//cpp - 14):
        asm_file.write("  nop\n")
    asm_file.write("  dec r17\n")
    asm_file.write("  breq pixel_row_inner_done\n")
    asm_file.write(f"  subi r30, low({640//stretch})\n")
    asm_file.write(f"  sbci r31, high({640//stretch})\n")
    asm_file.write("  lpm r18, Z+\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  jmp pixel_row_inner\n")
    asm_file.write("pixel_row_inner_done:\n")
    asm_file.write(f"  ldi r17, {stretch}\n")
    asm_file.write("  dec r16\n")
    asm_file.write("  breq pixel_row_loop_done\n")
    asm_file.write("  lpm r18, Z+\n")
    asm_file.write("  jmp pixel_row_loop\n")
    asm_file.write("pixel_row_loop_done:\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")

    # Vertical front porch
    asm_file.write("  ldi r16, 24\n")
    asm_file.write("vertical_front_porch_loop:\n")
    # 640 pixel visible area + 24 pixel front porch
    for _ in range(640//cpp + 24//cpp):
        asm_file.write("  nop\n")
    # 40 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(40//cpp - 2):
        asm_file.write("  nop\n")
    # 128 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
    for _ in range(128//cpp - 7):
        asm_file.write("  nop\n")
    asm_file.write("  dec r16\n")
    asm_file.write("  breq vertical_front_porch_loop_done\n")
    asm_file.write("  jmp vertical_front_porch_loop\n")
    asm_file.write("vertical_front_porch_loop_done:\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")

    # Vertical sync
    for row_idx in range(2):
        # 640 pixel visible area + 24 pixel front porch
        if row_idx == 0:
            asm_file.write("  cbi PORTB, 1\n")  # Start the vertical pulse
        else:
            asm_file.write("  nop\n")
            asm_file.write("  nop\n")
        for _ in range(640//cpp + 24//cpp - 2):
            asm_file.write("  nop\n")
        # 40 pixel horizontal sync pulse
        asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
        for _ in range(40//cpp - 2):
            asm_file.write("  nop\n")
        # 128 pixel back porch
        asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
        for _ in range(128//cpp - 3):
            asm_file.write("  nop\n")
        if row_idx == 0:
            asm_file.write("  nop\n")
        else:
            asm_file.write("  ldi r16, 28\n")
   
    # Vertical back porch, 29 lines total
    # Lines 0 - 28
    asm_file.write("  sbi PORTB, 1\n")  # Stop the vertical pulse
    asm_file.write("  vertical_back_porch_loop:\n")
    # 640 pixel visible area + 24 pixel front porch
    for _ in range(640//cpp + 24//cpp - 2):
        asm_file.write("  nop\n")
    # 40 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(40//cpp - 2):
        asm_file.write("  nop\n")
    # 128 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
    for _ in range(128//cpp - 5):
        asm_file.write("  nop\n")
    asm_file.write("  dec r16\n")
    asm_file.write("  breq vertical_back_porch_loop_done\n")
    asm_file.write("  jmp vertical_back_porch_loop\n")
    asm_file.write("vertical_back_porch_loop_done:\n")

    # Line 28
    # 640 pixel visible area + 24 pixel front porch
    for _ in range(640//cpp + 24//cpp + 2):
        asm_file.write("  nop\n")
    # 40 pixel sync pulse
    asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
    for _ in range(40//cpp - 2):
        asm_file.write("  nop\n")
    # 128 pixel back porch
    asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
    asm_file.write("  jmp vga_loop\n")  # Restart the loop

    # Image data
    asm_file.write("\n")
    asm_file.write("image_data:\n")
    for row_idx in range(480 // stretch):
        row_start = 0x4000 - (640//stretch) * ((480 // stretch) - row_idx)
        asm_file.write(f".org {hex(row_start)}\n")
        asm_file.write(".db " + ", ".join(["0xff"] * (640//stretch)) + '\n')
